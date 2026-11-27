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
    "title": "Mở Lời Trước Khi Con Phải Tự Tìm Trên Mạng",
    "slug": "mo-loi-truoc-khi-con-phai-tu-tim-tren-mang",
    "short_description": "Cẩm nang đồng hành dành cho phụ huynh có con 4–12 tuổi: cách trả lời câu hỏi khó, bảo vệ ranh giới cơ thể và xây dựng niềm tin trước tuổi dậy thì.",
    "description": (
        "**Đối tượng:** Phụ huynh có con trong độ tuổi khoảng 4–12 tuổi.\n\n"
        "Khóa học cung cấp cho cha mẹ những kỹ năng và phương pháp giao tiếp cởi mở, đúng khoa học và phù hợp lứa tuổi về giáo dục giới tính: "
        "từ cách đón nhận những câu hỏi bất ngờ đầu tiên, dạy con gọi đúng tên các bộ phận cơ thể và ranh giới an toàn, giải thích nguồn gốc thai kỳ một cách chân thực, "
        "đến việc truyền tải giá trị gia đình và chủ động mở lời đối thoại khi con bước vào giai đoạn tiền dậy thì.\n\n"
        "**Cấu trúc khóa học:** Gồm 6 bài học kèm video chuyên sâu từ AMAZE Parents và Planned Parenthood, bài tập tình huống thực tế và 6 bài kiểm tra trắc nghiệm củng cố kiến thức (đạt 8/10 trở lên)."
    ),
    "learning_objectives": (
        "- Bình tĩnh đón nhận và trả lời khéo léo những câu hỏi bất ngờ đầu tiên của con về cơ thể và giới tính.\n"
        "- Dạy con gọi đúng tên các bộ phận cơ thể (bao gồm vùng riêng tư) và thiết lập quy tắc ranh giới cơ thể an toàn.\n"
        "- Giải thích nguồn gốc em bé và thai kỳ một cách chân thực, ngắn gọn và phù hợp nhận thức của trẻ.\n"
        "- Truyền tải giá trị gia đình dựa trên sự tôn trọng, đối thoại và không bóp méo sự thật khoa học.\n"
        "- Nhận diện giai đoạn tiền dậy thì và kỹ năng chủ động mở lời đối thoại ngay cả khi con chưa chủ động hỏi."
    ),
    "thumbnail_url": "https://images.unsplash.com/photo-1491438590914-bc09fcaaf77a?auto=format&fit=crop&w=1200&q=80",
    "target_audience": "PARENT",
    "is_published": True,
}

LESSONS_DATA = [
    {
        "order_index": 1,
        "title": "Bài 1 — Câu hỏi đầu tiên: trả lời sao để con còn muốn hỏi tiếp?",
        "video_url": "https://www.youtube.com/watch?v=YbtXbnkP690",
        "duration_minutes": 12,
        "content_type": "HYBRID",
        "content_body": """### 1. Điểm xuất phát
Trẻ nhỏ có thể hỏi bất chợt về cơ thể, tình cảm hoặc sinh sản. Hãy bình tĩnh, cảm ơn con đã hỏi và tìm hiểu chính xác điều con muốn biết trước khi trả lời. Một câu trả lời ngắn, trung thực và phù hợp tuổi giúp giữ cuộc đối thoại mở.

### 2. Ba bước dễ thực hiện
- Hỏi lại: *“Con đã nghe điều đó ở đâu?”* hoặc *“Con đang thắc mắc phần nào?”*.
- Trả lời đúng trọng tâm câu hỏi bằng từ ngữ rõ ràng, trung thực.
- Hỏi lại: *“Câu trả lời này đã giúp con hiểu chưa?”*. Không biến một câu hỏi nhỏ thành bài thuyết trình quá dài.

### 3. Khi thấy khó nói
Có thể nói: *“Bố/mẹ cần nghĩ thêm để giải thích cho đúng; tối nay mình nói tiếp nhé”*, rồi thực sự quay lại trao đổi với con. Tránh trách mắng hoặc gán việc tò mò là xấu hay hư.

### 4. Thực hành
Khi con hỏi *“Vì sao cơ thể mọi người khác nhau?”*, thử đáp: *“Mỗi cơ thể có những điểm giống và khác nhau. Con đang tò mò về điều gì cụ thể?”*

> [!NOTE]
> **Trọng tâm nguồn:** AMAZE Parents, *How do you talk to young kids about sex?*  
> **Tài liệu đối chiếu:** [https://amaze.org/jrParents/](https://amaze.org/jrParents/)
""",
        "quiz_title": "Củng cố bài 1 — Câu hỏi đầu tiên: trả lời sao để con còn muốn hỏi tiếp?",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Con đặt câu hỏi bất ngờ về cơ thể; phản ứng đầu tiên phù hợp là gì?",
                "options": [
                    "Cảm ơn con đã hỏi và lắng nghe điều con thắc mắc",
                    "Yêu cầu con đừng nhắc đến nữa",
                    "Giải thích mọi kiến thức sinh sản ngay lập tức",
                    "Chuyển hẳn chủ đề sang bài tập"
                ],
                "correct_index": 0,
                "explanation": "Sự bình tĩnh và lắng nghe giúp con tiếp tục hỏi."
            },
            {
                "question_text": "Vì sao nên hỏi “Con đã nghe điều đó ở đâu?”",
                "options": [
                    "Để phạt người đã nói với con",
                    "Để hiểu bối cảnh và điều con thật sự muốn biết",
                    "Để trì hoãn mọi câu trả lời",
                    "Để kiểm tra trí nhớ của con"
                ],
                "correct_index": 1,
                "explanation": "Biết bối cảnh giúp trả lời trúng thắc mắc."
            },
            {
                "question_text": "Trẻ hỏi một ý rất cụ thể; độ dài câu trả lời nên thế nào?",
                "options": [
                    "Luôn ít nhất 30 phút",
                    "Chỉ nói “sau này con sẽ biết”",
                    "Ngắn, thật và phù hợp mức hiểu của trẻ",
                    "Đưa toàn bộ sách y khoa"
                ],
                "correct_index": 2,
                "explanation": "Trả lời vừa đủ tạo chỗ cho câu hỏi tiếp theo."
            },
            {
                "question_text": "Sau khi giải thích, cha mẹ nên làm gì?",
                "options": [
                    "Đóng cuộc trò chuyện ngay",
                    "Bắt con nhắc lại nguyên văn",
                    "Kiểm tra điểm số",
                    "Hỏi xem câu trả lời đã giúp con hiểu chưa"
                ],
                "correct_index": 3,
                "explanation": "Câu hỏi kiểm tra hiểu biết mở đường cho đối thoại."
            },
            {
                "question_text": "Nếu chưa biết trả lời chính xác, lựa chọn nào tốt nhất?",
                "options": [
                    "Hẹn thời điểm tìm hiểu và quay lại",
                    "Đoán đại để giữ uy tín",
                    "Nói câu hỏi vô lễ",
                    "Giả vờ không nghe"
                ],
                "correct_index": 0,
                "explanation": "Thừa nhận chưa biết và quay lại đáng tin hơn đoán."
            },
            {
                "question_text": "Câu nào dễ khiến trẻ ngại hỏi tiếp?",
                "options": [
                    "“Con muốn biết thêm phần nào?”",
                    "“Chuyện đó xấu, không được hỏi”",
                    "“Cảm ơn con đã hỏi”",
                    "“Mình cùng tìm hiểu nhé”"
                ],
                "correct_index": 1,
                "explanation": "Gắn tò mò với xấu hổ có thể đóng cuộc trò chuyện."
            },
            {
                "question_text": "Cha mẹ muốn hiểu câu hỏi mơ hồ của con, nên hỏi gì?",
                "options": [
                    "“Sao con hỏi kỳ vậy?”",
                    "“Con có học thuộc chưa?”",
                    "“Con đang muốn biết điều gì cụ thể?”",
                    "“Con không được hỏi ai khác”"
                ],
                "correct_index": 2,
                "explanation": "Hỏi cụ thể tránh diễn giải quá mức."
            },
            {
                "question_text": "Một cuộc trò chuyện hiệu quả với trẻ nhỏ thường là gì?",
                "options": [
                    "Một bài thuyết trình duy nhất",
                    "Một kỳ thi có điểm",
                    "Một lời cảnh cáo",
                    "Nhiều lượt trao đổi ngắn, có thể quay lại"
                ],
                "correct_index": 3,
                "explanation": "Trao đổi lặp lại phù hợp với câu hỏi đang phát triển."
            },
            {
                "question_text": "Khi trẻ dùng một từ nghe từ bạn, cha mẹ nên ưu tiên gì?",
                "options": [
                    "Tìm hiểu con hiểu từ đó ra sao",
                    "Tự động phạt trẻ",
                    "Giả định trẻ đã biết tất cả",
                    "Yêu cầu trẻ không chơi với bạn nữa"
                ],
                "correct_index": 0,
                "explanation": "Cùng một từ có thể mang ý nghĩa khác nhau trong đầu trẻ."
            },
            {
                "question_text": "Mục tiêu của câu trả lời đầu tiên là gì?",
                "options": [
                    "Nói càng nhiều càng tốt",
                    "Cung cấp thông tin đúng và duy trì sự tin cậy",
                    "Bắt con đồng ý ngay",
                    "Chấm dứt mọi câu hỏi sau này"
                ],
                "correct_index": 1,
                "explanation": "Đúng thông tin và giữ cửa trao đổi đều quan trọng."
            }
        ]
    },
    {
        "order_index": 2,
        "title": "Bài 2 — Gọi đúng tên cơ thể: lời nhỏ, lá chắn lớn",
        "video_url": "https://www.youtube.com/watch?v=EinNeciMgpQ",
        "duration_minutes": 12,
        "content_type": "HYBRID",
        "content_body": """### 1. Ngôn ngữ rõ ràng
Dạy tên đúng của các bộ phận cơ thể, gồm các bộ phận riêng tư, theo độ tuổi; tránh biến chúng thành điều đáng xấu hổ. Cơ thể mỗi trẻ khác nhau, và các quy tắc tôn trọng cơ thể áp dụng cho mọi trẻ.

### 2. Ranh giới cơ thể
Dạy con có thể nói “không” với đụng chạm khiến con khó chịu, kể cả ôm hôn theo phép lịch sự; người lớn cần tôn trọng. Giải thích chăm sóc sức khỏe, vệ sinh có thể cần chạm vào cơ thể nhưng người chăm sóc phải giải thích và bảo đảm an toàn.

### 3. Bí mật và tìm trợ giúp
Phân biệt bất ngờ vui có ngày bật mí với lời dặn giữ kín chuyện khiến con sợ hoặc không an toàn. Con có thể kể với người lớn tin cậy; nếu người đầu tiên không nghe, hãy nói tiếp với người khác. Khi con kể, hãy nghe, tin và tìm hỗ trợ phù hợp.

### 4. Thực hành
Tập cho trẻ các câu phản xạ: *“Con không muốn ôm lúc này”* và *“Có chuyện làm con khó chịu, con cần nói với người lớn con tin”*.

> [!NOTE]
> **Trọng tâm nguồn:** Planned Parenthood, *How To Talk To Preschoolers About Anatomy & Body Safety*  
> **Tài liệu đối chiếu:** [https://www.plannedparenthood.org/learn/parents/preschool/how-do-i-talk-my-preschooler-about-their-body](https://www.plannedparenthood.org/learn/parents/preschool/how-do-i-talk-my-preschooler-about-their-body)
""",
        "quiz_title": "Củng cố bài 2 — Gọi đúng tên cơ thể: lời nhỏ, lá chắn lớn",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Dạy trẻ tên bộ phận cơ thể nên theo cách nào?",
                "options": [
                    "Dùng tên rõ ràng phù hợp tuổi, không gây xấu hổ",
                    "Chỉ dùng biệt danh mơ hồ",
                    "Cấm gọi tên bộ phận riêng tư",
                    "Chỉ dạy khi trẻ đã lớn"
                ],
                "correct_index": 0,
                "explanation": "Tên rõ ràng giúp trẻ mô tả cơ thể và nhu cầu an toàn."
            },
            {
                "question_text": "Con không muốn ôm một người quen; cha mẹ nên làm gì?",
                "options": [
                    "Ép con để lịch sự",
                    "Tôn trọng lựa chọn của con và gợi ý cách chào khác",
                    "Nói con ích kỷ",
                    "Bỏ qua lời con"
                ],
                "correct_index": 1,
                "explanation": "Ranh giới cơ thể vẫn có hiệu lực với người quen."
            },
            {
                "question_text": "Quy tắc an toàn cơ thể áp dụng cho ai?",
                "options": [
                    "Chỉ trẻ có một kiểu cơ thể",
                    "Chỉ trẻ nhỏ hơn sáu tuổi",
                    "Mọi trẻ, bất kể giới hay đặc điểm cơ thể",
                    "Chỉ trẻ đã đến tuổi dậy thì"
                ],
                "correct_index": 2,
                "explanation": "Mọi trẻ đều cần quyền và ngôn ngữ về cơ thể."
            },
            {
                "question_text": "Nếu ai bảo trẻ giữ kín chuyện khiến trẻ sợ, nên dạy trẻ gì?",
                "options": [
                    "Luôn giữ lời hứa bí mật",
                    "Đợi đến khi trưởng thành",
                    "Giải quyết một mình",
                    "Kể với người lớn tin cậy"
                ],
                "correct_index": 3,
                "explanation": "An toàn quan trọng hơn lời dặn giữ kín gây lo sợ."
            },
            {
                "question_text": "Khi con kể về đụng chạm khiến con khó chịu, phản ứng đầu tiên là gì?",
                "options": [
                    "Bình tĩnh lắng nghe và bảo đảm con được hỗ trợ",
                    "Trách con vì đã ở đó",
                    "Hỏi dồn dập theo cách buộc tội",
                    "Hứa tuyệt đối không kể với bất kỳ ai"
                ],
                "correct_index": 0,
                "explanation": "Lắng nghe, bảo vệ và tìm hỗ trợ cần thiết."
            },
            {
                "question_text": "Nếu người lớn đầu tiên không lắng nghe, con cần biết gì?",
                "options": [
                    "Không ai có thể giúp",
                    "Có thể tiếp tục kể với người lớn tin cậy khác",
                    "Con đã làm sai",
                    "Chỉ được giữ kín"
                ],
                "correct_index": 1,
                "explanation": "Trẻ cần nhiều điểm tựa đáng tin."
            },
            {
                "question_text": "Ví dụ nào là một ranh giới cơ thể hợp lệ?",
                "options": [
                    "“Con phải ôm bất kỳ ai người lớn bảo”",
                    "“Con không được nói về cơ thể”",
                    "“Con muốn chào bằng cách vẫy tay”",
                    "“Người quen luôn được chạm vào con”"
                ],
                "correct_index": 2,
                "explanation": "Có thể từ chối ôm và chọn cách chào khác."
            },
            {
                "question_text": "Điểm khác giữa bất ngờ vui và bí mật nguy hiểm là gì?",
                "options": [
                    "Không có khác biệt",
                    "Bất ngờ vui luôn phải giữ mãi",
                    "Bí mật nguy hiểm chỉ do người lạ tạo ra",
                    "Bất ngờ vui được bật mí; chuyện gây sợ cần được kể"
                ],
                "correct_index": 3,
                "explanation": "Không yêu cầu trẻ giữ kín điều khiến trẻ không an toàn."
            },
            {
                "question_text": "Khi chăm sóc sức khỏe cần đụng chạm cơ thể trẻ, người lớn nên làm gì?",
                "options": [
                    "Giải thích mục đích và bảo đảm an toàn, tôn trọng trẻ",
                    "Nói trẻ không có quyền thắc mắc",
                    "Giấu mọi thao tác",
                    "Chê trẻ xấu hổ"
                ],
                "correct_index": 0,
                "explanation": "Giải thích giúp phân biệt chăm sóc cần thiết và xâm phạm."
            },
            {
                "question_text": "Mục đích dạy tên cơ thể và ranh giới là gì?",
                "options": [
                    "Làm trẻ sợ mọi người lớn",
                    "Giúp trẻ diễn đạt và tìm trợ giúp khi cần",
                    "Biến trẻ thành bác sĩ",
                    "Khiến trẻ không bao giờ đặt câu hỏi"
                ],
                "correct_index": 1,
                "explanation": "Ngôn ngữ và ranh giới hỗ trợ giao tiếp an toàn."
            }
        ]
    },
    {
        "order_index": 3,
        "title": "Bài 3 — Em bé từ đâu ra? Trả lời thật, đúng tầm tuổi",
        "video_url": "https://www.youtube.com/watch?v=-1bDV2Kx88I",
        "duration_minutes": 12,
        "content_type": "HYBRID",
        "content_body": """### 1. Bắt đầu từ câu hỏi của con
Hỏi con đã biết gì và đang thắc mắc chuyện thai nhi lớn lên, sinh nở hay sự hình thành thai. Trả lời đúng phần ấy, bằng từ chính xác; có thể bổ sung khi con lớn hơn hoặc hỏi tiếp.

### 2. Một cách nói phù hợp trẻ nhỏ
*“Em bé phát triển trong tử cung. Để bắt đầu một thai kỳ, tinh trùng và trứng kết hợp; đôi khi cần sự hỗ trợ của bác sĩ. Có nhiều cách tạo dựng gia đình.”* Nếu con hỏi thêm về cách tinh trùng gặp trứng, hãy giải thích chính xác theo mức hiểu và câu hỏi của con.

### 3. Không đồng nhất gia đình
Người nuôi dưỡng, người sinh con và cách một gia đình hình thành có thể khác nhau. Tránh nói mọi gia đình đều giống nhau hoặc chỉ có một cách sinh con.

### 4. Thực hành
Khi con hỏi: *“Em bé ở bụng hay ở đâu?”*, có thể đáp: *“Em bé phát triển trong một cơ quan gọi là tử cung. Con muốn biết em bé lớn lên hay ra đời thế nào?”*

> [!NOTE]
> **Trọng tâm nguồn:** AMAZE Parents, *What to say when your kids ask “Where do babies come from?”*  
> **Tài liệu đối chiếu:** [https://www.plannedparenthood.org/learn/parents/elementary-school/how-do-i-talk-my-elementary-school-aged-child-about-pregnancy-and-reproduction](https://www.plannedparenthood.org/learn/parents/elementary-school/how-do-i-talk-my-elementary-school-aged-child-about-pregnancy-and-reproduction)
""",
        "quiz_title": "Củng cố bài 3 — Em bé từ đâu ra? Trả lời thật, đúng tầm tuổi",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Khi trẻ hỏi “Em bé từ đâu ra?”, bước đầu là gì?",
                "options": [
                    "Hỏi trẻ muốn biết phần nào và đã nghe gì",
                    "Nói trẻ chưa đủ tuổi để biết bất cứ điều gì",
                    "Kể một chuyện bịa như sự thật",
                    "Đọc nguyên sách giáo khoa"
                ],
                "correct_index": 0,
                "explanation": "Xác định câu hỏi giúp trả lời vừa mức."
            },
            {
                "question_text": "Em bé phát triển trong cơ quan nào trong thai kỳ?",
                "options": [
                    "Dạ dày",
                    "Tử cung",
                    "Phổi",
                    "Bàng quang"
                ],
                "correct_index": 1,
                "explanation": "Thai phát triển trong tử cung."
            },
            {
                "question_text": "Để một thai kỳ bắt đầu, yếu tố sinh học nào kết hợp?",
                "options": [
                    "Hai trứng",
                    "Hai tinh trùng",
                    "Tinh trùng và trứng",
                    "Máu và sữa"
                ],
                "correct_index": 2,
                "explanation": "Sự kết hợp tinh trùng và trứng là phần sinh học cơ bản."
            },
            {
                "question_text": "Nếu con hỏi thêm chi tiết, cách xử lý phù hợp là gì?",
                "options": [
                    "Lặp lại chuyện bịa",
                    "Cấm hỏi",
                    "Giả vờ không nghe",
                    "Trả lời thật, theo tuổi và đúng thắc mắc"
                ],
                "correct_index": 3,
                "explanation": "Thông tin chính xác có thể mở rộng theo câu hỏi."
            },
            {
                "question_text": "Phát biểu nào tôn trọng sự đa dạng gia đình?",
                "options": [
                    "Gia đình có nhiều cách hình thành và chăm sóc trẻ",
                    "Mọi gia đình hình thành theo cùng một cách",
                    "Gia đình chỉ có một kiểu",
                    "Trẻ không được hỏi về gia đình khác"
                ],
                "correct_index": 0,
                "explanation": "Cách hình thành và chăm sóc gia đình đa dạng."
            },
            {
                "question_text": "Trẻ hỏi “Có phải em bé ở trong dạ dày?”; nên nói gì?",
                "options": [
                    "“Đúng, vì thức ăn nuôi em bé”",
                    "“Em bé phát triển trong tử cung; tử cung khác dạ dày”",
                    "“Không ai biết”",
                    "“Chỉ bác sĩ được nói”"
                ],
                "correct_index": 1,
                "explanation": "Sửa hiểu lầm bằng tên đúng và ngắn gọn."
            },
            {
                "question_text": "Tại sao không nên đưa mọi chi tiết cùng lúc?",
                "options": [
                    "Vì chủ đề luôn nguy hiểm",
                    "Vì trẻ không cần thông tin đúng",
                    "Vì nên đáp đúng điều trẻ đang hỏi và cho phép hỏi tiếp",
                    "Vì cha mẹ không được nói về sinh sản"
                ],
                "correct_index": 2,
                "explanation": "Câu trả lời có thể phát triển qua nhiều cuộc trò chuyện."
            },
            {
                "question_text": "Nhận định nào đúng về hỗ trợ sinh sản?",
                "options": [
                    "Không tồn tại",
                    "Chỉ cần kể cho mọi trẻ toàn bộ thủ thuật",
                    "Làm mọi gia đình giống nhau",
                    "Một số gia đình có sự hỗ trợ của nhân viên y tế để có con"
                ],
                "correct_index": 3,
                "explanation": "Thừa nhận các con đường hình thành gia đình khác nhau."
            },
            {
                "question_text": "Nếu trẻ nhầm người sinh với người nuôi dưỡng, cha mẹ nên làm gì?",
                "options": [
                    "Giải thích nhẹ nhàng rằng vai trò có thể khác nhau",
                    "Khẳng định luôn là một người",
                    "Chỉ kể về một kiểu gia đình",
                    "Chê trẻ hỏi sai"
                ],
                "correct_index": 0,
                "explanation": "Vai trò trong gia đình có thể đa dạng."
            },
            {
                "question_text": "Câu trả lời mẫu nào đúng và không bịa chuyện?",
                "options": [
                    "“Em bé do chim mang đến”",
                    "“Em bé lớn lên trong tử cung”",
                    "“Em bé lớn trong dạ dày”",
                    "“Không bao giờ được hỏi điều đó”"
                ],
                "correct_index": 1,
                "explanation": "Giải thích tử cung là một điểm khởi đầu chính xác."
            }
        ]
    },
    {
        "order_index": 4,
        "title": "Bài 4 — Giá trị gia đình: nói điều mình tin mà vẫn nghe điều con nghĩ",
        "video_url": "https://www.youtube.com/watch?v=kBNYwEtLniE",
        "duration_minutes": 12,
        "content_type": "HYBRID",
        "content_body": """### 1. Giá trị được truyền qua đối thoại
Cha mẹ có thể nói rõ điều gia đình trân trọng, như tôn trọng, trung thực, trách nhiệm, chăm sóc và sự đồng thuận. Phân biệt điều cha mẹ tin với thông tin có thể kiểm chứng; không đổi sự thật sinh học để phù hợp một quan điểm.

### 2. Nói bằng tình huống
Hỏi: *“Nếu bạn không muốn ôm thì con sẽ làm gì?”* rồi cùng phân tích cách tôn trọng lựa chọn của bạn. Kể vì sao gia đình coi trọng sự tử tế và an toàn bằng ví dụ gần gũi.

### 3. Lắng nghe khi con khác ý
Mời con nói suy nghĩ, đặt câu hỏi không phán xét và nhắc rằng con luôn có thể quay lại. Tôn trọng sự khác biệt giữa các gia đình; không gán đặc điểm đạo đức cho giới hoặc cấu trúc gia đình.

### 4. Thực hành
Thử câu: *“Gia đình mình coi trọng việc hỏi ý trước khi chạm vào người khác. Con nghĩ điều đó có ích khi nào?”*

> [!NOTE]
> **Trọng tâm nguồn:** AMAZE Parents, *How can I teach my kids my values?*  
> **Tài liệu đối chiếu:** [https://amaze.org/video/amazejr-how-can-i-teach-my-values/](https://amaze.org/video/amazejr-how-can-i-teach-my-values/)
""",
        "quiz_title": "Củng cố bài 4 — Giá trị gia đình: nói điều mình tin mà vẫn nghe điều con nghĩ",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Cách chia sẻ giá trị gia đình phù hợp là gì?",
                "options": [
                    "Nói rõ giá trị và mời con trao đổi",
                    "Buộc con đọc thuộc lòng không được hỏi",
                    "Dùng xấu hổ để ép con nghe",
                    "Thay thông tin khoa học bằng niềm tin"
                ],
                "correct_index": 0,
                "explanation": "Đối thoại giúp trẻ hiểu lý do của giá trị."
            },
            {
                "question_text": "Nhận định nào cần phân biệt rõ?",
                "options": [
                    "Sự tử tế và sự tôn trọng",
                    "Niềm tin gia đình và sự thật có thể kiểm chứng",
                    "Câu hỏi và câu trả lời",
                    "Người lớn và trẻ nhỏ"
                ],
                "correct_index": 1,
                "explanation": "Giá trị không nên làm sai thông tin thực tế."
            },
            {
                "question_text": "Ví dụ nào thể hiện tôn trọng ranh giới?",
                "options": [
                    "Bắt bạn ôm để chứng minh tình bạn",
                    "Cười khi bạn nói không",
                    "Hỏi ý và chấp nhận nếu bạn không muốn ôm",
                    "Giữ tay bạn cho tới khi bạn đồng ý"
                ],
                "correct_index": 2,
                "explanation": "Tôn trọng bao gồm việc chấp nhận lời từ chối."
            },
            {
                "question_text": "Khi con có ý kiến khác, cha mẹ nên làm gì?",
                "options": [
                    "Ngắt lời ngay",
                    "Quy mọi khác biệt thành hư hỏng",
                    "Bỏ chủ đề mãi mãi",
                    "Lắng nghe và hỏi lý do con nghĩ vậy"
                ],
                "correct_index": 3,
                "explanation": "Lắng nghe giữ trao đổi cởi mở."
            },
            {
                "question_text": "Giá trị nào có thể minh họa bằng cách xin phép trước khi chạm?",
                "options": [
                    "Tôn trọng quyền tự quyết với cơ thể",
                    "Phải phục tùng mọi người lớn",
                    "Không bao giờ trò chuyện",
                    "Phải đồng ý để được yêu quý"
                ],
                "correct_index": 0,
                "explanation": "Xin phép thể hiện tôn trọng cơ thể người khác."
            },
            {
                "question_text": "Điều nào nên tránh khi nói về gia đình khác?",
                "options": [
                    "Thừa nhận có nhiều kiểu gia đình",
                    "Gán rằng chỉ một kiểu gia đình mới tốt",
                    "Dạy con ứng xử tử tế",
                    "Hỏi con muốn hiểu thêm không"
                ],
                "correct_index": 1,
                "explanation": "Không suy diễn đạo đức từ cấu trúc gia đình."
            },
            {
                "question_text": "Một câu hỏi mở tốt trong chủ đề giá trị là gì?",
                "options": [
                    "“Con sẽ đồng ý với bố mẹ chứ?”",
                    "“Con có thuộc bài không?”",
                    "“Con nghĩ điều này giúp ai, và giúp thế nào?”",
                    "“Con có chịu im lặng không?”"
                ],
                "correct_index": 2,
                "explanation": "Câu hỏi mở mời con suy nghĩ."
            },
            {
                "question_text": "Khi giải thích điều gia đình coi trọng, cách nào dễ hiểu với trẻ?",
                "options": [
                    "Chỉ dùng khẩu hiệu trừu tượng",
                    "Chỉ đọc quy định",
                    "Không đưa ví dụ",
                    "Dùng tình huống gần gũi để cùng phân tích"
                ],
                "correct_index": 3,
                "explanation": "Ví dụ cụ thể cho thấy cách áp dụng giá trị."
            },
            {
                "question_text": "Nếu con hỏi thông tin sinh học trái với điều cha mẹ từng nghe, nên làm gì?",
                "options": [
                    "Kiểm tra nguồn đáng tin và sửa thông tin sai",
                    "Cấm con tìm hiểu",
                    "Giữ thông tin sai để tránh khó xử",
                    "Đổi chủ đề"
                ],
                "correct_index": 0,
                "explanation": "Sự thật có thể kiểm chứng cần được trình bày đúng."
            },
            {
                "question_text": "Mục tiêu lâu dài của đối thoại về giá trị là gì?",
                "options": [
                    "Không cho con nghĩ khác",
                    "Giúp con hiểu, suy nghĩ và có thể tiếp tục trò chuyện",
                    "Đảm bảo con không đặt câu hỏi",
                    "Chỉ để kiểm tra vâng lời"
                ],
                "correct_index": 1,
                "explanation": "Trao đổi hỗ trợ hiểu biết và sự tin cậy."
            }
        ]
    },
    {
        "order_index": 5,
        "title": "Bài 5 — Tiền dậy thì: mở cửa đối thoại trước ngày cơ thể đổi thay",
        "video_url": "https://www.youtube.com/watch?v=SBlvWOV-8dE",
        "duration_minutes": 12,
        "content_type": "HYBRID",
        "content_body": """### 1. Đừng đợi đến một “buổi nói chuyện lớn”
Với trẻ tiền dậy thì, những lần trò chuyện ngắn về thay đổi cơ thể, tình bạn, quyền riêng tư, đồng thuận và thông tin trên mạng thường dễ tiếp nhận hơn một buổi thuyết giảng. Hỏi con đã biết gì và con muốn hiểu điều gì.

### 2. Thông tin phù hợp mọi giới
Giải thích dậy thì diễn ra ở các thời điểm khác nhau; người học nên hiểu cả kinh nguyệt, xuất tinh trong khi ngủ và những thay đổi khác, bất kể cơ thể của mình. Không trêu chọc hoặc đoán bản dạng của con từ cơ thể.

### 3. Tạo đường quay lại
Hỏi: *“Điều con thấy trên mạng có làm con bối rối không?”*; thừa nhận cha mẹ có thể cần kiểm tra nguồn. Chỉ con cách chọn người lớn tin cậy và nguồn y tế phù hợp khi câu hỏi liên quan sức khỏe.

### 4. Thực hành
Trong lúc đi bộ hoặc sinh hoạt, thử nói: *“Sắp tới nhiều người có thay đổi cơ thể. Nếu con đọc điều gì lạ trên mạng, mình cùng kiểm tra nhé.”*

> [!NOTE]
> **Trọng tâm nguồn:** Planned Parenthood, *How do I talk with my preteen about sex?*  
> **Tài liệu đối chiếu:** [https://www.plannedparenthood.org/learn/parents/tips-talking](https://www.plannedparenthood.org/learn/parents/tips-talking)
""",
        "quiz_title": "Củng cố bài 5 — Tiền dậy thì: mở cửa đối thoại trước ngày cơ thể đổi thay",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Với trẻ tiền dậy thì, cách bắt đầu phù hợp là gì?",
                "options": [
                    "Các cuộc trò chuyện ngắn, lặp lại và có chỗ cho con hỏi",
                    "Một buổi giảng bắt buộc nhiều giờ",
                    "Chờ con tự tìm câu trả lời trên mạng",
                    "Chỉ nói khi trẻ có quan hệ tình cảm"
                ],
                "correct_index": 0,
                "explanation": "Trao đổi thường xuyên giúp giải đáp theo từng giai đoạn."
            },
            {
                "question_text": "Trước khi giải thích một chủ đề, cha mẹ nên tìm hiểu gì?",
                "options": [
                    "Điểm số môn toán",
                    "Con đã biết gì và đang muốn hỏi phần nào",
                    "Ý kiến mọi người trên mạng",
                    "Con có thuộc sách không"
                ],
                "correct_index": 1,
                "explanation": "Điểm xuất phát của con quyết định cách nói phù hợp."
            },
            {
                "question_text": "Dậy thì thường diễn ra theo cách nào?",
                "options": [
                    "Mọi người cùng một ngày",
                    "Chỉ một giới trải qua",
                    "Thời điểm và trải nghiệm khác nhau giữa từng người",
                    "Chỉ bắt đầu sau tuổi trưởng thành"
                ],
                "correct_index": 2,
                "explanation": "Dậy thì có sự khác biệt cá nhân."
            },
            {
                "question_text": "Ai có thể học về kinh nguyệt và xuất tinh trong khi ngủ?",
                "options": [
                    "Chỉ người có kinh nguyệt",
                    "Chỉ người có xuất tinh trong khi ngủ",
                    "Không ai trước tuổi 18",
                    "Mọi học sinh, để hiểu cơ thể và tôn trọng người khác"
                ],
                "correct_index": 3,
                "explanation": "Kiến thức dậy thì không nên bị giới hạn theo giới."
            },
            {
                "question_text": "Nếu con hỏi về thông tin khó hiểu trên mạng, nên làm gì?",
                "options": [
                    "Cùng xem xét nguồn đáng tin và giải thích",
                    "Giả định mọi nội dung trên mạng đều đúng",
                    "Phạt ngay vì con hỏi",
                    "Bỏ qua vì cha mẹ không rành mạng"
                ],
                "correct_index": 0,
                "explanation": "Cùng kiểm tra thông tin tạo thói quen tìm nguồn."
            },
            {
                "question_text": "Câu nào mời con trao đổi thay vì thẩm vấn?",
                "options": [
                    "“Ai cho phép con xem?”",
                    "“Có điều gì con nghe mà muốn cùng kiểm tra không?”",
                    "“Con phải trả lời ngay mọi câu hỏi của bố mẹ”",
                    "“Con không được có quan điểm riêng”"
                ],
                "correct_index": 1,
                "explanation": "Lời mời mở ít gây phòng thủ hơn."
            },
            {
                "question_text": "Nếu cha mẹ chưa chắc một thông tin sức khỏe, nên làm gì?",
                "options": [
                    "Khẳng định điều chưa kiểm chứng",
                    "Hỏi bất kỳ tài khoản ẩn danh",
                    "Kiểm tra nguồn y tế phù hợp hoặc hỏi chuyên gia",
                    "Chê con hỏi khó"
                ],
                "correct_index": 2,
                "explanation": "Câu hỏi sức khỏe cần nguồn đáng tin."
            },
            {
                "question_text": "Quyền riêng tư của trẻ tiền dậy thì nên được hiểu thế nào?",
                "options": [
                    "Không tồn tại",
                    "Cho phép giấu mọi nguy cơ",
                    "Phụ thuộc giới",
                    "Cần được tôn trọng đồng thời có kênh báo điều không an toàn"
                ],
                "correct_index": 3,
                "explanation": "Tôn trọng riêng tư và giữ đường hỗ trợ an toàn."
            },
            {
                "question_text": "Khi con phát triển khác bạn cùng tuổi, cha mẹ nên nói gì?",
                "options": [
                    "Tốc độ thay đổi khác nhau; nếu lo sức khỏe có thể hỏi nhân viên y tế",
                    "Con chắc chắn có bệnh",
                    "Con phải giống bạn",
                    "Đừng nhắc tới cảm giác của con"
                ],
                "correct_index": 0,
                "explanation": "Khác nhau về thời điểm thường gặp; lo lắng cụ thể nên hỏi chuyên môn."
            },
            {
                "question_text": "Điều gì giúp con quay lại hỏi ở lần sau?",
                "options": [
                    "Dọa cấm mạng khi con hỏi",
                    "Trả lời bình tĩnh, không trêu chọc và mời hỏi tiếp",
                    "Chế giễu câu hỏi",
                    "Phát tán câu hỏi của con cho người khác"
                ],
                "correct_index": 1,
                "explanation": "Thái độ tôn trọng xây dựng tin cậy."
            }
        ]
    },
    {
        "order_index": 6,
        "title": "Bài 6 — Con không hỏi: cha mẹ có nên im lặng?",
        "video_url": None,
        "duration_minutes": 15,
        "content_type": "TEXT",
        "content_body": """### 1. Không hỏi không đồng nghĩa không tò mò
Trẻ có thể ngại, chưa biết cách đặt câu hỏi hoặc đã nghe từ nguồn khác. Cha mẹ có thể chủ động mở chuyện bằng tình huống đời thường mà không ép con tiết lộ điều riêng tư.

### 2. Những lời mở nhẹ nhàng
- *“Mình vừa thấy một cảnh phim nói về sự tôn trọng cơ thể; con nghĩ sao?”*
- *“Nếu một ngày con muốn hỏi về thay đổi cơ thể, con có thể hỏi bố/mẹ bất cứ lúc nào.”*
Hỏi một câu rồi kiên nhẫn chờ, chấp nhận nếu con chưa muốn nói ngay lúc đó.

### 3. Nhịp trao đổi
Quay lại vào lúc khác; cho con biết có thể hỏi trực tiếp, viết ra giấy hoặc tìm người lớn tin cậy khác. Nếu có dấu hiệu trẻ không an toàn, cần lắng nghe và tìm hỗ trợ phù hợp thay vì chỉ chờ con tự mở lời.

### 4. Lời khuyên chủ động kết nối từ chuyên gia
- **Chủ động mở lời từ những tình huống đời thường:** Đừng chờ đến khi con có băn khoăn lớn mới bắt đầu. Cha mẹ có thể lồng ghép các câu hỏi tự nhiên khi cùng xem một bộ phim hoạt hình hoặc đọc truyện tranh thiếu nhi.
- **Tôn trọng sự im lặng của con:** Nếu con ngập ngừng hoặc chưa muốn nói, việc kiên nhẫn và khẳng định: *"Bố/mẹ luôn sẵn sàng lắng nghe bất cứ khi nào con muốn"* sẽ tạo cho con sự an tâm rất lớn.
- **Xây dựng mạng lưới người lớn tin cậy:** Giới thiệu thêm những người lớn đáng tin cậy khác (thầy cô giáo, bác sĩ gia đình) để con luôn biết nơi tìm kiếm sự hỗ trợ an toàn khi cần.

> [!TIP]
> **Nguồn tài liệu tham khảo chuyên môn:**
> - [AMAZE Jr Parents — Làm gì khi con không chủ động hỏi?](https://amaze.org/video/amazejr-what-if-my-kids-dont-ask/)
> - [Planned Parenthood — Nghệ thuật trò chuyện về cơ thể cùng trẻ nhỏ](https://www.plannedparenthood.org/learn/parents/tips-talking)
""",
        "quiz_title": "Củng cố bài 6 — Con không hỏi: cha mẹ có nên im lặng?",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Trẻ không chủ động hỏi có nghĩa là gì?",
                "options": [
                    "Không thể suy ra trẻ không cần thông tin",
                    "Trẻ đã biết tất cả",
                    "Trẻ chắc chắn không có thắc mắc",
                    "Cha mẹ phải ngừng đề cập chủ đề"
                ],
                "correct_index": 0,
                "explanation": "Im lặng có nhiều nguyên nhân."
            },
            {
                "question_text": "Cách chủ động mở chuyện nào ít gây áp lực?",
                "options": [
                    "Bắt trẻ kể mọi điều riêng tư",
                    "Dùng một tình huống đời thường để mời con chia sẻ",
                    "Hỏi liên tục cho tới khi trẻ trả lời",
                    "Thông báo trẻ bị kiểm tra"
                ],
                "correct_index": 1,
                "explanation": "Tình huống cụ thể tạo cơ hội trao đổi."
            },
            {
                "question_text": "Nếu con chưa muốn nói lúc đó, cha mẹ nên làm gì?",
                "options": [
                    "Kết luận con có vấn đề",
                    "Buộc con tiếp tục",
                    "Tôn trọng và nhắc con có thể quay lại sau",
                    "Tỏ ra giận dỗi"
                ],
                "correct_index": 2,
                "explanation": "Tôn trọng nhịp của con duy trì tin cậy."
            },
            {
                "question_text": "Ngoài hỏi trực tiếp, trẻ có thể chọn cách nào?",
                "options": [
                    "Không được hỏi ai khác",
                    "Chỉ hỏi người lạ trên mạng",
                    "Phải giữ kín mọi thứ",
                    "Viết câu hỏi hoặc hỏi người lớn tin cậy"
                ],
                "correct_index": 3,
                "explanation": "Nhiều kênh giúp trẻ tiếp cận hỗ trợ."
            },
            {
                "question_text": "Một lời mở phù hợp là gì?",
                "options": [
                    "“Nếu muốn hỏi về cơ thể, con có thể hỏi bố/mẹ bất cứ lúc nào”",
                    "“Con im lặng nghĩa là con đã hiểu hết”",
                    "“Phải kể ngay bí mật của con”",
                    "“Không được hỏi về cơ thể”"
                ],
                "correct_index": 0,
                "explanation": "Lời mời rõ và không ép trẻ nói ngay."
            },
            {
                "question_text": "Vì sao cha mẹ nên mở chuyện nhiều lần?",
                "options": [
                    "Để kiểm soát mọi suy nghĩ của con",
                    "Nhu cầu và câu hỏi của trẻ thay đổi theo thời gian",
                    "Để hỏi hết trong một ngày",
                    "Để chứng minh con im lặng là sai"
                ],
                "correct_index": 1,
                "explanation": "Đối thoại là quá trình, không phải sự kiện một lần."
            },
            {
                "question_text": "Khi dùng cảnh phim làm điểm mở, nên hỏi gì?",
                "options": [
                    "“Con có làm giống nhân vật không, khai thật đi?”",
                    "“Con không được xem nữa”",
                    "“Con nghĩ nhân vật đã tôn trọng ranh giới người kia chưa?”",
                    "“Con phải đồng ý với bố/mẹ”"
                ],
                "correct_index": 2,
                "explanation": "Hỏi về tình huống giảm áp lực tự tiết lộ."
            },
            {
                "question_text": "Nếu có dấu hiệu con không an toàn, cha mẹ nên làm gì?",
                "options": [
                    "Chờ con tự nói mọi chi tiết rồi mới quan tâm",
                    "Bỏ qua vì con không hỏi",
                    "Chỉ tăng số bài quiz",
                    "Lắng nghe và tìm người hỗ trợ phù hợp"
                ],
                "correct_index": 3,
                "explanation": "An toàn cần được ưu tiên khi có dấu hiệu đáng lo."
            },
            {
                "question_text": "Quiz bài NotebookLM nên được xử lý thế nào trước xuất bản?",
                "options": [
                    "Đối chiếu từng câu với video đã tạo và sửa chỗ lệch",
                    "Xuất bản nguyên trạng dù video khác nội dung",
                    "Bỏ luôn phần kiểm tra nguồn",
                    "Thay mọi đáp án thành A"
                ],
                "correct_index": 0,
                "explanation": "Video sau tạo phải khớp nội dung và câu hỏi."
            },
            {
                "question_text": "Thông điệp chính của bài là gì?",
                "options": [
                    "Ép con phải hỏi ngay",
                    "Cha mẹ có thể mở lời nhẹ nhàng và giữ kênh trò chuyện",
                    "Im lặng luôn chứng minh trẻ an toàn",
                    "Chỉ nói chuyện khi trẻ chủ động"
                ],
                "correct_index": 1,
                "explanation": "Cha mẹ có thể tạo cơ hội trao đổi mà tôn trọng nhịp trẻ."
            }
        ]
    }
]

async def seed_course_4():
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
        print(f"Created Course 4: {course.title} (ID: {course_id})")

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
        print("SEEDING COURSE 4 COMPLETED SUCCESSFULLY!")
        print(f"Course: {COURSE_DATA['title']}")
        print(f"Target Audience: {COURSE_DATA['target_audience']}")
        print(f"Lessons: {len(LESSONS_DATA)}")
        print(f"Quizzes: {len(LESSONS_DATA)}")
        print(f"Total Questions: {total_questions}")
        print(f"Total Options: {total_options}")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(seed_course_4())
