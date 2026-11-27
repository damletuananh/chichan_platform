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
    "title": "Chiếc Điện Thoại Biết Quá Nhiều Về Chúng Ta",
    "slug": "chiec-dien-thoai-biet-qua-nhieu-ve-chung-ta",
    "short_description": "Khóa học đồng hành dành cho phụ huynh và học sinh: thấu hiểu dấu vết số, nhận diện nguy cơ kết bạn trực tuyến, bảo vệ ranh giới cá nhân, xử lý khủng hoảng tống tiền hình ảnh và thiết lập quy ước gia đình an toàn số.",
    "description": (
        "**Đối tượng:** Phụ huynh và học sinh cùng học (thiếu niên và người chăm sóc).\n\n"
        "Khóa học trang bị bộ kỹ năng số toàn diện và thực tế nhất cho cả gia đình trong thời đại số hóa: "
        "từ việc thấu hiểu cơ chế lưu trữ của 'dấu vết kỹ thuật số' (digital footprint) khi một tấm ảnh hay thông tin được đăng tải, "
        "cảnh giác trước những tài khoản ảo và nguy cơ dụ dỗ qua mạng, bảo vệ thông tin đời tư và lịch trình cá nhân, "
        "nắm vững quy trình xử lý khủng hoảng trong 10 phút đầu khi bị đe dọa tống tiền hình ảnh (sextortion), "
        "sử dụng đúng cách các công cụ ngăn chặn phát tán ảnh như Take It Down và kết nối Tổng đài Quốc gia 111, "
        "cho đến việc cả nhà cùng thảo luận xây dựng bản quy ước sử dụng mạng công bằng, tôn trọng và an toàn.\n\n"
        "**Lưu ý an toàn:** Học liệu mang tính giáo dục kỹ năng phòng ngừa. Khi có đe dọa hoặc xâm hại trẻ em tại Việt Nam, "
        "liên hệ ngay Tổng đài Quốc gia Bảo vệ Trẻ em **111** (miễn phí 24/7). "
        "Tuyệt đối không tải về hay chuyển tiếp hình ảnh nhạy cảm của trẻ để tránh phát tán thêm dữ liệu riêng tư."
    ),
    "learning_objectives": (
        "- Nhận thức rõ ràng về dấu vết kỹ thuật số và các rủi ro tiềm ẩn khi chia sẻ hình ảnh, thông tin cá nhân trên mạng xã hội.\n"
        "- Cùng thảo luận và thống nhất nguyên tắc tôn trọng ranh giới: luôn hỏi ý kiến trước khi đăng ảnh của người khác (kể cả cha mẹ đăng ảnh con).\n"
        "- Cảnh giác trước các hồ sơ ảo, lời rủ rê gặp mặt trực tiếp hoặc yêu cầu giữ bí mật độc hại từ người quen qua mạng.\n"
        "- Nắm vững quy trình 3 bước xử lý khẩn cấp trong 10 phút đầu khi bị đe dọa tống tiền hình ảnh: An toàn thân thể -> Từ chối yêu sách -> Lưu chứng cứ & Báo cáo.\n"
        "- Hiểu đúng phạm vi hoạt động của công cụ Take It Down (NCMEC) và cách kết nối kịp thời với Tổng đài Quốc gia Bảo vệ Trẻ em 111.\n"
        "- Cùng nhau thiết lập bản quy ước sử dụng thiết bị và mạng xã hội công bằng, tôn trọng, không đổ lỗi trong gia đình."
    ),
    "thumbnail_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
    "target_audience": "BOTH",
    "is_published": True,
}

LESSONS_DATA = [
    {
        "order_index": 1,
        "title": "Bài 1 — Một tấm ảnh có thể đi xa đến đâu?",
        "video_url": "https://www.youtube.com/watch?v=ottnH427Fr8",
        "duration_minutes": 14,
        "content_type": "HYBRID",
        "content_body": """### 1. Dấu vết số (Digital Footprint)
Video từ Common Sense Education phân tích về hiện tượng chia sẻ quá mức (oversharing) và những gì thực sự xảy ra với dấu vết số của chúng ta. Khi một tấm ảnh được đăng tải, thông tin vị trí, tài khoản, những người được gắn thẻ và bối cảnh xung quanh có thể tiếp tục được người khác chụp lại màn hình, tải về hoặc chuyển tiếp ngoài tầm kiểm soát của người đăng ban đầu. Việc xóa bài đăng không đảm bảo bức ảnh sẽ biến mất hoàn toàn khỏi Internet.

### 2. Nguyên tắc cùng hỏi trước khi đăng
Trước khi nhấn nút chia sẻ bất kỳ tấm ảnh nào, cả phụ huynh và con cái hãy cùng dừng lại vài giây để tự hỏi 3 câu hỏi quan trọng:
1. *Những người xuất hiện trong ảnh đã đồng ý để ảnh được công khai chưa?*
2. *Ảnh có vô tình để lộ tên trường học, địa chỉ nhà, biển số xe hay lịch trình sinh hoạt hàng ngày không?*
3. *Nếu bức ảnh này bị người lạ chia sẻ lại hoặc lưu trữ nhiều năm sau, người trong ảnh sẽ cảm thấy như thế nào?*

### 3. Tôn trọng ranh giới từ cả hai phía
Tôn trọng quyền riêng tư là quy tắc hai chiều: cha mẹ hãy làm gương bằng cách luôn hỏi ý kiến con trước khi đăng ảnh của con lên mạng xã hội; học sinh cũng rèn luyện thói quen xin phép bạn bè trước khi gắn thẻ hay đăng ảnh nhóm. Nếu không may hình ảnh riêng tư bị phát tán hoặc đe dọa, hãy lập tức tìm kiếm sự trợ giúp từ người lớn tin cậy; tuyệt đối không đổ lỗi hay phán xét người xuất hiện trong bức ảnh.

### 4. Bài tập thực hành: Soi chi tiết giảm rủi ro
Cả nhà cùng chọn một bức ảnh phong cảnh hoặc ảnh minh họa giả định (không dùng ảnh người thật), cùng chỉ ra 3 chi tiết có nguy cơ tiết lộ thông tin riêng tư (như biển chỉ đường, góc phố, đồng phục) và đề xuất 1 cách chỉnh sửa (cắt xén hoặc che mờ) để giảm thiểu rủi ro trước khi đăng.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [Common Sense Education — Digital Footprint & Identity](https://www.commonsense.org/education/digital-citizenship/topic/digital-footprint-and-identity)
""",
        "quiz_title": "Củng cố bài 1 — Một tấm ảnh có thể đi xa đến đâu?",
        "quiz_description": "Bài trắc nghiệm 10 câu kiểm tra nhận thức về dấu vết kỹ thuật số, nguyên tắc xin phép trước khi đăng ảnh và bảo vệ thông tin riêng tư.",
        "questions": [
            {
                "question_text": "Dấu vết số là gì?",
                "options": [
                    "Thông tin có thể lưu lại từ hoạt động trên mạng",
                    "Chỉ vết mực trên màn hình",
                    "Chỉ mật khẩu đã quên",
                    "Chỉ lịch sử gọi điện",
                ],
                "correct_index": 0,
                "explanation": "Hoạt động và chia sẻ tạo dấu vết trực tuyến.",
            },
            {
                "question_text": "Trước khi đăng ảnh có bạn bè, nên?",
                "options": [
                    "Đăng rồi hỏi sau",
                    "Hỏi ý những người trong ảnh",
                    "Gắn tên mọi người bắt buộc",
                    "Tự ý chia sẻ cho nhóm lạ",
                ],
                "correct_index": 1,
                "explanation": "Sự đồng ý của người trong ảnh quan trọng.",
            },
            {
                "question_text": "Chi tiết nào dễ lộ địa điểm?",
                "options": [
                    "Một mảng màu nền đơn sắc",
                    "Hình vẽ không chứa chữ",
                    "Tên trường và biển chỉ đường phía sau",
                    "Ảnh nền trống",
                ],
                "correct_index": 2,
                "explanation": "Bối cảnh ảnh có thể tiết lộ thông tin riêng.",
            },
            {
                "question_text": "Xóa bài đăng có bảo đảm ảnh biến mất khỏi mọi nơi?",
                "options": [
                    "Có, tuyệt đối",
                    "Có nếu nhiều lượt thích",
                    "Có nếu ứng dụng thông báo đã xóa",
                    "Không; bản chụp hoặc chuyển tiếp có thể còn",
                ],
                "correct_index": 3,
                "explanation": "Nội dung có thể tồn tại ở nơi khác.",
            },
            {
                "question_text": "Quy tắc đăng ảnh áp dụng cho ai trong gia đình?",
                "options": [
                    "Cả cha mẹ và học sinh",
                    "Chỉ học sinh",
                    "Chỉ cha mẹ",
                    "Chỉ người có mạng xã hội công khai",
                ],
                "correct_index": 0,
                "explanation": "Người lớn cũng tôn trọng ảnh của con.",
            },
            {
                "question_text": "Nếu bạn đề nghị gỡ ảnh có bạn, nên?",
                "options": [
                    "Cười nhạo",
                    "Lắng nghe và gỡ/trao đổi tôn trọng",
                    "Đăng thêm để chứng minh quyền",
                    "Chuyển cho nhóm khác",
                ],
                "correct_index": 1,
                "explanation": "Tôn trọng mong muốn của người xuất hiện.",
            },
            {
                "question_text": "Một ảnh tưởng bình thường có thể tiết lộ gì?",
                "options": [
                    "Chỉ độ phân giải",
                    "Không bao giờ có thông tin",
                    "Lịch trình hay địa điểm qua chi tiết nền",
                    "Luôn là vị trí GPS chính xác",
                ],
                "correct_index": 2,
                "explanation": "Thông tin ngữ cảnh có thể bị suy ra.",
            },
            {
                "question_text": "Lượt xem cao có đồng nghĩa ảnh an toàn?",
                "options": [
                    "Có",
                    "Có nếu tài khoản mới",
                    "Có nếu bạn bè nhấn thích",
                    "Không",
                ],
                "correct_index": 3,
                "explanation": "Độ phổ biến không bảo đảm riêng tư.",
            },
            {
                "question_text": "Khi ảnh riêng tư bị đe dọa phát tán, phản ứng phù hợp?",
                "options": [
                    "Tìm người tin cậy và kênh bảo vệ, không trách người trong ảnh",
                    "Đăng rộng để cảnh báo",
                    "Chuyển ảnh cho mọi bạn bè",
                    "Giữ kín mãi",
                ],
                "correct_index": 0,
                "explanation": "Nạn nhân cần hỗ trợ an toàn.",
            },
            {
                "question_text": "Bài tập chung nên dùng loại ảnh nào?",
                "options": [
                    "Ảnh riêng của bạn trong lớp",
                    "Ảnh giả định không tiết lộ người thật",
                    "Ảnh nhạy cảm của trẻ",
                    "Ảnh định danh người lạ",
                ],
                "correct_index": 1,
                "explanation": "Tình huống giả định bảo vệ riêng tư.",
            },
        ],
    },
    {
        "order_index": 2,
        "title": "Bài 2 — Ai đang ở đầu kia màn hình?",
        "video_url": "https://www.youtube.com/watch?v=Nb1zAY_cc8o",
        "duration_minutes": 14,
        "content_type": "HYBRID",
        "content_body": """### 1. Câu chuyện cảnh giác từ NSTeens
Trong video từ NCMEC NetSmartz, nhân vật Keyan làm quen với một người bạn trên mạng xã hội; người này liên tục thúc giục muốn gặp mặt trực tiếp ngoài đời, khiến bạn bè xung quanh Keyan vô cùng lo lắng. Video chỉ ra những rủi ro khi đặt niềm tin tuyệt đối vào một hồ sơ số và nhấn mạnh vai trò quý giá của những người bạn biết lên tiếng can ngăn, tìm kiếm sự trợ giúp.

### 2. Kiểm chứng cẩn trọng trước khi trao niềm tin
Tên hiển thị, hình ảnh đại diện và những lời giới thiệu ngọt ngào trên mạng hoàn toàn có thể được dàn dựng hoặc giả mạo. Tuyệt đối không gửi thông tin địa chỉ nhà, trường học, số điện thoại hay lịch trình cá nhân cho người mới quen qua mạng. Phụ huynh khi biết con kết bạn trực tuyến cần giữ thái độ bình tĩnh lắng nghe thay vì trách mắng, để con luôn tin tưởng tâm sự.

### 3. Quy tắc ứng phó khi có lời mời gặp mặt
Nếu người quen qua mạng đề nghị gặp mặt riêng:
- **Dừng lại ngay:** Từ chối lời mời gặp riêng tư ở những nơi vắng vẻ.
- **Kể với người lớn tin cậy:** Chia sẻ ngay với cha mẹ hoặc thầy cô giáo để cùng đánh giá mức độ an toàn.
- **Xử lý khi bị ép buộc/đe dọa:** Nếu đối phương có dấu hiệu thao túng, bắt giữ bí mật hoặc đe dọa, hãy lưu lại thông tin tài khoản, chặn liên hệ và báo cáo với nền tảng hoặc cơ quan bảo vệ trẻ em.

### 4. Thảo luận đóng vai trong gia đình
Cha mẹ và con cái cùng thực hành đóng vai: một người đóng vai người bạn chân thành bày tỏ sự lo lắng và khuyên bạn không nên đi gặp người lạ một mình; người kia thực hành cách chủ động mở lời nhờ người lớn tin cậy hỗ trợ.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [NCMEC NetSmartz — Online Enticement & Safety](https://www.ncmec.org/netsmartz/topics/online-enticement)
""",
        "quiz_title": "Củng cố bài 2 — Ai đang ở đầu kia màn hình?",
        "quiz_description": "Bài trắc nghiệm 10 câu về kỹ năng nhận diện hồ sơ giả mạo, phòng tránh nguy cơ dụ dỗ qua mạng và ứng phó an toàn khi có lời rủ gặp.",
        "questions": [
            {
                "question_text": "Trong video, Keyan được ai rủ gặp?",
                "options": [
                    "Một người quen qua mạng",
                    "Giáo viên trong lớp",
                    "Bác sĩ",
                    "Người thân ở nhà",
                ],
                "correct_index": 0,
                "explanation": "Video nói về bạn quen trực tuyến.",
            },
            {
                "question_text": "Tại sao ảnh đại diện không đủ xác minh danh tính?",
                "options": [
                    "Ảnh luôn hiển thị hộ chiếu",
                    "Người dùng có thể dựng hồ sơ không đúng thực tế",
                    "Mọi ảnh đều được kiểm duyệt",
                    "Ảnh chỉ chứa màu sắc",
                ],
                "correct_index": 1,
                "explanation": "Hồ sơ số không bảo đảm ai ở phía sau.",
            },
            {
                "question_text": "Trước lời rủ gặp riêng từ người chỉ quen mạng, nên?",
                "options": [
                    "Đi một mình ngay",
                    "Đưa địa chỉ nhà",
                    "Dừng lại và hỏi người lớn tin cậy",
                    "Giữ bí mật vì đã hứa",
                ],
                "correct_index": 2,
                "explanation": "Đánh giá an toàn với người đáng tin.",
            },
            {
                "question_text": "Vai trò tích cực của bạn bè Keyan?",
                "options": [
                    "Đăng lời rủ rộng rãi",
                    "Thách nhau đi gặp",
                    "Bỏ qua hoàn toàn",
                    "Nhận ra rủi ro và hỗ trợ thay vì chế giễu",
                ],
                "correct_index": 3,
                "explanation": "Bạn bè có thể giúp kết nối người lớn.",
            },
            {
                "question_text": "Khi cha mẹ biết con đã kết bạn trực tuyến, nên?",
                "options": [
                    "Hỏi chuyện bình tĩnh và cùng đánh giá an toàn",
                    "Đổ lỗi ngay",
                    "Công khai mọi tin nhắn",
                    "Cấm mọi cuộc trò chuyện không giải thích",
                ],
                "correct_index": 0,
                "explanation": "Lắng nghe giúp con nói ra tình huống.",
            },
            {
                "question_text": "Thông tin nào không nên đưa cho người chưa xác minh?",
                "options": [
                    "Tên một bộ phim phổ biến",
                    "Địa chỉ và lịch trình",
                    "Ý kiến về một bài hát",
                    "Sở thích đọc sách chung chung",
                ],
                "correct_index": 1,
                "explanation": "Thông tin riêng có thể tăng rủi ro.",
            },
            {
                "question_text": "Nếu đối phương ép giữ bí mật chuyện gặp mặt?",
                "options": [
                    "Là bằng chứng họ thật lòng",
                    "Phải giữ lời bằng mọi giá",
                    "Đây là dấu hiệu cần cảnh giác và kể với người tin cậy",
                    "Không liên quan an toàn",
                ],
                "correct_index": 2,
                "explanation": "Bí mật kèm ép buộc làm tăng rủi ro.",
            },
            {
                "question_text": "Video thuộc chương trình nào?",
                "options": [
                    "Bản tin thời tiết",
                    "Quảng cáo ngân hàng",
                    "Phim điện ảnh hư cấu",
                    "NCMEC NetSmartz",
                ],
                "correct_index": 3,
                "explanation": "NetSmartz phát hành video giáo dục an toàn số.",
            },
            {
                "question_text": "Khi người lạ đe dọa, điều gì hữu ích?",
                "options": [
                    "Ghi tài khoản/lời đe dọa không chia sẻ ảnh nhạy cảm, tìm trợ giúp",
                    "Đáp ứng ngay yêu sách",
                    "Đối chất trực tiếp một mình",
                    "Gửi thêm dữ liệu riêng",
                ],
                "correct_index": 0,
                "explanation": "Tìm trợ giúp và giữ thông tin cần thiết.",
            },
            {
                "question_text": "Bài học không kết luận điều gì?",
                "options": [
                    "Có thể cần xác minh danh tính",
                    "Mọi người quen qua mạng đều chắc chắn gây hại",
                    "Lời rủ gặp riêng cần cân nhắc",
                    "Bạn bè có thể giúp",
                ],
                "correct_index": 1,
                "explanation": "Không suy diễn về mọi mối quan hệ trực tuyến.",
            },
        ],
    },
    {
        "order_index": 3,
        "title": "Bài 3 — Lời rủ rê, bí mật và dấu hiệu cần cảnh giác",
        "video_url": "https://www.youtube.com/watch?v=HxySrSbSY7o",
        "duration_minutes": 14,
        "content_type": "HYBRID",
        "content_body": """### 1. Ba hành động an toàn số từ AMAZE
Video của AMAZE hướng dẫn người học 3 nguyên tắc nền tảng khi tham gia không gian mạng: cẩn trọng trước khi chia sẻ thông tin cá nhân, chủ động báo cáo khi gặp người khiến mình cảm thấy khó chịu/bất an, và nắm vững các thiết lập quyền riêng tư trên ứng dụng. Internet là kho tàng tuyệt vời để học hỏi và khám phá, nhưng cần được đồng hành cùng các kỹ năng phòng vệ thông minh.

### 2. Nhận diện tình huống cần bấm nút "Dừng lại"
Hãy lập tức cảnh giác khi một người (dù là người lạ hay người quen):
- Liên tục hỏi han chi tiết về lịch trình đi lại, trường lớp, địa chỉ nhà hay xin ảnh riêng tư.
- Ép buộc con phải giữ bí mật với cha mẹ, thầy cô hoặc bạn bè.
- Dùng lời nói gây cảm giác sợ hãi, bối rối hoặc thao túng tâm lý.
> **Quy tắc vàng:** Đánh giá dựa trên *hành vi* của đối phương, không phụ thuộc vào việc họ tự xưng là ai hay có quen biết từ trước hay không.

### 3. Tối ưu hóa cài đặt quyền riêng tư
Cùng nhau kiểm tra lại thiết lập bảo mật trên các tài khoản mạng xã hội: ai có thể xem bài đăng, ai được phép gửi tin nhắn trực tiếp, và ứng dụng nào đang truy cập vị trí thời gian thực. Cài đặt riêng tư là tấm lá chắn hữu ích giúp giảm thiểu rủi ro bị tiếp cận không mong muốn.

### 4. Bài tập thực hành: Xây dựng ranh giới số
Sử dụng một hồ sơ mạng xã hội giả định, cha mẹ và con cùng xác định các thông tin cần ẩn khỏi chế độ công khai, luyện tập câu nói dứt khoát để từ chối cuộc trò chuyện khó chịu: *“Mình không muốn tiếp tục cuộc trò chuyện này nữa”*, và lên danh sách những người lớn tin cậy có thể tìm đến hỗ trợ.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [AMAZE Org — Being Safe on the Internet](https://amaze.org/video/being-safe-on-the-internet/)
""",
        "quiz_title": "Củng cố bài 3 — Lời rủ rê, bí mật và dấu hiệu cần cảnh giác",
        "quiz_description": "Bài trắc nghiệm 10 câu về ranh giới cá nhân trực tuyến, cách từ chối lời ép giữ bí mật và sử dụng cài đặt riêng tư bảo vệ bản thân.",
        "questions": [
            {
                "question_text": "AMAZE khuyên gì về thông tin cá nhân?",
                "options": [
                    "Cẩn trọng trước khi chia sẻ",
                    "Đăng toàn bộ địa chỉ",
                    "Gửi lịch học cho tài khoản lạ",
                    "Công khai mật khẩu",
                ],
                "correct_index": 0,
                "explanation": "Video nhấn mạnh bảo vệ thông tin riêng.",
            },
            {
                "question_text": "Nếu ai khiến con không thoải mái qua mạng, nên?",
                "options": [
                    "Luôn im lặng",
                    "Báo người tin cậy hoặc nền tảng phù hợp",
                    "Tiếp tục đáp mọi yêu cầu",
                    "Chỉ trách bản thân",
                ],
                "correct_index": 1,
                "explanation": "Video khuyến khích báo cáo.",
            },
            {
                "question_text": "Cài đặt riêng tư giúp gì?",
                "options": [
                    "Xóa mọi dấu vết đã tồn tại",
                    "Bảo đảm tuyệt đối",
                    "Giới hạn người có thể xem hoặc liên hệ tùy dịch vụ",
                    "Tự thay người lớn hỗ trợ",
                ],
                "correct_index": 2,
                "explanation": "Cài đặt giảm rủi ro trong phạm vi nền tảng.",
            },
            {
                "question_text": "Lời yêu cầu giữ bí mật gây sợ nên xử lý?",
                "options": [
                    "Luôn giữ dù nguy hiểm",
                    "Chuyển cho nhóm lớp",
                    "Đi gặp một mình",
                    "Nói với người lớn tin cậy",
                ],
                "correct_index": 3,
                "explanation": "An toàn quan trọng hơn lời ép giữ kín.",
            },
            {
                "question_text": "Câu nào đánh giá đúng rủi ro?",
                "options": [
                    "Xem hành vi, kể cả khi người nhắn tự nhận là bạn",
                    "Chỉ người lạ mới gây hại",
                    "Người có ảnh thật luôn an toàn",
                    "Bạn học không bao giờ ép buộc",
                ],
                "correct_index": 0,
                "explanation": "Hành vi cần được xem xét.",
            },
            {
                "question_text": "Khi một tài khoản xin lịch học hàng ngày, nên?",
                "options": [
                    "Gửi kèm địa chỉ",
                    "Không gửi lịch riêng và hỏi người lớn tin cậy nếu bối rối",
                    "Công khai trong bình luận",
                    "Đưa số điện thoại cả nhà",
                ],
                "correct_index": 1,
                "explanation": "Lịch trình là thông tin cần bảo vệ.",
            },
            {
                "question_text": "Nếu con lỡ gửi thông tin riêng, cha mẹ nên?",
                "options": [
                    "Sỉ nhục con",
                    "Giả vờ không biết",
                    "Bình tĩnh cùng đổi cài đặt/báo hỗ trợ",
                    "Phát tán tiếp",
                ],
                "correct_index": 2,
                "explanation": "Hỗ trợ thực tế và không đổ lỗi.",
            },
            {
                "question_text": "Video cho rằng Internet thế nào?",
                "options": [
                    "Luôn chỉ có hại",
                    "Tự động an toàn tuyệt đối",
                    "Không cần cài đặt riêng tư",
                    "Hữu ích để khám phá nhưng cần thói quen an toàn",
                ],
                "correct_index": 3,
                "explanation": "Video đặt lợi ích bên cạnh kỹ năng bảo vệ.",
            },
            {
                "question_text": "Một câu dừng liên hệ là?",
                "options": [
                    "“Mình không muốn tiếp tục cuộc trò chuyện này”",
                    "“Mình sẽ gửi thêm ảnh”",
                    "“Đây là địa chỉ nhà”",
                    "“Mình sẽ đi gặp riêng”",
                ],
                "correct_index": 0,
                "explanation": "Có thể từ chối và tìm hỗ trợ.",
            },
            {
                "question_text": "Bài tập chung nên dùng tài khoản nào?",
                "options": [
                    "Bắt trẻ đưa mật khẩu thật",
                    "Tài khoản giả định, không cần lộ tài khoản thật của trẻ",
                    "Đăng ảnh bạn bè",
                    "Đọc toàn bộ chat riêng",
                ],
                "correct_index": 1,
                "explanation": "Thực hành không xâm phạm riêng tư.",
            },
        ],
    },
    {
        "order_index": 4,
        "title": "Bài 4 — Bị đe dọa trên mạng: cùng làm gì trong 10 phút đầu?",
        "video_url": "https://www.youtube.com/watch?v=9Q4pxdUimAU",
        "duration_minutes": 14,
        "content_type": "HYBRID",
        "content_body": """### 1. Hiểu đúng về hành vi tống tiền bằng hình ảnh (Sextortion)
Video từ NCMEC phân tích rõ thủ đoạn của kẻ xấu khi dùng hình ảnh riêng tư để đe dọa, ép buộc nạn nhân chuyển tiền hoặc gửi thêm hình ảnh nhạy cảm khác. Khái niệm *"10 phút đầu"* là khung thời gian thực hành nhằm giúp nạn nhân và gia đình ghi nhớ thứ tự các hành động ưu tiên khẩn cấp, không bị hoảng loạn, chứ không phải lời hứa giải quyết dứt điểm sự việc trong 10 phút.

### 2. Ba hành động ưu tiên sống còn
1. **Bảo đảm an toàn thân thể:** Đưa con về bên cạnh người lớn tin cậy, ngắt kết nối mạng của thiết bị nếu thấy lo sợ.
2. **Tuyệt đối không đáp ứng yêu sách:** Không chuyển tiền, không gửi thêm bất kỳ hình ảnh nào và không đồng ý gặp mặt trực tiếp. Việc đáp ứng yêu sách chỉ khiến kẻ tống tiền tiếp tục đòi hỏi nhiều hơn.
3. **Lưu giữ dấu vết số an toàn:** Chụp ảnh màn hình tin nhắn tống tiền, lưu lại tên tài khoản, đường link (URL) trang cá nhân và mốc thời gian. **Tuyệt đối không** chuyển tiếp hay phát tán thêm hình ảnh nhạy cảm của con.

### 3. Câu nói mở lời giúp giải tỏa áp lực
Phụ huynh cần là chỗ dựa bình tĩnh đầu tiên của con:
> *“Người đang đe dọa con là kẻ làm sai pháp luật. Bố/mẹ sẽ luôn ở bên bảo vệ con và không bao giờ trách phạt con. Hiện tại con có đang an toàn không?”*
Nếu phát hiện dấu hiệu trẻ hoảng loạn tột độ hoặc có ý nghĩ tiêu cực, hãy luôn túc trực bên con và gọi ngay đến **Tổng đài 111** để được hỗ trợ chuyên môn khẩn cấp.

### 4. Bài tập phản xạ: Sắp xếp 3 thẻ hành động
Gia đình cùng thực hành với 3 thẻ ưu tiên: **An toàn thân thể -> Từ chối yêu sách -> Thu thập chứng cứ & Báo cáo**. Luyện tập tình huống con dũng cảm báo tin và cha mẹ phản hồi bằng sự yêu thương, không phán xét.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [NCMEC — The Issues: Sextortion](https://www.ncmec.org/theissues/sextortion)
> - **Tổng đài Quốc gia Bảo vệ Trẻ em 111:** Miễn phí 24/7.
""",
        "quiz_title": "Củng cố bài 4 — Bị đe dọa trên mạng: cùng làm gì trong 10 phút đầu?",
        "quiz_description": "Bài trắc nghiệm 10 câu củng cố quy trình phản ứng khẩn cấp khi bị tống tiền hình ảnh, kỹ năng lưu chứng cứ an toàn và kết nối Tổng đài 111.",
        "questions": [
            {
                "question_text": "“10 phút đầu” trong bài là gì?",
                "options": [
                    "Khung thực hành để nhớ ưu tiên, không phải thời hạn giải quyết",
                    "Cam kết xóa mọi ảnh",
                    "Quy định pháp luật",
                    "Giới hạn liên hệ 111",
                ],
                "correct_index": 0,
                "explanation": "Không thể hứa xử lý hoàn tất trong 10 phút.",
            },
            {
                "question_text": "Khi bị đe dọa đòi tiền, hành động phù hợp?",
                "options": [
                    "Trả nhanh để chắc chắn xong",
                    "Không trả tiền, tìm người tin cậy và báo cáo",
                    "Gửi thêm hình",
                    "Chấp nhận gặp riêng",
                ],
                "correct_index": 1,
                "explanation": "Đáp ứng yêu sách có thể tăng rủi ro.",
            },
            {
                "question_text": "Việc đầu tiên nên kiểm tra?",
                "options": [
                    "Có bao nhiêu lượt xem",
                    "Bạn nào bình luận",
                    "Con có an toàn ngay lúc này không",
                    "Điểm quiz bao nhiêu",
                ],
                "correct_index": 2,
                "explanation": "An toàn của trẻ được ưu tiên.",
            },
            {
                "question_text": "Thông tin nào nên ghi nhận để báo cáo?",
                "options": [
                    "Ảnh nhạy cảm gửi vào nhóm",
                    "Mật khẩu của mọi bạn bè",
                    "Ảnh tải mới từ nơi khác",
                    "Tên tài khoản, đường dẫn, lời đe dọa không chứa ảnh nhạy cảm",
                ],
                "correct_index": 3,
                "explanation": "Giữ thông tin báo cáo mà không lan ảnh.",
            },
            {
                "question_text": "Vai trò bạn bè trong video?",
                "options": [
                    "Nhận dấu hiệu và giúp tìm hỗ trợ",
                    "Chia sẻ ảnh để cảnh báo",
                    "Cười nạn nhân",
                    "Thách người đe dọa",
                ],
                "correct_index": 0,
                "explanation": "Người chứng kiến có thể hỗ trợ.",
            },
            {
                "question_text": "Nếu cha mẹ nổi giận, nên làm gì?",
                "options": [
                    "Trách trẻ ngay",
                    "Tạm điều chỉnh cảm xúc, trấn an và tập trung an toàn",
                    "Công khai câu chuyện",
                    "Nói trẻ tự lo",
                ],
                "correct_index": 1,
                "explanation": "Phản ứng bình tĩnh giữ kênh giúp đỡ.",
            },
            {
                "question_text": "Nếu trẻ có ý nghĩ tự làm hại, cần?",
                "options": [
                    "Chờ hết tuần",
                    "Chỉ đọc thêm quiz",
                    "Ở bên và liên hệ trợ giúp khẩn cấp phù hợp",
                    "Để trẻ một mình",
                ],
                "correct_index": 2,
                "explanation": "Nguy cơ tức thời cần hành động ngay.",
            },
            {
                "question_text": "Có nên gửi ảnh riêng tư trẻ cho người quen làm bằng chứng?",
                "options": [
                    "Có nếu nhiều người",
                    "Có nếu người quen hứa kín",
                    "Có nếu muốn cảnh báo",
                    "Không",
                ],
                "correct_index": 3,
                "explanation": "Không lan truyền ảnh nhạy cảm trẻ.",
            },
            {
                "question_text": "Nếu ở Việt Nam cần tư vấn bảo vệ trẻ, số nào?",
                "options": [
                    "111",
                    "115 chỉ cho mọi tình huống",
                    "Tổng đài nước ngoài",
                    "Số tài khoản mạng xã hội",
                ],
                "correct_index": 0,
                "explanation": "111 là tổng đài quốc gia bảo vệ trẻ em.",
            },
            {
                "question_text": "Câu trấn an phù hợp?",
                "options": [
                    "“Đó là lỗi của con”",
                    "“Người đe dọa làm sai; mình cùng tìm giúp đỡ”",
                    "“Đừng nói với ai”",
                    "“Hãy gửi thêm ảnh”",
                ],
                "correct_index": 1,
                "explanation": "Không đổ lỗi giúp trẻ tìm hỗ trợ.",
            },
        ],
    },
    {
        "order_index": 5,
        "title": "Bài 5 — Báo cáo, chặn và tìm hỗ trợ: ảnh không phải món nợ",
        "video_url": "https://www.youtube.com/watch?v=pAaXbBzVdJE",
        "duration_minutes": 14,
        "content_type": "HYBRID",
        "content_body": """### 1. Giới thiệu công cụ Take It Down
Video từ NCMEC giới thiệu dịch vụ miễn phí Take It Down — nền tảng hỗ trợ ngăn chặn và gỡ bỏ việc lan truyền các hình ảnh, video nhạy cảm được tạo ra khi người trong ảnh dưới 18 tuổi. Công cụ này hoạt động bằng cách tạo ra một "mã băm" (vân tay kỹ thuật số độc nhất) ngay trên thiết bị của người dùng mà không cần tải hay gửi bức ảnh gốc lên máy chủ; mã băm này sau đó được chia sẻ tới các nền tảng công nghệ lớn tham gia liên minh để tự động quét và chặn nội dung tương ứng.

### 2. Nguyên tắc vàng: Tuyệt đối không gửi hay tải thêm ảnh
- Người dùng **không bao giờ** được tải thêm ảnh về máy, chuyển tiếp cho người khác hoặc đăng lên mạng để "nhờ gỡ hộ".
- Nếu thiết bị không còn lưu file gốc, hãy đọc kỹ phần FAQ của dịch vụ hoặc tìm kiếm sự hướng dẫn từ các cơ quan bảo vệ pháp lý chính thống.
- Cần hiểu rõ: Take It Down là công cụ kỹ thuật hỗ trợ đắc lực trên các nền tảng tham gia, nhưng không thể đảm bảo xóa sạch 100% mọi tệp lưu trữ ngoại tuyến trên toàn thế giới.

### 3. Quy trình báo cáo và liên hệ tại Việt Nam
- **Báo cáo vi phạm trên mạng xã hội:** Sử dụng tính năng báo cáo (Report) hành vi quấy rối / tống tiền trực tiếp trên nền tảng nơi vụ việc xảy ra.
- **Chặn liên lạc:** Sau khi đã chụp màn hình lưu giữ thông tin tài khoản và bằng chứng đe dọa, lập tức chặn tài khoản kẻ xấu.
- **Đầu mối can thiệp trong nước:** NCMEC là tổ chức có trụ sở tại Hoa Kỳ; do đó tại Việt Nam, đầu mối hỗ trợ pháp lý và bảo vệ trẻ em chính thức là **Tổng đài Quốc gia 111** (miễn phí 24/7). Hãy gọi ngay để nhận được sự đồng hành từ chuyên gia bảo vệ quyền trẻ em.

### 4. Bài tập thực hành: Thiết lập thẻ hỗ trợ khẩn cấp
Cả nhà cùng lập một tấm thẻ danh bạ an toàn: ghi rõ tên và số điện thoại của người lớn tin cậy, liên kết báo cáo của các ứng dụng con hay dùng, hotline **Tổng đài 111** và trang chủ công cụ Take It Down.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [Take It Down (NCMEC) — Hướng dẫn bằng tiếng Việt](https://takeitdown.ncmec.org/vi/)
> - **Tổng đài Quốc gia Bảo vệ Trẻ em 111:** Kênh can thiệp và hỗ trợ pháp lý miễn phí tại Việt Nam.
""",
        "quiz_title": "Củng cố bài 5 — Báo cáo, chặn và tìm hỗ trợ: ảnh không phải món nợ",
        "quiz_description": "Bài trắc nghiệm 10 câu về cách vận hành của Take It Down, nguyên tắc không lan truyền ảnh nhạy cảm và quy trình báo cáo bảo vệ trẻ.",
        "questions": [
            {
                "question_text": "Take It Down dùng cho nội dung được chụp khi nào?",
                "options": [
                    "Khi người trong ảnh dưới 18 tuổi",
                    "Chỉ sau tuổi 18",
                    "Chỉ trong lớp học",
                    "Chỉ ảnh phong cảnh",
                ],
                "correct_index": 0,
                "explanation": "Phạm vi tuổi tính theo thời điểm tạo nội dung.",
            },
            {
                "question_text": "Cần gửi ảnh nhạy cảm lên dịch vụ không?",
                "options": [
                    "Có, gửi cho bất kỳ ai",
                    "Không; công cụ tạo dấu vân tay số trên thiết bị",
                    "Có, đăng công khai trước",
                    "Có, chuyển nhóm bạn",
                ],
                "correct_index": 1,
                "explanation": "Không chia sẻ ảnh để dùng công cụ.",
            },
            {
                "question_text": "Take It Down có xóa mọi bản sao khắp Internet?",
                "options": [
                    "Có tuyệt đối",
                    "Có cả tệp ngoại tuyến của mọi người",
                    "Không bảo đảm; phụ thuộc nền tảng tham gia và điều kiện",
                    "Có ngay trong một phút",
                ],
                "correct_index": 2,
                "explanation": "Dịch vụ có phạm vi kỹ thuật.",
            },
            {
                "question_text": "Nếu không có ảnh gốc trên thiết bị, nên?",
                "options": [
                    "Tải ảnh từ nơi khác về ngay",
                    "Xin bạn bè chuyển ảnh",
                    "Đăng ảnh công khai",
                    "Đọc FAQ và tìm kênh hỗ trợ chính thức, không tải thêm ảnh",
                ],
                "correct_index": 3,
                "explanation": "FAQ lưu ý không tải nội dung chỉ để nộp.",
            },
            {
                "question_text": "Số hỗ trợ bảo vệ trẻ tại Việt Nam?",
                "options": [
                    "111",
                    "Một số ngẫu nhiên trên mạng",
                    "Chỉ đường dây của Mỹ",
                    "Số của người đe dọa",
                ],
                "correct_index": 0,
                "explanation": "111 là kênh trong nước.",
            },
            {
                "question_text": "Báo nội dung vi phạm trên nền tảng nhằm?",
                "options": [
                    "Bảo đảm mọi nơi gỡ tức thì",
                    "Yêu cầu xem xét và gỡ/chặn theo cơ chế nền tảng",
                    "Thay toàn bộ trợ giúp",
                    "Tăng lượt xem nội dung",
                ],
                "correct_index": 1,
                "explanation": "Báo cáo là một kênh xử lý.",
            },
            {
                "question_text": "Trước khi chặn tài khoản đe dọa, có thể làm gì?",
                "options": [
                    "Đưa mật khẩu cho họ",
                    "Gửi thêm ảnh",
                    "Ghi nhận tên tài khoản/đường dẫn và lời đe dọa an toàn",
                    "Xóa mọi thông tin để quên",
                ],
                "correct_index": 2,
                "explanation": "Thông tin liên hệ giúp báo cáo.",
            },
            {
                "question_text": "NCMEC có phải cơ quan bảo vệ trẻ em của Việt Nam?",
                "options": [
                    "Có",
                    "Là trường học Việt Nam",
                    "Là nền tảng mạng xã hội Việt Nam",
                    "Không; NCMEC là tổ chức tại Mỹ",
                ],
                "correct_index": 3,
                "explanation": "Phân biệt công cụ quốc tế và đầu mối trong nước.",
            },
            {
                "question_text": "Khi bị đe dọa hình ảnh, người trong ảnh có “mắc nợ” người đe dọa?",
                "options": [
                    "Không",
                    "Có, phải trả tiền",
                    "Có, phải gửi thêm ảnh",
                    "Có, phải gặp riêng",
                ],
                "correct_index": 0,
                "explanation": "Đe dọa là hành vi sai.",
            },
            {
                "question_text": "Thẻ hỗ trợ gia đình nên chứa gì?",
                "options": [
                    "Ảnh thật của trẻ",
                    "Người lớn tin cậy, báo nền tảng, 111 và công cụ phù hợp",
                    "Mật khẩu công khai",
                    "Danh sách người để đổ lỗi",
                ],
                "correct_index": 1,
                "explanation": "Thẻ hỗ trợ tập trung đường tìm trợ giúp.",
            },
        ],
    },
    {
        "order_index": 6,
        "title": "Bài 6 — Quy ước dùng mạng mà cả nhà cùng giữ",
        "video_url": None,
        "duration_minutes": 17,
        "content_type": "TEXT",
        "content_body": """### 1. Cùng xây dựng quy ước thay vì áp đặt một chiều
Dựa trên các nghiên cứu về nuôi dạy con trong kỷ nguyên số của UNICEF và Child Mind Institute, việc cha mẹ cùng con cái ngồi lại thảo luận và thống nhất các quy tắc dùng thiết bị sẽ mang lại hiệu quả bền vững hơn rất nhiều so với những mệnh lệnh cấm đoán cứng nhắc. Khi được tôn trọng và tham gia vào quá trình xây dựng quy ước, học sinh sẽ có ý thức trách nhiệm và sự tự giác cao hơn.

### 2. Bốn nguyên tắc cốt lõi cả nhà cùng áp dụng
1. **Tôn trọng hình ảnh của nhau:** Luôn xin phép trước khi chụp hoặc đăng ảnh của người khác lên mạng; cha mẹ cũng xin ý kiến con trước khi chia sẻ ảnh con lên trang cá nhân.
2. **Bảo vệ dữ liệu đời tư:** Tuyệt đối không công khai địa chỉ nhà, trường lớp, lịch trình di chuyển chi tiết hay mật khẩu tài khoản trên các nền tảng trực tuyến.
3. **Kích hoạt quy trình ứng phó khi gặp nguy cơ:** Khi gặp tin nhắn quấy rối, ép buộc hay đe dọa: lập tức dừng tương tác, tâm sự với người lớn tin cậy và báo cáo nền tảng; gọi **Tổng đài 111** nếu cần hỗ trợ can thiệp.
4. **Cập nhật thỏa thuận định kỳ:** Đặt lịch xem lại quy ước mỗi 6 tháng một lần để điều chỉnh phù hợp với sự phát triển và độ tuổi của con.

### 3. Thiết lập lối thoát an toàn và giới hạn giám sát
Quy ước cần khẳng định rõ: con có quyền tìm kiếm sự giúp đỡ từ cha mẹ mà không lo sợ bị mắng mỏ hay tước đoạt thiết bị. Phụ huynh giải thích rõ ràng và minh bạch về các biện pháp an toàn kỹ thuật thay vì âm thầm đọc lén tin nhắn; chỉ can thiệp đặc biệt khi phát hiện nguy cơ đe dọa đến sức khỏe, tâm lý hay an toàn thân thể của con.

### 4. Lời khuyên đồng hành và nguồn tài liệu tham khảo cho gia đình
- **Người lớn làm gương:** Sự đồng thuận trong gia đình bắt đầu từ việc cha mẹ cũng tuân thủ quy tắc số (không lướt điện thoại trong bữa cơm, tôn trọng không gian riêng của con).
- **Kiên nhẫn và cởi mở:** Khi con gặp rắc rối trên mạng, thái độ đón nhận bình tĩnh của cha mẹ sẽ quyết định việc con có tiếp tục mở lòng trong tương lai hay không.
- **Đồng hành dài hạn:** An toàn số không phải là bài học một lần duy nhất, mà là quá trình rèn luyện thói quen và tư duy phản biện liên tục cùng con lớn lên.

> [!TIP]
> **Nguồn tài liệu tham khảo chuyên môn:**
> - [UNICEF — Giữ an toàn cho trẻ trên không gian mạng](https://www.unicef.org/parenting/child-care/keep-your-child-safe-online)
> - [Child Mind Institute — Hướng dẫn sử dụng công nghệ lành mạnh trong gia đình](https://childmind.org/positiveparenting/healthy-technology-use/)
> - [Common Sense Education — Dấu vết kỹ thuật số và danh tính trực tuyến](https://www.commonsense.org/education/digital-citizenship/topic/digital-footprint-and-identity)
> - **Tổng đài Quốc gia Bảo vệ Trẻ em 111:** Hỗ trợ tư vấn an toàn số và bảo vệ trẻ em 24/7.
""",
        "quiz_title": "Củng cố bài 6 — Quy ước dùng mạng mà cả nhà cùng giữ",
        "quiz_description": "Bài trắc nghiệm 10 câu về cách thiết lập thỏa thuận an toàn số gia đình, tôn trọng quyền riêng tư và tạo kênh kết nối tin cậy.",
        "questions": [
            {
                "question_text": "Ai nên tham gia viết quy ước dùng mạng?",
                "options": [
                    "Phụ huynh và học sinh cùng trao đổi",
                    "Chỉ người lớn",
                    "Chỉ giáo viên",
                    "Chỉ ứng dụng",
                ],
                "correct_index": 0,
                "explanation": "Cùng xây quy ước tăng hiểu và thực hiện.",
            },
            {
                "question_text": "Trước khi cha mẹ đăng ảnh con, nên?",
                "options": [
                    "Đăng ngay vì là cha mẹ",
                    "Hỏi ý con phù hợp tuổi",
                    "Gắn địa chỉ nhà",
                    "Bỏ qua cảm giác của con",
                ],
                "correct_index": 1,
                "explanation": "Người lớn làm gương tôn trọng riêng tư.",
            },
            {
                "question_text": "Quy ước nên nêu gì khi bị đe dọa?",
                "options": [
                    "Trẻ phải giấu kín",
                    "Chỉ trả tiền",
                    "Cách báo người tin cậy và tìm hỗ trợ không bị đổ lỗi",
                    "Tự xử hoàn toàn",
                ],
                "correct_index": 2,
                "explanation": "Đường xin giúp là phần cốt lõi.",
            },
            {
                "question_text": "Quy ước có cần thay đổi khi con lớn?",
                "options": [
                    "Không bao giờ",
                    "Chỉ khi điện thoại hỏng",
                    "Chỉ nếu đạt 100% quiz",
                    "Có thể cùng rà soát định kỳ",
                ],
                "correct_index": 3,
                "explanation": "Khả năng tự quản thay đổi theo tuổi.",
            },
            {
                "question_text": "Thông tin nào không nên công khai?",
                "options": [
                    "Địa chỉ, lịch trình và mật khẩu",
                    "Một sở thích chung chung",
                    "Tên bài hát yêu thích",
                    "Ý kiến về phim",
                ],
                "correct_index": 0,
                "explanation": "Thông tin riêng giúp hạn chế rủi ro.",
            },
            {
                "question_text": "Gia đình nên phản hồi khi con báo bị ép?",
                "options": [
                    "Trách con trước",
                    "Cảm ơn con đã nói, kiểm tra an toàn và tìm trợ giúp",
                    "Đăng tin lên nhóm",
                    "Cấm con nhắc chuyện",
                ],
                "correct_index": 1,
                "explanation": "Không đổ lỗi giúp giữ kênh báo nguy.",
            },
            {
                "question_text": "Ngoại lệ an toàn tức thời cần?",
                "options": [
                    "Chỉ sửa hình nền",
                    "Chờ tới tháng sau",
                    "Hành động bảo vệ ngay, không chờ buổi rà soát định kỳ",
                    "Hoàn thành quiz trước",
                ],
                "correct_index": 2,
                "explanation": "Nguy cơ trực tiếp ưu tiên xử lý.",
            },
            {
                "question_text": "Giám sát thiết bị nên thế nào?",
                "options": [
                    "Âm thầm đọc hết mặc định",
                    "Không bao giờ thảo luận",
                    "Dùng để phạt mọi câu hỏi",
                    "Giải thích phạm vi và lý do, tôn trọng riêng tư phù hợp tuổi",
                ],
                "correct_index": 3,
                "explanation": "Minh bạch hỗ trợ lòng tin.",
            },
            {
                "question_text": "Quy tắc xin phép đăng ảnh áp dụng cho ai?",
                "options": [
                    "Mọi người trong nhà",
                    "Chỉ học sinh",
                    "Chỉ người không có điện thoại",
                    "Chỉ người ngoài nhà",
                ],
                "correct_index": 0,
                "explanation": "Trách nhiệm chia sẻ ảnh là chung.",
            },
            {
                "question_text": "Quiz bài NotebookLM khi nào sẵn sàng đăng?",
                "options": [
                    "Ngay khi có tiêu đề",
                    "Sau khi đối chiếu video đã tạo và chỉnh chỗ lệch",
                    "Khi đủ 10 câu bất kể nội dung",
                    "Khi chưa xem nguồn",
                ],
                "correct_index": 1,
                "explanation": "Cần bảo đảm video và quiz đồng bộ.",
            },
        ],
    },
]

async def seed_course_8():
    async with AsyncSessionLocal() as session:
        print("Starting seed for Course 8: Chiếc Điện Thoại Biết Quá Nhiều Về Chúng Ta...")

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
        print(f"Created Course 8: {course.title} (ID: {course_id})")

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
        print("SEEDING COURSE 8 COMPLETED SUCCESSFULLY!")
        print(f"Course: {COURSE_DATA['title']}")
        print(f"Target Audience: {COURSE_DATA['target_audience']}")
        print(f"Lessons: {len(LESSONS_DATA)}")
        print(f"Quizzes: {len(LESSONS_DATA)}")
        print(f"Total Questions: {total_questions}")
        print(f"Total Options: {total_options}")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(seed_course_8())
