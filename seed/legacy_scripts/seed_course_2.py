# -*- coding: utf-8 -*-
import sys, os
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
import asyncio
import sys
import uuid
from sqlalchemy import text
from core.database import AsyncSessionLocal
import models.role
import models.profile
import models.user
from models.course import Course
from models.lesson import Lesson
from models.quiz import Quiz, QuizQuestion, QuizQuestionOption

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

COURSE_DATA = {
    "title": "Dậy Thì Không Có “Phiên Bản Chuẩn”",
    "slug": "day-thi-khong-co-phien-ban-chuan",
    "short_description": "Khóa học giáo dục dậy thì toàn diện cho học sinh: thấu hiểu sự biến đổi cơ thể, kinh nguyệt, mộng tinh và gỡ bỏ chiếc bẫy so sánh ngoại hình.",
    "description": (
        "**Đối tượng:** Học sinh mọi giới.\n\n"
        "Khóa học giúp học sinh tiếp cận kiến thức khoa học và tâm lý tuổi dậy thì, thấu hiểu rằng mỗi cơ thể đều phát triển theo một nhịp điệu riêng biệt "
        "và không hề có một “phiên bản chuẩn” nào để so sánh. Nội dung mang tính giáo dục y khoa thường thức, thúc đẩy sự tôn trọng bản thân và bạn bè, "
        "xóa bỏ định kiến và kỳ thị cơ thể.\n\n"
        "**Cấu trúc khóa học:** Gồm các bài học trọng tâm kết hợp video khoa học từ AMAZE Org, các hướng dẫn chăm sóc cơ thể thực tế và bài tập củng cố kiến thức 10 câu trắc nghiệm (đạt 8/10 trở lên)."
    ),
    "learning_objectives": (
        "- Thấu hiểu các thay đổi tự nhiên của cơ thể trong giai đoạn dậy thì (hormone, da, lông, mụn và mùi cơ thể).\n"
        "- Nhận thức đúng đắn và văn minh về kinh nguyệt và mộng tinh, loại bỏ tâm lý xấu hổ hay trêu chọc bạn bè.\n"
        "- Vượt qua áp lực so sánh ngoại hình và nhận diện chiếc bẫy “cơ thể hoàn hảo” từ quảng cáo và mạng xã hội.\n"
        "- Biết cách chăm sóc vệ sinh cá nhân phù hợp và tìm kiếm sự tư vấn y tế khi cần thiết."
    ),
    "thumbnail_url": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=1200&q=80",
    "target_audience": "CHILD",
    "is_published": True,
}

LESSONS_DATA = [
    {
        "order_index": 1,
        "title": "Bài 1 — Cơ thể tôi đổi khác: có gì đáng lo?",
        "video_url": "https://www.youtube.com/watch?v=00BYyDr8Xdg",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Cơ thể thay đổi thế nào?
Trong tuổi dậy thì, hormone thay đổi; da có thể tiết nhiều dầu, xuất hiện mụn, lông cơ thể và mùi mồ hôi khác trước. Các thay đổi không xuất hiện cùng thời điểm ở mọi người. Có thay đổi không có nghĩa cơ thể bạn “bẩn” hoặc sai.

### 2. Chăm sóc cơ thể
Video AMAZE khuyến khích thói quen vệ sinh phù hợp: tắm hoặc rửa người đều đặn, mặc quần áo sạch và cân nhắc sản phẩm khử mùi khi cần. Nếu mụn dai dẳng hoặc khiến bạn khó chịu, có thể hỏi nhân viên y tế về cách chăm sóc da. Đừng dùng sản phẩm gây kích ứng chỉ vì quảng cáo hoặc lời trêu chọc.

> [!NOTE]
> **Nguồn đối chiếu video:** [AMAZE Org — Taking Care of Your Body](https://amaze.org/video/puberty-taking-care-of-your-body-during-puberty/)  
> **Bổ sung của bài học:** Cách ứng xử không chế giễu bạn bè và việc hỏi người chăm sóc khi lo lắng.
""",
        "quiz_title": "Bài tập củng cố kiến thức Bài 1",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video đầu tiên nói về giai đoạn nào?",
                "options": ["Dậy thì", "Sơ sinh", "Tuổi già", "Thai kỳ"],
                "correct_index": 0,  # A
                "explanation": "Video mô tả thay đổi cơ thể trong tuổi dậy thì."
            },
            {
                "question_text": "Da tiết dầu nhiều hơn có thể liên quan điều gì?",
                "options": ["Hormone thay đổi", "Tên của bạn", "Điểm số", "Màu áo"],
                "correct_index": 0,  # A
                "explanation": "Hormone và dầu trên da được nhắc trong video."
            },
            {
                "question_text": "Mụn có thể xuất hiện khi nào?",
                "options": ["Trong dậy thì", "Chỉ sau 60 tuổi", "Chỉ khi đi máy bay", "Không bao giờ"],
                "correct_index": 0,  # A
                "explanation": "Da có thể thay đổi và nổi mụn khi dậy thì."
            },
            {
                "question_text": "Điều nào có thể thay đổi trong dậy thì?",
                "options": ["Lông cơ thể", "Nhóm máu hằng ngày", "Số ngón tay", "Màu mắt từng giờ"],
                "correct_index": 0,  # A
                "explanation": "Sự phát triển của lông cơ thể là một ví dụ trong video."
            },
            {
                "question_text": "Mùi cơ thể thay đổi có mặc nhiên nghĩa là một người “bẩn” không?",
                "options": ["Có", "Không", "Chỉ với một giới", "Chỉ ở trường"],
                "correct_index": 1,  # B
                "explanation": "Thay đổi cơ thể không phải là lý do kỳ thị."
            },
            {
                "question_text": "Video nêu nhóm thay đổi nào?",
                "options": ["Hormone, da dầu, lông, mụn và mùi", "Chỉ chiều cao", "Chỉ thị lực", "Chỉ màu tóc"],
                "correct_index": 0,  # A
                "explanation": "Đó là các nội dung trong mô tả video của AMAZE."
            },
            {
                "question_text": "Khi cơ thể thay đổi, cách chăm sóc phù hợp là gì?",
                "options": ["Điều chỉnh vệ sinh cá nhân", "Bỏ mặc mọi thay đổi", "Dùng mọi sản phẩm quảng cáo", "Chế giễu bạn"],
                "correct_index": 0,  # A
                "explanation": "Thói quen chăm sóc có thể thay đổi theo nhu cầu."
            },
            {
                "question_text": "Nếu mụn làm bạn lo lắng nhiều, nên làm gì?",
                "options": ["Hỏi người chăm sóc hoặc nhân viên y tế", "Tự nặn bằng vật sắc", "Tin lời đồn", "Giấu mọi triệu chứng"],
                "correct_index": 0,  # A
                "explanation": "Có thể tìm tư vấn phù hợp với tình trạng riêng."
            },
            {
                "question_text": "Nên ứng xử thế nào khi bạn có mùi cơ thể sau vận động?",
                "options": ["Tôn trọng, không trêu chọc", "Phát tán biệt danh", "Quay video", "Chế giễu"],
                "correct_index": 0,  # A
                "explanation": "Tôn trọng bạn bè và khuyến khích chăm sóc kín đáo."
            },
            {
                "question_text": "Có nên lấy tốc độ phát triển của bạn làm chuẩn cho mình?",
                "options": ["Có", "Không", "Chỉ trên mạng", "Chỉ trong lớp"],
                "correct_index": 1,  # B
                "explanation": "Mỗi người phát triển theo nhịp khác nhau."
            }
        ]
    },
    {
        "order_index": 2,
        "title": "Bài 2 — Kinh nguyệt: tín hiệu cơ thể, không phải điều xấu hổ",
        "video_url": "https://www.youtube.com/watch?v=TPzJaXMJcS8",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Kinh nguyệt là gì?
Khi cơ thể có tử cung bước vào dậy thì, hormone điều phối sự thay đổi của niêm mạc tử cung. Nếu không có thai, lớp niêm mạc bong ra và thoát qua âm đạo thành kỳ kinh. Kinh nguyệt là hiện tượng sinh lý; chu kỳ của mỗi người có thể khác nhau.

### 2. Kỳ thị gây hại ra sao?
Video AMAZE nói về việc người có kinh bị phán xét, xấu hổ hoặc bị hạn chế tham gia học tập và sinh hoạt vì lời đồn. Mọi học sinh đều có thể giúp thay đổi: không chế giễu, không kể chuyện sức khỏe riêng của bạn, hỗ trợ kín đáo khi ai đó cần sản phẩm kinh nguyệt. Nếu đau hoặc ra máu ảnh hưởng đáng kể đến sinh hoạt, hãy tìm tư vấn y tế.

> [!NOTE]
> **Nguồn đối chiếu video:** [AMAZE Org — Menstruation Stigma](https://amaze.org/video/menstruation-stigma/)  
> **Bổ sung của bài học:** Tình huống giúp bạn ở trường và hướng dẫn hỏi nhân viên y tế.
""",
        "quiz_title": "Bài tập củng cố kiến thức Bài 2",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "“Stigma” trong tiêu đề video gần nghĩa gì?",
                "options": ["Kỳ thị", "Dinh dưỡng", "Thể thao", "Chiều cao"],
                "correct_index": 0,  # A
                "explanation": "Video bàn về thái độ kỳ thị kinh nguyệt."
            },
            {
                "question_text": "Kinh nguyệt có phải là lý do để chế giễu?",
                "options": ["Có", "Không", "Chỉ khi ở lớp", "Chỉ trên mạng"],
                "correct_index": 1,  # B
                "explanation": "Đây là hiện tượng sinh lý, không phải điều đáng xấu hổ."
            },
            {
                "question_text": "Ai có thể học bài này?",
                "options": ["Mọi học sinh", "Chỉ người có kinh", "Chỉ giáo viên", "Không ai"],
                "correct_index": 0,  # A
                "explanation": "Người không có kinh cũng cần hiểu và tôn trọng."
            },
            {
                "question_text": "Lời đồn về kinh nguyệt nên được xử lý thế nào?",
                "options": ["Kiểm tra nguồn đáng tin", "Tin ngay", "Truyền tiếp", "Dùng trêu bạn"],
                "correct_index": 0,  # A
                "explanation": "Video hướng tới xóa bỏ ngộ nhận."
            },
            {
                "question_text": "Nếu bạn học cần đồ dùng kinh nguyệt, thái độ phù hợp?",
                "options": ["Giúp kín đáo", "Báo cả lớp", "Chụp ảnh", "Đặt biệt danh"],
                "correct_index": 0,  # A
                "explanation": "Hỗ trợ và bảo vệ riêng tư."
            },
            {
                "question_text": "Kinh nguyệt liên quan cơ quan nào?",
                "options": ["Tử cung", "Phổi", "Gan", "Tai"],
                "correct_index": 0,  # A
                "explanation": "Đây là một phần chu kỳ sinh sản ở người có tử cung."
            },
            {
                "question_text": "“Có kinh nghĩa là bẩn” là nhận định thế nào?",
                "options": ["Kỳ thị và sai", "Luật trường", "Chẩn đoán", "Chỉ dẫn y khoa"],
                "correct_index": 0,  # A
                "explanation": "Không đồng nhất hiện tượng sinh lý với sự dơ bẩn."
            },
            {
                "question_text": "Điều nào thể hiện tôn trọng bạn bè?",
                "options": ["Không bình phẩm chuyện kinh nguyệt của họ", "Kể chuyện riêng của họ", "Đoán ngày có kinh", "Chụp ảnh đồ dùng"],
                "correct_index": 0,  # A
                "explanation": "Sức khỏe cá nhân thuộc về người đó."
            },
            {
                "question_text": "Khi đau hoặc ra máu làm gián đoạn sinh hoạt, nên làm gì?",
                "options": ["Hỏi nhân viên y tế", "Chỉ nghe lời đồn", "Tự chịu đựng mãi", "Dùng thuốc bất kỳ"],
                "correct_index": 0,  # A
                "explanation": "Tình trạng ảnh hưởng đời sống cần được đánh giá."
            },
            {
                "question_text": "Thông điệp chính của bài là gì?",
                "options": ["Hiểu đúng và giảm kỳ thị", "Bắt mọi người im lặng", "So sánh chu kỳ", "Mua sản phẩm"],
                "correct_index": 0,  # A
                "explanation": "Mục tiêu là kiến thức và tôn trọng."
            }
        ]
    },
    {
        "order_index": 3,
        "title": "Bài 3 — Mộng tinh: chuyện cơ thể, đừng để lời đồn dọa bạn",
        "video_url": "https://www.youtube.com/watch?v=uotzoDDRW_s",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Mộng tinh là gì?
Video AMAZE giới thiệu hiện tượng giải phóng dịch sinh dục không chủ ý khi ngủ trong giai đoạn dậy thì. Có người trải nghiệm thường xuyên, có người hiếm khi hoặc không trải nghiệm; riêng điều đó không cho biết họ khỏe hơn hay kém hơn bạn bè.

### 2. Khi gặp hoặc nghe bạn hỏi
Không cần thấy có lỗi hay xấu hổ. Nếu quần áo hoặc chăn ga bị dính dịch, có thể thay và giặt như các đồ dùng thường ngày. Tránh lấy trải nghiệm của mình áp lên người khác. Khi có đau hoặc lo lắng kéo dài, hãy hỏi nhân viên y tế.

> [!NOTE]
> **Nguồn đối chiếu video:** [AMAZE Org — Wet Dreams](https://amaze.org/video/puberty-wet-dreams/)  
> **Bổ sung của bài học:** Cách hỗ trợ bạn bè và xử lý lo lắng kéo dài.
""",
        "quiz_title": "Bài tập củng cố kiến thức Bài 3",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video “What is a Wet Dream?” giải thích điều gì?",
                "options": ["Mộng tinh", "Cảm cúm", "Sâu răng", "Cận thị"],
                "correct_index": 0,  # A
                "explanation": "Trọng tâm video là hiện tượng trong giấc ngủ."
            },
            {
                "question_text": "Mộng tinh xảy ra khi nào?",
                "options": ["Khi ngủ", "Khi làm bài", "Khi bơi", "Khi chạy"],
                "correct_index": 0,  # A
                "explanation": "Đây là hiện tượng xảy ra trong lúc ngủ."
            },
            {
                "question_text": "Không có mộng tinh có mặc nhiên là bệnh không?",
                "options": ["Có", "Không", "Chắc chắn vô sinh", "Chắc chắn thiếu ngủ"],
                "correct_index": 1,  # B
                "explanation": "Có người không trải nghiệm hiện tượng này."
            },
            {
                "question_text": "Có mộng tinh có phải điều đáng xấu hổ?",
                "options": ["Có", "Không", "Chỉ nếu ở trường", "Chỉ nếu có bạn bè"],
                "correct_index": 1,  # B
                "explanation": "Đây có thể là một phần phát triển cơ thể."
            },
            {
                "question_text": "Tần suất mộng tinh có giống nhau ở tất cả mọi người?",
                "options": ["Có", "Không", "Phải mỗi đêm", "Phải mỗi tuần"],
                "correct_index": 1,  # B
                "explanation": "Có người gặp thường xuyên, có người không."
            },
            {
                "question_text": "Khi một bạn hỏi về mộng tinh, nên làm gì?",
                "options": ["Trả lời tôn trọng hoặc gợi nguồn tin cậy", "Chế giễu", "Đăng lên mạng", "Bịa thêm lời đồn"],
                "correct_index": 0,  # A
                "explanation": "Chủ đề riêng tư cần sự tôn trọng."
            },
            {
                "question_text": "Có nên lấy trải nghiệm bạn bè làm chuẩn bắt buộc?",
                "options": ["Có", "Không", "Chỉ nếu cùng tuổi", "Chỉ trên mạng"],
                "correct_index": 1,  # B
                "explanation": "Cơ thể mỗi người khác nhau."
            },
            {
                "question_text": "Nếu hiện tượng kèm đau hoặc lo kéo dài, nên làm gì?",
                "options": ["Hỏi nhân viên y tế", "Tự dùng thuốc", "Tin lời đồn", "Im lặng mãi"],
                "correct_index": 0,  # A
                "explanation": "Cần đánh giá cá nhân khi có triệu chứng."
            },
            {
                "question_text": "Video nói khả năng nào có thể bình thường?",
                "options": ["Có hoặc không có mộng tinh", "Chỉ có mỗi đêm", "Chỉ không có", "Không được hỏi"],
                "correct_index": 0,  # A
                "explanation": "Nhà sản xuất nêu cả hai tình huống."
            },
            {
                "question_text": "Ai nên hiểu chủ đề này?",
                "options": ["Mọi học sinh", "Chỉ một giới", "Chỉ giáo viên", "Không ai"],
                "correct_index": 0,  # A
                "explanation": "Hiểu cơ thể giúp mọi người bớt kỳ thị."
            }
        ]
    },
    {
        "order_index": 4,
        "title": "Bài 4 — So mình với người khác: chiếc bẫy mang tên “cơ thể hoàn hảo”",
        "video_url": "https://www.youtube.com/watch?v=v7zUHOEYlN8",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Hình ảnh cơ thể và truyền thông
Video AMAZE *Why Don’t I Like The Way I Look?* giải thích hình ảnh cơ thể là cách ta cảm nhận và đánh giá ngoại hình của mình. Gia đình, bạn bè và hình ảnh truyền thông có thể ảnh hưởng cảm nhận ấy; một số hình trên mạng được chỉnh sửa và không đại diện cho cơ thể ngoài đời. Mọi giới đều có thể thấy tự ti; hãy tránh so sánh với một hình mẫu duy nhất và tôn trọng khác biệt.

> [!NOTE]
> **Nguồn video đối chiếu:** [AMAZE Org — Why Don’t I Like The Way I Look?](https://amaze.org/video/why-dont-i-like-the-way-i-look/)  
> **Nguồn bổ sung về nhịp phát triển cơ thể:** [KidsHealth — Growing Up Normal](https://kidshealth.org/en/kids/growing-up-normal.html)
""",
        "quiz_title": "Bài tập củng cố kiến thức Bài 4",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video về hình ảnh cơ thể đặt trọng tâm vào điều gì?",
                "options": ["Cách ta cảm nhận ngoại hình", "Lái xe", "Địa lý", "Thú cưng"],
                "correct_index": 0,  # A
                "explanation": "Chủ đề là body image."
            },
            {
                "question_text": "“Hình ảnh cơ thể” gần nghĩa gì?",
                "options": ["Cách nghĩ và cảm nhận về cơ thể mình", "Ảnh hộ chiếu", "Bảng điểm", "Đồng phục"],
                "correct_index": 0,  # A
                "explanation": "Đó là nhận thức và cảm xúc với cơ thể."
            },
            {
                "question_text": "Mọi người có cần giống hình mẫu quảng cáo không?",
                "options": ["Có", "Không", "Chỉ ở trường", "Chỉ khi lớn"],
                "correct_index": 1,  # B
                "explanation": "Cơ thể thật đa dạng."
            },
            {
                "question_text": "Điều gì có thể khiến ta tự ti?",
                "options": ["So sánh liên tục với một hình mẫu", "Tìm hỗ trợ", "Tôn trọng bản thân", "Nghỉ ngơi"],
                "correct_index": 0,  # A
                "explanation": "So sánh thiếu thực tế dễ làm ta nhìn cơ thể tiêu cực."
            },
            {
                "question_text": "Giá trị của một người có phụ thuộc hoàn toàn ngoại hình?",
                "options": ["Có", "Không", "Chỉ trên mạng", "Chỉ ở lớp"],
                "correct_index": 1,  # B
                "explanation": "Ngoại hình không định nghĩa toàn bộ con người."
            },
            {
                "question_text": "Nên ứng xử thế nào với bạn tự ti ngoại hình?",
                "options": ["Lắng nghe, tôn trọng", "Chế giễu", "Ép thay đổi", "Đăng ảnh bạn"],
                "correct_index": 0,  # A
                "explanation": "Hỗ trợ tốt hơn phán xét."
            },
            {
                "question_text": "Khi nội dung mạng làm bạn thấy xấu về cơ thể, nên làm gì?",
                "options": ["Tạm dừng và tìm người đáng tin để trao đổi", "Xem nhiều hơn", "Bỏ ăn", "Trêu người khác"],
                "correct_index": 0,  # A
                "explanation": "Điều chỉnh nguồn nội dung và tìm hỗ trợ là hợp lý."
            },
            {
                "question_text": "Câu nào thể hiện thái độ lành mạnh?",
                "options": ["Cơ thể mỗi người khác nhau", "Ai cũng phải giống một mẫu", "Ngoại hình quyết định tất cả", "Tự ti thì đừng nói"],
                "correct_index": 0,  # A
                "explanation": "Sự đa dạng cơ thể là bình thường."
            },
            {
                "question_text": "Bình phẩm ngoại hình người khác có thể gây gì?",
                "options": ["Tổn thương và tự ti", "Chữa mụn", "Tăng kiến thức", "Không tác động"],
                "correct_index": 0,  # A
                "explanation": "Lời bình phẩm có thể ảnh hưởng cảm xúc."
            },
            {
                "question_text": "Vì sao ảnh trên mạng không nên là chuẩn bắt buộc cho mọi cơ thể?",
                "options": ["Một số ảnh được chỉnh sửa và chỉ thể hiện một hình mẫu", "Tất cả ảnh đều là hồ sơ y tế", "Mọi ảnh đều không có người thật", "Không ai dùng mạng"],
                "correct_index": 0,  # A
                "explanation": "AMAZE nêu tác động của truyền thông và những hình ảnh được chỉnh sửa."
            }
        ]
    }
]

async def seed_course_2():
    async with AsyncSessionLocal() as session:
        # Find instructor id
        res = await session.execute(text("SELECT u.id FROM users u JOIN roles r ON u.role_id = r.id WHERE r.role_code = 'INSTRUCTOR' LIMIT 1"))
        instructor_row = res.fetchone()
        if not instructor_row:
            res = await session.execute(text("SELECT u.id FROM users u JOIN roles r ON u.role_id = r.id WHERE r.role_code = 'ADMIN' LIMIT 1"))
            instructor_row = res.fetchone()

        if not instructor_row:
            print("ERROR: No instructor or admin user found to assign course to.")
            return

        instructor_id = uuid.UUID(str(instructor_row[0])) if not isinstance(instructor_row[0], uuid.UUID) else instructor_row[0]
        print(f"Assigning course to instructor: {instructor_id}")

        # Check if course with this slug already exists
        res = await session.execute(text("SELECT id FROM courses WHERE slug = :slug"), {"slug": COURSE_DATA["slug"]})
        existing_course = res.fetchone()
        if existing_course:
            print(f"Course with slug '{COURSE_DATA['slug']}' already exists ({existing_course[0]}). Deleting old instance...")
            await session.execute(text("DELETE FROM courses WHERE id = :id"), {"id": existing_course[0]})
            await session.commit()

        # Create Course
        course_id = uuid.uuid4()
        course = Course(
            id=course_id,
            instructor_id=instructor_id,
            title=COURSE_DATA["title"],
            slug=COURSE_DATA["slug"],
            short_description=COURSE_DATA["short_description"],
            description=COURSE_DATA["description"],
            learning_objectives=COURSE_DATA["learning_objectives"],
            thumbnail_url=COURSE_DATA["thumbnail_url"],
            target_audience=COURSE_DATA["target_audience"],
            is_published=COURSE_DATA["is_published"],
        )
        session.add(course)
        await session.flush()
        print(f"Created Course 2: {course.title} (ID: {course_id})")

        total_questions = 0
        total_options = 0

        for l_data in LESSONS_DATA:
            lesson_id = uuid.uuid4()
            lesson = Lesson(
                id=lesson_id,
                course_id=course_id,
                title=l_data["title"],
                content_type=l_data["content_type"],
                video_url=l_data["video_url"],
                content_body=l_data["content_body"],
                order_index=l_data["order_index"],
                duration_minutes=l_data["duration_minutes"],
            )
            session.add(lesson)
            await session.flush()
            print(f"  -> Created Lesson {l_data['order_index']}: {lesson.title}")

            quiz_id = uuid.uuid4()
            quiz = Quiz(
                id=quiz_id,
                course_id=course_id,
                lesson_id=lesson_id,
                title=l_data["quiz_title"],
                description=l_data["quiz_description"],
                passing_score=80,
                show_correct_answers=True,
                max_attempts=10,
                cooldown_minutes=0,
            )
            session.add(quiz)
            await session.flush()
            print(f"     * Created Quiz: {quiz.title}")

            for q_idx, q_data in enumerate(l_data["questions"], start=1):
                question_id = uuid.uuid4()
                question = QuizQuestion(
                    id=question_id,
                    quiz_id=quiz_id,
                    question_text=q_data["question_text"],
                    explanation=q_data["explanation"],
                    order_index=q_idx,
                )
                session.add(question)
                await session.flush()
                total_questions += 1

                for opt_idx, opt_text in enumerate(q_data["options"], start=1):
                    option_id = uuid.uuid4()
                    is_correct = (opt_idx - 1) == q_data["correct_index"]
                    option = QuizQuestionOption(
                        id=option_id,
                        question_id=question_id,
                        option_text=opt_text,
                        is_correct=is_correct,
                        order_index=opt_idx,
                    )
                    session.add(option)
                    total_options += 1

        await session.commit()
        print("\n=======================================================")
        print("SEEDING COURSE 2 COMPLETED SUCCESSFULLY!")
        print(f"Course: {COURSE_DATA['title']}")
        print(f"Lessons: {len(LESSONS_DATA)}")
        print(f"Quizzes: {len(LESSONS_DATA)}")
        print(f"Total Questions: {total_questions}")
        print(f"Total Options: {total_options}")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(seed_course_2())
