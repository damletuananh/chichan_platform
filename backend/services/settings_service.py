import time
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException
from repositories import settings_repository, forum_repository
from models.course import Course
from models.user import User
from uuid import UUID

# Bộ nhớ tạm (In-memory TTL Cache) giảm thiểu round-trip mạng tới Supabase Cloud
_home_cache = None
_home_cache_time = 0.0
_about_cache = None
_about_cache_time = 0.0
CACHE_TTL_SECONDS = 30.0

def invalidate_settings_cache():
    global _home_cache, _home_cache_time, _about_cache, _about_cache_time
    _home_cache = None
    _home_cache_time = 0.0
    _about_cache = None
    _about_cache_time = 0.0

async def get_all_settings_list(db: AsyncSession):
    return await settings_repository.get_all_settings(db)

async def update_site_setting(db: AsyncSession, key_name: str, value_content: str, description: str = None):
    updated = await settings_repository.update_setting(db, key_name, value_content, description)
    invalidate_settings_cache()
    return {
        "key_name": updated.key_name,
        "updated_at": updated.updated_at
    }

async def get_home_page_data(db: AsyncSession):
    global _home_cache, _home_cache_time
    now = time.time()
    if _home_cache is not None and (now - _home_cache_time) < CACHE_TTL_SECONDS:
        return _home_cache

    # 1. Lấy cấu hình hero banner chỉ trong 1 truy vấn SQL (thay vì 2 truy vấn tuần tự)
    settings_map = await settings_repository.get_settings_by_keys(
        db, ["home_hero_title", "home_hero_subtitle"]
    )
    hero_title = settings_map.get(
        "home_hero_title",
        "Nền tảng Giáo dục Giới tính Trực tuyến An toàn & Khoa học"
    )
    hero_sub = settings_map.get(
        "home_hero_subtitle",
        "Đồng hành cùng thanh thiếu niên và phụ huynh Việt Nam xây dựng nhận thức đúng đắn."
    )

    # 2. Lấy toàn bộ khóa học công khai trong 1 truy vấn duy nhất (thay vì 2 lượt PARENT & CHILD riêng biệt)
    courses_query = (
        select(Course)
        .options(
            selectinload(Course.lessons),
            joinedload(Course.instructor).joinedload(User.role),
            joinedload(Course.instructor).joinedload(User.profile)
        )
        .where(Course.is_published == True)
        .order_by(Course.created_at.desc())
        .limit(16)
    )
    courses_result = await db.execute(courses_query)
    all_courses = courses_result.scalars().all()

    parent_list = []
    child_list = []
    for c in all_courses:
        item = {
            "id": str(c.id),
            "title": c.title,
            "thumbnail_url": c.thumbnail_url,
            "instructor_name": c.instructor.full_name if c.instructor else "Unknown",
            "total_lessons": len(c.lessons) if c.lessons else 0
        }
        if c.target_audience in ("PARENT", "BOTH") and len(parent_list) < 6:
            parent_list.append(item)
        if c.target_audience in ("CHILD", "BOTH") and len(child_list) < 6:
            child_list.append(item)

    # 3. Lấy bài viết diễn đàn gần nhất và đếm comment trong 1 nhóm
    posts = await forum_repository.get_posts(db, include_hidden_deleted=False, limit=4)
    comment_counts = await forum_repository.count_comments_for_posts(db, [p.id for p in posts])
    recent_posts = []
    for p in posts:
        comment_count = comment_counts.get(p.id, 0)
        is_anon = p.is_anonymous
        author_name = "Người dùng ẩn danh" if is_anon else (p.author.full_name if p.author else "Unknown")
        author_avatar = None if is_anon else (p.author.profile.avatar_url if p.author and p.author.profile else None)
        short_content = (p.content[:140] + "...") if len(p.content) > 140 else p.content
        recent_posts.append({
            "id": str(p.id),
            "title": p.title,
            "short_content": short_content,
            "category_name": p.category.name if p.category else "Thảo luận chung",
            "author_name": author_name,
            "author_avatar": author_avatar,
            "is_anonymous": is_anon,
            "likes_count": p.likes_count or 0,
            "comment_count": comment_count,
            "created_at": p.created_at
        })

    data = {
        "hero_banner": {
            "title": hero_title,
            "subtitle": hero_sub
        },
        "parent_courses": parent_list,
        "child_courses": child_list,
        "recent_forum_posts": recent_posts
    }

    _home_cache = data
    _home_cache_time = time.time()
    return data

async def get_about_us_data(db: AsyncSession):
    global _about_cache, _about_cache_time
    now = time.time()
    if _about_cache is not None and (now - _about_cache_time) < CACHE_TTL_SECONDS:
        return _about_cache

    # Lấy toàn bộ cấu hình trang About trong 1 truy vấn duy nhất (thay vì 4 truy vấn tuần tự)
    keys = [
        "about_us_research_title",
        "about_us_research_purpose",
        "about_us_methodology",
        "about_us_authors_json"
    ]
    settings_map = await settings_repository.get_settings_by_keys(db, keys)

    title_val = settings_map.get(
        "about_us_research_title",
        "Nghiên cứu và Ứng dụng Nền tảng E-learning trong Phổ biến Kiến thức Giáo dục Giới tính tại Việt Nam"
    )
    purpose_val = settings_map.get(
        "about_us_research_purpose",
        "Đề tài hướng tới việc xóa bỏ các rào cản tâm lý e ngại, cung cấp nguồn học liệu chuẩn y khoa, giúp thanh thiếu niên chủ động bảo vệ bản thân và phụ huynh có kỹ năng đồng hành cùng con."
    )
    method_val = settings_map.get(
        "about_us_methodology",
        "Kết hợp học tập trực tuyến cá nhân hóa theo nhóm đối tượng và diễn đàn trao đổi an toàn."
    )
    authors_json = settings_map.get("about_us_authors_json")

    authors = []
    if authors_json:
        try:
            authors = json.loads(authors_json)
        except Exception:
            authors = [{"name": "Nhóm Nghiên cứu Khoa học", "role": "Tác giả & Phát triển Nền tảng", "contact": "research.chichan@example.edu.vn"}]
    else:
        authors = [{"name": "Nhóm Nghiên cứu Khoa học", "role": "Tác giả & Phát triển Nền tảng", "contact": "research.chichan@example.edu.vn"}]

    data = {
        "research_title": title_val,
        "research_purpose": purpose_val,
        "methodology": method_val,
        "authors": authors
    }

    _about_cache = data
    _about_cache_time = time.time()
    return data
