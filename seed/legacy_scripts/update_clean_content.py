# -*- coding: utf-8 -*-
import sys, os
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
import asyncio
import sys
from sqlalchemy import text
from core.database import AsyncSessionLocal
import models.role
import models.profile
import models.user
import models.course
import models.lesson
import models.quiz

from seed_course_4 import LESSONS_DATA as C4_LESSONS
from seed_course_5 import LESSONS_DATA as C5_LESSONS
from seed_course_6 import LESSONS_DATA as C6_LESSONS
from seed_course_7 import LESSONS_DATA as C7_LESSONS

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

async def update_lessons():
    async with AsyncSessionLocal() as session:
        updates = [
            ("mo-loi-truoc-khi-con-phai-tu-tim-tren-mang", C4_LESSONS),
            ("tuoi-teen-dong-cua-phong-cha-me-mo-cua-doi-thoai", C5_LESSONS),
            ("khi-con-gap-nguy-hiem-binh-tinh-de-bao-ve", C6_LESSONS),
            ("nha-minh-noi-chuyen-ve-co-the-duoc-ma", C7_LESSONS),
        ]

        total_updated = 0
        for slug, lessons in updates:
            res = await session.execute(text("SELECT id, title FROM courses WHERE slug = :slug"), {"slug": slug})
            course = res.fetchone()
            if not course:
                print(f"Warning: course '{slug}' not found.")
                continue
            
            course_id = course[0]
            print(f"\nUpdating lessons for Course: {course[1]} ({course_id})...")

            for l_data in lessons:
                res = await session.execute(
                    text("UPDATE lessons SET content_body = :body WHERE course_id = :cid AND order_index = :idx RETURNING id"),
                    {"body": l_data["content_body"], "cid": course_id, "idx": l_data["order_index"]}
                )
                updated_row = res.fetchone()
                if updated_row:
                    print(f"  ✓ Updated Lesson {l_data['order_index']}: {l_data['title']}")
                    total_updated += 1
                else:
                    print(f"  ✗ Lesson {l_data['order_index']} not found for course {slug}")

        await session.commit()
        print(f"\nDone! Successfully updated {total_updated} lessons in database.")

if __name__ == "__main__":
    asyncio.run(update_lessons())
