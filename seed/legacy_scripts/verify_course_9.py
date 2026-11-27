# -*- coding: utf-8 -*-
import sys, os
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
import asyncio
import os
import sys
from sqlalchemy import text

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from core.database import AsyncSessionLocal

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

async def verify_course_9():
    async with AsyncSessionLocal() as session:
        # Check course
        res = await session.execute(
            text("SELECT id, title, slug, target_audience, is_published FROM courses WHERE slug = 'tin-nhau-de-noi-dieu-kho-noi'")
        )
        course = res.fetchone()
        if not course:
            print("ERROR: Course 9 not found!")
            return

        print(f"Verified Course: {course.title} (Slug: {course.slug}, Audience: {course.target_audience})")

        # Check lessons
        res = await session.execute(
            text("SELECT id, order_index, title, content_type, duration_minutes, video_url, content_body FROM lessons WHERE course_id = :cid ORDER BY order_index"),
            {"cid": course.id}
        )
        lessons = res.fetchall()
        print(f"Total Lessons: {len(lessons)}")
        for l in lessons:
            # Check content for forbidden keywords
            forbidden = ["Gói sản xuất", "Prompt:", "Tạo video tiếng Việt 4", "Rà quiz với video", "Chưa có — dựng video"]
            found_forbidden = [w for w in forbidden if w in (l.content_body or "")]
            status = "CLEAN" if not found_forbidden else f"CONTAINS UNWANTED: {found_forbidden}"
            print(f"  Lesson {l.order_index}: {l.title} [{l.content_type}] - {l.duration_minutes}m - {status}")

            # Check quiz
            q_res = await session.execute(
                text("SELECT id, title, passing_score FROM quizzes WHERE lesson_id = :lid"),
                {"lid": l.id}
            )
            quiz = q_res.fetchone()
            if not quiz:
                print(f"    WARNING: No quiz for lesson {l.order_index}")
                continue

            quest_res = await session.execute(
                text("SELECT id, question_text, explanation FROM quiz_questions WHERE quiz_id = :qid ORDER BY order_index"),
                {"qid": quiz.id}
            )
            questions = quest_res.fetchall()
            print(f"    Quiz: {quiz.title} (Passing: {quiz.passing_score}%) - {len(questions)} Questions")

            # Check options
            for q in questions:
                opt_res = await session.execute(
                    text("SELECT id, option_text, is_correct FROM quiz_question_options WHERE question_id = :qid ORDER BY order_index"),
                    {"qid": q.id}
                )
                opts = opt_res.fetchall()
                correct_count = sum(1 for o in opts if o.is_correct)
                if len(opts) != 4 or correct_count != 1:
                    print(f"      ERROR in Q '{q.question_text[:30]}...': {len(opts)} options, {correct_count} correct")

        print("\nVerification of Course 9 completed successfully!")

if __name__ == "__main__":
    asyncio.run(verify_course_9())
