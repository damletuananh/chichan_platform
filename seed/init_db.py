# -*- coding: utf-8 -*-
"""
Script Khởi tạo và Nạp dữ liệu Toàn diện cho ChiChan Platform (Data-Driven Architecture)
Cơ sở dữ liệu cục bộ: database/chichan.db
Nguồn học liệu JSON: seed/data/courses/, seed/data/forum/, seed/data/activity/
"""
import sys
import os
import glob
import asyncio
import uuid
import json
from datetime import datetime, timezone

# Đảm bảo import được module backend
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import select, text
from core.database import engine, AsyncSessionLocal, Base
from core.config import settings

# Import models để SQLAlchemy đăng ký đầy đủ metadata
import models.role
import models.user
import models.profile
import models.session
import models.course
import models.lesson
import models.course_enrollment
import models.lesson_progress
import models.forum
import models.site_setting
import models.quiz
import models.ai_scenario
import models.ai_session
import models.ai_message
import models.ai_knowledge_vector
import models.ai_game_evaluation

from models.role import Role
from models.user import User
from models.profile import UserProfile
from models.site_setting import SiteSetting
from models.forum import ForumCategory, ForumPost, ForumComment
from models.ai_scenario import AIScenario
from models.ai_knowledge_vector import AIKnowledgeVector
from models.course import Course
from models.lesson import Lesson
from models.quiz import Quiz, QuizQuestion, QuizQuestionOption, QuizSubmission
from models.course_enrollment import CourseEnrollment
from models.lesson_progress import LessonProgress

# Hash mật khẩu "123456" chuẩn bcrypt
DEFAULT_PASSWORD_HASH = "$2b$12$wUFmsMz9qzVOisDjoVIkUe09FbhpOpt0zq9AtynI9iqyGyFr7oe6."

# Fixed UUIDs cho các tài khoản mẫu
ID_ADMIN = uuid.UUID("a0000000-0000-0000-0000-000000000001")
ID_DR_LANANH = uuid.UUID("b0000000-0000-0000-0000-000000000002")
ID_PHUHUYNH_MAI = uuid.UUID("c0000000-0000-0000-0000-000000000003")
ID_HOCSINH_MINH = uuid.UUID("d0000000-0000-0000-0000-000000000004")
ID_THAY_HOANG = uuid.UUID("b0000000-0000-0000-0000-000000000005")
ID_CHUYENGIA_ANHTUAN = uuid.UUID("b0000000-0000-0000-0000-000000000006")
ID_PHUHUYNH_HUNG = uuid.UUID("c0000000-0000-0000-0000-000000000007")
ID_PHUHUYNH_THANH = uuid.UUID("c0000000-0000-0000-0000-000000000008")
ID_HOCSINH_LINH = uuid.UUID("d0000000-0000-0000-0000-000000000009")
ID_HOCSINH_KHOA = uuid.UUID("d0000000-0000-0000-0000-000000000010")

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))


async def init_schema(drop_existing: bool = True):
    """Khởi tạo cấu trúc schema sạch sẽ"""
    print("=" * 65)
    print("1. KHỞI TẠO CẤU TRÚC BẢNG (SCHEMA)")
    print(f"   Database target: {settings.resolved_database_url}")
    print("=" * 65)

    async with engine.begin() as conn:
        if drop_existing:
            print("▶ Đang xóa các bảng cũ nếu tồn tại...")
            if "sqlite" in settings.resolved_database_url:
                await conn.execute(text("PRAGMA foreign_keys = OFF;"))
            await conn.run_sync(Base.metadata.drop_all)
            if "sqlite" in settings.resolved_database_url:
                await conn.execute(text("PRAGMA foreign_keys = ON;"))

        print("▶ Đang tạo mới toàn bộ các bảng...")
        await conn.run_sync(Base.metadata.create_all)

    print("✔ Đã tạo thành công schema trong database/chichan.db!\n")


async def seed_core_data():
    """Nạp dữ liệu nền tảng: Roles, Users, Profiles, Site Settings, Forum Categories, Scenarios, RAG Vectors"""
    print("=" * 65)
    print("2. NẠP DỮ LIỆU NỀN TẢNG (ROLES, USERS, SETTINGS, FORUM, AI)")
    print("=" * 65)

    async with AsyncSessionLocal() as session:
        # 1. ROLES
        roles_data = [
            (1, "ADMIN", "Quản trị viên", "Quản trị hệ thống, cấp quyền giảng viên, kiểm duyệt diễn đàn"),
            (2, "INSTRUCTOR", "Giảng viên", "Giảng viên, tạo và quản lý khóa học, bài giảng"),
            (3, "STUDENT_PARENT", "Phụ huynh", "Học viên đối tượng Phụ huynh, học nội dung đồng hành cùng con"),
            (4, "STUDENT_CHILD", "Trẻ nhỏ", "Học viên đối tượng Trẻ nhỏ, tiếp cận bài học sinh động"),
        ]
        for r_id, code, name, desc in roles_data:
            session.add(Role(id=r_id, role_code=code, role_name=name, description=desc))
        await session.flush()
        print("✔ Đã nạp 4 Roles cơ bản.")

        # 2. DEFAULT USERS & PROFILES
        users_data = [
            (
                ID_ADMIN,
                1, "admin", "admin@chichan.vn", "Quản Trị Viên Hệ Thống",
                "Quản trị viên trưởng nền tảng ChiChan.", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"
            ),
            (
                ID_DR_LANANH,
                2, "dr_lananh", "lananh@chichan.vn", "TS. BS. Nguyễn Lan Anh",
                "Chuyên gia Y học Vị thành niên & Cố vấn nội dung Giáo dục Giới tính.", "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=300&q=80"
            ),
            (
                ID_THAY_HOANG,
                2, "thay_hoang", "hoang.le@chichan.vn", "ThS. Lê Hoàng",
                "Giáo viên GDCD & Cố vấn Kỹ năng sống Trường THPT Giồng Ông Tố.", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80"
            ),
            (
                ID_CHUYENGIA_ANHTUAN,
                2, "chuyengia_anhtuan", "tuan.nguyen@chichan.vn", "ThS. Nguyễn Anh Tuấn",
                "Chuyên gia Tâm lý Học đường & Tham vấn Trẻ vị thành niên.", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80"
            ),
            (
                ID_PHUHUYNH_MAI,
                3, "phuhuynh_mai", "parent@chichan.vn", "Trần Thị Mai",
                "Phụ huynh có con trong độ tuổi dậy thì (13-16 tuổi).", "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=80"
            ),
            (
                ID_PHUHUYNH_HUNG,
                3, "phuhuynh_hung", "hung.do@chichan.vn", "Đỗ Mạnh Hùng",
                "Kỹ sư CNTT, phụ huynh có con trai học lớp 9, quan tâm an toàn số.", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=300&q=80"
            ),
            (
                ID_PHUHUYNH_THANH,
                3, "phuhuynh_thanh", "thanh.le@chichan.vn", "Lê Thị Phương Thanh",
                "Giáo viên tiểu học, mẹ của 2 bạn nữ tuổi mới lớn.", "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80"
            ),
            (
                ID_HOCSINH_MINH,
                4, "hocsinh_minh", "student@chichan.vn", "Nguyễn Nhật Minh",
                "Học sinh lớp 10, quan tâm kỹ năng tự vệ số và chăm sóc bản thân.", "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=300&q=80"
            ),
            (
                ID_HOCSINH_LINH,
                4, "hocsinh_linh", "linh.pham@chichan.vn", "Phạm Thảo Linh",
                "Nữ sinh lớp 11, Trưởng ban Truyền thông CLB Kỹ năng sống.", "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=300&q=80"
            ),
            (
                ID_HOCSINH_KHOA,
                4, "hocsinh_khoa", "khoa.tran@chichan.vn", "Trần Đăng Khoa",
                "Nam sinh lớp 10, yêu thích thể thao, lập trình và an toàn số.", "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=300&q=80"
            ),
        ]

        for u_id, r_id, uname, email, fname, bio, avatar in users_data:
            u = User(
                id=u_id,
                role_id=r_id,
                username=uname,
                email=email,
                password_hash=DEFAULT_PASSWORD_HASH,
                full_name=fname,
                status="ACTIVE"
            )
            session.add(u)
            await session.flush()
            p = UserProfile(
                user_id=u_id,
                avatar_url=avatar,
                bio=bio,
                gender="OTHER"
            )
            session.add(p)
        await session.flush()
        print("✔ Đã nạp 4 Tài khoản mẫu (Mật khẩu: 123456): admin, dr_lananh, phuhuynh_mai, hocsinh_minh.")

        # 3. SITE SETTINGS
        settings_data = [
            ("home_hero_title", "Nền tảng Giáo dục Giới tính Trực tuyến An toàn & Khoa học", "Tiêu đề Hero trang chủ"),
            ("home_hero_subtitle", "Đồng hành cùng thanh thiếu niên và phụ huynh Việt Nam xây dựng nhận thức đúng đắn và phản xạ tự bảo vệ bản thân.", "Mô tả phụ Hero trang chủ"),
            ("about_us_research_title", "Nghiên cứu và Ứng dụng Nền tảng E-learning trong Phổ biến Kiến thức Giáo dục Giới tính tại Việt Nam", "Tiêu đề đề tài nghiên cứu khoa học"),
            ("about_us_research_purpose", "Đề tài hướng tới việc xóa bỏ các rào cản tâm lý e ngại, cung cấp nguồn học liệu chuẩn y khoa, giúp thanh thiếu niên chủ động bảo vệ bản thân và phụ huynh có kỹ năng đồng hành cùng con.", "Mục tiêu đề tài"),
            ("about_us_methodology", "Kết hợp học tập trực tuyến cá nhân hóa theo nhóm đối tượng, mô phỏng phản xạ ứng phó bằng AI và diễn đàn trao đổi bảo mật.", "Phương pháp nghiên cứu"),
            ("about_us_authors_json", json.dumps([
                {"name": "Nhóm Nghiên cứu Khoa học THPT Giồng Ông Tố", "role": "Tác giả & Phát triển Nền tảng", "contact": "research.chichan@example.edu.vn"}
            ], ensure_ascii=False), "Danh sách tác giả đề tài"),
        ]
        for key, val, desc in settings_data:
            session.add(SiteSetting(key_name=key, value_content=val, description=desc))
        await session.flush()
        print("✔ Đã nạp Cấu hình hệ thống (Site Settings).")

        # 4. FORUM CATEGORIES
        cat_data = [
            (1, "Dậy thì & Thay đổi cơ thể", "day-thi-thay-doi-co-the", "Nơi chia sẻ và giải đáp về các biến đổi thể chất, sinh lý tuổi dậy thì."),
            (2, "An toàn mạng & Kỹ năng số", "an-toan-mang-ky-nang-so", "Nhận diện các cạm bẫy trực tuyến, phòng chống dụ dỗ, tống tiền bằng hình ảnh riêng tư."),
            (3, "Tình bạn & Tình yêu tuổi học trò", "tinh-ban-tinh-yeu-tuoi-hoc-tro", "Thảo luận về các mối quan hệ, sự đồng thuận, ranh giới và cảm xúc."),
            (4, "Góc Phụ huynh", "goc-phu-huynh", "Kinh nghiệm đồng hành, trò chuyện cởi mở cùng con về giới tính và sức khỏe."),
        ]
        for cid, name, slug, desc in cat_data:
            session.add(ForumCategory(id=cid, name=name, slug=slug, description=desc))
        await session.flush()
        print("✔ Đã nạp 4 Chuyên mục Diễn đàn (Forum Categories).")

        # 5. AI ROLEPLAY SCENARIOS
        scenarios_data = [
            {
                "id": 1,
                "room_code": "ROOM_STRANGER",
                "title": "Kẻ ẩn danh & Ranh giới an toàn",
                "npc_name": "Quân Kool",
                "npc_avatar_url": "/images/roleplay/quan-kool.jpg",
                "initial_score": 50,
                "target_audience": "CHILD",
                "is_active": True,
                "description": "Một người lạ tiếp cận qua mạng xã hội, dần dần thăm dò thông tin cá nhân và đề nghị gặp mặt bí mật.",
                "guide_script": "Hãy luôn cảnh giác, không cung cấp thông tin nhạy cảm, dứt khoát từ chối và báo ngay cho người lớn đáng tin cậy.",
                "first_message_sender": "NPC",
                "opening_message": "Chào em, anh thấy em học trường gần nhà anh nè. Nói chuyện chút cho vui nhé?",
                "gender_info": "Nam, 19 tuổi (tài khoản ảo)"
            },
            {
                "id": 2,
                "room_code": "ROOM_SEXTORTION",
                "title": "Bẫy tống tiền & Bản lĩnh đối mặt",
                "npc_name": "Tuấn Anh",
                "npc_avatar_url": "/avatars/cyber-alert.svg",
                "initial_score": 50,
                "target_audience": "CHILD",
                "is_active": True,
                "description": "Người quen trên mạng đe dọa phát tán ảnh riêng tư để tống tiền hoặc ép gặp mặt.",
                "guide_script": "Tuyệt đối không chuyển tiền, không thỏa hiệp, lưu lại toàn bộ bằng chứng và tìm kiếm sự trợ giúp từ chuyên gia hoặc cơ quan chức năng.",
                "first_message_sender": "NPC",
                "opening_message": "Mày có 15 phút để chuyển 2 triệu, không thì toàn bộ ảnh này sẽ xuất hiện trên nhóm trường!",
                "gender_info": "Người quen ẩn danh"
            },
            {
                "id": 3,
                "room_code": "ROOM_DOCTOR",
                "title": "Phòng tư vấn Tuổi mới lớn",
                "npc_name": "BS. Minh Trang",
                "npc_avatar_url": "/images/roleplay/doctor-trang.jpg",
                "initial_score": 50,
                "target_audience": "CHILD",
                "is_active": True,
                "description": "Không gian an toàn, bảo mật để hỏi mọi thắc mắc tế nhị về sinh lý, cơ thể và tâm lý tuổi dậy thì.",
                "guide_script": "Hãy thoải mái và chân thành hỏi bất kỳ điều gì bạn đang băn khoăn về cơ thể mình.",
                "first_message_sender": "NPC",
                "opening_message": "Chào em, chị là Bác sĩ Minh Trang. Ở đây mọi câu hỏi về cơ thể đều hoàn toàn bình thường, em cứ thoải mái chia sẻ nhé!",
                "gender_info": "Nữ, Bác sĩ vị thành niên"
            },
            {
                "id": 4,
                "room_code": "ROOM_TEEN_CHILD",
                "title": "Thấu hiểu con cái tuổi dậy thì",
                "npc_name": "Bảo Khang",
                "npc_avatar_url": "/images/roleplay/bao-khang.jpg",
                "initial_score": 50,
                "target_audience": "PARENT",
                "is_active": True,
                "description": "Kịch bản đóng vai dành cho phụ huynh luyện tập kỹ năng lắng nghe và trò chuyện không phán xét cùng con.",
                "guide_script": "Lắng nghe thấu cảm, tránh áp đặt hoặc chỉ trích để con mở lòng chia sẻ.",
                "first_message_sender": "NPC",
                "opening_message": "Mẹ lúc nào cũng cấm đoán con, mẹ có bao giờ hiểu con nghĩ gì đâu!",
                "gender_info": "Con trai, 14 tuổi"
            },
        ]

        for s_data in scenarios_data:
            session.add(AIScenario(**s_data))
        await session.flush()
        print("✔ Đã nạp 4 Kịch bản AI Roleplay (Scenarios).")

        # 6. KNOWLEDGE VECTORS (Mẫu RAG chuẩn)
        knowledge_data = [
            ("ONLINE_SAFETY", "Quy tắc 5 Không trên mạng xã hội", "Không cung cấp địa chỉ nhà, tên trường lớp, số điện thoại cá nhân. Không gửi ảnh nhạy cảm dưới bất kỳ hình thức nào. Không nhấp link lạ. Không đồng ý gặp mặt một mình ngoài đời. Không giấu giếm khi bị đe dọa."),
            ("ONLINE_SAFETY", "Xử lý khi bị tống tiền Sextortion", "1. Giữ bình tĩnh, tuyệt đối không chuyển tiền vì kẻ tống tiền sẽ tiếp tục đòi thêm. 2. Không xóa tin nhắn mà chụp ảnh màn hình lưu chứng cứ. 3. Chặn kẻ xấu và báo cáo tài khoản. 4. Báo ngay cho người lớn, thầy cô hoặc gọi Tổng đài bảo vệ trẻ em 111."),
            ("PUBERTY_ANATOMY", "Mộng tinh và xuất tinh ban đêm", "Mộng tinh là hiện tượng sinh lý hoàn toàn tự nhiên ở nam giới tuổi dậy thì khi tinh dịch xuất ra tự động trong lúc ngủ. Đây là dấu hiệu cho thấy cơ thể phát triển khỏe mạnh bình thường, không phải là bệnh tật."),
            ("PUBERTY_ANATOMY", "Kinh nguyệt ở bạn nữ", "Kinh nguyệt là hiện tượng lớp niêm mạc tử cung bong ra khi trứng không được thụ tinh. Chu kỳ bình thường từ 28-35 ngày. Vệ sinh sạch sẽ bằng nước sạch và thay băng vệ sinh mỗi 3-4 tiếng để tránh viêm nhiễm."),
            ("COMMUNICATION_SKILLS", "Nguyên tắc đồng thuận (Consent)", "Đồng thuận phải xuất phát từ sự tự nguyện, tỉnh táo, có thể rút lại bất kỳ lúc nào và không có sự ép buộc, đe dọa hay thao túng tâm lý."),
        ]
        dummy_vec = [0.01 * (i % 10) for i in range(768)]
        for cat, topic, chunk in knowledge_data:
            session.add(AIKnowledgeVector(
                category=cat,
                topic=topic,
                content_chunk=chunk,
                embedding=dummy_vec
            ))
        await session.flush()
        print("✔ Đã nạp Tri thức mẫu (AI Knowledge Vectors).")

        await session.commit()
    print("✔ Nạp dữ liệu nền tảng hoàn tất!\n")


async def seed_courses_from_json():
    """Nạp toàn bộ khóa học, bài học và bài kiểm tra từ thư mục seed/data/courses/*.json"""
    print("=" * 65)
    print("3. NẠP KHÓA HỌC CHUẨN (COURSES, LESSONS, QUIZZES TỪ JSON)")
    print("=" * 65)

    courses_glob = os.path.join(DATA_DIR, "courses", "*.json")
    course_files = sorted(glob.glob(courses_glob))

    if not course_files:
        print("⚠ Không tìm thấy file JSON nào trong seed/data/courses/!")
        return

    async with AsyncSessionLocal() as session:
        total_courses = 0
        total_lessons = 0
        total_quizzes = 0
        total_questions = 0

        for fpath in course_files:
            with open(fpath, "r", encoding="utf-8") as f:
                cdata = json.load(f)

            # Phân bổ giảng viên chuyên môn phù hợp
            inst_id = ID_DR_LANANH
            slug_str = cdata["slug"]
            if any(k in slug_str for k in ["phap-ly", "bullying", "public-safety", "tu-ve", "bao-luc"]):
                inst_id = ID_THAY_HOANG
            elif any(k in slug_str for k in ["mental-health", "tinh-yeu", "emotions", "parenting", "academic", "lgbt"]):
                inst_id = ID_CHUYENGIA_ANHTUAN

            course = Course(
                instructor_id=inst_id,
                title=cdata["title"],
                slug=cdata["slug"],
                short_description=cdata.get("short_description"),
                description=cdata.get("description"),
                thumbnail_url=cdata.get("thumbnail_url"),
                target_audience=cdata.get("target_audience", "CHILD"),
                learning_objectives=cdata.get("learning_objectives"),
                outro_content=cdata.get("outro_content"),
                is_published=cdata.get("is_published", True)
            )
            session.add(course)
            await session.flush()
            total_courses += 1

            # Nạp bài học và lesson quizzes
            lessons_data = cdata.get("lessons", [])
            for l_item in lessons_data:
                lesson = Lesson(
                    course_id=course.id,
                    title=l_item["title"],
                    content_type=l_item.get("content_type", "HYBRID"),
                    video_url=l_item.get("video_url"),
                    content_body=l_item.get("content_body"),
                    order_index=l_item.get("order_index", 1),
                    duration_minutes=l_item.get("duration_minutes", 15)
                )
                session.add(lesson)
                await session.flush()
                total_lessons += 1

                # Lesson Quiz
                q_data = l_item.get("quiz")
                if q_data:
                    quiz = Quiz(
                        course_id=course.id,
                        lesson_id=lesson.id,
                        title=q_data.get("title", f"Kiểm tra: {lesson.title}"),
                        description=q_data.get("description"),
                        passing_score=q_data.get("passing_score", 80),
                        show_correct_answers=True,
                        max_attempts=3,
                        cooldown_minutes=15
                    )
                    session.add(quiz)
                    await session.flush()
                    total_quizzes += 1

                    for q_idx, question_item in enumerate(q_data.get("questions", []), start=1):
                        qq = QuizQuestion(
                            quiz_id=quiz.id,
                            question_text=question_item["question_text"],
                            explanation=question_item.get("explanation"),
                            order_index=question_item.get("order_index", q_idx)
                        )
                        session.add(qq)
                        await session.flush()
                        total_questions += 1

                        for opt_idx, opt in enumerate(question_item.get("options", []), start=1):
                            opt_obj = QuizQuestionOption(
                                question_id=qq.id,
                                option_text=opt["option_text"],
                                is_correct=opt["is_correct"],
                                order_index=opt.get("order_index", opt_idx)
                            )
                            session.add(opt_obj)
                    await session.flush()

            # Final Quiz của khóa học (nếu có)
            final_quiz_data = cdata.get("final_quiz")
            if final_quiz_data:
                final_quiz = Quiz(
                    course_id=course.id,
                    lesson_id=None,
                    title=final_quiz_data.get("title", f"Đánh giá Hoàn thành: {course.title}"),
                    description=final_quiz_data.get("description"),
                    passing_score=final_quiz_data.get("passing_score", 80),
                    show_correct_answers=True,
                    max_attempts=3,
                    cooldown_minutes=15
                )
                session.add(final_quiz)
                await session.flush()
                total_quizzes += 1

                for q_idx, question_item in enumerate(final_quiz_data.get("questions", []), start=1):
                    qq = QuizQuestion(
                        quiz_id=final_quiz.id,
                        question_text=question_item["question_text"],
                        explanation=question_item.get("explanation"),
                        order_index=question_item.get("order_index", q_idx)
                    )
                    session.add(qq)
                    await session.flush()
                    total_questions += 1

                    for opt_idx, opt in enumerate(question_item.get("options", []), start=1):
                        opt_obj = QuizQuestionOption(
                            question_id=qq.id,
                            option_text=opt["option_text"],
                            is_correct=opt["is_correct"],
                            order_index=opt.get("order_index", opt_idx)
                        )
                        session.add(opt_obj)
                await session.flush()

            print(f"✔ Đã nạp Khóa học: '{course.title}' ({len(lessons_data)} bài học, {'có' if final_quiz_data else 'không có'} Final Quiz)")

        await session.commit()
        print(f"\n✔ Tổng kết Học liệu: {total_courses} Khóa học | {total_lessons} Bài học | {total_quizzes} Đề thi Quiz | {total_questions} Câu trắc nghiệm!\n")


async def seed_forum_from_json():
    """Nạp bài viết và bình luận diễn đàn từ seed/data/forum/forum_posts.json"""
    print("=" * 65)
    print("4. NẠP DIỄN ĐÀN HỎI ĐÁP (FORUM POSTS & COMMENTS TỪ JSON)")
    print("=" * 65)

    fpath = os.path.join(DATA_DIR, "forum", "forum_posts.json")
    if not os.path.exists(fpath):
        print("⚠ Không tìm thấy seed/data/forum/forum_posts.json!")
        return

    with open(fpath, "r", encoding="utf-8") as f:
        posts_data = json.load(f)

    async with AsyncSessionLocal() as session:
        post_count = 0
        comment_count = 0

        for p_item in posts_data:
            post = ForumPost(
                id=uuid.UUID(p_item["id"]),
                category_id=p_item["category_id"],
                author_id=uuid.UUID(p_item["author_id"]),
                title=p_item["title"],
                content=p_item["content"],
                is_anonymous=p_item.get("is_anonymous", False),
                views_count=p_item.get("views_count", 0),
                likes_count=p_item.get("likes_count", 0),
                status=p_item.get("status", "PUBLISHED"),
                created_at=datetime.fromisoformat(p_item["created_at"]) if "created_at" in p_item else datetime.now(timezone.utc)
            )
            session.add(post)
            await session.flush()
            post_count += 1

            for c_item in p_item.get("comments", []):
                comment = ForumComment(
                    id=uuid.UUID(c_item["id"]),
                    post_id=post.id,
                    author_id=uuid.UUID(c_item["author_id"]),
                    content=c_item["content"],
                    is_anonymous=c_item.get("is_anonymous", False),
                    status=c_item.get("status", "PUBLISHED"),
                    created_at=datetime.fromisoformat(c_item["created_at"]) if "created_at" in c_item else datetime.now(timezone.utc)
                )
                session.add(comment)
                await session.flush()
                comment_count += 1

        await session.commit()
        print(f"✔ Đã nạp thành công {post_count} Bài viết Diễn đàn và {comment_count} Bình luận tư vấn chuyên gia!\n")


async def seed_activity_from_json():
    """Nạp tiến độ học tập và bài thi mẫu từ seed/data/activity/simulated_progress.json"""
    print("=" * 65)
    print("5. NẠP TIẾN ĐỘ HỌC TẬP VÀ BÀI THI MẪU (SIMULATED ACTIVITY)")
    print("=" * 65)

    fpath = os.path.join(DATA_DIR, "activity", "simulated_progress.json")
    if not os.path.exists(fpath):
        print("⚠ Không tìm thấy seed/data/activity/simulated_progress.json!")
        return

    with open(fpath, "r", encoding="utf-8") as f:
        act_data = json.load(f)

    async with AsyncSessionLocal() as session:
        # 1. Course Enrollments
        for enr in act_data.get("enrollments", []):
            cq = await session.execute(select(Course).where(Course.slug == enr["course_slug"]))
            course = cq.scalar_one_or_none()
            if not course:
                continue

            enrolled_at = datetime.fromisoformat(enr["enrolled_at"]) if enr.get("enrolled_at") else datetime.now(timezone.utc)
            completed_at = datetime.fromisoformat(enr["completed_at"]) if enr.get("completed_at") else None

            enrollment = CourseEnrollment(
                user_id=uuid.UUID(enr["user_id"]),
                course_id=course.id,
                status=enr.get("status", "IN_PROGRESS"),
                enrolled_at=enrolled_at,
                completed_at=completed_at
            )
            session.add(enrollment)
        await session.flush()
        print(f"✔ Đã nạp {len(act_data.get('enrollments', []))} Lượt đăng ký khóa học mẫu (Enrollments).")

        # 2. Completed Lessons
        for lprog in act_data.get("completed_lessons", []):
            cq = await session.execute(select(Course).where(Course.slug == lprog["course_slug"]))
            course = cq.scalar_one_or_none()
            if not course:
                continue

            lq = await session.execute(
                select(Lesson).where(
                    Lesson.course_id == course.id,
                    Lesson.order_index == lprog["lesson_order_index"]
                )
            )
            lesson = lq.scalar_one_or_none()
            if not lesson:
                continue

            lp = LessonProgress(
                user_id=uuid.UUID(lprog["user_id"]),
                lesson_id=lesson.id,
                is_completed=True
            )
            session.add(lp)
        await session.flush()
        print(f"✔ Đã nạp {len(act_data.get('completed_lessons', []))} Tiến độ bài học đã hoàn thành (LessonProgress).")

        # 3. Quiz Submissions
        sub_count = 0
        for sub in act_data.get("quiz_submissions", []):
            cq = await session.execute(select(Course).where(Course.slug == sub["course_slug"]))
            course = cq.scalar_one_or_none()
            if not course:
                continue

            target_quiz = None
            if sub.get("is_final_quiz"):
                qq = await session.execute(
                    select(Quiz).where(Quiz.course_id == course.id, Quiz.lesson_id.is_(None))
                )
                target_quiz = qq.scalar_one_or_none()
            else:
                lq = await session.execute(
                    select(Lesson).where(
                        Lesson.course_id == course.id,
                        Lesson.order_index == sub["lesson_order_index"]
                    )
                )
                lesson = lq.scalar_one_or_none()
                if lesson:
                    qq = await session.execute(
                        select(Quiz).where(Quiz.lesson_id == lesson.id)
                    )
                    target_quiz = qq.scalar_one_or_none()

            if target_quiz:
                qsub = QuizSubmission(
                    user_id=uuid.UUID(sub["user_id"]),
                    quiz_id=target_quiz.id,
                    score=sub["score"],
                    passed=sub["passed"],
                    answers={"simulated": True}
                )
                session.add(qsub)
                sub_count += 1

        await session.commit()
        print(f"✔ Đã nạp {sub_count} Bài nộp Quiz mẫu đạt điểm cao (QuizSubmissions).\n")


def invalidate_app_cache():
    """Hủy cache in-memory của settings/home nếu service đang chạy"""
    try:
        from services.settings_service import settings_service
        settings_service.invalidate_settings_cache()
        print("✔ Đã làm mới Cache hệ thống (Invalidate Cache).")
    except Exception:
        pass


async def main():
    print("=" * 65)
    print("      CHICHAN PLATFORM - DATABASE INITIALIZATION & SEEDING      ")
    print("=" * 65)

    # 1. Khởi tạo schema sạch
    await init_schema(drop_existing=True)

    # 2. Nạp dữ liệu nền tảng
    await seed_core_data()

    # 3. Nạp 5 khóa học từ JSON
    await seed_courses_from_json()

    # 4. Nạp diễn đàn từ JSON
    await seed_forum_from_json()

    # 5. Nạp hoạt động mẫu từ JSON
    await seed_activity_from_json()

    # 6. Invalidate Cache
    invalidate_app_cache()

    print("=" * 65)
    print("🎉 TOÀN BỘ DỮ LIỆU ĐÃ ĐƯỢC NẠP THÀNH CÔNG VÀO database/chichan.db!")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(main())
