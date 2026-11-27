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

# Ensure console handles UTF-8 correctly on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

COURSE_DATA = {
    "title": "Giáo Dục Giới Tính & Sức Khỏe Sinh Sản — Lộ Trình Học Sinh",
    "slug": "giao-duc-gioi-tinh-va-suc-khoe-sinh-san-lo-trinh-hoc-sinh",
    "short_description": "Khóa học giáo dục giới tính, dậy thì, sức khỏe sinh sản và an toàn cá nhân dành cho mọi học sinh, xây dựng sự hiểu biết và tôn trọng cơ thể.",
    "description": (
        "**Đối tượng:** học sinh đã đến độ tuổi học về dậy thì, sức khỏe sinh sản và an toàn cá nhân, không chia lớp theo giới. "
        "Mọi học sinh học kiến thức về mọi loại cơ thể để hiểu và tôn trọng bản thân, bạn bè. Đây là nội dung giáo dục, không thay thế tư vấn y tế cá nhân. "
        "Khi gặp vấn đề sức khỏe hoặc bị đe dọa, hãy tìm người lớn đáng tin cậy và nhân viên y tế/cơ quan hỗ trợ.\n\n"
        "**Cấu trúc khóa học:** Gồm 6 bài học trọng tâm kết hợp video khoa học, kiến thức kiểm chứng và bài kiểm tra trắc nghiệm 10 câu để đánh giá mức độ tiếp thu (đạt 8/10 trở lên)."
    ),
    "learning_objectives": (
        "- Hiểu đúng về hiện tượng dậy thì, các cơ chế tự nhiên của cơ thể và bác bỏ các định kiến sai lệch.\n"
        "- Nắm rõ các biện pháp an toàn sinh sản, phòng tránh thai khẩn cấp và các bệnh lây truyền qua đường tình dục (STI/HPV).\n"
        "- Thực hành nguyên tắc đồng thuận (Consent) trong giao tiếp và các mối quan hệ thân mật.\n"
        "- Nhận diện hành vi tống tiền bằng hình ảnh riêng tư (Sextortion) và biết cách tìm kiếm sự hỗ trợ an toàn."
    ),
    "thumbnail_url": "https://images.unsplash.com/photo-1577896851231-70ef18881754?auto=format&fit=crop&w=1200&q=80",
    "target_audience": "CHILD",
    "is_published": True,
}

LESSONS_DATA = [
    {
        "order_index": 1,
        "title": "Bài 1 — Hiểu đúng về thủ dâm và những lời đồn",
        "video_url": "https://www.youtube.com/watch?v=GU3JqoUDkjA",
        "duration_minutes": 10,
        "content_type": "HYBRID",
        "content_body": """### Thông tin bài học & Video tham khảo
- **Nguồn & Tác giả:** AsapSCIENCE, *Is Masturbation Good For You?*
- **Kênh:** YouTube — AsapSCIENCE

### Mục tiêu bài học
Nhận diện một hành vi tự khám phá cơ thể, bác bỏ lời đồn và biết khi nào cần hỏi chuyên gia.

### Nội dung xoay quanh video
Thủ dâm là việc một người tự chạm cơ thể để cảm nhận khoái cảm. Có người thực hiện, có người không; cả hai đều không phải lý do để chế giễu. Những lời đồn như “mù mắt” hay “cạn tinh trùng” không phải kiến thức y khoa. Điều cần chú ý là sự riêng tư, cảm giác đau/tổn thương và ảnh hưởng tới sinh hoạt; nếu lo lắng, hãy hỏi nhân viên y tế. Không đo sức khỏe bằng một “số lần chuẩn” cho tất cả.

> [!NOTE]
> **Bổ sung có kiểm chứng:** Không cần mặc định bất cứ ai đều phải thủ dâm; cũng không chẩn đoán “nghiện” chỉ bằng tần suất.
> Nguồn tham khảo: [Planned Parenthood — masturbation](https://www.plannedparenthood.org/learn/sex-and-relationships/masturbation).
""",
        "quiz_title": "Quiz 1: Hiểu đúng về thủ dâm và những lời đồn",
        "quiz_description": "Bài kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Chủ đề chính của video là gì?",
                "options": ["Vắc xin", "Thủ dâm và sức khỏe", "Tránh thai khẩn cấp", "Dinh dưỡng"],
                "correct_index": 1,  # B
                "explanation": "Video tìm hiểu thủ dâm dưới góc nhìn sức khỏe."
            },
            {
                "question_text": "Nhận định nào phù hợp?",
                "options": ["Ai cũng phải làm", "Chỉ một giới mới có thể làm", "Mỗi người có lựa chọn và cảm nhận khác nhau", "Ai không làm đều bị bệnh"],
                "correct_index": 2,  # C
                "explanation": "Không có nghĩa vụ phải thực hiện."
            },
            {
                "question_text": "“Thủ dâm gây mù mắt” là gì?",
                "options": ["Kết luận y khoa", "Lời đồn không có căn cứ", "Quy định nhà trường", "Triệu chứng cấp cứu"],
                "correct_index": 1,  # B
                "explanation": "Không có bằng chứng cho lời đồn này."
            },
            {
                "question_text": "Một người không thủ dâm thì nên được đối xử ra sao?",
                "options": ["Chế giễu", "Bắt buộc thay đổi", "Tôn trọng", "Coi là bất thường"],
                "correct_index": 2,  # C
                "explanation": "Đây là lựa chọn riêng."
            },
            {
                "question_text": "Trường hợp nào nên tìm tư vấn?",
                "options": ["Chỉ vì nghe bạn kể", "Khi đau hoặc có tổn thương", "Vì mỗi người khác nhau", "Vì đã xem video"],
                "correct_index": 1,  # B
                "explanation": "Đau/tổn thương cần được đánh giá."
            },
            {
                "question_text": "Có một tần suất chung phù hợp cho mọi người không?",
                "options": ["Có, mỗi ngày", "Có, mỗi tuần một lần", "Có, theo giới", "Không"],
                "correct_index": 3,  # D
                "explanation": "Tình trạng và nhu cầu mỗi người khác nhau."
            },
            {
                "question_text": "Cách ứng xử phù hợp khi bạn cùng lớp hỏi chuyện riêng tư?",
                "options": ["Phát tán chuyện", "Tôn trọng quyền riêng tư", "Chụp màn hình chia sẻ", "Trêu chọc"],
                "correct_index": 1,  # B
                "explanation": "Chủ đề cơ thể cần được tôn trọng."
            },
            {
                "question_text": "Nếu một lời đồn khiến bạn lo về sức khỏe, nên làm gì?",
                "options": ["Tự kết luận mình bệnh", "Tin lời đồn", "Hỏi nguồn y tế đáng tin", "Chế giễu người hỏi"],
                "correct_index": 2,  # C
                "explanation": "Kiểm tra với nguồn chuyên môn."
            },
            {
                "question_text": "Lý do nào đáng để trao đổi với người hỗ trợ?",
                "options": ["Sở thích cá nhân khác bạn", "Hành vi làm gián đoạn học tập và gây khổ sở", "Không thấy mình giống quảng cáo", "Bạn bè bàn tán"],
                "correct_index": 1,  # B
                "explanation": "Tác động tới đời sống cần được hỗ trợ."
            },
            {
                "question_text": "Kết luận chính của bài là gì?",
                "options": ["Sợ hãi cơ thể", "Đánh giá bạn bè", "Hiểu cơ thể bằng thông tin đáng tin và tôn trọng lựa chọn", "Áp một quy tắc cho tất cả"],
                "correct_index": 2,  # C
                "explanation": "Kiến thức đi cùng sự tôn trọng."
            }
        ]
    },
    {
        "order_index": 2,
        "title": "Bài 2 — Tránh thai khẩn cấp: dùng khi nào và giới hạn nào?",
        "video_url": "https://www.youtube.com/watch?v=Z1LTban3Z84",
        "duration_minutes": 10,
        "content_type": "HYBRID",
        "content_body": """### Thông tin bài học & Video chính thức
- **Nguồn:** AMAZE Org, *What Is Emergency Contraception? (The Morning After Pill)*
- **Trang video chính thức:** [AMAZE Org — Emergency Contraception](https://amaze.org/video/personal-safety-emergency-contraception-morning-after-pill/)

### Mục tiêu bài học
Học sinh thuộc mọi giới cùng hiểu cách ngừa thai sau sự cố, giới hạn phòng STI và cách tìm trợ giúp.

### Nội dung xoay quanh video
Tránh thai khẩn cấp giúp **ngăn ngừa mang thai sau khi quan hệ không dùng biện pháp hoặc biện pháp thất bại**; nên tiếp cận sớm. Thuốc không chấm dứt thai kỳ đã hình thành và không phòng các bệnh lây qua đường tình dục (STI). Video cũng đề cập khi nào dùng và nơi có thể tìm thuốc; người có liên quan cùng có trách nhiệm hỗ trợ, không đổ lỗi cho riêng một người.

> [!NOTE]
> **Bổ sung có kiểm chứng, không phải câu hỏi về lời thoại video:** WHO nêu các lựa chọn thuốc hoặc vòng đồng và khuyến cáo tiếp cận càng sớm càng tốt trong phạm vi phù hợp từng phương pháp. Dùng lặp lại có thể gây rối loạn kinh nhưng **không có bằng chứng thuốc phá hủy buồng trứng hay gây vô sinh về sau**. Tư vấn dược sĩ/bác sĩ về loại thuốc, thời điểm và tương tác thuốc.
> Nguồn tham khảo: [WHO — Emergency Contraception](https://www.who.int/news-room/fact-sheets/detail/emergency-contraception).
""",
        "quiz_title": "Quiz 2: Tránh thai khẩn cấp: dùng khi nào và giới hạn nào?",
        "quiz_description": "Bài kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Mục đích của tránh thai khẩn cấp?",
                "options": ["Chữa STI", "Giúp ngừa thai sau sự cố", "Chữa đau bụng", "Tiêm vắc xin"],
                "correct_index": 1,  # B
                "explanation": "Sử dụng sau nguy cơ mang thai."
            },
            {
                "question_text": "Tình huống nào được video nêu là ví dụ cần tìm hiểu phương án khẩn cấp?",
                "options": ["Bao cao su bị rách", "Đau đầu", "Cảm lạnh", "Dị ứng phấn hoa"],
                "correct_index": 0,  # A
                "explanation": "Biện pháp tránh thai thất bại."
            },
            {
                "question_text": "Có cần đợi đúng “sáng hôm sau” mới được tìm hỗ trợ không?",
                "options": ["Có", "Chỉ sau một tuần", "Không, nên sớm", "Chỉ khi đau"],
                "correct_index": 2,  # C
                "explanation": "Tên gọi không có nghĩa phải đợi."
            },
            {
                "question_text": "Thuốc tránh thai khẩn cấp có phòng STI không?",
                "options": ["Có, tất cả", "Chỉ HIV", "Chỉ HPV", "Không"],
                "correct_index": 3,  # D
                "explanation": "Cần biện pháp phòng STI thích hợp."
            },
            {
                "question_text": "Thuốc có làm chấm dứt thai kỳ đã hình thành không?",
                "options": ["Có", "Không", "Luôn gây sảy thai", "Chỉ khi uống với nước"],
                "correct_index": 1,  # B
                "explanation": "Đây không phải thuốc phá thai."
            },
            {
                "question_text": "Khi lo có nguy cơ mang thai sau sự cố, bước hợp lý là?",
                "options": ["Chờ nhiều tuần", "Tìm thông tin/tư vấn y tế sớm", "Tự dùng thuốc bất kỳ", "Giữ kín dù cần hỗ trợ"],
                "correct_index": 1,  # B
                "explanation": "Thời gian ảnh hưởng lựa chọn."
            },
            {
                "question_text": "Ai cần học kiến thức này?",
                "options": ["Chỉ nữ", "Chỉ nam", "Mọi học sinh", "Chỉ nhân viên y tế"],
                "correct_index": 2,  # C
                "explanation": "Trách nhiệm an toàn là chung."
            },
            {
                "question_text": "Nếu muốn vừa giảm nguy cơ mang thai vừa giảm nguy cơ STI, điều nào cần nhớ?",
                "options": ["Thuốc khẩn cấp đủ cho cả hai", "Bao cao su giúp giảm nguy cơ STI", "Không cần tìm hiểu thêm", "Chỉ thuốc kháng sinh"],
                "correct_index": 1,  # B
                "explanation": "Thuốc khẩn cấp không phòng STI."
            },
            {
                "question_text": "Video AMAZE đặt trọng tâm vào điều gì?",
                "options": ["Định nghĩa, thời điểm, nơi tiếp cận biện pháp", "Phẫu thuật", "Chăm sóc răng", "Kiểm tra thị lực"],
                "correct_index": 0,  # A
                "explanation": "Đây là phạm vi được nhà sản xuất giới thiệu."
            },
            {
                "question_text": "Thái độ phù hợp với người gặp sự cố?",
                "options": ["Đổ lỗi", "Phát tán chuyện", "Hỗ trợ tìm nguồn tư vấn kín đáo", "Bỏ mặc"],
                "correct_index": 2,  # C
                "explanation": "Hỗ trợ giúp quyết định kịp thời."
            }
        ]
    },
    {
        "order_index": 3,
        "title": "Bài 3 — Đồng thuận: “Im lặng” không phải lời đồng ý",
        "video_url": "https://www.youtube.com/watch?v=oQbei5JGiT8",
        "duration_minutes": 10,
        "content_type": "HYBRID",
        "content_body": """### Thông tin bài học & Video chính thức
- **Nguồn & Tác giả:** Blue Seat Studios / Emmeline May, *Tea Consent*
- **Kênh:** YouTube — Blue Seat Studios

### Mục tiêu bài học
Dùng phép so sánh “mời trà” để hiểu người khác có quyền đồng ý, từ chối hoặc đổi ý.

### Nội dung xoay quanh video
Nếu một người không muốn uống trà, đừng ép họ; họ từng muốn uống không có nghĩa họ muốn lúc này; nếu họ không tỉnh táo hoặc không phản hồi thì không thể suy ra họ đồng ý. Phép so sánh áp dụng cho tiếp xúc thân mật: hỏi rõ, lắng nghe và dừng khi người kia đổi ý. Người học thuộc mọi giới cần biết tôn trọng ranh giới của người khác và ranh giới của mình.

> [!NOTE]
> **Bổ sung có kiểm chứng:** F.R.I.E.S (Freely given - Tự nguyện, Reversible - Có thể rút lại, Informed - Có đủ thông tin, Enthusiastic - Chủ động/Nhiệt tình, Specific - Cụ thể) là khung của **Planned Parenthood**, **không phải tên/mô hình do video Tea Consent giảng giải**.
> Nguồn tham khảo: [Planned Parenthood — Sexual Consent](https://www.plannedparenthood.org/learn/relationships/sexual-consent).
""",
        "quiz_title": "Quiz 3: Đồng thuận: “Im lặng” không phải lời đồng ý",
        "quiz_description": "Bài kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video dùng ví dụ gì để giải thích đồng thuận?",
                "options": ["Mời trà", "Chơi cờ", "Đi xe đạp", "Nấu cơm"],
                "correct_index": 0,  # A
                "explanation": "“Tea Consent”."
            },
            {
                "question_text": "Người khác nói không muốn uống trà: nên làm gì?",
                "options": ["Ép uống", "Tôn trọng lời từ chối", "Hỏi liên tục đến khi đổi ý", "Tự rót vào miệng"],
                "correct_index": 1,  # B
                "explanation": "“Không” cần được tôn trọng."
            },
            {
                "question_text": "Đã đồng ý hôm qua có đồng nghĩa hôm nay đồng ý?",
                "options": ["Luôn luôn", "Chỉ với bạn thân", "Không", "Chỉ cuối tuần"],
                "correct_index": 2,  # C
                "explanation": "Đồng thuận xét tại thời điểm hiện tại."
            },
            {
                "question_text": "Một người đổi ý sau khi đồng ý, bạn nên?",
                "options": ["Tiếp tục", "Dừng và tôn trọng", "Dọa họ", "Nhờ bạn ép"],
                "correct_index": 1,  # B
                "explanation": "Có thể rút lại đồng thuận."
            },
            {
                "question_text": "Im lặng hoặc không phản ứng có tự động là “đồng ý” không?",
                "options": ["Có", "Không", "Tùy người xem", "Nếu đã từng quen"],
                "correct_index": 1,  # B
                "explanation": "Không suy diễn từ im lặng."
            },
            {
                "question_text": "Người không tỉnh táo có thể được xem như đang chủ động đồng ý không?",
                "options": ["Có", "Chỉ khi im lặng", "Không", "Chỉ nếu quen nhau"],
                "correct_index": 2,  # C
                "explanation": "Cần khả năng đưa ra quyết định."
            },
            {
                "question_text": "Có nên ép người đã từ chối đổi ý?",
                "options": ["Có", "Chỉ khi yêu", "Không", "Chỉ trong buổi hẹn"],
                "correct_index": 2,  # C
                "explanation": "Ép buộc làm mất tính tự nguyện."
            },
            {
                "question_text": "Điều gì nên làm khi không chắc người kia có muốn một hành động?",
                "options": ["Đoán", "Hỏi và lắng nghe", "Làm thử", "Nhờ người khác quyết định"],
                "correct_index": 1,  # B
                "explanation": "Giao tiếp rõ ràng."
            },
            {
                "question_text": "Ai có quyền rút lại sự đồng ý?",
                "options": ["Chỉ bạn nữ", "Chỉ bạn nam", "Bất kỳ người nào", "Chỉ người lớn"],
                "correct_index": 2,  # C
                "explanation": "Quyền áp dụng cho mọi người."
            },
            {
                "question_text": "Ví dụ uống trà muốn truyền đạt điều gì?",
                "options": ["Trà chữa bệnh", "Tôn trọng quyết định của người khác", "Ai cũng thích trà", "Mời trà thay lời xin lỗi"],
                "correct_index": 1,  # B
                "explanation": "Đây là phép so sánh về ranh giới."
            }
        ]
    },
    {
        "order_index": 4,
        "title": "Bài 4 — HPV liên quan đến sức khỏe của mọi giới",
        "video_url": "https://www.youtube.com/watch?v=auqcLrV70go",
        "duration_minutes": 10,
        "content_type": "HYBRID",
        "content_body": """### Thông tin bài học & Video chính thức
- **Nguồn:** AMAZE Org, *What is HPV? (Human Papillomavirus)*
- **Kênh:** YouTube — AMAZE Org

### Mục tiêu bài học
Hiểu HPV là gì, đường lây, giới hạn của bao cao su và vai trò vắc xin.

### Nội dung xoay quanh video
HPV là vi rút rất phổ biến, thường lây qua tiếp xúc thân mật, có thể ảnh hưởng người có bất kỳ giới nào. Một số chủng gây mụn cóc sinh dục; một số chủng làm tăng nguy cơ ung thư sau nhiều năm. Bao cao su giúp giảm nguy cơ nhưng không che phủ toàn bộ vùng da tiếp xúc. Tiêm vắc xin là cách phòng ngừa quan trọng; trao đổi với nhân viên y tế theo tuổi và lịch tiêm tại địa phương.

> [!NOTE]
> **Bổ sung có kiểm chứng:** CDC khuyến cáo tiêm thường quy lúc **11–12 tuổi** (có thể bắt đầu từ 9), tiêm bù đến **26 tuổi** nếu chưa tiêm đủ; **27–45 tuổi** cân nhắc với bác sĩ, không tiêm thường quy cho tất cả. HPV liên quan **ung thư hầu họng**, không gọi chung là “ung thư vòm họng”.
> Nguồn tham khảo: [CDC — HPV Vaccination](https://www.cdc.gov/hpv/hcp/vaccination-considerations/) và [CDC — Oropharyngeal Cancer](https://www.cdc.gov/cancer/hpv/oropharyngeal-cancer.html).
""",
        "quiz_title": "Quiz 4: HPV liên quan đến sức khỏe của mọi giới",
        "quiz_description": "Bài kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "HPV là gì?",
                "options": ["Vi khuẩn", "Vi rút", "Nấm", "Thuốc"],
                "correct_index": 1,  # B
                "explanation": "Human papillomavirus."
            },
            {
                "question_text": "Ai có thể bị ảnh hưởng bởi HPV?",
                "options": ["Chỉ người có cổ tử cung", "Chỉ nam", "Mọi giới", "Chỉ người già"],
                "correct_index": 2,  # C
                "explanation": "Mọi giới đều cần hiểu HPV."
            },
            {
                "question_text": "HPV có thể lây qua hình thức nào?",
                "options": ["Tiếp xúc thân mật da với da", "Nói chuyện từ xa", "Dùng chung vở", "Nhìn nhau"],
                "correct_index": 0,  # A
                "explanation": "Có thể lây khi tiếp xúc vùng có vi rút."
            },
            {
                "question_text": "Biện pháp nào giúp phòng các chủng HPV có trong vắc xin?",
                "options": ["Kháng sinh", "Vắc xin HPV", "Vitamin", "Thuốc giảm đau"],
                "correct_index": 1,  # B
                "explanation": "Vắc xin phòng ngừa, không điều trị nhiễm sẵn có."
            },
            {
                "question_text": "Bao cao su có che phủ mọi vùng da có thể tiếp xúc không?",
                "options": ["Có", "Không", "Chỉ khi trời lạnh", "Chỉ với người lớn"],
                "correct_index": 1,  # B
                "explanation": "Vẫn có vùng da không được che."
            },
            {
                "question_text": "HPV chỉ liên quan ung thư cổ tử cung?",
                "options": ["Đúng", "Sai", "Chỉ mùa đông", "Không rõ"],
                "correct_index": 1,  # B
                "explanation": "Còn liên quan các ung thư khác."
            },
            {
                "question_text": "Chủng HPV nào có thể gây mụn cóc sinh dục?",
                "options": ["Một số chủng", "Tất cả chủng", "Không chủng nào", "Vi khuẩn khác"],
                "correct_index": 0,  # A
                "explanation": "Tác động khác nhau theo chủng."
            },
            {
                "question_text": "Nam giới có cần học về phòng HPV không?",
                "options": ["Không", "Có", "Chỉ sau tuổi 45", "Chỉ khi có triệu chứng"],
                "correct_index": 1,  # B
                "explanation": "HPV có thể ảnh hưởng mọi giới."
            },
            {
                "question_text": "Vắc xin HPV có phải thuốc chữa khỏi nhiễm HPV đang có?",
                "options": ["Có", "Không", "Luôn luôn", "Chỉ khi sốt"],
                "correct_index": 1,  # B
                "explanation": "Mục đích chính là dự phòng."
            },
            {
                "question_text": "Khi chưa rõ lịch tiêm phù hợp nên?",
                "options": ["Đoán", "Hỏi cơ sở tiêm chủng/nhân viên y tế", "Uống kháng sinh", "Bỏ qua"],
                "correct_index": 1,  # B
                "explanation": "Lịch tiêm phụ thuộc tuổi và quy định hiện hành."
            }
        ]
    },
    {
        "order_index": 5,
        "title": "Bài 5 — Nhận diện tống tiền bằng hình ảnh riêng tư",
        "video_url": "https://www.youtube.com/watch?v=PMv39d1LJgI",
        "duration_minutes": 10,
        "content_type": "HYBRID",
        "content_body": """### Thông tin bài học & Video chính thức
- **Nguồn:** FBI và National Center for Missing & Exploited Children (NCMEC) (thông điệp cảnh báo về sextortion)
- **Kênh:** YouTube — FBI & NCMEC

### Mục tiêu bài học
Nhận diện đe dọa phát tán ảnh và tìm sự hỗ trợ an toàn, không đổ lỗi nạn nhân.

### Nội dung xoay quanh video
Sextortion là việc đe dọa phát tán hình ảnh thân mật nhằm ép một người đưa tiền, ảnh khác hoặc đáp ứng yêu cầu. Kẻ xấu có thể tiếp cận qua mạng và gây sợ hãi, xấu hổ. Nếu gặp chuyện: ngừng làm theo yêu cầu, giữ bằng chứng, báo với người lớn đáng tin/cơ quan có thẩm quyền và báo cáo tài khoản trên nền tảng. Người bị đe dọa cần được giúp đỡ, không phải bị chế giễu.

> [!NOTE]
> **Bổ sung có kiểm chứng:** Take It Down hỗ trợ hình ảnh được chụp khi người trong ảnh **dưới 18 tuổi**: [takeitdown.ncmec.org/vi/](https://takeitdown.ncmec.org/vi/); từ 18 tuổi trở lên xem [stopncii.org](https://stopncii.org/).
> Tại Việt Nam, trẻ em có thể gọi **Tổng đài Quốc gia Bảo vệ Trẻ em 111** để xin hỗ trợ.
> Không tải lại hoặc chuyển tiếp ảnh nhạy cảm của người khác để “lấy bằng chứng”; lưu tin nhắn, tên tài khoản, URL và nhờ người hỗ trợ hướng dẫn.
> Nguồn tham khảo: [NCMEC — Sextortion](https://www.missingkids.org/theissues/sextortion).
""",
        "quiz_title": "Quiz 5: Nhận diện tống tiền bằng hình ảnh riêng tư",
        "quiz_description": "Bài kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Sextortion là gì?",
                "options": ["Tư vấn sức khỏe", "Đe dọa dùng ảnh riêng tư để ép buộc", "Bài tập", "Trò chơi"],
                "correct_index": 1,  # B
                "explanation": "Đó là hành vi tống tiền/tống ép."
            },
            {
                "question_text": "Kẻ đe dọa yêu cầu tiền, nên làm gì?",
                "options": ["Chuyển ngay", "Tìm sự giúp đỡ, không làm theo yêu cầu", "Gửi thêm ảnh", "Giấu mãi"],
                "correct_index": 1,  # B
                "explanation": "Không có bảo đảm trả tiền sẽ chấm dứt đe dọa."
            },
            {
                "question_text": "Bằng chứng hữu ích là gì?",
                "options": ["Tên tài khoản và tin nhắn đe dọa", "Mật khẩu của bạn", "Tin đồn", "Ảnh của bạn bè"],
                "correct_index": 0,  # A
                "explanation": "Giữ thông tin liên hệ và lời đe dọa."
            },
            {
                "question_text": "Nên tìm ai giúp khi là học sinh?",
                "options": ["Người lớn đáng tin", "Chính kẻ đe dọa", "Người lạ bình luận", "Không ai"],
                "correct_index": 0,  # A
                "explanation": "Cần hỗ trợ kịp thời."
            },
            {
                "question_text": "Ai có thể bị sextortion?",
                "options": ["Chỉ nữ", "Chỉ nam", "Bất kỳ ai", "Chỉ người nổi tiếng"],
                "correct_index": 2,  # C
                "explanation": "Không phân biệt giới."
            },
            {
                "question_text": "Cách ứng xử với nạn nhân?",
                "options": ["Đổ lỗi", "Chế giễu", "Lắng nghe và hỗ trợ", "Chia sẻ ảnh"],
                "correct_index": 2,  # C
                "explanation": "Trách nhiệm thuộc về kẻ đe dọa."
            },
            {
                "question_text": "Có nên chuyển tiếp ảnh nhạy cảm của người khác để cảnh báo?",
                "options": ["Có", "Không", "Nếu là bạn thân", "Nếu gửi ẩn danh"],
                "correct_index": 1,  # B
                "explanation": "Việc chia sẻ làm tăng tổn hại."
            },
            {
                "question_text": "Bên cạnh nhờ giúp đỡ, có thể làm gì trên ứng dụng?",
                "options": ["Báo cáo tài khoản đe dọa", "Công khai mật khẩu", "Gửi tiền", "Tắt mọi hỗ trợ"],
                "correct_index": 0,  # A
                "explanation": "Nền tảng có công cụ báo cáo."
            },
            {
                "question_text": "Nguồn của video trong bài là đơn vị nào?",
                "options": ["TED-Ed", "FBI và NCMEC", "AMAZE", "Blue Seat Studios"],
                "correct_index": 1,  # B
                "explanation": "Đúng với URL video được gắn."
            },
            {
                "question_text": "Thông điệp quan trọng là gì?",
                "options": ["Tự chịu đựng", "Vẫn có thể tìm người giúp và báo cáo", "Không ai giúp được", "Gửi thêm ảnh"],
                "correct_index": 1,  # B
                "explanation": "Hỗ trợ sớm giúp giảm tổn hại."
            }
        ]
    },
    {
        "order_index": 6,
        "title": "Bài 6 — Dịch tiết âm đạo: hiểu một thay đổi bình thường của cơ thể",
        "video_url": "https://www.youtube.com/watch?v=FKUc8vg_Lus",
        "duration_minutes": 10,
        "content_type": "HYBRID",
        "content_body": """### Thông tin bài học & Video chính thức
- **Nguồn & Tác giả:** TED-Ed, Elizabeth Micks, *What is vaginal discharge and why does it happen?*
- **Trang bài học chính thức:** [TED-Ed Lesson](https://ed.ted.com/lessons/what-is-vaginal-discharge-and-what-does-it-say-about-your-health-elizabeth-micks)

### Mục tiêu bài học
Mọi học sinh hiểu dịch tiết âm đạo là một hiện tượng cơ thể, nhận diện thay đổi bất thường và không trêu chọc người khác. Bài này nói về một bộ phận cơ thể, không dành riêng cho một giới học sinh; không bắt học sinh nào tự mô tả cơ thể trước lớp.

### Nội dung xoay quanh video
Cơ thể tạo ra nhiều loại dịch tiết; âm đạo cũng có dịch tiết thay đổi theo thời gian. Dịch tiết thông thường không tự động là dấu hiệu “bẩn” hay bệnh. Điều đáng quan tâm là sự thay đổi rõ rệt so với bình thường của cá nhân hoặc kèm triệu chứng khó chịu; khi đó hãy nói với người chăm sóc/nhân viên y tế. Người có hoặc không có âm đạo đều nên hiểu, tôn trọng sự riêng tư và tránh kỳ thị.

> [!NOTE]
> **Bổ sung có kiểm chứng:** Không thụt rửa bên trong âm đạo để “làm sạch”; vệ sinh nhẹ nhàng phần bên ngoài. Không tự dùng sản phẩm tạo mùi để che triệu chứng. Nguồn: [CDC — Bacterial Vaginosis](https://www.cdc.gov/bacterial-vaginosis/about/index.html).
> *Hai ý này là bổ sung có kiểm chứng, không coi là lời thoại xác nhận của video.*
""",
        "quiz_title": "Quiz 6: Dịch tiết âm đạo: hiểu một thay đổi bình thường của cơ thể",
        "quiz_description": "Bài kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video TED-Ed tập trung vào hiện tượng nào?",
                "options": ["Dịch tiết âm đạo", "Cảm cúm", "HPV", "Răng miệng"],
                "correct_index": 0,  # A
                "explanation": "Đây là chủ đề của video."
            },
            {
                "question_text": "Dịch tiết âm đạo xuất hiện có luôn là bệnh?",
                "options": ["Có", "Không", "Luôn là STI", "Luôn là chấn thương"],
                "correct_index": 1,  # B
                "explanation": "Có dịch tiết sinh lý."
            },
            {
                "question_text": "Lượng và đặc điểm dịch có thể thay đổi theo thời gian?",
                "options": ["Không", "Có", "Chỉ ở người lớn tuổi", "Chỉ khi uống thuốc"],
                "correct_index": 1,  # B
                "explanation": "Cơ thể biến đổi theo chu kỳ và hoàn cảnh."
            },
            {
                "question_text": "Điều nào đáng chú ý hơn khi đánh giá sức khỏe?",
                "options": ["So sánh với quảng cáo", "Thay đổi bất thường kèm khó chịu", "Trêu chọc bạn bè", "Che giấu mọi triệu chứng"],
                "correct_index": 1,  # B
                "explanation": "Cần chú ý triệu chứng mới."
            },
            {
                "question_text": "Khi có mùi lạ rõ rệt hoặc ngứa/đau kéo dài, nên?",
                "options": ["Tự chẩn đoán trên mạng", "Hỏi nhân viên y tế", "Xịt nước hoa", "Bỏ mặc"],
                "correct_index": 1,  # B
                "explanation": "Cần đánh giá phù hợp."
            },
            {
                "question_text": "Ai nên học về hiện tượng này?",
                "options": ["Chỉ người có âm đạo", "Mọi học sinh", "Chỉ học sinh nữ", "Chỉ bác sĩ"],
                "correct_index": 1,  # B
                "explanation": "Hiểu cơ thể giúp tránh kỳ thị."
            },
            {
                "question_text": "Bạn nghe người khác trêu chọc một học sinh về dịch tiết, nên?",
                "options": ["Hùa theo", "Tôn trọng, không lan truyền chuyện riêng tư", "Chụp ảnh", "Kể cả lớp"],
                "correct_index": 1,  # B
                "explanation": "Sức khỏe cá nhân cần được tôn trọng."
            },
            {
                "question_text": "Điều nào phù hợp với mục tiêu của video?",
                "options": ["Phân biệt thay đổi bình thường và dấu hiệu cần quan tâm", "Bắt mọi người giống nhau", "Quảng bá nước hoa", "Thay thế bác sĩ"],
                "correct_index": 0,  # A
                "explanation": "TED-Ed giới thiệu đúng trọng tâm này."
            },
            {
                "question_text": "Nếu không chắc một thay đổi có đáng lo, cách làm phù hợp?",
                "options": ["Hỏi người có chuyên môn", "Uống thuốc của bạn", "Tự giấu", "Tin quảng cáo"],
                "correct_index": 0,  # A
                "explanation": "Chuyên môn giúp đánh giá."
            },
            {
                "question_text": "Ý chính của bài là gì?",
                "options": ["Cơ thể phải không có dịch", "Hiểu biến đổi cơ thể và biết khi nào tìm hỗ trợ", "Mọi mùi đều là bệnh", "Học sinh không nên hỏi"],
                "correct_index": 1,  # B
                "explanation": "Kiến thức giúp bớt lo và hành động đúng."
            }
        ]
    }
]

async def seed_curriculum():
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
        print(f"Created Course: {course.title} (ID: {course_id})")

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
        print("SEEDING COMPLETED SUCCESSFULLY!")
        print(f"Course: {COURSE_DATA['title']}")
        print(f"Lessons: {len(LESSONS_DATA)}")
        print(f"Quizzes: {len(LESSONS_DATA)}")
        print(f"Total Questions: {total_questions}")
        print(f"Total Options: {total_options}")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(seed_curriculum())
