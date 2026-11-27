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
    "title": "Yêu, Thích Và Những Ranh Giới Không Thể Đoán Mò",
    "slug": "yeu-thich-va-nhung-ranh-gioi-khong-the-doan-mo",
    "short_description": "Khóa học giáo dục kỹ năng kết nối, phân biệt quan hệ lành mạnh, nguyên tắc đồng thuận và cách thiết lập ranh giới an toàn cho học sinh tuổi teen.",
    "description": (
        "**Đối tượng:** Học sinh mọi giới, phù hợp lứa tuổi thanh thiếu niên (tuổi teen).\n\n"
        "Khóa học trang bị các kỹ năng thiết thực về cảm xúc lứa đôi, tình bạn và các mối quan hệ xã hội: từ việc nhận diện cảm xúc thích một người, "
        "xây dựng sự kết nối văn minh, phân biệt mối quan hệ lành mạnh và thiếu lành mạnh, đến việc thực hành nguyên tắc đồng thuận rõ ràng, "
        "bảo vệ quyền riêng tư cá nhân trên không gian mạng và cách rời đi an toàn khi một mối quan hệ trở nên độc hại.\n\n"
        "**Cấu trúc khóa học:** Gồm 6 bài học trọng tâm kết hợp video khoa học từ AMAZE Org, các tình huống suy ngẫm thực tế và bài tập củng cố kiến thức 10 câu trắc nghiệm (đạt 8/10 trở lên)."
    ),
    "learning_objectives": (
        "- Nhận diện cảm xúc yêu thích, biết cách tiếp cận tôn trọng và chấp nhận phản hồi từ đối phương.\n"
        "- Phân biệt các dấu hiệu của mối quan hệ lành mạnh (Healthy) và thiếu lành mạnh (Unhealthy).\n"
        "- Hiểu và thực hành nguyên tắc đồng thuận (Consent) trong giao tiếp và tiếp xúc cơ thể: hỏi rõ, lắng nghe và dừng lại.\n"
        "- Tự bảo vệ an toàn cá nhân trong tin nhắn riêng tư, phòng tránh rủi ro phát tán hình ảnh nhạy cảm.\n"
        "- Nhận biết các biểu hiện kiểm soát, thao túng và biết cách lập kế hoạch rời đi an toàn khi bị đe dọa hoặc làm tổn thương."
    ),
    "thumbnail_url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&q=80",
    "target_audience": "CHILD",
    "is_published": True,
}

LESSONS_DATA = [
    {
        "order_index": 1,
        "title": "Bài 1 — Cảm nắng không phải mật mã: bắt đầu kết nối thế nào?",
        "video_url": "https://www.youtube.com/watch?v=lGnEMi8jHHs",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Trọng tâm video
Video giới thiệu cảm giác thích ai đó và các bước tìm hiểu: tiếp cận tôn trọng, tò mò về đối phương, tìm điểm chung, giữ bản sắc của mình và chấp nhận khả năng tình cảm không được đáp lại. Không ai có nghĩa vụ đáp lại tình cảm của người khác.

### 2. Áp dụng
- Học sinh thuộc mọi giới đều có quyền đặt ranh giới và trách nhiệm tôn trọng người khác.
- Nếu gặp tình huống gây sợ hãi hoặc bị ép buộc, hãy tìm người lớn đáng tin hoặc chuyên gia phù hợp.

### 3. Tình huống suy ngẫm
Bạn muốn trò chuyện với một người mình thích. Hãy bắt đầu bằng chủ đề chung, quan sát họ có muốn tiếp tục nói chuyện hay không. Nếu họ từ chối hoặc không thoải mái, hãy dừng. Bạn vẫn có thể giữ tình bạn và sở thích của riêng mình. Cảm giác hụt hẫng sau khi bị từ chối là có thể xảy ra; không biến cảm giác ấy thành áp lực lên người khác.

> [!NOTE]
> **Video tham khảo:** *What To Do When You Have a Crush (Ft. Huntrix)* — AMAZE Org.
> Nguồn đối chiếu: [https://www.youtube.com/watch?v=lGnEMi8jHHs](https://www.youtube.com/watch?v=lGnEMi8jHHs)
""",
        "quiz_title": "Bài tập củng cố kiến thức Bài 1",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video tập trung vào điều gì?",
                "options": ["Cách ứng xử khi thích một người", "Kế hoạch mua nhà", "Tư vấn thuốc", "Luật giao thông"],
                "correct_index": 0,  # A
                "explanation": "Đó là chủ đề được nhà sản xuất nêu."
            },
            {
                "question_text": "Bước nào phù hợp khi muốn tìm hiểu người mình thích?",
                "options": ["Hỏi về sở thích của họ", "Theo dõi bí mật", "Ép họ trả lời", "Đăng chuyện riêng"],
                "correct_index": 0,  # A
                "explanation": "Tìm hiểu bằng trò chuyện tôn trọng."
            },
            {
                "question_text": "“Tìm điểm chung” nghĩa là gì?",
                "options": ["Khám phá sở thích cùng chia sẻ", "Giả vờ giống hệt người ấy", "Kiểm tra điện thoại", "Bắt họ đổi ý"],
                "correct_index": 0,  # A
                "explanation": "Video nêu việc tìm hiểu điểm chung."
            },
            {
                "question_text": "Nếu cảm xúc không được đáp lại, nên làm gì?",
                "options": ["Tôn trọng và chăm sóc bản thân", "Gây áp lực", "Đăng lời xúc phạm", "Đe dọa"],
                "correct_index": 0,  # A
                "explanation": "Không ai bắt buộc phải đáp lại."
            },
            {
                "question_text": "Khi thích ai đó, có cần đánh mất sở thích của mình?",
                "options": ["Có", "Không", "Chỉ trên mạng", "Chỉ ở trường"],
                "correct_index": 1,  # B
                "explanation": "Video khuyên giữ đúng bản thân."
            },
            {
                "question_text": "Sự tò mò phù hợp là gì?",
                "options": ["Hỏi và lắng nghe nếu người kia muốn chia sẻ", "Xem trộm tin nhắn", "Hỏi liên tục sau khi bị từ chối", "Nhờ bạn ép"],
                "correct_index": 0,  # A
                "explanation": "Tò mò đi cùng tôn trọng ranh giới."
            },
            {
                "question_text": "Cảm nắng có đồng nghĩa đã ở trong một mối quan hệ?",
                "options": ["Có", "Không", "Chỉ nếu cùng lớp", "Chỉ khi nhắn tin"],
                "correct_index": 1,  # B
                "explanation": "Cảm xúc của một người không tạo ra cam kết của người khác."
            },
            {
                "question_text": "Điều gì có thể giúp bắt đầu kết nối?",
                "options": ["Trò chuyện tự nhiên về điểm chung", "Tung tin đồn", "Đăng ảnh riêng tư", "Đòi mật khẩu"],
                "correct_index": 0,  # A
                "explanation": "Video gợi ý tìm điểm chung."
            },
            {
                "question_text": "Khi bị từ chối, cách ứng xử nào phù hợp?",
                "options": ["Chấp nhận quyết định của họ", "Tiếp tục ép", "Trả đũa", "Lôi kéo bạn bè"],
                "correct_index": 0,  # A
                "explanation": "Tôn trọng lựa chọn của người khác."
            },
            {
                "question_text": "Thông điệp bao trùm bài là gì?",
                "options": ["Kết nối tôn trọng cả hai bên", "Có mẹo khiến ai cũng thích mình", "Tình cảm là quyền sở hữu", "Thích ai phải công khai"],
                "correct_index": 0,  # A
                "explanation": "Một kết nối tốt bắt đầu từ tôn trọng."
            }
        ]
    },
    {
        "order_index": 2,
        "title": "Bài 2 — Đèn xanh hay đèn đỏ? Nhận diện một mối quan hệ",
        "video_url": "https://www.youtube.com/watch?v=Gn7ZQ2x0cOE",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Trọng tâm video
Video so sánh tình bạn và tình cảm lành mạnh với quan hệ thiếu lành mạnh. Những dấu hiệu tích cực gồm hỗ trợ, lắng nghe, bất đồng với sự tôn trọng và không để một người phải nhượng bộ mọi lần. Một mối quan hệ nên giúp người trong cuộc cảm thấy được tôn trọng; khi thấy sợ hãi hoặc bị kiểm soát, có thể tìm người lớn đáng tin giúp đỡ.

### 2. Áp dụng
- Học sinh thuộc mọi giới đều có quyền đặt ranh giới và trách nhiệm tôn trọng người khác.
- Nếu gặp tình huống gây sợ hãi hoặc bị ép buộc, hãy tìm người lớn đáng tin hoặc chuyên gia phù hợp.

### 3. Dấu hiệu để tự kiểm tra
Trong một tình bạn hoặc tình cảm, hai người có thể bất đồng mà vẫn lắng nghe nhau. Nếu một người thường xuyên sợ nêu ý kiến, bị cô lập khỏi bạn bè hoặc luôn phải nhượng bộ, đó là lý do để tìm người lớn đáng tin trao đổi. Một dấu hiệu riêng lẻ không đủ để kết luận về toàn bộ mối quan hệ; hãy xem hành vi lặp lại và cảm giác an toàn của người trong cuộc.

> [!NOTE]
> **Video tham khảo:** *Healthy vs Unhealthy Relationships* — AMAZE Org.
> Nguồn đối chiếu: [https://amaze.org/video/healthy-vs-unhealthy-relationships/](https://amaze.org/video/healthy-vs-unhealthy-relationships/)
""",
        "quiz_title": "Bài tập củng cố kiến thức Bài 2",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video so sánh điều gì?",
                "options": ["Quan hệ lành mạnh và thiếu lành mạnh", "Hai môn học", "Hai loại điện thoại", "Hai món ăn"],
                "correct_index": 0,  # A
                "explanation": "Đó là chủ đề video."
            },
            {
                "question_text": "Dấu hiệu nào thường tích cực?",
                "options": ["Hai người lắng nghe nhau", "Một người luôn kiểm soát", "Dọa chia tay", "Cấm có bạn bè"],
                "correct_index": 0,  # A
                "explanation": "Lắng nghe là nền tảng quan hệ lành mạnh."
            },
            {
                "question_text": "Bất đồng có tự động làm quan hệ thiếu lành mạnh?",
                "options": ["Có", "Không, cách trao đổi mới quan trọng", "Chỉ với bạn bè", "Chỉ trên mạng"],
                "correct_index": 1,  # B
                "explanation": "Có thể bất đồng mà vẫn tôn trọng."
            },
            {
                "question_text": "Nếu cùng một người luôn phải nhượng bộ, nên nghĩ gì?",
                "options": ["Cần xem lại sự cân bằng", "Đó là bắt buộc", "Chắc chắn bình thường", "Cần giấu"],
                "correct_index": 0,  # A
                "explanation": "Thỏa hiệp không nên chỉ đặt lên một người."
            },
            {
                "question_text": "Bạn tốt thường quan tâm điều gì?",
                "options": ["Suy nghĩ và cảm nhận của bạn", "Chỉ mật khẩu", "Chỉ số người theo dõi", "Chỉ lời khen"],
                "correct_index": 0,  # A
                "explanation": "Quan hệ tốt có sự lắng nghe."
            },
            {
                "question_text": "Dấu hiệu nào đáng lo?",
                "options": ["Người kia khiến bạn sợ nói thật", "Lắng nghe", "Tôn trọng giới hạn", "Khích lệ sở thích"],
                "correct_index": 0,  # A
                "explanation": "Sợ hãi có thể báo hiệu quan hệ không an toàn."
            },
            {
                "question_text": "Một quan hệ tốt giúp bạn cảm thấy thế nào?",
                "options": ["Được tôn trọng là chính mình", "Luôn phải đóng vai", "Luôn sợ sai", "Bị cô lập"],
                "correct_index": 0,  # A
                "explanation": "Sự an toàn và tôn trọng là quan trọng."
            },
            {
                "question_text": "Khi thấy quan hệ có dấu hiệu kiểm soát, nên?",
                "options": ["Tìm người lớn đáng tin trao đổi", "Đổ lỗi bản thân", "Giấu mãi", "Chấp nhận mọi yêu cầu"],
                "correct_index": 0,  # A
                "explanation": "Hỗ trợ bên ngoài có thể hữu ích."
            },
            {
                "question_text": "Từ chối một yêu cầu mình không thoải mái có thể là gì?",
                "options": ["Thể hiện ranh giới", "Bằng chứng không quan tâm", "Luôn ích kỷ", "Một tội lỗi"],
                "correct_index": 0,  # A
                "explanation": "Mỗi người có quyền đặt giới hạn."
            },
            {
                "question_text": "Bài học áp dụng cho những mối quan hệ nào?",
                "options": ["Tình bạn và tình cảm", "Chỉ người đã kết hôn", "Chỉ người lớn", "Chỉ người nổi tiếng"],
                "correct_index": 0,  # A
                "explanation": "Video nói cả bạn bè và quan hệ tình cảm."
            }
        ]
    },
    {
        "order_index": 3,
        "title": "Bài 3 — “Im lặng” có phải câu trả lời? Hỏi rõ trước khi chạm",
        "video_url": "https://www.youtube.com/watch?v=1wOqcU79Rh8",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Trọng tâm video
Video giải thích đồng thuận và giao tiếp. Không nghe thấy “không” không có nghĩa đã nghe thấy “có”. Một người có thể nói rõ mong muốn hoặc ranh giới, người kia cần lắng nghe và dừng khi không có sự đồng ý. Nếu bị chạm vào trái ý muốn, học sinh có thể nói dừng lại và tìm người lớn đáng tin; người bị xâm phạm không có lỗi.

### 2. Áp dụng
- Học sinh thuộc mọi giới đều có quyền đặt ranh giới và trách nhiệm tôn trọng người khác.
- Nếu gặp tình huống gây sợ hãi hoặc bị ép buộc, hãy tìm người lớn đáng tin hoặc chuyên gia phù hợp.

### 3. Tập nói rõ ranh giới
Có thể dùng câu ngắn như “Mình không muốn”, “Hãy dừng lại” hoặc “Mình cần thêm thời gian”. Khi nghe lời từ chối, hãy dừng hành động và không tranh luận để buộc người kia đổi ý. Nếu bị chạm vào trái ý muốn hoặc khó tự bảo vệ, hãy tìm người lớn đáng tin; bạn không có lỗi vì hành vi vượt ranh giới của người khác.

> [!NOTE]
> **Video tham khảo:** *Consent and Communication* — AMAZE Org.
> Nguồn đối chiếu: [https://amaze.org/video/healthy-relationships-consent-and-communication/](https://amaze.org/video/healthy-relationships-consent-and-communication/)
""",
        "quiz_title": "Bài tập củng cố kiến thức Bài 3",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Đồng thuận cần điều gì?",
                "options": ["Sự đồng ý rõ ràng", "Sự im lặng", "Một lời đồn", "Chỉ ánh mắt"],
                "correct_index": 0,  # A
                "explanation": "Không thể suy ra đồng ý khi người kia im lặng."
            },
            {
                "question_text": "Không nghe thấy “không” có tự động nghĩa là “có”?",
                "options": ["Có", "Không", "Chỉ với bạn thân", "Chỉ trên mạng"],
                "correct_index": 1,  # B
                "explanation": "Video nhấn mạnh cần giao tiếp rõ."
            },
            {
                "question_text": "Khi không chắc bạn có muốn một cái ôm, nên?",
                "options": ["Hỏi bạn trước", "Tự đoán", "Bất ngờ ôm", "Nhờ người khác quyết"],
                "correct_index": 0,  # A
                "explanation": "Hỏi là cách tôn trọng ranh giới."
            },
            {
                "question_text": "Nếu người kia nói dừng lại, nên?",
                "options": ["Dừng ngay", "Cố thêm lần nữa", "Tranh luận", "Cười trừ rồi tiếp tục"],
                "correct_index": 0,  # A
                "explanation": "Quyết định của họ phải được tôn trọng."
            },
            {
                "question_text": "Nếu ai đó chạm vào bạn trái ý muốn, điều nào phù hợp?",
                "options": ["Nói dừng và tìm người lớn đáng tin", "Tự nhận lỗi", "Im lặng mãi", "Chiều theo"],
                "correct_index": 0,  # A
                "explanation": "Có thể yêu cầu dừng và tìm hỗ trợ."
            },
            {
                "question_text": "Người bị chạm trái ý muốn có phải người gây lỗi?",
                "options": ["Có", "Không", "Chỉ khi là bạn bè", "Chỉ lúc đi học"],
                "correct_index": 1,  # B
                "explanation": "Trách nhiệm thuộc về người vượt ranh giới."
            },
            {
                "question_text": "Một lời đồng ý cho hành động A có tự động áp dụng hành động B?",
                "options": ["Có", "Không", "Chỉ khi quen lâu", "Chỉ nếu cùng lớp"],
                "correct_index": 1,  # B
                "explanation": "Cần hỏi về hành động cụ thể."
            },
            {
                "question_text": "Giao tiếp về ranh giới giúp gì?",
                "options": ["Hiểu mong muốn của nhau", "Bỏ quyền từ chối", "Thay lời xin lỗi", "Giấu sự không thoải mái"],
                "correct_index": 0,  # A
                "explanation": "Giao tiếp làm ranh giới rõ hơn."
            },
            {
                "question_text": "Nếu bạn ngại nói trực tiếp, nên làm gì?",
                "options": ["Tìm cách diễn đạt hoặc người hỗ trợ phù hợp", "Coi im lặng là đồng ý", "Để người kia quyết hết", "Ép bản thân"],
                "correct_index": 0,  # A
                "explanation": "Bạn có quyền giao tiếp theo cách an toàn."
            },
            {
                "question_text": "Thông điệp chính là gì?",
                "options": ["Hỏi, lắng nghe và tôn trọng câu trả lời", "Đoán ý người khác", "Thử trước hỏi sau", "Chỉ nghe lời bạn bè"],
                "correct_index": 0,  # A
                "explanation": "Đồng thuận cần giao tiếp rõ ràng."
            }
        ]
    },
    {
        "order_index": 4,
        "title": "Bài 4 — Tin nhắn riêng tư có thật sự riêng tư?",
        "video_url": "https://www.youtube.com/watch?v=RWxAimnKupE",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Trọng tâm video
Video nói về rủi ro của việc gửi ảnh nhạy cảm qua tin nhắn: ảnh có thể bị chia sẻ tiếp hoặc đăng mạng. Mỗi người có quyền từ chối gửi ảnh; cảm giác thích ai đó không tạo nghĩa vụ gửi ảnh. Nếu bị gây áp lực hoặc đe dọa, hãy tìm người lớn đáng tin và không phát tán ảnh của người khác. Pháp luật tùy quốc gia; không áp nguyên văn ví dụ luật của video Mỹ vào Việt Nam.

### 2. Áp dụng
- Học sinh thuộc mọi giới đều có quyền đặt ranh giới và trách nhiệm tôn trọng người khác.
- Nếu gặp tình huống gây sợ hãi hoặc bị ép buộc, hãy tìm người lớn đáng tin hoặc chuyên gia phù hợp.

### 3. An toàn trong tin nhắn
Trước khi chia sẻ ảnh hay tin nhắn riêng tư, hãy nghĩ đến khả năng nội dung bị lưu, chụp màn hình hoặc chuyển tiếp. Khi bị gây áp lực, có thể từ chối mà không cần chứng minh tình cảm. Nếu ai đó đe dọa phát tán ảnh, đừng gửi thêm nội dung; lưu thông tin đe dọa và tìm người lớn đáng tin giúp. Không tự chuyển tiếp ảnh nhạy cảm để “lấy bằng chứng”.

> [!NOTE]
> **Video tham khảo:** *Sexting: What Should You Do?* — AMAZE Org.
> Nguồn đối chiếu: [https://amaze.org/video/personal-safety-sexting/](https://amaze.org/video/personal-safety-sexting/)
""",
        "quiz_title": "Bài tập củng cố kiến thức Bài 4",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video nói về điều gì?",
                "options": ["Gửi ảnh nhạy cảm và rủi ro chia sẻ", "Nấu ăn", "Học bơi", "Tiêm chủng"],
                "correct_index": 0,  # A
                "explanation": "Đó là tình huống chính của video."
            },
            {
                "question_text": "Sau khi gửi một ảnh, người gửi có kiểm soát tuyệt đối việc chia sẻ tiếp?",
                "options": ["Có", "Không", "Chỉ trên điện thoại mới", "Chỉ nếu yêu nhau"],
                "correct_index": 1,  # B
                "explanation": "Ảnh có thể bị chuyển tiếp hoặc đăng mạng."
            },
            {
                "question_text": "Nếu người khác gây áp lực buộc gửi ảnh, bạn có quyền?",
                "options": ["Từ chối", "Phải gửi", "Chỉ được im lặng", "Phải trả tiền"],
                "correct_index": 0,  # A
                "explanation": "Không ai có quyền ép bạn gửi ảnh."
            },
            {
                "question_text": "Thích một người có nghĩa phải gửi ảnh thân mật?",
                "options": ["Có", "Không", "Chỉ ở lớp", "Chỉ khi nhắn lâu"],
                "correct_index": 1,  # B
                "explanation": "Tình cảm không tạo nghĩa vụ gửi ảnh."
            },
            {
                "question_text": "Nhận được ảnh riêng tư của người khác thì nên?",
                "options": ["Không chuyển tiếp", "Đăng lên nhóm", "Gửi bạn xem", "Dùng đe dọa"],
                "correct_index": 0,  # A
                "explanation": "Chuyển tiếp làm tăng tổn hại."
            },
            {
                "question_text": "Nếu bị đe dọa phát tán ảnh, nên?",
                "options": ["Tìm người lớn đáng tin hỗ trợ", "Tự gánh một mình", "Gửi thêm ảnh", "Phát tán ảnh khác"],
                "correct_index": 0,  # A
                "explanation": "Cần hỗ trợ an toàn và kịp thời."
            },
            {
                "question_text": "Pháp luật được nhắc trong video Mỹ có tự động áp dụng y hệt ở Việt Nam?",
                "options": ["Có", "Không", "Chỉ trên mạng", "Chỉ với học sinh"],
                "correct_index": 1,  # B
                "explanation": "Quy định pháp luật tùy quốc gia."
            },
            {
                "question_text": "Nội dung trên mạng có thể lan rộng vì điều gì?",
                "options": ["Người nhận lưu hoặc chia sẻ tiếp", "Ảnh tự biến mất chắc chắn", "Không ai có thể chụp lại", "Mọi app bảo đảm riêng tư tuyệt đối"],
                "correct_index": 0,  # A
                "explanation": "Tin nhắn và ảnh có thể được lưu/chuyển tiếp."
            },
            {
                "question_text": "Cách bày tỏ sự thích một người nào phù hợp?",
                "options": ["Giao tiếp và tôn trọng", "Ép gửi ảnh", "Đòi mật khẩu", "Đe dọa chia tay"],
                "correct_index": 0,  # A
                "explanation": "Có nhiều cách thể hiện tình cảm không gây áp lực."
            },
            {
                "question_text": "Ai có trách nhiệm khi cố tình phát tán ảnh riêng tư?",
                "options": ["Người thực hiện hành vi phát tán", "Nạn nhân", "Bạn cùng lớp", "Người hỏi giúp"],
                "correct_index": 0,  # A
                "explanation": "Không đổ lỗi cho người bị xâm phạm quyền riêng tư."
            }
        ]
    },
    {
        "order_index": 5,
        "title": "Bài 5 — Yêu mà phải sợ: đó có phải yêu?",
        "video_url": "https://www.youtube.com/watch?v=UB9anEZx9LU",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Trọng tâm video
Video nêu các đặc điểm của quan hệ lành mạnh: giao tiếp, tin cậy, an toàn về thể chất lẫn cảm xúc và tôn trọng. Bình đẳng có nghĩa hai người đều có tiếng nói; không dùng im lặng hay sức ép để kiểm soát bất đồng. Nội dung áp dụng cho tình bạn lẫn mối quan hệ tình cảm, mọi giới.

### 2. Áp dụng
- Học sinh thuộc mọi giới đều có quyền đặt ranh giới và trách nhiệm tôn trọng người khác.
- Nếu gặp tình huống gây sợ hãi hoặc bị ép buộc, hãy tìm người lớn đáng tin hoặc chuyên gia phù hợp.

### 3. Giao tiếp cân bằng
Mỗi người được nói điều mình nghĩ, bày tỏ nhu cầu và từ chối điều không phù hợp. Lắng nghe không có nghĩa đồng ý mọi yêu cầu; thỏa hiệp cũng không có nghĩa một người luôn phải nhường. Nếu nỗi sợ phản ứng của đối phương khiến bạn không dám nói thật, hãy xem đó là dấu hiệu để tìm hỗ trợ, thay vì coi sự kiểm soát là tình yêu.

> [!NOTE]
> **Video tham khảo:** *What Makes A Relationship Healthy?* — AMAZE Org.
> Nguồn đối chiếu: [https://amaze.org/video/healthy-relationships-makes-relationship-healthy/](https://amaze.org/video/healthy-relationships-makes-relationship-healthy/)
""",
        "quiz_title": "Bài tập củng cố kiến thức Bài 5",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video nêu phẩm chất nào của quan hệ lành mạnh?",
                "options": ["Tôn trọng", "Kiểm soát", "Cô lập", "Đe dọa"],
                "correct_index": 0,  # A
                "explanation": "Tôn trọng là một đặc điểm quan trọng."
            },
            {
                "question_text": "Giao tiếp tốt nghĩa là gì?",
                "options": ["Có thể nói và nghe một cách cởi mở", "Một người chỉ ra lệnh", "Cố tình im lặng để phạt", "Đoán mọi ý"],
                "correct_index": 0,  # A
                "explanation": "Hai bên cùng trao đổi cảm xúc và nhu cầu."
            },
            {
                "question_text": "Một quan hệ an toàn về cảm xúc cho phép điều gì?",
                "options": ["Nói thật mà không sợ bị đe dọa", "Luôn phải đồng ý", "Không được có bạn riêng", "Không được hỏi"],
                "correct_index": 0,  # A
                "explanation": "An toàn cảm xúc giúp bày tỏ ý kiến."
            },
            {
                "question_text": "Nếu một người muốn kiểm soát mọi quyết định, đó là dấu hiệu gì?",
                "options": ["Thiếu bình đẳng", "Luôn là quan tâm", "Luôn là tình yêu", "Chỉ là sở thích"],
                "correct_index": 0,  # A
                "explanation": "Kiểm soát làm mất tiếng nói của người kia."
            },
            {
                "question_text": "Niềm tin trong quan hệ có đồng nghĩa phải đưa mật khẩu?",
                "options": ["Có", "Không", "Chỉ nếu thân", "Chỉ nếu nhắn tin"],
                "correct_index": 1,  # B
                "explanation": "Tôn trọng riêng tư không đòi mật khẩu."
            },
            {
                "question_text": "Khi bất đồng, cách ứng xử nào phù hợp?",
                "options": ["Nói rõ và lắng nghe", "Im lặng trừng phạt", "Đe dọa", "Bôi nhọ"],
                "correct_index": 0,  # A
                "explanation": "Video coi trao đổi tôn trọng là tích cực."
            },
            {
                "question_text": "An toàn thể chất và cảm xúc thuộc về ai?",
                "options": ["Cả hai bên", "Chỉ một người", "Chỉ phụ huynh", "Chỉ người lớn"],
                "correct_index": 0,  # A
                "explanation": "Mọi người đều cần cảm thấy an toàn."
            },
            {
                "question_text": "Nếu người kia nói “không”, nên?",
                "options": ["Tôn trọng", "Coi là thử thách", "Ép tiếp", "Dọa bỏ đi"],
                "correct_index": 0,  # A
                "explanation": "Tôn trọng ranh giới là nền tảng quan hệ."
            },
            {
                "question_text": "Thỏa hiệp cân bằng là gì?",
                "options": ["Cả hai có tiếng nói", "Một người luôn nhường", "Một người quyết mọi thứ", "Không ai được nói"],
                "correct_index": 0,  # A
                "explanation": "Quan hệ bình đẳng cần phối hợp hai chiều."
            },
            {
                "question_text": "Video dành cho việc đánh giá quan hệ nào?",
                "options": ["Bạn bè và tình cảm", "Chỉ hôn nhân", "Chỉ người nổi tiếng", "Chỉ giao dịch"],
                "correct_index": 0,  # A
                "explanation": "Kỹ năng này áp dụng nhiều mối quan hệ."
            }
        ]
    },
    {
        "order_index": 6,
        "title": "Bài 6 — Khi quan hệ làm mình đau: kế hoạch rời đi an toàn",
        "video_url": "https://www.youtube.com/watch?v=lv2q7LWSl8s",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Trọng tâm video
Video giới thiệu dấu hiệu một mối quan hệ thiếu lành mạnh và cách lập kế hoạch kết thúc, trao đổi phù hợp, nhờ người lớn đáng tin khi cần. An toàn được ưu tiên: nếu lo sợ bị trả đũa hoặc bạo lực, đừng tự gặp riêng đối phương; trao đổi với người hỗ trợ và chọn cách liên hệ an toàn.

### 2. Áp dụng
- Học sinh thuộc mọi giới đều có quyền đặt ranh giới và trách nhiệm tôn trọng người khác.
- Nếu gặp tình huống gây sợ hãi hoặc bị ép buộc, hãy tìm người lớn đáng tin hoặc chuyên gia phù hợp.

### 3. Kế hoạch rời đi an toàn
Viết ra người lớn đáng tin có thể gọi, địa điểm an toàn và cách liên lạc nếu đối phương gây áp lực. Chọn cách thông báo phù hợp mức độ an toàn; không bắt buộc gặp riêng khi có nguy cơ bị đe dọa. Sau khi kết thúc, có thể chặn liên lạc quấy rối và nhờ nhà trường hoặc cơ quan hỗ trợ khi cần. Nếu bạn đang trong nguy hiểm tức thời, ưu tiên rời khỏi nơi nguy hiểm và gọi trợ giúp khẩn cấp ở địa phương.

> [!NOTE]
> **Video tham khảo:** *How to Get Out of an Unhealthy Relationship* — AMAZE Org.
> Nguồn đối chiếu: [https://amaze.org/video/how-to-get-out-of-an-unhealthy-relationship/](https://amaze.org/video/how-to-get-out-of-an-unhealthy-relationship/)
""",
        "quiz_title": "Bài tập củng cố kiến thức Bài 6",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video hướng dẫn điều gì?",
                "options": ["Rời một quan hệ thiếu lành mạnh", "Cách nấu ăn", "Chăm sóc thú cưng", "Luyện thi"],
                "correct_index": 0,  # A
                "explanation": "Đó là mục đích video."
            },
            {
                "question_text": "Dấu hiệu nào cần chú ý?",
                "options": ["Bạn thường xuyên thấy sợ hãi hoặc bị kiểm soát", "Bạn được tôn trọng", "Bạn có thể nói không", "Bạn được lắng nghe"],
                "correct_index": 0,  # A
                "explanation": "Sợ hãi và kiểm soát là dấu hiệu cảnh báo."
            },
            {
                "question_text": "Trước khi kết thúc quan hệ khó khăn, nên?",
                "options": ["Lập kế hoạch an toàn", "Quyết định khi đang bị đe dọa", "Đến nơi vắng một mình", "Phát tán ảnh"],
                "correct_index": 0,  # A
                "explanation": "Video nói về kế hoạch chia tay."
            },
            {
                "question_text": "Ai có thể hỗ trợ học sinh?",
                "options": ["Người lớn đáng tin", "Chỉ người đang đe dọa", "Tài khoản vô danh", "Không ai"],
                "correct_index": 0,  # A
                "explanation": "Video khuyến khích tìm người lớn đáng tin."
            },
            {
                "question_text": "Nếu sợ bị trả đũa, có bắt buộc gặp riêng để nói trực tiếp?",
                "options": ["Có", "Không", "Chỉ ban đêm", "Chỉ ở nhà"],
                "correct_index": 1,  # B
                "explanation": "Ưu tiên an toàn và nhờ hỗ trợ."
            },
            {
                "question_text": "Khi kết thúc quan hệ, có cần quản lý cảm xúc thay cho đối phương?",
                "options": ["Có, mọi lúc", "Không, chỉ cần trao đổi rõ và an toàn", "Phải hứa quay lại", "Phải tiết lộ mật khẩu"],
                "correct_index": 1,  # B
                "explanation": "Bạn chịu trách nhiệm về quyết định và an toàn của mình."
            },
            {
                "question_text": "Một kế hoạch có thể bao gồm gì?",
                "options": ["Người hỗ trợ và cách liên hệ an toàn", "Chỉ lời đe dọa", "Chỉ tin nhắn công khai", "Không thông tin nào"],
                "correct_index": 0,  # A
                "explanation": "Lập kế hoạch giúp xử lý tình huống."
            },
            {
                "question_text": "Nếu bạn thân nói họ sợ người yêu, nên?",
                "options": ["Lắng nghe và giúp tìm người hỗ trợ", "Chế giễu", "Đăng chuyện lên mạng", "Ép họ tự giải quyết"],
                "correct_index": 0,  # A
                "explanation": "Hỗ trợ không phán xét hữu ích."
            },
            {
                "question_text": "Một người có quyền kết thúc quan hệ không phù hợp không?",
                "options": ["Có", "Không", "Chỉ nếu đối phương cho phép", "Chỉ nếu có lý do công khai"],
                "correct_index": 0,  # A
                "explanation": "Quyền quyết định tham gia quan hệ thuộc về mỗi người."
            },
            {
                "question_text": "Thông điệp chính của bài là gì?",
                "options": ["Rời đi có kế hoạch và tìm hỗ trợ khi cần", "Chịu đựng bằng mọi giá", "Tự gặp đối phương khi nguy hiểm", "Giữ bí mật mọi đe dọa"],
                "correct_index": 0,  # A
                "explanation": "An toàn cá nhân được ưu tiên."
            }
        ]
    }
]

async def seed_course_3():
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
        print(f"Created Course 3: {course.title} (ID: {course_id})")

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
        print("SEEDING COURSE 3 COMPLETED SUCCESSFULLY!")
        print(f"Course: {COURSE_DATA['title']}")
        print(f"Lessons: {len(LESSONS_DATA)}")
        print(f"Quizzes: {len(LESSONS_DATA)}")
        print(f"Total Questions: {total_questions}")
        print(f"Total Options: {total_options}")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(seed_course_3())
