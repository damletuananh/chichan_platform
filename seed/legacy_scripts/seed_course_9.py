# -*- coding: utf-8 -*-
import sys, os
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
import asyncio
import os
import sys
import uuid
from sqlalchemy import text

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

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
    "title": "Tin Nhau Để Nói Điều Khó Nói",
    "slug": "tin-nhau-de-noi-dieu-kho-noi",
    "short_description": "Khóa học đồng hành dành cho phụ huynh và học sinh: rèn luyện kỹ năng lắng nghe chủ động, tôn trọng ranh giới khi con nói 'không', bất đồng tích cực, cởi mở chia sẻ về rung động tuổi mới lớn và xây dựng bản đồ cứu hộ gia đình.",
    "description": (
        "**Đối tượng:** Phụ huynh và học sinh cùng học (thiếu niên và người chăm sóc).\n\n"
        "Khóa học được xây dựng nhằm bồi đắp và củng cố niềm tin giữa các thế hệ trong gia đình, giúp biến tổ ấm thành nơi an toàn nhất để sẻ chia những điều khó nói: "
        "từ kỹ năng lắng nghe hết câu trước khi phản ứng và tách bạch giữa việc lắng nghe với việc đưa ra giải pháp, "
        "nghệ thuật tôn trọng ranh giới thân thể khi con nói 'không' ngay từ những việc nhỏ trong nhà, "
        "cách biểu đạt bất đồng quan điểm mà không phán xét hay biến nhau thành người xấu, "
        "đón nhận những rung động đầu đời của con bằng sự thấu hiểu thay vì tra hỏi danh tính, "
        "đến việc chủ động chuẩn bị tâm lý và lựa chọn người lớn tin cậy để cùng tháo gỡ vướng mắc, "
        "và cùng nhau lập nên một 'Bản đồ cứu hộ gia đình' với các đầu mối hỗ trợ khẩn cấp (như Tổng đài 111) khi đối mặt với nguy cơ mất an toàn.\n\n"
        "**Lưu ý an toàn:** Học liệu mang tính giáo dục kỹ năng giao tiếp và tâm lý gia đình. "
        "Nếu trẻ đang đối diện với nguy cơ xâm hại hoặc đe dọa tức thời, hãy ưu tiên đưa trẻ đến nơi an toàn và liên hệ ngay Tổng đài Quốc gia Bảo vệ Trẻ em **111** (miễn phí 24/7 tại Việt Nam)."
    ),
    "learning_objectives": (
        "- Rèn luyện kỹ năng lắng nghe chủ động, không ngắt lời và biết hỏi nhu cầu của người nói ('muốn được lắng nghe hay cùng tìm cách').\n"
        "- Xây dựng thói quen tôn trọng ranh giới thân thể và cảm xúc ngay trong gia đình; hiểu rằng 'dừng lại' có nghĩa là dừng lại.\n"
        "- Biết cách biểu đạt bất đồng dựa trên hành vi cụ thể thay vì gắn nhãn hay công kích nhân cách của đối phương.\n"
        "- Tạo không gian cởi mở để con thoải mái chia sẻ về cảm xúc rung động (crush) mà không bị tra hỏi, phán xét hay bêu riếu.\n"
        "- Nắm vững cách chuẩn bị nội dung và lựa chọn nhiều người lớn đáng tin cậy khác nhau khi gặp chuyện khó nói.\n"
        "- Cùng nhau thiết lập 'Bản đồ cứu hộ gia đình' với các mức độ phản ứng rõ ràng và liên hệ kịp thời với Tổng đài 111 khi khẩn cấp."
    ),
    "thumbnail_url": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?auto=format&fit=crop&w=1200&q=80",
    "target_audience": "BOTH",
    "is_published": True,
}

LESSONS_DATA = [
    {
        "order_index": 1,
        "title": "Bài 1 — Lắng nghe hết câu trước khi phản ứng",
        "video_url": "https://www.youtube.com/watch?v=RVqjzzfCEk0",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Lắng nghe là một hành động chủ động
Video từ AMAZE (*How to Be a Good Listener*) nhấn mạnh rằng lắng nghe không phải là sự im lặng thụ động, mà là một kỹ năng cần rèn luyện tích cực: khi người kia bắt đầu chia sẻ, hãy tạm dừng việc đang làm (như lướt điện thoại hay làm việc riêng), duy trì ánh mắt quan tâm, kiên nhẫn đợi họ nói trọn vẹn câu mà không chen ngang, và nhắc lại ý chính để xác nhận mình đã hiểu đúng. Cả phụ huynh lẫn học sinh đều có thể cùng nhau thực hành kỹ năng này mỗi ngày.

### 2. Tách bạch giữa việc lắng nghe và việc vội vã giải quyết
Một thói quen phổ biến của người lớn là vội vàng đưa ra lời khuyên hoặc phán xét ngay khi con vừa mở lời. Trước khi đề xuất bất kỳ giải pháp nào, hãy hỏi một câu đơn giản:
> *“Con/Bố/Mẹ muốn được lắng nghe để giải tỏa cảm xúc hay muốn mình cùng nhau tìm hướng giải quyết?”*
*(Ngoại lệ: Nếu sự việc có nguy cơ đe dọa an toàn tức thời, hãy ưu tiên hành động can thiệp bảo vệ ngay lập tức).*

### 3. Bài tập đóng vai hai chiều
Hai bên cùng chọn một tình huống giả định:
- *Người nói:* “Dạo này con/mình thấy rất khó chịu và buồn mỗi khi bị bạn bè trêu chọc về đặc điểm ngoại hình.”
- *Người nghe:* “Bố/Mẹ/Mình nghe thấy bạn đang cảm thấy tổn thương vì những lời đùa đó. Bạn muốn mình lắng nghe chia sẻ hay cùng nhau nghĩ cách ứng phó?”
*(Đổi vai để cả hai cùng trải nghiệm cảm giác được lắng nghe trọn vẹn mà không bị ép phải kể chuyện đời tư thực tế).*

### 4. Kiểm tra sự thấu hiểu trước khi kết thúc
Trước khi đưa ra lời khuyên hay chuyển chủ đề, hãy hỏi lại: *“Bố/Mẹ hiểu như vậy đã đúng ý con chưa?”* để người nói có cơ hội làm rõ hoặc điều chỉnh. Lắng nghe để thấu cảm không đồng nghĩa với việc bắt buộc phải đồng tình 100% với mọi quan điểm cá nhân, mà là sự công nhận cảm xúc của nhau.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [AMAZE Org — Healthy Relationships: How to Be a Good Listener](https://amaze.org/video/healthy-relationships-good-listener/)
""",
        "quiz_title": "Củng cố bài 1 — Lắng nghe hết câu trước khi phản ứng",
        "quiz_description": "Bài trắc nghiệm 10 câu về kỹ năng lắng nghe chủ động, cách đặt câu hỏi phân định nhu cầu và thấu cảm không phán xét.",
        "questions": [
            {
                "question_text": "Kỹ năng trung tâm của video là?",
                "options": [
                    "Lắng nghe người khác một cách chủ động",
                    "Đáp nhanh nhất có thể",
                    "Thắng cuộc tranh luận",
                    "Đoán suy nghĩ của con",
                ],
                "correct_index": 0,
                "explanation": "Video hướng dẫn cách lắng nghe.",
            },
            {
                "question_text": "Khi người kia chưa nói hết, nên?",
                "options": [
                    "Cắt lời để sửa",
                    "Đợi và tránh ngắt lời",
                    "Mở điện thoại xem tin",
                    "Nói hộ câu cuối",
                ],
                "correct_index": 1,
                "explanation": "Không ngắt giúp hiểu đủ ý.",
            },
            {
                "question_text": "Câu nào kiểm tra mình nghe đúng?",
                "options": [
                    "“Bạn chắc chắn sai”",
                    "“Đừng giải thích”",
                    "“Mình hiểu là bạn đang khó chịu, đúng không?”",
                    "“Mình biết hết rồi”",
                ],
                "correct_index": 2,
                "explanation": "Phản hồi và hỏi lại giúp xác nhận.",
            },
            {
                "question_text": "Trước khi đưa giải pháp, có thể hỏi?",
                "options": [
                    "“Bạn đã sai ở đâu?”",
                    "“Ai bắt bạn nói?”",
                    "“Bạn có chịu nghe lời không?”",
                    "“Bạn muốn mình nghe hay cùng tìm cách?”",
                ],
                "correct_index": 3,
                "explanation": "Hỏi nhu cầu hỗ trợ của người kể.",
            },
            {
                "question_text": "Lắng nghe có nghĩa phải đồng ý mọi ý?",
                "options": [
                    "Không",
                    "Có",
                    "Có nếu là cha mẹ",
                    "Có nếu là học sinh",
                ],
                "correct_index": 0,
                "explanation": "Có thể hiểu cảm xúc dù bất đồng.",
            },
            {
                "question_text": "Bài tập đôi dùng tình huống gì?",
                "options": [
                    "Buộc kể bí mật",
                    "Giả định để không ép kể chuyện thật",
                    "Đưa hồ sơ y tế",
                    "Công khai tin nhắn",
                ],
                "correct_index": 1,
                "explanation": "Tình huống giả định bảo vệ riêng tư.",
            },
            {
                "question_text": "Khi có nguy cơ an toàn tức thời, cần?",
                "options": [
                    "Chờ hết câu chuyện rất lâu",
                    "Chỉ viết quiz",
                    "Tìm trợ giúp ngay bên cạnh việc lắng nghe",
                    "Bỏ qua vì riêng tư",
                ],
                "correct_index": 2,
                "explanation": "An toàn cấp bách cần hành động.",
            },
            {
                "question_text": "Nghe về việc bị đùa ngoại hình, phản hồi tốt?",
                "options": [
                    "“Có gì đâu”",
                    "“Ai cũng bị vậy”",
                    "“Bạn quá nhạy cảm”",
                    "“Mình nghe bạn thấy khó chịu vì lời đùa đó”",
                ],
                "correct_index": 3,
                "explanation": "Ghi nhận cảm giác người nói.",
            },
            {
                "question_text": "Nếu hiểu sai lời người kia, nên?",
                "options": [
                    "Cho họ sửa và nghe tiếp",
                    "Tranh cãi rằng mình đúng",
                    "Đổi chủ đề",
                    "Kể với người khác",
                ],
                "correct_index": 0,
                "explanation": "Lắng nghe cho phép điều chỉnh.",
            },
            {
                "question_text": "Ai cần thực hành lắng nghe trong khóa cùng học?",
                "options": [
                    "Chỉ học sinh",
                    "Cả phụ huynh và học sinh",
                    "Chỉ người lớn",
                    "Chỉ giáo viên",
                ],
                "correct_index": 1,
                "explanation": "Đối thoại là tương tác hai chiều.",
            },
        ],
    },
    {
        "order_index": 2,
        "title": "Bài 2 — Con nói “không”: ranh giới cần được tôn trọng",
        "video_url": "https://www.youtube.com/watch?v=7MGvGhacwjo",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Từ ranh giới gia đình đến các mối quan hệ xã hội
Video từ Planned Parenthood hướng dẫn cách thiết lập và tôn trọng các giới hạn thân thể: luôn hỏi ý kiến trước khi chạm vào cơ thể hay tóc của người khác; hiểu rõ rằng *“không”* có nghĩa là không, và *“dừng lại”* có nghĩa là dừng lại. Trẻ em có toàn quyền từ chối những cái ôm, nụ hôn hay trò đùa đụng chạm khiến con thấy không thoải mái, kể cả với người thân trong nhà.

### 2. Làm gương tôn trọng ngay tại tổ ấm
Phụ huynh hãy làm gương bằng cách không ép buộc con phải ôm người khác để tỏ ra "lịch sự"; thay vào đó, hãy gợi ý những hình thức chào hỏi thân thiện khác như vẫy tay, cúi chào hay chào bằng lời nói. Học sinh cũng rèn luyện thói quen xin phép trước khi chụp ảnh, mượn đồ dùng hoặc tiếp xúc thân mật với bạn bè. Ranh giới cá nhân áp dụng công bằng cho mọi giới tính và lứa tuổi.

### 3. Ngoại lệ chăm sóc sức khỏe và bảo vệ an toàn
Các hoạt động vệ sinh cá nhân khi trẻ còn nhỏ, thăm khám y tế hay can thiệp khẩn cấp có thể đòi hỏi người lớn phải hỗ trợ; tuy nhiên, người chăm sóc luôn cần giải thích rõ ràng mục đích, lắng nghe cảm xúc của trẻ và thực hiện với thái độ tôn trọng nhất có thể.

### 4. Bài tập thực hành: Tôn trọng lời từ chối
Hai bên cùng thực hành đoạn hội thoại ngắn:
- *Bên A:* “Hôm nay mình/con không muốn ôm.”
- *Bên B:* “Được chứ, vậy chúng mình chào nhau bằng một cái vẫy tay và lời chúc nhé!”
*(Khi người lớn biết xin lỗi nếu lỡ vượt quá ranh giới của trẻ, con sẽ học được cách tôn trọng ranh giới của chính mình và của người khác).*

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [Planned Parenthood — How Do I Talk With My Kid About Healthy Relationships?](https://www.plannedparenthood.org/learn/parents/relationships)
""",
        "quiz_title": "Củng cố bài 2 — Con nói “không”: ranh giới cần được tôn trọng",
        "quiz_description": "Bài trắc nghiệm 10 câu về ranh giới cá nhân, quyền từ chối đụng chạm và cách làm gương tôn trọng trong gia đình.",
        "questions": [
            {
                "question_text": "Theo video, “dừng lại” có nghĩa là?",
                "options": [
                    "Ngừng hành động người kia không muốn",
                    "Thử thêm lần nữa",
                    "Hỏi trước cả lớp",
                    "Đổi cách ép",
                ],
                "correct_index": 0,
                "explanation": "Tôn trọng giới hạn người khác.",
            },
            {
                "question_text": "Trẻ không muốn ôm khách, cha mẹ có thể?",
                "options": [
                    "Ép ôm",
                    "Tôn trọng và gợi ý cách chào khác",
                    "Trêu chọc",
                    "Phạt vì từ chối",
                ],
                "correct_index": 1,
                "explanation": "Trẻ có thể chọn cách chào phù hợp.",
            },
            {
                "question_text": "Ai cần hỏi trước khi chạm vào tóc/cơ thể người khác?",
                "options": [
                    "Chỉ người nhỏ tuổi",
                    "Chỉ một giới",
                    "Mọi người",
                    "Chỉ người lạ",
                ],
                "correct_index": 2,
                "explanation": "Xin phép là quy tắc chung.",
            },
            {
                "question_text": "Một lời đáp tôn trọng khi con nói không?",
                "options": [
                    "“Con phải ôm”",
                    "“Không được từ chối”",
                    "“Bố mẹ sẽ giữ bí mật”",
                    "“Được, mình có thể chào bằng lời”",
                ],
                "correct_index": 3,
                "explanation": "Đáp án cho thấy tôn trọng lời từ chối.",
            },
            {
                "question_text": "Người lớn cần can thiệp để chăm sóc y tế thì?",
                "options": [
                    "Giải thích lý do và tôn trọng trẻ trong khả năng",
                    "Không nói gì",
                    "Bỏ qua sức khỏe",
                    "Chế giễu trẻ",
                ],
                "correct_index": 0,
                "explanation": "Chăm sóc cần giao tiếp rõ.",
            },
            {
                "question_text": "Bài học áp dụng theo giới nào?",
                "options": [
                    "Chỉ nam",
                    "Mọi học sinh và phụ huynh",
                    "Chỉ nữ",
                    "Chỉ người trưởng thành",
                ],
                "correct_index": 1,
                "explanation": "Quyền ranh giới không phân giới.",
            },
            {
                "question_text": "Xin phép trước khi đăng ảnh bạn có liên quan bài này?",
                "options": [
                    "Không bao giờ",
                    "Chỉ khi ảnh đẹp",
                    "Có, vì tôn trọng ranh giới và lựa chọn của bạn",
                    "Chỉ khi ảnh đông người",
                ],
                "correct_index": 2,
                "explanation": "Tôn trọng không gian số cũng quan trọng.",
            },
            {
                "question_text": "Việc nào là làm gương tốt?",
                "options": [
                    "Buộc trẻ chịu đựng",
                    "Phớt lờ lời không",
                    "Dọa trẻ",
                    "Người lớn xin lỗi khi vượt ranh giới của trẻ",
                ],
                "correct_index": 3,
                "explanation": "Người lớn làm mẫu cách tôn trọng.",
            },
            {
                "question_text": "Nếu người kia đổi ý về một hoạt động, nên?",
                "options": [
                    "Dừng và hỏi điều họ muốn tiếp tục",
                    "Nói họ phải theo lời hứa",
                    "Tiếp tục bất chấp",
                    "Cười cợt",
                ],
                "correct_index": 0,
                "explanation": "Lời đồng ý có thể thay đổi.",
            },
            {
                "question_text": "Ranh giới trong bài chỉ nói chuyện tình dục?",
                "options": [
                    "Có, chỉ người lớn",
                    "Không, bắt đầu từ quan hệ hằng ngày",
                    "Có, chỉ người yêu",
                    "Không áp dụng trong gia đình",
                ],
                "correct_index": 1,
                "explanation": "Video dùng ôm, tóc và tình bạn làm ví dụ.",
            },
        ],
    },
    {
        "order_index": 3,
        "title": "Bài 3 — Bất đồng mà không biến nhau thành người xấu",
        "video_url": "https://www.youtube.com/watch?v=qBt1-CrzxSc",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Khác biệt ý kiến nhưng vẫn giữ sự tôn trọng
Video từ PBS KIDS minh họa hai nhóm nhảy có phong cách khác nhau, nhưng thông qua việc lắng nghe và đối thoại tích cực, họ đã cùng nhau tạo nên một màn biểu diễn hòa hợp. Dù video hướng tới lứa tuổi nhỏ, các bạn học sinh lớn và phụ huynh hoàn toàn có thể áp dụng tinh thần này vào các bất đồng trong đời sống gia đình (như thời gian dùng điện thoại, quyền riêng tư hay thói quen sinh hoạt).

### 2. Tập trung vào hành vi cụ thể, tuyệt đối không gắn nhãn con người
Khi có mâu thuẫn, việc chỉ trích nhân cách sẽ biến cuộc trò chuyện thành cuộc chiến công kích. Hãy chuyển đổi cách diễn đạt:
- **Tránh gắn nhãn:** *“Con lúc nào cũng vô trách nhiệm!”* hay *“Bố mẹ thật độc đoán và chẳng hiểu gì cả!”*.
- **Diễn đạt hành vi & cảm xúc:** *“Bố mẹ rất lo lắng khi thấy con chia sẻ công khai vị trí thời gian thực trên mạng”* hoặc *“Con muốn giải thích lý do vì sao con cần trao đổi nhóm với bạn bè trong khung giờ này”*.

### 3. Quy trình 3 bước thương lượng tích cực
1. **Nêu mối lo / nhu cầu:** Mỗi bên lần lượt trình bày điều mình đang băn khoăn hoặc mong muốn.
2. **Nhắc lại để xác nhận:** Bên kia tóm tắt lại ý chính để chắc chắn mình đã hiểu đúng tâm tư đối phương.
3. **Thỏa thuận thử nghiệm:** Cùng thống nhất một phương án thử nghiệm trong 1-2 tuần, có mốc thời gian rõ ràng để đánh giá lại.
*(Lưu ý: Nếu không khí trở nên quá căng thẳng, hãy chủ động xin tạm dừng 15-30 phút để hạ nhiệt trước khi tiếp tục).*

### 4. Bài tập thực hành: Xử lý tình huống mạng xã hội
Hai bên cùng giải quyết một tình huống giả định: học sinh muốn đăng bức ảnh chụp chung cả lớp sau buổi dã ngoại, nhưng phụ huynh lo lắng bức ảnh để lộ tên trường và địa điểm. Cùng thảo luận phương án: hỏi ý kiến bạn bè trong ảnh và sử dụng công cụ che mờ vị trí hoặc cắt bớt chi tiết nhạy cảm.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [PBS KIDS — Together We Can: Sometimes it’s OK to Disagree](https://www.wpbstv.org/together-we-can-sometimes-its-ok-to-disagree-pbs-kids/)
""",
        "quiz_title": "Củng cố bài 3 — Bất đồng mà không biến nhau thành người xấu",
        "quiz_description": "Bài trắc nghiệm 10 câu về nghệ thuật giao tiếp khi bất đồng, tránh gán nhãn nhân cách và quy trình thương lượng thỏa thuận gia đình.",
        "questions": [
            {
                "question_text": "Video PBS minh họa điều gì?",
                "options": [
                    "Hai nhóm khác ý vẫn lắng nghe và bất đồng tôn trọng",
                    "Chỉ một nhóm được lên tiếng",
                    "Ai nói to hơn thắng",
                    "Khác ý là hết quan hệ",
                ],
                "correct_index": 0,
                "explanation": "Khác biệt ý tưởng có thể trao đổi.",
            },
            {
                "question_text": "Vì sao bài áp dụng thêm vào chuyện điện thoại?",
                "options": [
                    "Video trực tiếp nói về mọi ứng dụng",
                    "Đó là tình huống thực hành gia đình dựa trên kỹ năng video",
                    "Video chẩn đoán tâm lý",
                    "Video về sức khỏe sinh sản",
                ],
                "correct_index": 1,
                "explanation": "Nội dung video là kỹ năng bất đồng chung.",
            },
            {
                "question_text": "Câu nào nói về hành vi thay vì gắn nhãn?",
                "options": [
                    "“Con vô trách nhiệm”",
                    "“Bố mẹ độc đoán”",
                    "“Bố mẹ lo ảnh công khai vị trí”",
                    "“Con chẳng biết gì”",
                ],
                "correct_index": 2,
                "explanation": "Diễn đạt mối lo cụ thể bớt công kích.",
            },
            {
                "question_text": "Khi hai bên đang nóng, nên?",
                "options": [
                    "Ép nói cho xong",
                    "Tăng âm lượng",
                    "Đăng tranh cãi lên mạng",
                    "Tạm nghỉ và hẹn quay lại",
                ],
                "correct_index": 3,
                "explanation": "Tạm nghỉ giúp điều chỉnh cảm xúc.",
            },
            {
                "question_text": "Bước trước khi đề xuất phương án?",
                "options": [
                    "Nhắc lại điều người kia lo hoặc cần",
                    "Cắt lời",
                    "Tự quyết",
                    "Đổ lỗi",
                ],
                "correct_index": 0,
                "explanation": "Xác nhận hiểu đúng mới thương lượng.",
            },
            {
                "question_text": "Nếu đăng ảnh tập thể, nên nhớ?",
                "options": [
                    "Đăng ngay",
                    "Hỏi ý người trong ảnh và xem vị trí có lộ không",
                    "Gắn địa chỉ của mọi người",
                    "Công khai số điện thoại",
                ],
                "correct_index": 1,
                "explanation": "Đây là áp dụng kỹ năng vào riêng tư số.",
            },
            {
                "question_text": "Bất đồng có đồng nghĩa xem người kia là xấu?",
                "options": [
                    "Có",
                    "Chỉ với cha mẹ",
                    "Không",
                    "Chỉ với học sinh",
                ],
                "correct_index": 2,
                "explanation": "Không gán nhãn con người vì một quan điểm.",
            },
            {
                "question_text": "Thỏa thuận thử có ích khi nào?",
                "options": [
                    "Khi muốn cấm mọi ý khác",
                    "Khi muốn tránh nói chuyện mãi",
                    "Khi cần ép một bên",
                    "Khi cần đánh giá lại sau thời gian cụ thể",
                ],
                "correct_index": 3,
                "explanation": "Hẹn ngày xem lại giúp điều chỉnh.",
            },
            {
                "question_text": "Nhóm tuổi chính của video PBS KIDS?",
                "options": [
                    "Trẻ nhỏ; người học lớn dùng ví dụ để chuyển sang tình huống phù hợp",
                    "Chỉ phụ huynh trưởng thành",
                    "Chỉ bác sĩ",
                    "Chỉ sinh viên",
                ],
                "correct_index": 0,
                "explanation": "Cần biết phạm vi tuổi của video.",
            },
            {
                "question_text": "Ai được nói trong cuộc bất đồng?",
                "options": [
                    "Chỉ người lớn",
                    "Cả phụ huynh và học sinh",
                    "Chỉ người có điện thoại",
                    "Chỉ người chấm quiz",
                ],
                "correct_index": 1,
                "explanation": "Quy trình hai chiều.",
            },
        ],
    },
    {
        "order_index": 4,
        "title": "Bài 4 — Con thích ai: hỏi về cảm xúc, không hỏi cung",
        "video_url": "https://www.youtube.com/watch?v=lGnEMi8jHHs",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Rung động đầu đời là cảm xúc tự nhiên có thể trò chuyện
Video từ AMAZE chia sẻ góc nhìn ấm áp về cảm giác "thích một ai đó" (crush) và cách ứng xử văn minh trong tình bạn, tình yêu tuổi học trò. Gia đình không cần phải tra hỏi xem con đang thích bạn nào hay tò mò về xu hướng của con; thay vào đó, hãy biến đây thành dịp để trao đổi về lòng tự trọng, sự tôn trọng lẫn nhau, và cách đối diện khi tình cảm không được đáp lại.

### 2. Bốn câu hỏi mở đồng hành cùng con
Thay vì điều tra danh tính, cha mẹ hãy bắt đầu bằng những câu hỏi gợi mở về cảm xúc:
1. *“Cảm giác rung động này mang lại cho con những trải nghiệm hay cảm xúc như thế nào?”*
2. *“Con trân trọng những phẩm chất tốt đẹp nào ở bạn ấy hoặc ở một tình bạn đẹp?”*
3. *“Trong mối quan hệ này, con có luôn cảm thấy ranh giới của mình được tôn trọng không?”*
4. *“Nếu lỡ đối phương không có cùng tình cảm, con muốn tìm ai để tâm sự và giải tỏa?”*

### 3. Tôn trọng quyền riêng tư của con
Học sinh hoàn toàn có quyền giữ kín những rung động cá nhân hoặc chỉ chia sẻ về nhân vật trong video thay vì câu chuyện đời thực của mình. Phụ huynh tuyệt đối tránh đem chuyện tình cảm của con ra làm trò đùa trước họ hàng hay bạn bè, vì điều này sẽ phá vỡ niềm tin của con.
*(Nếu phát hiện dấu hiệu con bị kiểm soát, đe dọa hoặc quấy rối, hãy lập tức ưu tiên bảo vệ an toàn cho con).*

### 4. Bài tập thực hành: Tỏ bày lịch thiệp & Tôn trọng phản hồi
Cùng thảo luận tình huống nhân vật trong video: Khi bạn thích một người nhưng chưa rõ người đó có muốn nói chuyện không, cách tiếp cận phù hợp là gì? Mở lời một cách lịch sự, chân thành và hoàn toàn tôn trọng quyết định của người kia (dù là đồng ý hay từ chối).

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [AMAZE Org — Healthy Relationships: What To Do When You Have a Crush](https://amaze.org/video/healthy-relationships-what-to-do-when-you-have-a-crush/)
""",
        "quiz_title": "Củng cố bài 4 — Con thích ai: hỏi về cảm xúc, không hỏi cung",
        "quiz_description": "Bài trắc nghiệm 10 câu về tâm lý rung động tuổi học trò, kỹ năng lắng nghe thấu cảm của cha mẹ và tôn trọng ranh giới cảm xúc.",
        "questions": [
            {
                "question_text": "Video bàn về chủ đề gì?",
                "options": [
                    "Cảm giác thích một người và cách ứng xử",
                    "Cách chọn ngành học",
                    "Kỹ thuật chụp ảnh",
                    "Luật giao thông",
                ],
                "correct_index": 0,
                "explanation": "Nội dung là crush và quan hệ.",
            },
            {
                "question_text": "Người thích ai đó có phải tiết lộ danh tính trong lớp?",
                "options": [
                    "Có",
                    "Không",
                    "Chỉ nếu cha mẹ muốn",
                    "Chỉ khi đạt điểm cao",
                ],
                "correct_index": 1,
                "explanation": "Học kiến thức không buộc tiết lộ đời tư.",
            },
            {
                "question_text": "Nếu người kia không đáp lại, nên?",
                "options": [
                    "Ép họ đồng ý",
                    "Đăng tin đồn",
                    "Tôn trọng phản hồi và chăm sóc cảm xúc của mình",
                    "Đe dọa",
                ],
                "correct_index": 2,
                "explanation": "Sự tôn trọng áp dụng hai chiều.",
            },
            {
                "question_text": "Phụ huynh hỏi gì dễ giữ đối thoại?",
                "options": [
                    "“Nêu tên ngay”",
                    "“Con phải thích người này”",
                    "“Con chưa được có cảm xúc”",
                    "“Con cảm thấy thế nào khi thích ai đó?”",
                ],
                "correct_index": 3,
                "explanation": "Hỏi cảm giác, không điều tra danh tính.",
            },
            {
                "question_text": "Có nên đoán giới của người con thích?",
                "options": [
                    "Không",
                    "Có, luôn luôn",
                    "Có để sửa con",
                    "Có để chấm quiz",
                ],
                "correct_index": 0,
                "explanation": "Không mặc định giới hay xu hướng từ câu chuyện.",
            },
            {
                "question_text": "Bài tập chung có thể thảo luận về?",
                "options": [
                    "Nhật ký riêng của con",
                    "Nhân vật trong video thay vì chuyện riêng của trẻ",
                    "Tin nhắn chưa cho phép",
                    "Danh sách bạn bè con phải khai",
                ],
                "correct_index": 1,
                "explanation": "Thảo luận gián tiếp bớt áp lực.",
            },
            {
                "question_text": "Nếu người con thích khiến con sợ hoặc ép buộc, ưu tiên?",
                "options": [
                    "Giữ bí mật bằng mọi giá",
                    "Cố ở lại để không mất mặt",
                    "An toàn và người hỗ trợ tin cậy",
                    "Lờ đi dấu hiệu",
                ],
                "correct_index": 2,
                "explanation": "Nguy cơ đe dọa cần giúp đỡ.",
            },
            {
                "question_text": "Tỏ tình có nghĩa người kia phải đồng ý?",
                "options": [
                    "Có",
                    "Có nếu thân lâu",
                    "Có nếu bạn bè cổ vũ",
                    "Không",
                ],
                "correct_index": 3,
                "explanation": "Mỗi người có quyền phản hồi riêng.",
            },
            {
                "question_text": "Phụ huynh nên tránh việc nào?",
                "options": [
                    "Dùng chuyện con kể để trêu trước người khác",
                    "Lắng nghe",
                    "Hỏi mở",
                    "Tôn trọng riêng tư",
                ],
                "correct_index": 0,
                "explanation": "Bêu chuyện riêng làm giảm tin cậy.",
            },
            {
                "question_text": "Cách mở lời lịch sự khi thích một người?",
                "options": [
                    "Gửi nhiều tin dù bị từ chối",
                    "Hỏi xem họ có muốn trò chuyện rồi tôn trọng câu trả lời",
                    "Ép gặp riêng",
                    "Đòi xem điện thoại",
                ],
                "correct_index": 1,
                "explanation": "Quan hệ bắt đầu bằng tôn trọng ý muốn.",
            },
        ],
    },
    {
        "order_index": 5,
        "title": "Bài 5 — Chuyện khó nói: chọn ai để cùng gỡ?",
        "video_url": "https://www.youtube.com/watch?v=Ib8qHBR0LK8",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Nhận diện người lớn đáng tin cậy quanh mình
Video của AMAZE khuyến khích các bạn trẻ xác định những người lớn đáng tin cậy trong mạng lưới xung quanh: đó có thể là cha mẹ, thầy cô giáo, chuyên viên tư vấn tâm lý học đường, cô chú hoặc bác sĩ gia đình. Mỗi người có thể hỗ trợ con ở một khía cạnh khác nhau; việc có nhiều đầu mối giúp con luôn tìm được lối thoát an toàn khi gặp rắc rối.

### 2. Chuẩn bị lời mở đầu để vượt qua cảm giác ngượng ngùng
Khi muốn mở lời về một chủ đề nhạy cảm, hãy chuẩn bị trước trong đầu hoặc ghi ra mẩu giấy:
- **Lời mở từ học sinh:** *“Con đang có một thắc mắc về cảm xúc / sự thay đổi cơ thể, nhưng con chưa biết bắt đầu thế nào. Bố/mẹ có thể dành chút thời gian lắng nghe con được không?”*
- **Lời đáp từ phụ huynh:** *“Cảm ơn con đã tin tưởng hỏi bố mẹ. Mình có thể nói từng chút một nhé. Nếu có điều gì chưa rõ, bố mẹ sẽ cùng con tìm kiếm lời khuyên từ chuyên gia.”*

### 3. Phải làm gì nếu người đầu tiên không sẵn sàng lắng nghe?
Nếu người lớn đầu tiên bạn tiếp cận quá bận rộn, phản ứng thiếu bình tĩnh hoặc chưa đủ chuyên môn giải đáp, **đừng bỏ cuộc hay giấu kín một mình**. Hãy kiên trì tìm đến người lớn tin cậy thứ hai hoặc nhân viên y tế / nhà trường. Khi gặp tình huống xâm hại thân thể hay đe dọa khẩn cấp tại Việt Nam, hãy gọi ngay đến **Tổng đài Quốc gia Bảo vệ Trẻ em 111**.

### 4. Bài tập thực hành: Danh bạ 3 người tin cậy
Mỗi người viết ra danh sách 3 người lớn đáng tin cậy mà mình có thể tìm đến tâm sự khi gặp khó khăn (không bắt buộc công khai tên thật trước tập thể), cùng luyện tập một câu xin hẹn lịch trò chuyện riêng tư.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [AMAZE Org — Conversations to Have with an Adult: Puberty & Emotions](https://amaze.org/video/healthy-relationships-adult-conversations-puberty-emotions/)
> - **Tổng đài Quốc gia Bảo vệ Trẻ em 111:** Hỗ trợ tư vấn và can thiệp bảo vệ 24/7.
""",
        "quiz_title": "Củng cố bài 5 — Chuyện khó nói: chọn ai để cùng gỡ?",
        "quiz_description": "Bài trắc nghiệm 10 câu về cách mở lời chia sẻ vấn đề khó nói, tìm kiếm người lớn tin cậy và xử lý khi người đầu tiên chưa sẵn sàng lắng nghe.",
        "questions": [
            {
                "question_text": "Video gợi ý chuẩn bị trước câu chuyện bằng cách nào?",
                "options": [
                    "Viết ý cần nói hoặc nghĩ trước",
                    "Không được chuẩn bị",
                    "Chỉ đăng công khai",
                    "Đợi người khác đoán",
                ],
                "correct_index": 0,
                "explanation": "Chuẩn bị lời giúp giảm ngại.",
            },
            {
                "question_text": "Có thể hỏi nhiều người lớn tin cậy không?",
                "options": [
                    "Không bao giờ",
                    "Có, vì mỗi người có thể giúp một phần",
                    "Chỉ một người duy nhất",
                    "Chỉ người lạ",
                ],
                "correct_index": 1,
                "explanation": "Nguồn nêu có thể có nhiều người hỗ trợ.",
            },
            {
                "question_text": "Nếu người lớn đầu không lắng nghe, nên?",
                "options": [
                    "Giữ kín mọi chuyện",
                    "Tự nhận mình sai",
                    "Tìm người tin cậy khác",
                    "Đăng lên nhóm lạ",
                ],
                "correct_index": 2,
                "explanation": "Cần nhiều đường tiếp cận giúp đỡ.",
            },
            {
                "question_text": "Một câu mở phù hợp của học sinh?",
                "options": [
                    "“Con không cần ai giúp”",
                    "“Con phải kể hết ngay”",
                    "“Mọi người đều biết rồi”",
                    "“Con muốn hỏi nhưng chưa biết bắt đầu thế nào”",
                ],
                "correct_index": 3,
                "explanation": "Câu mở ngắn cũng đủ.",
            },
            {
                "question_text": "Phụ huynh nên đáp thế nào?",
                "options": [
                    "“Cảm ơn con đã hỏi; mình nói từng chút nhé”",
                    "“Đừng hỏi”",
                    "“Con làm phiền quá”",
                    "“Chỉ có một cách đúng là im lặng”",
                ],
                "correct_index": 0,
                "explanation": "Không phán xét giữ kênh đối thoại.",
            },
            {
                "question_text": "Nếu câu hỏi là về sức khỏe cần đánh giá, nên?",
                "options": [
                    "Đoán trên mạng",
                    "Tìm nhân viên y tế phù hợp",
                    "Chỉ làm quiz",
                    "Giữ kín bất kể đau",
                ],
                "correct_index": 1,
                "explanation": "Nguồn hỗ trợ thay đổi theo nhu cầu.",
            },
            {
                "question_text": "Nếu trẻ gặp xâm hại tại Việt Nam, có thể liên hệ?",
                "options": [
                    "Chỉ bạn bình luận mạng",
                    "Chỉ tài khoản ẩn danh",
                    "Tổng đài 111 hoặc hỗ trợ khẩn cấp phù hợp",
                    "Không ai",
                ],
                "correct_index": 2,
                "explanation": "111 là kênh bảo vệ trẻ tại Việt Nam.",
            },
            {
                "question_text": "Người lớn tin cậy có đặc điểm nào?",
                "options": [
                    "Luôn phán xét",
                    "Yêu cầu giữ bí mật nguy hiểm",
                    "Đưa lời khuyên không nguồn",
                    "Lắng nghe và tôn trọng, giúp kết nối hỗ trợ",
                ],
                "correct_index": 3,
                "explanation": "Đáng tin gắn với lắng nghe và an toàn.",
            },
            {
                "question_text": "Bài tập lớp có bắt công khai tên người giúp?",
                "options": [
                    "Không",
                    "Có",
                    "Chỉ học sinh nam",
                    "Chỉ học sinh nữ",
                ],
                "correct_index": 0,
                "explanation": "Bảo vệ riêng tư của người học.",
            },
            {
                "question_text": "Nếu học sinh ngại nói trực tiếp, có thể?",
                "options": [
                    "Bỏ cuộc",
                    "Gửi giấy nhắn hoặc xin lịch nói riêng",
                    "Chỉ hỏi người lạ",
                    "Đợi có khủng hoảng",
                ],
                "correct_index": 1,
                "explanation": "Có nhiều cách mở lời.",
            },
        ],
    },
    {
        "order_index": 6,
        "title": "Bài 6 — Bản đồ cứu hộ của nhà mình: ai, khi nào, nói thế nào?",
        "video_url": None,
        "duration_minutes": 17,
        "content_type": "TEXT",
        "content_body": """### 1. Xây dựng bản đồ hỗ trợ an toàn cho cả gia đình
Dựa trên các hướng dẫn từ AMAZE và Child Mind Institute, việc chủ động lập một "Bản đồ cứu hộ" ngay từ khi cuộc sống đang êm đềm sẽ giúp các thành viên không bị lúng túng hay hoảng loạn khi biến cố ập đến. Mỗi người trong nhà hãy chọn ra 2-3 người lớn tin cậy kèm số điện thoại liên lạc, thông tin của cơ sở y tế gần nhất, giáo viên chủ nhiệm / phòng tâm lý học đường, và **Tổng đài Quốc gia 111** tiếp nhận bảo vệ trẻ em tại Việt Nam.

### 2. Phân loại 3 mức độ phản ứng trong đời sống
1. **Mức 1 — Câu hỏi thông thường về cơ thể và cảm xúc:** Chọn một khung giờ thư thả (sau bữa tối, cuối tuần) để cùng ngồi lại trò chuyện nhẹ nhàng.
2. **Mức 2 — Tình huống gây lo âu, bối rối (bị trêu chọc, nhận tin nhắn lạ):** Báo ngay cho người lớn tin cậy trong ngày; cha mẹ và con cùng nhau xác thực thông tin và tìm cách giải quyết.
3. **Mức 3 — Nguy cơ mất an toàn khẩn cấp (đe dọa tống tiền, bạo lực, ý nghĩ tự làm hại):** Lập tức gác lại mọi việc, luôn ở bên cạnh con, liên hệ ngay với cơ quan chức năng hoặc gọi đến **Tổng đài 111** để được hướng dẫn can thiệp kịp thời. Tuyệt đối không dùng lịch hẹn thông thường để trì hoãn xử lý nguy hiểm.

### 3. Cam kết hai chiều giữa cha mẹ và con cái
- **Về phía học sinh:** Con hoàn toàn có quyền nói: *“Con đang cần giúp đỡ”* mà chưa bắt buộc phải kể hết mọi chi tiết riêng tư ngay từ phút đầu tiên.
- **Về phía phụ huynh:** Cam kết luôn giữ thái độ bình tĩnh, thấu hiểu; giải thích minh bạch cho con biết mình sẽ cần chia sẻ thông tin với ai (chuyên gia tâm lý, bác sĩ hay nhà trường) để bảo vệ con tốt nhất, và luôn đồng hành theo sát tiến triển sau đó.

### 4. Lời khuyên đồng hành và nguồn tài liệu tham khảo cho gia đình
- **Lưu giữ bản đồ ở nơi dễ tiếp cận:** Ghi lại các số liên lạc khẩn cấp vào một tấm thẻ nhỏ để trong ví, dán lên tủ lạnh hoặc lưu trong danh bạ khẩn cấp của điện thoại.
- **Cập nhật định kỳ:** Khi hoàn cảnh gia đình hoặc các mối quan hệ thay đổi, hãy cùng nhau rà soát lại danh sách để đảm bảo các kênh hỗ trợ luôn sẵn sàng hoạt động.
- **Lắng nghe để bảo vệ:** Không gian an toàn nhất của một đứa trẻ chính là sự thấu hiểu và tin cậy tuyệt đối từ cha mẹ mình.

> [!TIP]
> **Nguồn tài liệu tham khảo chuyên môn:**
> - [AMAZE Org — Healthy Relationships: Finding an Adult You Can Trust](https://amaze.org/video/healthy-relationships-finding-an-adult-you-can-trust/)
> - [Child Mind Institute — Kỹ năng giao tiếp và đồng hành cùng trẻ tuổi teen](https://childmind.org/article/tips-communicating-with-teen/)
> - **Tổng đài Quốc gia Bảo vệ Trẻ em 111:** Miễn phí 24/7 tại Việt Nam.
""",
        "quiz_title": "Củng cố bài 6 — Bản đồ cứu hộ của nhà mình: ai, khi nào, nói thế nào?",
        "quiz_description": "Bài trắc nghiệm 10 câu về cách thiết lập bản đồ người lớn tin cậy, phân loại 3 mức độ phản ứng và cam kết đồng hành an toàn trong gia đình.",
        "questions": [
            {
                "question_text": "Bản đồ hỗ trợ nên có gì?",
                "options": [
                    "Người tin cậy, cách liên hệ và kênh phù hợp khi khẩn cấp",
                    "Chỉ mật khẩu của con",
                    "Chỉ điểm quiz",
                    "Danh sách người phải trách",
                ],
                "correct_index": 0,
                "explanation": "Kế hoạch cần đường tìm trợ giúp.",
            },
            {
                "question_text": "Một câu hỏi thông thường nên?",
                "options": [
                    "Luôn gọi cấp cứu",
                    "Chọn thời điểm trò chuyện phù hợp",
                    "Cấm hỏi",
                    "Đăng công khai",
                ],
                "correct_index": 1,
                "explanation": "Không phải mọi thắc mắc đều cấp bách.",
            },
            {
                "question_text": "Nếu trẻ bị đe dọa ngay, nên?",
                "options": [
                    "Hẹn tháng sau",
                    "Chỉ chấm quiz",
                    "Ở bên trẻ và tìm trợ giúp khẩn cấp phù hợp",
                    "Bắt trẻ tự xử",
                ],
                "correct_index": 2,
                "explanation": "Nguy cơ tức thời cần can thiệp ngay.",
            },
            {
                "question_text": "Học sinh có cần kể mọi chi tiết mới được xin giúp?",
                "options": [
                    "Có",
                    "Chỉ một giới cần",
                    "Chỉ khi có giấy tờ",
                    "Không",
                ],
                "correct_index": 3,
                "explanation": "Một câu xin giúp đủ để bắt đầu.",
            },
            {
                "question_text": "Người lớn khi cần chia sẻ thông tin với chuyên gia nên?",
                "options": [
                    "Giải thích cho trẻ biết ai cần được biết và vì sao",
                    "Hứa bí mật tuyệt đối dù nguy hiểm",
                    "Đăng lên mạng",
                    "Kể với tất cả hàng xóm",
                ],
                "correct_index": 0,
                "explanation": "Minh bạch giúp bảo vệ riêng tư.",
            },
            {
                "question_text": "Tổng đài 111 có phạm vi nào?",
                "options": [
                    "Bảo đảm chữa mọi bệnh",
                    "Tư vấn và tiếp nhận thông tin bảo vệ trẻ em tại Việt Nam",
                    "Xóa mọi ảnh toàn thế giới",
                    "Thay mọi cấp cứu",
                ],
                "correct_index": 1,
                "explanation": "111 là kênh bảo vệ trẻ.",
            },
            {
                "question_text": "Vì sao có nhiều người lớn tin cậy?",
                "options": [
                    "Để công khai chuyện riêng",
                    "Để không cần hỏi ai",
                    "Người đầu tiên có thể không sẵn hoặc không đúng chuyên môn",
                    "Để bỏ trách nhiệm gia đình",
                ],
                "correct_index": 2,
                "explanation": "Nhiều lựa chọn tăng khả năng trợ giúp.",
            },
            {
                "question_text": "Bản đồ hỗ trợ nên được xem lại khi?",
                "options": [
                    "Không bao giờ",
                    "Chỉ sau khi nguy hiểm",
                    "Chỉ khi quiz sai",
                    "Khi số liên hệ hay hoàn cảnh gia đình thay đổi",
                ],
                "correct_index": 3,
                "explanation": "Kế hoạch cần còn dùng được.",
            },
            {
                "question_text": "Trong quiz công khai, có nên ghi số riêng của trẻ?",
                "options": [
                    "Không",
                    "Có",
                    "Có nếu cả lớp đồng ý",
                    "Có nếu giáo viên yêu cầu",
                ],
                "correct_index": 0,
                "explanation": "Không đưa dữ liệu riêng vào học liệu công khai.",
            },
            {
                "question_text": "Trước khi đăng video NotebookLM và quiz, cần?",
                "options": [
                    "Chỉ kiểm tra tên khóa",
                    "Đối chiếu câu hỏi với video, nguồn và bước xử lý an toàn",
                    "Giữ mọi câu hỏi dù sai",
                    "Không xem lại",
                ],
                "correct_index": 1,
                "explanation": "Đồng bộ và an toàn cần kiểm tra.",
            },
        ],
    },
]

async def seed_course_9():
    async with AsyncSessionLocal() as session:
        print("Starting seed for Course 9: Tin Nhau Để Nói Điều Khó Nói...")

        # Find Instructor
        res = await session.execute(
            text("SELECT u.id FROM users u JOIN roles r ON u.role_id = r.id WHERE r.role_code = 'INSTRUCTOR' LIMIT 1")
        )
        instructor = res.fetchone()
        if not instructor:
            res = await session.execute(text("SELECT id FROM users LIMIT 1"))
            instructor = res.fetchone()
        
        instructor_id = (uuid.UUID(str(instructor[0])) if not isinstance(instructor[0], uuid.UUID) else instructor[0]) if instructor else None
        print(f"Assigning instructor_id: {instructor_id}")

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
        print(f"Created Course 9: {course.title} (ID: {course_id})")

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
        print("SEEDING COURSE 9 COMPLETED SUCCESSFULLY!")
        print(f"Course: {COURSE_DATA['title']}")
        print(f"Target Audience: {COURSE_DATA['target_audience']}")
        print(f"Lessons: {len(LESSONS_DATA)}")
        print(f"Quizzes: {len(LESSONS_DATA)}")
        print(f"Total Questions: {total_questions}")
        print(f"Total Options: {total_options}")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(seed_course_9())
