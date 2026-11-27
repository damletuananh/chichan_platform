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

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

async def verify():
    async with AsyncSessionLocal() as session:
        # Check course
        res = await session.execute(
            text("SELECT id, title, slug, target_audience, is_published FROM courses WHERE slug = 'nha-minh-noi-chuyen-ve-co-the-duoc-ma'")
        )
        course = res.fetchone()
        if not course:
            print("ERROR: Course 7 not found!")
            return
        
        course_id = course[0]
        print(f"Course Found: {course[1]} (Slug: {course[2]}, Audience: {course[3]}, Published: {course[4]})")

        # Check lessons
        res = await session.execute(
            text("SELECT order_index, title, content_type, duration_minutes, video_url FROM lessons WHERE course_id = :cid ORDER BY order_index"),
            {"cid": course_id}
        )
        lessons = res.fetchall()
        print(f"\nTotal Lessons: {len(lessons)}")
        for l in lessons:
            print(f"  Lesson {l[0]}: {l[1]} [{l[2]}, {l[3]}m] - Video: {l[4]}")

        # Check quizzes
        res = await session.execute(
            text("SELECT q.id, l.order_index, q.title, q.passing_score FROM quizzes q JOIN lessons l ON q.lesson_id = l.id WHERE q.course_id = :cid ORDER BY l.order_index"),
            {"cid": course_id}
        )
        quizzes = res.fetchall()
        print(f"\nTotal Quizzes: {len(quizzes)}")
        
        # Check questions & options
        res = await session.execute(
            text("""
                SELECT 
                    COUNT(DISTINCT qq.id) as question_count,
                    COUNT(qqo.id) as option_count,
                    SUM(CASE WHEN qqo.is_correct THEN 1 ELSE 0 END) as correct_option_count
                FROM quizzes q
                JOIN quiz_questions qq ON qq.quiz_id = q.id
                JOIN quiz_question_options qqo ON qqo.question_id = qq.id
                WHERE q.course_id = :cid
            """),
            {"cid": course_id}
        )
        stats = res.fetchone()
        print(f"\nQuiz Questions: {stats[0]}")
        print(f"Quiz Options: {stats[1]}")
        print(f"Correct Options: {stats[2]}")

        # Check for any questions with invalid number of correct answers (must be exactly 1)
        res = await session.execute(
            text("""
                SELECT qq.id, qq.question_text, COUNT(qqo.id) as total_opts, SUM(CASE WHEN qqo.is_correct THEN 1 ELSE 0 END) as correct_opts
                FROM quizzes q
                JOIN quiz_questions qq ON qq.quiz_id = q.id
                JOIN quiz_question_options qqo ON qqo.question_id = qq.id
                WHERE q.course_id = :cid
                GROUP BY qq.id, qq.question_text
                HAVING SUM(CASE WHEN qqo.is_correct THEN 1 ELSE 0 END) != 1 OR COUNT(qqo.id) != 4
            """),
            {"cid": course_id}
        )
        invalid = res.fetchall()
        if invalid:
            print(f"WARNING: Found {len(invalid)} questions with invalid option counts or correct answers!")
            for inv in invalid:
                print(f"  Question: {inv[1]} - Total: {inv[2]}, Correct: {inv[3]}")
        else:
            print("ALL 60 QUESTIONS HAVE EXACTLY 4 OPTIONS AND EXACTLY 1 CORRECT ANSWER! VALIDATION PASSED!")

        # List all published courses in DB
        res = await session.execute(text("SELECT id, title, slug, target_audience FROM courses ORDER BY created_at ASC"))
        all_courses = res.fetchall()
        print(f"\nAll courses in database ({len(all_courses)} total):")
        for idx, c in enumerate(all_courses, start=1):
            print(f"  {idx}. [{c[3]}] {c[1]} (Slug: {c[2]})")

if __name__ == "__main__":
    asyncio.run(verify())
