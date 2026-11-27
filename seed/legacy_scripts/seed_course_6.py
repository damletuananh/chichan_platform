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
    "title": "Khi Con Gặp Nguy Hiểm: Bình Tĩnh Để Bảo Vệ",
    "slug": "khi-con-gap-nguy-hiem-binh-tinh-de-bao-ve",
    "short_description": "Cẩm nang hướng dẫn phụ huynh xử lý khủng hoảng an toàn: lắng nghe khi con tiết lộ bị xâm hại, ứng phó tống tiền hình ảnh, bảo vệ chứng cứ và đồng hành hồi phục tâm lý.",
    "description": (
        "**Đối tượng:** Phụ huynh có con ở mọi lứa tuổi (trẻ em và thiếu niên).\n\n"
        "Khóa học trang bị các kỹ năng và kiến thức thiết yếu để cha mẹ trở thành điểm tựa an toàn vững chắc nhất khi con gặp tình huống nguy hiểm: "
        "từ cách giữ bình tĩnh và lắng nghe thấu cảm khi con tiết lộ có người làm con khó chịu, kỹ năng ngăn chặn vòng xoáy tống tiền bằng hình ảnh nhạy cảm (sextortion), "
        "nhận diện hành vi thao túng và kiểm soát độc hại, giải tỏa mặc cảm tội lỗi cho trẻ, đến quy trình lưu giữ dấu vết số an toàn để trình báo cơ quan chức năng "
        "và các bước đồng hành giúp trẻ từng ngày lấy lại cảm giác an toàn sau biến cố.\n\n"
        "**Lưu ý y tế & pháp lý:** Học liệu mang tính giáo dục kỹ năng, không thay thế việc xử lý tình huống khẩn cấp, can thiệp y tế hay hướng dẫn từ cơ quan chức năng. "
        "Tại Việt Nam, Tổng đài Quốc gia Bảo vệ Trẻ em **111** tiếp nhận cuộc gọi miễn phí 24/7."
    ),
    "learning_objectives": (
        "- Giữ bình tĩnh, lắng nghe không phán xét và không đổ lỗi khi con tiết lộ việc bị xâm hại hoặc vượt ranh giới.\n"
        "- Xử lý an toàn khi con bị đe dọa tống tiền hình ảnh: không trả tiền, không gửi thêm ảnh, dừng liên hệ và tìm trợ giúp.\n"
        "- Nhận biết các biểu hiện của mối quan hệ kiểm soát độc hại, thao túng tâm lý và dấu hiệu nguy cơ xâm hại.\n"
        "- Giúp trẻ vượt qua sự xấu hổ, tội lỗi để can đảm mở lời tìm kiếm sự giúp đỡ từ người lớn tin cậy.\n"
        "- Nắm vững quy trình lưu giữ chứng cứ số an toàn (không phát tán thêm ảnh) và kết nối với Tổng đài 111 / cơ quan chức năng.\n"
        "- Thiết lập môi trường sinh hoạt dễ đoán và hỗ trợ tâm lý dài hạn giúp con hồi phục sau sang chấn."
    ),
    "thumbnail_url": "https://images.unsplash.com/photo-1476703993599-0035a21b17a9?auto=format&fit=crop&w=1200&q=80",
    "target_audience": "PARENT",
    "is_published": True,
}

LESSONS_DATA = [
    {
        "order_index": 1,
        "title": "Bài 1 — Con nói “có người làm con khó chịu”: tin và lắng nghe thế nào?",
        "video_url": "https://www.youtube.com/watch?v=bvJ5uBlGYgE",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Dừng lại và lắng nghe
Khi con tiết lộ điều gây lo sợ, hãy giữ bình tĩnh, cảm ơn vì con đã nói, công nhận cảm xúc và khẳng định cho con biết con không hề có lỗi. Không biểu lộ sự sốc quá mức, không trách mắng, không buộc con phải kể lại trước mặt nhiều người.

### 2. Hỏi vừa đủ để bảo vệ
Dùng câu hỏi mở như: *“Con muốn kể thêm điều gì?”* và *“Bây giờ con có an toàn không?”*. Không đặt câu hỏi gợi ý hay dẫn dắt, không tự điều tra hoặc yêu cầu con kể lặp lại nhiều lần; ghi nhận lại lời con bằng chính từ ngữ của con khi phù hợp.

### 3. Không hứa giữ kín tuyệt đối
Giải thích nhẹ nhàng rằng cha mẹ có thể cần nhờ người có trách nhiệm chuyên môn để bảo vệ con. Nếu có nguy cơ ngay trước mắt, lập tức đưa con đến nơi an toàn và liên hệ hỗ trợ khẩn cấp tại địa phương.

> [!IMPORTANT]
> **Kênh hỗ trợ quốc gia:** Tại Việt Nam, **Tổng đài Quốc gia Bảo vệ Trẻ em 111** tiếp nhận tư vấn, thông báo và can thiệp bảo vệ trẻ em miễn phí 24/7.

### 4. Câu mẫu thực hành
*“Cảm ơn con đã dũng cảm kể cho bố mẹ. Chuyện này hoàn toàn không phải lỗi của con. Bây giờ con đang an toàn chứ? Bố mẹ sẽ luôn ở bên và cùng con tìm người có thể giúp đỡ mình.”*

> [!NOTE]
> **Nguồn video:** NSPCC Learning — *Responding to a Child’s Disclosure of Abuse*  
> **Nguồn đối chiếu:** [https://www.nspcc.org.uk/keeping-children-safe/reporting-abuse/what-to-do-child-reveals-abuse/](https://www.nspcc.org.uk/keeping-children-safe/reporting-abuse/what-to-do-child-reveals-abuse/)
""",
        "quiz_title": "Củng cố bài 1 — Con nói “có người làm con khó chịu”: tin và lắng nghe thế nào?",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Khi trẻ vừa kể chuyện đáng lo, điều đầu tiên nên làm?",
                "options": [
                    "Bình tĩnh nghe và ghi nhận việc con đã nói",
                    "Hỏi dồn đến khi có đủ mọi chi tiết",
                    "Trách con đã đến nơi đó",
                    "Đăng chuyện lên mạng"
                ],
                "correct_index": 0,
                "explanation": "Lắng nghe hỗ trợ trẻ tiếp tục tiết lộ."
            },
            {
                "question_text": "Vì sao không nên hứa giữ kín tuyệt đối?",
                "options": [
                    "Vì mọi người đều cần biết",
                    "Có thể cần chia sẻ đúng người để bảo vệ trẻ",
                    "Vì quyền riêng tư của trẻ không có giá trị",
                    "Vì câu chuyện phải đăng công khai"
                ],
                "correct_index": 1,
                "explanation": "Người bảo vệ có thể cần được thông báo."
            },
            {
                "question_text": "Câu hỏi nào ít dẫn dắt hơn?",
                "options": [
                    "“Có phải người đó làm việc X không?”",
                    "“Con đã tự gây chuyện đúng không?”",
                    "“Con muốn kể thêm điều gì?”",
                    "“Con chắc chắn không nói dối chứ?”"
                ],
                "correct_index": 2,
                "explanation": "Câu hỏi mở để trẻ dùng ngôn ngữ của mình."
            },
            {
                "question_text": "Điều nào nên tránh sau khi nghe trẻ kể?",
                "options": [
                    "Hỏi trẻ có đang an toàn không",
                    "Lắng nghe không phán xét",
                    "Liên hệ nguồn hỗ trợ",
                    "Bắt trẻ thuật lại nhiều lần cho nhiều người"
                ],
                "correct_index": 3,
                "explanation": "Kể lặp lại có thể gây thêm căng thẳng."
            },
            {
                "question_text": "Lời trấn an phù hợp?",
                "options": [
                    "“Con không có lỗi vì người khác làm con khó chịu”",
                    "“Lẽ ra con phải biết”",
                    "“Đừng làm bố mẹ xấu hổ”",
                    "“Con phải tự giải quyết”"
                ],
                "correct_index": 0,
                "explanation": "Lỗi thuộc về người gây hại."
            },
            {
                "question_text": "Nếu trẻ hiện vẫn gần người bị nghi gây hại?",
                "options": [
                    "Chờ hết tuần",
                    "Ưu tiên đưa trẻ đến nơi an toàn và tìm trợ giúp",
                    "Để trẻ gặp riêng để đối chất",
                    "Chỉ làm quiz"
                ],
                "correct_index": 1,
                "explanation": "Bảo vệ an toàn hiện tại trước."
            },
            {
                "question_text": "Cách ghi nhớ lời trẻ nếu cần trình báo?",
                "options": [
                    "Biên soạn lại để có vẻ nghiêm trọng",
                    "Xóa mọi ghi chép",
                    "Ghi lời trẻ càng sát nguyên văn càng tốt, không ép kể thêm",
                    "Bảo trẻ học thuộc một bản kể"
                ],
                "correct_index": 2,
                "explanation": "Ghi trung thực hỗ trợ đánh giá sau này."
            },
            {
                "question_text": "Ai có thể gọi Tổng đài 111 tại Việt Nam?",
                "options": [
                    "Chỉ người đã đủ 18 tuổi",
                    "Chỉ nhân viên trường học",
                    "Chỉ người có giấy giới thiệu",
                    "Người cần thông báo hay tư vấn về bảo vệ trẻ em"
                ],
                "correct_index": 3,
                "explanation": "111 tiếp nhận thông tin và tư vấn về trẻ em."
            },
            {
                "question_text": "Khi hỏi chuyện khó, cha mẹ nên tránh thái độ nào?",
                "options": [
                    "Sốc, đổ lỗi hoặc nghi ngờ công kích",
                    "Bình tĩnh",
                    "Thừa nhận con đã dũng cảm",
                    "Tập trung an toàn"
                ],
                "correct_index": 0,
                "explanation": "Thái độ phán xét làm trẻ ngại nói."
            },
            {
                "question_text": "Bài học rút ra từ video NSPCC?",
                "options": [
                    "Tự điều tra thay chuyên gia",
                    "Lắng nghe, nghiêm túc và tìm hỗ trợ bảo vệ phù hợp",
                    "Giữ kín dù trẻ nguy hiểm",
                    "Bắt trẻ kể trước đám đông"
                ],
                "correct_index": 1,
                "explanation": "Video hướng dẫn phản ứng khi trẻ tiết lộ."
            }
        ]
    },
    {
        "order_index": 2,
        "title": "Bài 2 — Ảnh riêng tư bị đe dọa phát tán: dừng vòng xoáy tống tiền",
        "video_url": "https://www.youtube.com/watch?v=9Q4pxdUimAU",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Nhận diện thủ đoạn
Video NCMEC mô tả cách tống tiền bằng hình ảnh (sextortion) có thể bắt đầu, những dấu hiệu cảnh báo và vai trò của người chứng kiến trong việc hỗ trợ. Khi ai đó đe dọa phát tán hình ảnh riêng tư để đòi tiền, đòi gửi thêm ảnh hoặc điều kiện khác, trẻ không bao giờ phải tự xoay xở một mình.

### 2. Những việc cần làm ngay
- Giữ bình tĩnh, khẳng định con không đáng bị đe dọa.
- **Không trả tiền, không gửi thêm ảnh, không đáp ứng bất kỳ yêu sách nào.** Trả tiền không bao giờ chấm dứt đe dọa.
- Tạm ngừng liên hệ với đối tượng; lưu lại tài khoản, đường dẫn, tin nhắn đe dọa không chứa ảnh nhạy cảm để trình báo.
- Tránh chia sẻ hoặc tải thêm hình nhạy cảm của người dưới 18 tuổi.

### 3. Báo cáo đúng nơi
Báo cáo cho nền tảng mạng xã hội liên quan, cơ quan công an và Tổng đài 111 tại Việt Nam. Với hình ảnh chụp khi người trong ảnh dưới 18 tuổi, công cụ **Take It Down** của NCMEC có thể hỗ trợ gỡ trên các nền tảng tham gia (sử dụng trên thiết bị có sẵn tệp gốc, không tải hoặc phát tán tệp mới để dùng dịch vụ).

### 4. Câu mẫu thực hành
*“Kẻ đe dọa đang vi phạm pháp luật. Bố mẹ và con sẽ cùng nhau giải quyết an toàn; con tuyệt đối không cần chuyển tiền hay gửi thêm bất kỳ hình ảnh nào.”*

> [!NOTE]
> **Nguồn video:** NCMEC NetSmartz — *It’s Called Sextortion*  
> **Nguồn đối chiếu:** [https://www.ncmec.org/theissues/sextortion](https://www.ncmec.org/theissues/sextortion)
""",
        "quiz_title": "Củng cố bài 2 — Ảnh riêng tư bị đe dọa phát tán: dừng vòng xoáy tống tiền",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Dấu hiệu cốt lõi của tống tiền hình ảnh là gì?",
                "options": [
                    "Đe dọa phát tán hình để buộc làm theo yêu sách",
                    "Gửi lời chào lịch sự",
                    "Hỏi bài tập thông thường",
                    "Xin lịch hẹn khám"
                ],
                "correct_index": 0,
                "explanation": "Đe dọa nhằm ép buộc là trọng tâm."
            },
            {
                "question_text": "Khi đối tượng đòi tiền để không phát tán, nên?",
                "options": [
                    "Trả tiền ngay để chắc chắn xong",
                    "Không trả tiền và tìm trợ giúp, báo cáo",
                    "Gửi thêm ảnh",
                    "Xóa mọi bằng chứng trước khi tìm hỗ trợ"
                ],
                "correct_index": 1,
                "explanation": "Trả tiền không bảo đảm chấm dứt đe dọa."
            },
            {
                "question_text": "Video NCMEC nhấn mạnh vai trò nào của bạn bè?",
                "options": [
                    "Bạn bè nên lan truyền để cảnh báo",
                    "Bạn bè cần chê trách nạn nhân",
                    "Người chứng kiến có thể hỗ trợ và báo người tin cậy",
                    "Bạn bè chỉ nên bỏ qua"
                ],
                "correct_index": 2,
                "explanation": "Người chứng kiến có thể giúp kết nối hỗ trợ."
            },
            {
                "question_text": "Nếu cần ghi nhận tài khoản đe dọa, nên lưu gì?",
                "options": [
                    "Bản sao ảnh nhạy cảm gửi cho nhóm",
                    "Hình riêng tư tải từ nơi khác",
                    "Bài đăng công khai chuyện con",
                    "Tên tài khoản, đường dẫn và lời nhắn đe dọa không chứa ảnh nhạy cảm"
                ],
                "correct_index": 3,
                "explanation": "Thông tin liên hệ và đe dọa hỗ trợ trình báo mà tránh phát tán ảnh."
            },
            {
                "question_text": "Take It Down phù hợp trường hợp nào?",
                "options": [
                    "Ảnh hoặc video nhạy cảm được chụp khi người trong ảnh dưới 18 tuổi",
                    "Mọi hình ảnh bất kỳ",
                    "Chỉ ảnh chụp sau tuổi 18",
                    "Ảnh không có trên thiết bị và cần tải về"
                ],
                "correct_index": 0,
                "explanation": "Dịch vụ dành cho hình được tạo khi người trong ảnh là trẻ vị thành niên."
            },
            {
                "question_text": "Để dùng Take It Down, điều nào phải tránh?",
                "options": [
                    "Dùng tệp gốc đã có trên thiết bị",
                    "Tải hay chia sẻ thêm hình ảnh nhạy cảm nhằm gửi dịch vụ",
                    "Tìm hiểu FAQ chính thức",
                    "Báo nền tảng"
                ],
                "correct_index": 1,
                "explanation": "NCMEC dặn không tải hoặc chia sẻ hình để nộp."
            },
            {
                "question_text": "Khi trẻ sợ bị phạt, cha mẹ nên nói gì?",
                "options": [
                    "“Lỗi hoàn toàn tại con”",
                    "“Đừng làm phiền bố mẹ”",
                    "“Con không đáng bị đe dọa; bố mẹ sẽ cùng tìm hỗ trợ”",
                    "“Hãy làm theo đối tượng”"
                ],
                "correct_index": 2,
                "explanation": "Gỡ cảm giác tội lỗi giúp trẻ tìm hỗ trợ."
            },
            {
                "question_text": "Nền tảng và cơ quan nào có thể tham gia xử lý?",
                "options": [
                    "Chỉ nhóm chat bạn bè",
                    "Chỉ người đe dọa",
                    "Không ai",
                    "Nền tảng liên quan, cơ quan chức năng và 111 ở Việt Nam"
                ],
                "correct_index": 3,
                "explanation": "Báo cáo qua các kênh phù hợp bảo vệ trẻ."
            },
            {
                "question_text": "Lời hứa của người tống tiền có đáng tin để trả tiền?",
                "options": [
                    "Không; việc trả tiền không bảo đảm dừng phát tán",
                    "Có, luôn luôn",
                    "Có nếu chuyển nhanh",
                    "Có nếu giữ bí mật"
                ],
                "correct_index": 0,
                "explanation": "Không thể dựa vào lời hứa của kẻ đe dọa."
            },
            {
                "question_text": "Ưu tiên trước khi suy tính kỹ thuật là gì?",
                "options": [
                    "Điểm số quiz",
                    "An toàn và trạng thái tâm lý của trẻ",
                    "Thể diện gia đình",
                    "Tìm người để trách"
                ],
                "correct_index": 1,
                "explanation": "Trẻ cần biết mình được hỗ trợ ngay."
            }
        ]
    },
    {
        "order_index": 3,
        "title": "Bài 3 — Bắt nạt, ép buộc, xâm hại: dấu hiệu nằm ở sự kiểm soát",
        "video_url": "https://www.youtube.com/watch?v=ldjZCvqhNWw",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Quan hệ lành mạnh cần thời gian
Video và hướng dẫn thảo luận NCMEC cho thấy việc tìm hiểu nhau cần xây dựng lòng tin cậy, lắng nghe và giải quyết bất đồng một cách lành mạnh. Cha mẹ có thể cùng xem với con rồi hỏi về hành vi của nhân vật thay vì trực tiếp chất vấn đời tư của con.

### 2. Dấu hiệu đáng lo
Một người đòi giữ bí mật tiêu cực, cô lập con khỏi gia đình và bạn bè, thúc ép gửi ảnh riêng tư, đe dọa hoặc thao túng tâm lý. Dấu hiệu cảnh báo là lý do để trò chuyện và đánh giá an toàn, không vội vàng kết luận mà cần sự quan sát tinh tế.

### 3. Cách phản ứng
Hỏi con: *“Con có thấy được tôn trọng và có thể nói không trong mối quan hệ này không?”*. Nếu có nguy cơ trực tiếp, kết nối với Tổng đài 111 hoặc cơ quan bảo vệ. Tuyệt đối không ép con phải đối chất riêng với người bị nghi gây hại.

### 4. Luyện tập
*“Người đó có tôn trọng khi con không đồng ý không? Nếu con thấy lo lắng hay sợ hãi, bố mẹ sẽ cùng con tìm cách giải quyết.”*

> [!NOTE]
> **Nguồn video:** NCMEC NetSmartz — *Healthy Relationships*  
> **Nguồn đối chiếu:** [NCMEC Discussion Guide](https://www.ncmec.org/content/dam/netsmartz/downloadable/discussion-guides/ns-teen-healthy-relationships-discussion-guide.pdf)
""",
        "quiz_title": "Củng cố bài 3 — Bắt nạt, ép buộc, xâm hại: dấu hiệu nằm ở sự kiểm soát",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video NCMEC hướng đến điều gì?",
                "options": [
                    "Nhận biết hành vi lành mạnh và dấu hiệu bóc lột trong quan hệ",
                    "Dạy kiểm soát bạn bè",
                    "Buộc tiết lộ mật khẩu",
                    "Xếp hạng giới tính"
                ],
                "correct_index": 0,
                "explanation": "Video hỗ trợ nhận diện hành vi quan hệ."
            },
            {
                "question_text": "Hành vi nào là dấu hiệu đáng lo?",
                "options": [
                    "Tôn trọng lời từ chối",
                    "Ép giữ bí mật và cô lập khỏi người tin cậy",
                    "Lắng nghe bất đồng",
                    "Khuyến khích tìm trợ giúp"
                ],
                "correct_index": 1,
                "explanation": "Cô lập và bí mật có thể là dấu hiệu thao túng."
            },
            {
                "question_text": "Một dấu hiệu riêng lẻ có đủ kết luận xâm hại?",
                "options": [
                    "Có, luôn luôn",
                    "Có nếu nghe tin đồn",
                    "Không; cần hỏi chuyện, đánh giá an toàn và tìm hỗ trợ",
                    "Có nếu trẻ dùng mạng"
                ],
                "correct_index": 2,
                "explanation": "Tránh suy diễn; vẫn nghiêm túc với nguy cơ."
            },
            {
                "question_text": "Tại sao cần thời gian để xây tin cậy?",
                "options": [
                    "Để giấu người thân",
                    "Để gửi ảnh riêng tư",
                    "Để kiểm tra mật khẩu",
                    "Để quan sát cách người kia tôn trọng ranh giới và xử lý mâu thuẫn"
                ],
                "correct_index": 3,
                "explanation": "Tin cậy thể hiện trong hành vi theo thời gian."
            },
            {
                "question_text": "Câu hỏi mở về quan hệ của con?",
                "options": [
                    "“Con có thể nói không khi không thoải mái không?”",
                    "“Con bắt buộc phải kể mọi thứ”",
                    "“Con làm bố mẹ xấu hổ à?”",
                    "“Người đó thuộc giới nào?”"
                ],
                "correct_index": 0,
                "explanation": "Quyền từ chối là dấu hiệu an toàn quan trọng."
            },
            {
                "question_text": "Nếu người kia đe dọa, cha mẹ nên?",
                "options": [
                    "Bắt trẻ gặp riêng để làm hòa",
                    "Ưu tiên an toàn và liên hệ hỗ trợ thích hợp",
                    "Đăng danh tính trẻ lên mạng",
                    "Tự kết luận trẻ có lỗi"
                ],
                "correct_index": 1,
                "explanation": "Không ép trẻ tiếp xúc người gây hại."
            },
            {
                "question_text": "Quan hệ lành mạnh có đặc điểm nào?",
                "options": [
                    "Một người được ép người kia",
                    "Phải giấu mọi thứ",
                    "Tôn trọng ranh giới và đối thoại khi bất đồng",
                    "Mật khẩu chung là bắt buộc"
                ],
                "correct_index": 2,
                "explanation": "Tôn trọng và giao tiếp là trọng tâm."
            },
            {
                "question_text": "Bắt nạt có thể xuất hiện ở đâu?",
                "options": [
                    "Chỉ trong lớp",
                    "Chỉ ở nhà",
                    "Chỉ với người lạ",
                    "Cả trực tiếp lẫn không gian mạng"
                ],
                "correct_index": 3,
                "explanation": "Áp lực và đe dọa có thể xuất hiện nhiều môi trường."
            },
            {
                "question_text": "Khi nghi con bị thao túng, phản ứng nào tốt?",
                "options": [
                    "Nghe trải nghiệm của con và đánh giá an toàn",
                    "Cười vì con “dễ tin”",
                    "Tịch thu hết đồ không giải thích",
                    "Bắt con tự xử"
                ],
                "correct_index": 0,
                "explanation": "Lắng nghe giúp kết nối trợ giúp."
            },
            {
                "question_text": "Vai trò của cha mẹ khi xem video cùng con?",
                "options": [
                    "Thi hỏi đáp về chuyện riêng",
                    "Hỏi về tình huống, không ép con tiết lộ đời tư",
                    "Phê phán con",
                    "Coi video thay mọi hỗ trợ"
                ],
                "correct_index": 1,
                "explanation": "Trao đổi tình huống là điểm mở an toàn."
            }
        ]
    },
    {
        "order_index": 4,
        "title": "Bài 4 — Con thấy xấu hổ: làm sao để con dám tìm giúp đỡ?",
        "video_url": "https://www.youtube.com/watch?v=qGvChcGsASE",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Cảm xúc cản trở lên tiếng
Video NCMEC phân tích những rào cản cảm xúc mãnh liệt (xấu hổ, sợ bị trừng phạt, sợ gia đình mất mặt) khiến nạn nhân tống tiền hình ảnh chần chừ không dám tìm kiếm sự giúp đỡ. Nhiệm vụ đầu tiên của cha mẹ là xoa dịu nỗi sợ và giải tỏa cảm giác bị phán xét.

### 2. Một lối ra có thật
Nhắc con: *“Kẻ đe dọa đã làm sai hoàn toàn. Bố mẹ tin tưởng con và sẽ luôn đồng hành cùng con.”* Hỏi con muốn có ai ngồi cùng khi liên hệ hỗ trợ; ưu tiên bảo vệ tối đa quyền riêng tư của con.

### 3. Sau khi con lên tiếng
Thống nhất từng bước hành động: báo cáo nền tảng, gọi Tổng đài 111 và hỗ trợ tư vấn tâm lý chuyên sâu khi cần. Tránh yêu cầu con phải thuật lại nhiều lần, và tuyệt đối không hứa hẹn kết quả gỡ ảnh tuyệt đối trên toàn cõi Internet.

### 4. Thực hành
Luyện tập phản xạ trong 20 giây: Cảm ơn con -> Khẳng định con không có lỗi -> Kiểm tra mức độ an toàn -> Đề nghị cùng tìm kiếm sự trợ giúp chuyên môn.

> [!NOTE]
> **Nguồn video:** NCMEC — *I Am a Survivor of Sextortion*  
> **Nguồn đối chiếu:** [https://www.ncmec.org/blog/2024/new-sextortion-videos-safer-internet-day](https://www.ncmec.org/blog/2024/new-sextortion-videos-safer-internet-day)
""",
        "quiz_title": "Củng cố bài 4 — Con thấy xấu hổ: làm sao để con dám tìm giúp đỡ?",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video tập trung vào điều gì?",
                "options": [
                    "Cảm xúc khiến nạn nhân tống tiền ngại tìm giúp đỡ",
                    "Cách gửi hình",
                    "Cách che giấu hành vi phạm tội",
                    "Cách buộc trẻ kể"
                ],
                "correct_index": 0,
                "explanation": "NCMEC mô tả trải nghiệm cảm xúc của người bị hại."
            },
            {
                "question_text": "Câu nào giảm xấu hổ cho trẻ?",
                "options": [
                    "“Con làm bố mẹ mất mặt”",
                    "“Người đe dọa đã làm sai; con không phải đối mặt một mình”",
                    "“Đừng nói với ai”",
                    "“Con đáng bị vậy”"
                ],
                "correct_index": 1,
                "explanation": "Không đổ lỗi giúp trẻ tìm hỗ trợ."
            },
            {
                "question_text": "Cha mẹ nên tránh hứa gì?",
                "options": [
                    "Sẽ lắng nghe con",
                    "Sẽ cùng tìm nơi hỗ trợ",
                    "Chắc chắn xóa mọi bản sao trên toàn mạng",
                    "Sẽ tôn trọng riêng tư phù hợp"
                ],
                "correct_index": 2,
                "explanation": "Không thể đảm bảo mọi bản sao biến mất."
            },
            {
                "question_text": "Khi cần báo cơ quan có trách nhiệm, nên?",
                "options": [
                    "Kể rộng cho hàng xóm",
                    "Đe dọa con",
                    "Để trẻ tự lo",
                    "Giải thích cho trẻ các bước và đồng hành"
                ],
                "correct_index": 3,
                "explanation": "Minh bạch giúp trẻ lấy lại cảm giác kiểm soát."
            },
            {
                "question_text": "Vì sao không yêu cầu kể nhiều lần cho nhiều người?",
                "options": [
                    "Có thể gây thêm căng thẳng và xấu hổ",
                    "Vì trẻ không cần nói với ai",
                    "Vì không có nơi hỗ trợ",
                    "Vì kể là vô ích"
                ],
                "correct_index": 0,
                "explanation": "Giảm kể lặp lại khi không cần thiết."
            },
            {
                "question_text": "Nếu trẻ muốn một người tin cậy ngồi cạnh?",
                "options": [
                    "Cấm mọi người trợ giúp",
                    "Cân nhắc để người đó hỗ trợ nếu an toàn",
                    "Buộc trẻ một mình",
                    "Công bố lên mạng"
                ],
                "correct_index": 1,
                "explanation": "Sự đồng hành an toàn giúp trẻ lên tiếng."
            },
            {
                "question_text": "Việc nào nên đến trước tranh luận lỗi đúng?",
                "options": [
                    "Truy tìm lỗi của trẻ",
                    "Chấm điểm hành vi",
                    "Hỏi trẻ có an toàn và cần gì ngay",
                    "Đăng bản kể"
                ],
                "correct_index": 2,
                "explanation": "An toàn hiện tại là ưu tiên."
            },
            {
                "question_text": "Thông tin sự cố nên chia sẻ cho ai?",
                "options": [
                    "Tất cả người quen",
                    "Mọi nhóm chat",
                    "Bất kỳ người lạ",
                    "Những người cần biết để bảo vệ và hỗ trợ"
                ],
                "correct_index": 3,
                "explanation": "Giữ riêng tư bảo vệ trẻ."
            },
            {
                "question_text": "Khi trẻ nói sợ bố mẹ giận, nên?",
                "options": [
                    "Khẳng định sẽ nghe và giúp, điều chỉnh cảm xúc của mình",
                    "Mắng trước rồi hỏi",
                    "Đưa ra phạt ngay",
                    "Ngắt cuộc gọi"
                ],
                "correct_index": 0,
                "explanation": "Phản ứng người lớn ảnh hưởng khả năng trẻ tìm giúp."
            },
            {
                "question_text": "Mục đích quiz bài này là gì?",
                "options": [
                    "Chẩn đoán sang chấn",
                    "Luyện lời phản hồi giúp trẻ tìm trợ giúp",
                    "Xác định ai phạm tội",
                    "Thay thế tư vấn"
                ],
                "correct_index": 1,
                "explanation": "Quiz củng cố cách hỗ trợ giao tiếp."
            }
        ]
    },
    {
        "order_index": 5,
        "title": "Bài 5 — Giữ dấu vết, tìm đúng người: trợ giúp bắt đầu từ đâu?",
        "video_url": None,
        "duration_minutes": 16,
        "content_type": "TEXT",
        "content_body": """### 1. Sơ đồ ưu tiên hành động
Nếu có nguy cơ trực tiếp đối với thân thể, lập tức đưa con đến nơi an toàn và gọi cấp cứu hoặc cơ quan công an. Với thông tin đe dọa qua mạng, ghi nhận cẩn thận thời gian, đường dẫn (URL), tên tài khoản, nội dung tin nhắn không chứa ảnh nhạy cảm; hỏi cơ quan tiếp nhận cách lưu giữ bằng chứng đúng luật.

### 2. Tuyệt đối không lan truyền ảnh của trẻ
Không tải xuống, chuyển tiếp hoặc gửi ảnh nhạy cảm của con vào các nhóm chat với mục đích “làm bằng chứng”. Dùng tính năng báo cáo của chính nền tảng mạng xã hội. Theo hướng dẫn chính thức của NCMEC Take It Down: không tải hoặc chia sẻ thêm ảnh nhạy cảm để nộp dịch vụ.

### 3. Kênh tiếp nhận tại Việt Nam
- **Tổng đài 111:** Miễn phí 24/7, tiếp nhận thông báo bảo vệ trẻ em và hướng dẫn quy trình can thiệp khẩn cấp.
- Khi có tổn thương thể chất, đưa trẻ đến cơ sở y tế gần nhất kịp thời.
- Lưu ý: Dịch vụ eSafety của Úc hay CyberTipline của Mỹ có phạm vi xử lý lãnh thổ riêng, không đại diện cho cơ quan thụ lý pháp luật tại Việt Nam.

### 4. Hướng dẫn hành động chuẩn cho gia đình khi xử lý sự cố
- **Ưu tiên hàng đầu là sự an toàn của con:** Tạm ngắt kết nối với đối tượng đe dọa, đưa con về không gian an toàn và khẳng định với con rằng con không hề có lỗi; gia đình sẽ luôn ở bên bảo vệ con.
- **Lưu giữ dấu vết số an toàn và đúng quy chuẩn:** Chụp lại ảnh màn hình tin nhắn tống tiền, lưu tên tài khoản, đường link (URL) trang cá nhân và mốc thời gian cụ thể. **Tuyệt đối không** chuyển tiếp hay tải thêm hình ảnh nhạy cảm của trẻ vì hành vi này vô tình lan truyền dữ liệu riêng tư và vi phạm pháp luật.
- **Kích hoạt các kênh hỗ trợ chuyên nghiệp:** Sử dụng công cụ Take It Down để ngăn chặn hình ảnh phát tán, gửi báo cáo vi phạm đến nền tảng mạng xã hội, và gọi ngay đến **Tổng đài Quốc gia 111** để được hướng dẫn phối hợp cùng cơ quan chức năng bảo vệ trẻ.

> [!TIP]
> **Kênh hỗ trợ và công cụ bảo vệ:**
> - [Take It Down (NCMEC) — Công cụ ngăn chặn phát tán hình ảnh nhạy cảm](https://takeitdown.ncmec.org/faq/)
> - [eSafety Australia — Hướng dẫn xử lý sexting và an toàn số](https://www.esafety.gov.au/parents/issues-and-advice/sending-nudes-sexting)
> - **Tổng đài Quốc gia Bảo vệ Trẻ em 111:** Tiếp nhận tư vấn và can thiệp miễn phí 24/7 tại Việt Nam.
""",
        "quiz_title": "Củng cố bài 5 — Giữ dấu vết, tìm đúng người: trợ giúp bắt đầu từ đâu?",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Nếu trẻ có nguy cơ trực tiếp, việc trước tiên?",
                "options": [
                    "Đưa trẻ đến nơi an toàn và tìm trợ giúp khẩn cấp",
                    "Chỉ chụp đủ màn hình",
                    "Đợi kết quả quiz",
                    "Đăng mạng xã hội"
                ],
                "correct_index": 0,
                "explanation": "An toàn hiện tại luôn trước thủ tục."
            },
            {
                "question_text": "Thông tin nào có thể ghi nhận mà tránh lan ảnh nhạy cảm?",
                "options": [
                    "Bản sao ảnh gửi vào nhóm",
                    "Đường dẫn, tài khoản, thời điểm và lời đe dọa",
                    "Ảnh tải thêm từ nơi khác",
                    "Bài đăng công khai danh tính trẻ"
                ],
                "correct_index": 1,
                "explanation": "Có thể lưu metadata và đe dọa không chứa ảnh."
            },
            {
                "question_text": "Có nên tải ảnh nhạy cảm của trẻ về để dùng Take It Down?",
                "options": [
                    "Có, luôn luôn",
                    "Có nếu gửi cho bạn bè",
                    "Không; dịch vụ khuyên không tải hoặc chia sẻ ảnh để nộp",
                    "Có nếu làm bằng chứng trên mạng"
                ],
                "correct_index": 2,
                "explanation": "FAQ cấm tải thêm ảnh chỉ để nộp."
            },
            {
                "question_text": "Tổng đài 111 có vai trò gì tại Việt Nam?",
                "options": [
                    "Chỉ bán khóa học",
                    "Đảm bảo xóa mọi ảnh toàn cầu",
                    "Thay tất cả cấp cứu",
                    "Tiếp nhận và tư vấn bảo vệ trẻ em miễn phí 24/7"
                ],
                "correct_index": 3,
                "explanation": "111 là kênh bảo vệ trẻ em quốc gia."
            },
            {
                "question_text": "eSafety là cơ quan của nước nào?",
                "options": [
                    "Úc",
                    "Việt Nam",
                    "Canada",
                    "Nhật Bản"
                ],
                "correct_index": 0,
                "explanation": "Không trình bày thẩm quyền nước ngoài như của Việt Nam."
            },
            {
                "question_text": "Nếu nền tảng có công cụ báo cáo nội dung, nên?",
                "options": [
                    "Phát tán để mọi người biết",
                    "Báo nội dung vi phạm và yêu cầu hỗ trợ gỡ",
                    "Chỉ tranh cãi với người đe dọa",
                    "Không ghi nhận tài khoản"
                ],
                "correct_index": 1,
                "explanation": "Báo nền tảng là một kênh giảm lan truyền."
            },
            {
                "question_text": "Khi cơ quan chức năng yêu cầu vật chứng số, nên?",
                "options": [
                    "Tự gửi cho mọi người",
                    "Sao chép cho nhiều thiết bị",
                    "Hỏi họ cách cung cấp an toàn phù hợp",
                    "Cắt ghép nội dung"
                ],
                "correct_index": 2,
                "explanation": "Cơ quan tiếp nhận hướng dẫn cách giao nộp."
            },
            {
                "question_text": "Take It Down có thể bảo đảm xóa trên mọi nền tảng?",
                "options": [
                    "Có, mọi website",
                    "Có, cả tin nhắn mã hóa",
                    "Có, cả ảnh không tồn tại",
                    "Không; phụ thuộc nền tảng tham gia và điều kiện dịch vụ"
                ],
                "correct_index": 3,
                "explanation": "Dịch vụ nêu phạm vi nền tảng tham gia."
            },
            {
                "question_text": "Nếu cần hỗ trợ y tế sau xâm hại, nên?",
                "options": [
                    "Tiếp cận cơ sở y tế phù hợp kịp thời",
                    "Chỉ làm bài quiz",
                    "Dùng mẹo mạng không kiểm chứng",
                    "Đợi hết triệu chứng"
                ],
                "correct_index": 0,
                "explanation": "Nhân viên y tế đánh giá nhu cầu thực tế."
            },
            {
                "question_text": "Trước khi xuất bản video NotebookLM, phải?",
                "options": [
                    "Chỉ kiểm tra số phút",
                    "Đối chiếu quiz với lời thoại và nguồn cuối cùng",
                    "Mặc định AI luôn đúng",
                    "Bỏ tài liệu nguồn"
                ],
                "correct_index": 1,
                "explanation": "Cần kiểm tra tính nhất quán."
            }
        ]
    },
    {
        "order_index": 6,
        "title": "Bài 6 — Sau sự cố: từng ngày lấy lại cảm giác an toàn",
        "video_url": None,
        "duration_minutes": 16,
        "content_type": "TEXT",
        "content_body": """### 1. Tạo dựng an toàn và ổn định nhịp sống
Sau biến cố nguy hiểm, mỗi đứa trẻ có cách phản ứng và tốc độ xử lý khác nhau. Cha mẹ hãy giúp con cảm thấy an toàn bằng cách duy trì nhịp sinh hoạt quen thuộc, dễ đoán (giờ ăn, giờ ngủ, đi học khi sẵn sàng); tránh ép con phải “trở lại bình thường” ngay lập tức. Luôn hỏi ý con trước khi ôm và tuyệt đối tôn trọng lời từ chối.

### 2. Lắng nghe thay vì thúc ép con kể
Cho con quyền đặt câu hỏi, bộc lộ cảm xúc hoặc tạm thời giữ im lặng khi chưa sẵn sàng. Tránh đưa sự việc lên mạng xã hội, tránh bắt con kể đi kể lại câu chuyện cho nhiều người. Nếu các thay đổi về giấc ngủ, khẩu vị, tâm trạng hay học tập kéo dài hoặc nghiêm trọng, cần tìm kiếm sự hỗ trợ chuyên môn từ chuyên gia tâm lý.

### 3. Xử lý kịp thời các dấu hiệu nguy cơ
Nếu con có biểu hiện hoặc lời nói muốn tự làm hại bản thân hoặc vẫn tiếp tục bị đe dọa, hãy luôn túc trực bên con và liên hệ hỗ trợ khẩn cấp tại địa phương hoặc Tổng đài 111. Sự hồi phục là một hành trình dài không theo khuôn mẫu cố định nào.

### 4. Lời khuyên từ chuyên gia tâm lý: Kiên nhẫn đồng hành cùng con
- **Tạo dựng môi trường an toàn và dễ đoán:** Duy trì nhịp sinh hoạt thường nhật quen thuộc (giờ ăn, giờ ngủ, các hoạt động gia đình yêu thích) giúp trẻ từng bước lấy lại cảm giác an tâm và khả năng kiểm soát cuộc sống.
- **Lắng nghe thấu cảm, tuyệt đối không gượng ép:** Cho con thời gian và không gian riêng; lắng nghe khi con chủ động mở lời mà không bắt con phải nhắc lại chi tiết gây tổn thương. Luôn hỏi ý kiến con trước khi có những cử chỉ an ủi như ôm hay nắm tay.
- **Nhận diện các dấu hiệu sang chấn kéo dài:** Cần tìm kiếm sự tham vấn từ chuyên gia tâm lý nhi khoa nếu con xuất hiện các biểu hiện kéo dài như: ác mộng thường xuyên, thay đổi khẩu vị đột ngột, tâm trạng lo âu quá mức, thu mình cách ly hoặc kết quả học tập sụt giảm nghiêm trọng.

> [!NOTE]
> **Nguồn tài liệu tham khảo chuyên môn:**
> - [Child Mind Institute — Giúp trẻ vượt qua biến cố và sang chấn tâm lý](https://childmind.org/guide/helping-children-cope-after-a-traumatic-event/)
> - [Child Mind Institute — Nhận biết dấu hiệu sang chấn tâm lý ở trẻ em](https://childmind.org/article/signs-trauma-children/)
> - **Tổng đài Quốc gia Bảo vệ Trẻ em 111:** Hỗ trợ tư vấn tâm lý và kết nối mạng lưới can thiệp 24/7.
""",
        "quiz_title": "Củng cố bài 6 — Sau sự cố: từng ngày lấy lại cảm giác an toàn",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Sau sự cố, điều nào giúp trẻ ổn định?",
                "options": [
                    "Không gian an toàn và sinh hoạt dễ đoán",
                    "Ép trẻ kể liên tục",
                    "Đăng chuyện lên mạng",
                    "Buộc trẻ quên ngay"
                ],
                "correct_index": 0,
                "explanation": "Nguồn Child Mind nhấn mạnh an toàn và nếp sinh hoạt."
            },
            {
                "question_text": "Phản ứng của trẻ sau biến cố có giống nhau không?",
                "options": [
                    "Có, luôn khóc",
                    "Không; trẻ có thể xử lý theo nhiều cách và nhịp khác nhau",
                    "Có, luôn im lặng",
                    "Có, luôn hồi phục trong một ngày"
                ],
                "correct_index": 1,
                "explanation": "Không áp một khuôn phản ứng."
            },
            {
                "question_text": "Trước khi ôm trẻ để an ủi, nên?",
                "options": [
                    "Ôm bất kể lời trẻ",
                    "Nói trẻ phải biết ơn",
                    "Hỏi ý và tôn trọng nếu trẻ không muốn",
                    "Coi từ chối là hư"
                ],
                "correct_index": 2,
                "explanation": "Quyền kiểm soát cơ thể hỗ trợ an toàn."
            },
            {
                "question_text": "Nếu trẻ không muốn kể lại lúc đó?",
                "options": [
                    "Buộc kể trước cả nhà",
                    "Xem là nói dối",
                    "Cắt mọi nguồn hỗ trợ",
                    "Tôn trọng và cho biết có thể nói khi sẵn sàng"
                ],
                "correct_index": 3,
                "explanation": "Lắng nghe theo nhịp trẻ."
            },
            {
                "question_text": "Dấu hiệu nào nên tìm chuyên gia đánh giá?",
                "options": [
                    "Thay đổi kéo dài hoặc nghiêm trọng ảnh hưởng sinh hoạt",
                    "Một lần xin nghỉ ngơi",
                    "Một câu hỏi lặp lại",
                    "Một sở thích mới"
                ],
                "correct_index": 0,
                "explanation": "Cần xét mức ảnh hưởng chức năng và thời gian."
            },
            {
                "question_text": "Cha mẹ nên tránh cam kết nào?",
                "options": [
                    "“Bố mẹ sẽ lắng nghe”",
                    "“Con chắc chắn sẽ ổn hoàn toàn sau một tuần”",
                    "“Con có thể tìm người hỗ trợ”",
                    "“Mình giữ nếp sinh hoạt”"
                ],
                "correct_index": 1,
                "explanation": "Không thể bảo đảm lịch hồi phục."
            },
            {
                "question_text": "Nếu trẻ nói muốn tự làm hại bản thân?",
                "options": [
                    "Bảo trẻ tự ngủ",
                    "Chờ thêm vài tuần",
                    "Ở bên và tìm hỗ trợ khẩn cấp phù hợp",
                    "Chỉ giao bài quiz"
                ],
                "correct_index": 2,
                "explanation": "Cần hành động an toàn ngay."
            },
            {
                "question_text": "Vì sao nên hạn chế lan truyền câu chuyện?",
                "options": [
                    "Vì mọi người không quan tâm",
                    "Vì hỗ trợ chuyên môn không cần",
                    "Vì thông tin luôn vô ích",
                    "Bảo vệ quyền riêng tư và tránh làm trẻ tổn thương thêm"
                ],
                "correct_index": 3,
                "explanation": "Chia sẻ có chọn lọc với người cần giúp."
            },
            {
                "question_text": "Khi trẻ có nhiều câu hỏi lặp lại, cha mẹ nên?",
                "options": [
                    "Trả lời trung thực theo tuổi và kiên nhẫn",
                    "Cấm hỏi",
                    "Chê trẻ phiền",
                    "Đoán bừa"
                ],
                "correct_index": 0,
                "explanation": "Trẻ có thể cần thời gian xử lý sự việc."
            },
            {
                "question_text": "Quiz sau video NotebookLM có thể xuất bản ngay?",
                "options": [
                    "Có ngay sau nhấn tạo",
                    "Chỉ khi đã kiểm tra video, nguồn, đáp án và hướng dẫn an toàn",
                    "Có nếu đủ 10 câu",
                    "Có dù video đổi nội dung"
                ],
                "correct_index": 1,
                "explanation": "Khớp video và an toàn là điều kiện xuất bản."
            }
        ]
    }
]

async def seed_course_6():
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
        print(f"Created Course 6: {course.title} (ID: {course_id})")

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
        print("SEEDING COURSE 6 COMPLETED SUCCESSFULLY!")
        print(f"Course: {COURSE_DATA['title']}")
        print(f"Target Audience: {COURSE_DATA['target_audience']}")
        print(f"Lessons: {len(LESSONS_DATA)}")
        print(f"Quizzes: {len(LESSONS_DATA)}")
        print(f"Total Questions: {total_questions}")
        print(f"Total Options: {total_options}")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(seed_course_6())
