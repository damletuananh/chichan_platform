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
    "title": "Tuổi Teen Đóng Cửa Phòng: Cha Mẹ Mở Cửa Đối Thoại",
    "slug": "tuoi-teen-dong-cua-phong-cha-me-mo-cua-doi-thoai",
    "short_description": "Khóa học đồng hành cùng phụ huynh có con tuổi teen: thấu hiểu nhu cầu riêng tư, đối thoại cởi mở về tình cảm, sức khỏe tâm thần và an toàn trên không gian mạng.",
    "description": (
        "**Đối tượng:** Phụ huynh có con trong độ tuổi thiếu niên (tuổi teen).\n\n"
        "Bước vào tuổi dậy thì và vị thành niên, con thường có xu hướng khép kín, cần không gian riêng và ít tâm sự hơn với cha mẹ. "
        "Khóa học cung cấp cho cha mẹ các kỹ năng tâm lý thực chứng để chuyển hóa khoảng cách thành cơ hội kết nối: cách tôn trọng sự riêng tư mà không lơ là an toàn, "
        "nghệ thuật gợi mở khi con biết rung động hoặc hẹn hò, đặt ranh giới về tình dục an toàn không dựa trên sự đe dọa, cách xử lý khủng hoảng khi gặp tin nhắn sốc, "
        "nhận diện sớm các dấu hiệu khó khăn sức khỏe tâm thần và hướng dẫn con ứng phó với nội dung người lớn trên Internet.\n\n"
        "**Cấu trúc khóa học:** Gồm 6 bài học kèm video chuyên môn từ Child Mind Institute và Planned Parenthood, tài liệu đối chiếu quốc tế và 6 bài tập trắc nghiệm củng cố (đạt 8/10 trở lên)."
    ),
    "learning_objectives": (
        "- Phân biệt giữa nhu cầu tự chủ tự nhiên của tuổi teen và các dấu hiệu nguy cơ cần can thiệp bảo vệ.\n"
        "- Trò chuyện và lắng nghe cởi mở khi con có tình cảm với ai đó mà không phán xét hay áp đặt định kiến giới.\n"
        "- Đặt ra kỳ vọng và thảo luận về việc trì hoãn quan hệ tình dục dựa trên lòng tự trọng, không dùng nỗi sợ hãi.\n"
        "- Làm chủ cảm xúc và chọn cách phản ứng đầu tiên an toàn, thấu cảm khi con tiết lộ tin nhắn hoặc tình huống sốc.\n"
        "- Nhận biết sớm các rối loạn sức khỏe tâm thần tuổi dậy thì và biết thời điểm cần kết nối chuyên gia y tế.\n"
        "- Hướng dẫn kỹ năng an toàn số, giải mã các thông tin sai lệch từ nội dung khiêu dâm và bảo vệ quyền riêng tư hình ảnh."
    ),
    "thumbnail_url": "https://images.unsplash.com/photo-1516627145497-ae6968895b74?auto=format&fit=crop&w=1200&q=80",
    "target_audience": "PARENT",
    "is_published": True,
}

LESSONS_DATA = [
    {
        "order_index": 1,
        "title": "Bài 1 — Riêng tư không có nghĩa là hết quan tâm",
        "video_url": "https://www.youtube.com/watch?v=rw5flq67fJI",
        "duration_minutes": 14,
        "content_type": "HYBRID",
        "content_body": """### 1. Tuổi teen cần không gian
Con muốn tự quyết nhiều hơn và có lúc ít kể chuyện hơn. Điều đó không tự động chứng tỏ con gặp nguy hiểm. Cha mẹ giữ liên hệ bằng hoạt động chung, những câu hỏi mở và thỏa thuận ranh giới riêng tư.

### 2. Quan sát mà không rình mò
Thay câu *“Cho bố mẹ xem hết tin nhắn”* bằng *“Nếu có chuyện làm con thấy không an toàn, mình sẽ cùng xử lý”*. Thống nhất trước các trường hợp bắt buộc phải can thiệp: bị đe dọa, ép buộc, xâm hại hoặc nguy cơ tổn hại bản thân.

### 3. Mở lời
Thử nói: *“Bố mẹ tôn trọng thời gian riêng của con. Tối nay mình cùng ăn cơm nhé; nếu cần nói chuyện, bố mẹ luôn sẵn sàng.”*

> [!NOTE]
> **Nguồn trọng tâm:** Child Mind Institute: *How do I help my child through the challenges they face in the teen years?*  
> **Tài liệu đối chiếu:** [https://childmind.org/positiveparenting/teen-challenges/](https://childmind.org/positiveparenting/teen-challenges/)
""",
        "quiz_title": "Củng cố bài 1 — Riêng tư không có nghĩa là hết quan tâm",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Con muốn ở riêng nhiều hơn; diễn giải phù hợp?",
                "options": [
                    "Đó có thể là một phần nhu cầu tự chủ tuổi teen",
                    "Con chắc chắn giấu chuyện nguy hiểm",
                    "Cha mẹ phải kiểm tra mọi tin nhắn",
                    "Con không còn cần người lớn"
                ],
                "correct_index": 0,
                "explanation": "Không nên tự suy đoán chỉ từ việc muốn riêng tư."
            },
            {
                "question_text": "Cách giữ kết nối ít xâm phạm?",
                "options": [
                    "Đọc lén toàn bộ hội thoại",
                    "Duy trì hoạt động chung và cơ hội nói chuyện",
                    "Hỏi cung sau mỗi buổi học",
                    "Cấm con đóng cửa mọi lúc"
                ],
                "correct_index": 1,
                "explanation": "Sinh hoạt chung cho phép con mở lời khi sẵn sàng."
            },
            {
                "question_text": "Khi đặt quy tắc riêng tư, nên làm gì?",
                "options": [
                    "Đưa ra quy tắc bí mật không báo con",
                    "Để mọi tình huống tùy cảm xúc cha mẹ",
                    "Thống nhất trước các ngoại lệ liên quan an toàn",
                    "Nói riêng tư là đặc quyền vô nghĩa"
                ],
                "correct_index": 2,
                "explanation": "Quy tắc minh bạch giúp hiểu khi nào cần can thiệp."
            },
            {
                "question_text": "Dấu hiệu nào cần hỏi thăm kỹ hơn?",
                "options": [
                    "Con muốn nghe nhạc một mình",
                    "Con xin một giờ học yên tĩnh",
                    "Con thích mặc màu khác",
                    "Thay đổi rõ và kéo dài về sinh hoạt hoặc khả năng hoạt động"
                ],
                "correct_index": 3,
                "explanation": "Sự thay đổi ảnh hưởng sinh hoạt đáng được lắng nghe."
            },
            {
                "question_text": "Cha mẹ nên nói gì khi con muốn ở một mình?",
                "options": [
                    "“Bố mẹ tôn trọng, và luôn sẵn nếu con muốn nói”",
                    "“Con làm bố mẹ thất vọng”",
                    "“Bố mẹ sẽ kiểm tra điện thoại ngay”",
                    "“Từ nay không cần nói gì nữa”"
                ],
                "correct_index": 0,
                "explanation": "Thừa nhận nhu cầu riêng tư đồng thời giữ kênh hỗ trợ."
            },
            {
                "question_text": "Trường hợp nào cần ưu tiên an toàn?",
                "options": [
                    "Con đổi hình nền máy",
                    "Con báo bị đe dọa hoặc ép buộc",
                    "Con thích đọc sách riêng",
                    "Con muốn đi bộ với bạn"
                ],
                "correct_index": 1,
                "explanation": "Đe dọa và ép buộc cần can thiệp phù hợp."
            },
            {
                "question_text": "Theo video, mục tiêu của cha mẹ trong tuổi teen?",
                "options": [
                    "Quản lý từng suy nghĩ của con",
                    "Ngăn mọi sự tự chủ",
                    "Giữ đường giao tiếp trong giai đoạn chuyển đổi",
                    "Thuyết trình mỗi tối"
                ],
                "correct_index": 2,
                "explanation": "Nguồn nhấn mạnh giữ liên lạc trong giai đoạn biến đổi."
            },
            {
                "question_text": "Nếu con chưa muốn kể, bước tiếp theo?",
                "options": [
                    "Ép con giải thích ngay",
                    "Công khai chuyện trước cả nhà",
                    "Kết luận con nói dối",
                    "Tôn trọng và hẹn cơ hội trò chuyện khác"
                ],
                "correct_index": 3,
                "explanation": "Giữ cơ hội nói sau sẽ bớt áp lực."
            },
            {
                "question_text": "Quyền riêng tư đi cùng điều gì?",
                "options": [
                    "Kênh báo nguy cơ và sự hỗ trợ của người lớn",
                    "Cam kết không cần ai giúp",
                    "Quyền giấu mọi hành vi gây hại",
                    "Cấm cha mẹ quan tâm"
                ],
                "correct_index": 0,
                "explanation": "Tôn trọng riêng tư không cản trở hỗ trợ an toàn."
            },
            {
                "question_text": "Câu hỏi mở nào phù hợp?",
                "options": [
                    "“Con đã phạm lỗi gì?”",
                    "“Có điều gì dạo này khiến con thấy khó xử không?”",
                    "“Đưa máy đây ngay”",
                    "“Con có đồng ý là bố mẹ luôn đúng?”"
                ],
                "correct_index": 1,
                "explanation": "Lời hỏi mở mời con chia sẻ theo nhịp của mình."
            }
        ]
    },
    {
        "order_index": 2,
        "title": "Bài 2 — Con đang thích ai đó: hỏi sao để con còn muốn kể?",
        "video_url": "https://www.youtube.com/watch?v=7MGvGhacwjo",
        "duration_minutes": 14,
        "content_type": "HYBRID",
        "content_body": """### 1. Từ tình bạn đến rung động
Video lấy nền từ các mối quan hệ lành mạnh: cách người lớn làm gương, nghe và nói luân phiên, tạo cảm giác an toàn. Áp dụng vào chuyện con thích một người mà không mặc định giới tính của người ấy.

### 2. Hỏi về chất lượng quan hệ
Hỏi con: *“Con thấy được tôn trọng khi ở cạnh người đó không?”*; *“Nếu hai người bất đồng, các con xử lý ra sao?”*. Tránh bêu tên, đoán xu hướng tính dục hoặc ép con khai danh tính người mình thích.

### 3. Làm gương
Trong gia đình, xin lỗi khi sai, lắng nghe, tôn trọng lời từ chối. Cho con thấy sự quan tâm chân thành không đồng nghĩa với kiểm soát áp đặt.

### 4. Thực hành
*“Nếu con muốn kể, bố mẹ sẽ luôn lắng nghe. Điều quan trọng nhất với bố mẹ là con được đối xử tử tế và an toàn.”*

> [!NOTE]
> **Nguồn trọng tâm:** Planned Parenthood: *How Do I Talk With My Kid About Healthy Relationships?*  
> **Tài liệu đối chiếu:** [https://www.plannedparenthood.org/learn/parents/relationships](https://www.plannedparenthood.org/learn/parents/relationships)
""",
        "quiz_title": "Củng cố bài 2 — Con đang thích ai đó: hỏi sao để con còn muốn kể?",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Khi con nói đang thích ai, câu phản hồi nên là?",
                "options": [
                    "“Con thấy mối quan hệ này khiến con cảm thấy thế nào?”",
                    "“Đó là ai, cho xem tin nhắn ngay”",
                    "“Con chưa được có cảm xúc đó”",
                    "“Chỉ được thích người theo ý bố mẹ”"
                ],
                "correct_index": 0,
                "explanation": "Hỏi cảm nhận giữ không gian nói chuyện."
            },
            {
                "question_text": "Một quan hệ lành mạnh cần điều gì?",
                "options": [
                    "Một người quyết định tất cả",
                    "Tôn trọng và lắng nghe lẫn nhau",
                    "Cấm giữ bạn bè riêng",
                    "Kiểm tra điện thoại liên tục"
                ],
                "correct_index": 1,
                "explanation": "Nguồn nhấn mạnh lắng nghe và quan hệ tôn trọng."
            },
            {
                "question_text": "Cha mẹ nên làm gương bằng cách nào?",
                "options": [
                    "Yêu cầu mọi người im lặng",
                    "Đùa cợt cảm xúc của con",
                    "Xin lỗi khi sai và tôn trọng ranh giới người khác",
                    "Kiểm soát bạn của con"
                ],
                "correct_index": 2,
                "explanation": "Hành vi của người lớn là mẫu giao tiếp cho trẻ."
            },
            {
                "question_text": "Nên tránh giả định nào?",
                "options": [
                    "Con có thể kể hoặc chưa kể",
                    "Quan hệ cần tôn trọng",
                    "Trẻ có quyền hỏi",
                    "Người con thích nhất định phải thuộc một giới cụ thể"
                ],
                "correct_index": 3,
                "explanation": "Không gán giới cho người con thích."
            },
            {
                "question_text": "Câu hỏi nào giúp đánh giá quan hệ?",
                "options": [
                    "“Khi bất đồng, các con có nghe nhau không?”",
                    "“Ai nhiều điểm hơn?”",
                    "“Con phải nói tên ngay”",
                    "“Con định giấu bố mẹ à?”"
                ],
                "correct_index": 0,
                "explanation": "Cách giải quyết bất đồng phản ánh sự tôn trọng."
            },
            {
                "question_text": "Nếu con không kể tên, cha mẹ nên?",
                "options": [
                    "Công khai tra hỏi trước bạn bè",
                    "Không ép, tiếp tục nói về an toàn và tôn trọng",
                    "Đọc trộm toàn bộ điện thoại",
                    "Kết luận con hư"
                ],
                "correct_index": 1,
                "explanation": "Có thể hỗ trợ mà không đòi con tiết lộ mọi thông tin."
            },
            {
                "question_text": "Lắng nghe và nói luân phiên nghĩa là?",
                "options": [
                    "Ngắt lời để sửa từng câu",
                    "Chỉ cha mẹ được nói",
                    "Cho con thời gian diễn đạt rồi phản hồi",
                    "Không ai được đặt câu hỏi"
                ],
                "correct_index": 2,
                "explanation": "Video khuyến khích trao đổi hai chiều."
            },
            {
                "question_text": "Khi con đau buồn vì tình cảm, phản hồi đầu tiên?",
                "options": [
                    "Nói chuyện đó không đáng",
                    "Chê người con thích",
                    "Buộc con quên ngay",
                    "Công nhận cảm giác và lắng nghe"
                ],
                "correct_index": 3,
                "explanation": "Được lắng nghe giúp con tiếp tục tìm hỗ trợ."
            },
            {
                "question_text": "Sự quan tâm của cha mẹ khác kiểm soát ở điểm nào?",
                "options": [
                    "Quan tâm hỏi và hỗ trợ, tôn trọng ranh giới",
                    "Quan tâm cho phép đọc lén mọi thứ",
                    "Quan tâm bắt con đồng ý",
                    "Quan tâm cấm con có bạn"
                ],
                "correct_index": 0,
                "explanation": "Quan hệ tin cậy cần ranh giới."
            },
            {
                "question_text": "Điều nào quan trọng hơn đoán danh tính người con thích?",
                "options": [
                    "Người ấy học lớp nào",
                    "Con có an toàn và được tôn trọng không",
                    "Người ấy có bao nhiêu người theo dõi",
                    "Con có kể cho hàng xóm không"
                ],
                "correct_index": 1,
                "explanation": "Tập trung vào chất lượng quan hệ."
            }
        ]
    },
    {
        "order_index": 3,
        "title": "Bài 3 — Đặt giới hạn mà không dùng nỗi sợ",
        "video_url": "https://www.youtube.com/watch?v=lyeR7_mfdQ4",
        "duration_minutes": 14,
        "content_type": "HYBRID",
        "content_body": """### 1. Kỳ vọng đi kèm lý do
Video hướng dẫn cha mẹ nêu mong đợi về việc trì hoãn quan hệ tình dục, cùng con suy nghĩ mục tiêu tương lai, lòng tự trọng và khả năng quyết định. Có thể nêu giá trị gia đình rõ ràng mà không dọa nạt hoặc sỉ nhục.

### 2. Ranh giới và quyền quyết định
Con có quyền từ chối tình huống chưa sẵn sàng, kể cả khi đang hẹn hò. Hỏi con cách ứng phó với áp lực từ bạn hay người yêu; luyện câu phản xạ: *“Mình chưa sẵn sàng”*.

### 3. Cung cấp thông tin an toàn
Dù cha mẹ mong con chờ, vẫn cho con biết nơi tiếp cận thông tin sức khỏe sinh sản đáng tin, bao cao su và tránh thai khi phù hợp tuổi và nhu cầu; không coi thông tin là sự khuyến khích quan hệ.

### 4. Thực hành
*“Bố mẹ mong con đợi đến khi con thực sự sẵn sàng. Con nghĩ áp lực từ người khác có thể xuất hiện khi nào và muốn bố mẹ hỗ trợ ra sao?”*

> [!NOTE]
> **Nguồn trọng tâm:** Planned Parenthood: *Helping Your Teenager Wait To Have Sex*  
> **Tài liệu đối chiếu:** [https://www.plannedparenthood.org/learn/parents/high-school/what-should-i-teach-my-high-school-aged-teen-about-sex-and-sexua](https://www.plannedparenthood.org/learn/parents/high-school/what-should-i-teach-my-high-school-aged-teen-about-sex-and-sexua)
""",
        "quiz_title": "Củng cố bài 3 — Đặt giới hạn mà không dùng nỗi sợ",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video tập trung vào mục tiêu nào?",
                "options": [
                    "Giúp cha mẹ trò chuyện về trì hoãn quan hệ khi teen chưa sẵn sàng",
                    "Dạy cha mẹ dùng nỗi sợ",
                    "Cấm nói về sức khỏe",
                    "Ép con khai hết đời tư"
                ],
                "correct_index": 0,
                "explanation": "Nguồn nêu việc hỗ trợ teen chờ đến khi sẵn sàng."
            },
            {
                "question_text": "Cách nêu kỳ vọng phù hợp?",
                "options": [
                    "Dọa đuổi khỏi nhà",
                    "Giải thích giá trị và lý do, mời con suy nghĩ",
                    "Chỉ trích giá trị bản thân",
                    "Không lắng nghe phản hồi"
                ],
                "correct_index": 1,
                "explanation": "Lý do rõ ràng hỗ trợ quyết định."
            },
            {
                "question_text": "Khi con chịu áp lực từ người yêu, kỹ năng nào hữu ích?",
                "options": [
                    "Luôn đồng ý để giữ quan hệ",
                    "Giấu mọi lo lắng",
                    "Nói không và tìm hỗ trợ nếu cần",
                    "Để người khác quyết thay"
                ],
                "correct_index": 2,
                "explanation": "Quyền từ chối là nền tảng ranh giới."
            },
            {
                "question_text": "Trao đổi mục tiêu tương lai giúp gì?",
                "options": [
                    "Buộc con theo duy nhất một nghề",
                    "Thay thế thông tin sức khỏe",
                    "Loại bỏ mọi rủi ro",
                    "Đặt lựa chọn hiện tại vào điều con coi trọng"
                ],
                "correct_index": 3,
                "explanation": "Video hướng đến mục tiêu và sự tự tin của teen."
            },
            {
                "question_text": "Nếu cha mẹ mong con trì hoãn, có nên giấu thông tin bảo vệ sức khỏe?",
                "options": [
                    "Không; vẫn cung cấp nguồn đáng tin phù hợp",
                    "Có, vì biết là chắc chắn quan hệ",
                    "Có, vì thông tin luôn gây hại",
                    "Chỉ nói nếu trẻ đạt điểm cao"
                ],
                "correct_index": 0,
                "explanation": "Giữ kênh thông tin an toàn giúp teen tìm trợ giúp."
            },
            {
                "question_text": "Ai có quyền từ chối quan hệ khi chưa sẵn sàng?",
                "options": [
                    "Chỉ người lớn",
                    "Mọi người, bất kể giới",
                    "Chỉ một giới",
                    "Chỉ khi không hẹn hò"
                ],
                "correct_index": 1,
                "explanation": "Ranh giới áp dụng cho tất cả."
            },
            {
                "question_text": "Lời nói nào tăng tự tin khi đặt ranh giới?",
                "options": [
                    "“Mình phải đồng ý vì đã hẹn hò”",
                    "“Mình không được đổi ý”",
                    "“Mình chưa sẵn sàng và muốn dừng lại”",
                    "“Sợ mất bạn nên im lặng”"
                ],
                "correct_index": 2,
                "explanation": "Có thể nói rõ giới hạn và dừng."
            },
            {
                "question_text": "Cha mẹ nên tránh điều gì?",
                "options": [
                    "Trò chuyện về giá trị",
                    "Lắng nghe mục tiêu con",
                    "Giới thiệu nguồn y tế",
                    "Sỉ nhục hoặc lấy nỗi sợ làm cách thuyết phục"
                ],
                "correct_index": 3,
                "explanation": "Xấu hổ hóa làm khó việc tìm hỗ trợ."
            },
            {
                "question_text": "Nếu con không đồng ý kỳ vọng của cha mẹ?",
                "options": [
                    "Giữ trao đổi mở về sự sẵn sàng, an toàn và trách nhiệm",
                    "Đóng kênh liên lạc",
                    "Đe dọa ngay",
                    "Khẳng định con không còn được giúp"
                ],
                "correct_index": 0,
                "explanation": "Bất đồng không loại bỏ nghĩa vụ hỗ trợ."
            },
            {
                "question_text": "Quan hệ tình cảm đồng nghĩa phải quan hệ tình dục?",
                "options": [
                    "Có, luôn luôn",
                    "Không; mỗi người quyết định theo sự sẵn sàng của mình",
                    "Có, nếu đã lâu",
                    "Có, nếu đối phương yêu cầu"
                ],
                "correct_index": 1,
                "explanation": "Hẹn hò không tạo nghĩa vụ quan hệ."
            }
        ]
    },
    {
        "order_index": 4,
        "title": "Bài 4 — Một tin nhắn gây sốc: phản ứng đầu tiên quyết định điều gì?",
        "video_url": "https://www.youtube.com/watch?v=c7V08Q02ucg",
        "duration_minutes": 14,
        "content_type": "HYBRID",
        "content_body": """### 1. Dùng cơ hội đời thường
Video dùng một bài hát về mối quan hệ không lành mạnh làm điểm mở. Cha mẹ lắng nghe, tôn trọng teen như người đang trưởng thành, công nhận sự khó nói và hỏi con nghĩ gì.

### 2. Khi con tiết lộ chuyện nhạy cảm
Trước tiên điều chỉnh cảm xúc, cảm ơn con đã nói, hỏi con có đang an toàn không và con muốn được giúp điều gì. Không hứa giữ bí mật tuyệt đối nếu có nguy cơ xâm hại hay tổn hại.

### 3. Sửa phản ứng nếu lỡ nóng giận
Thành thật chia sẻ: *“Bố mẹ đã phản ứng quá mạnh. Xin lỗi con. Bây giờ bố mẹ muốn nghe và cùng con tìm cách an toàn.”* Nếu nguy cơ cấp bách, liên hệ dịch vụ khẩn cấp tại nơi ở.

### 4. Thực hành
Xem cảnh nhân vật bị kiểm soát: *“Bố mẹ thấy điều đó đáng lo; con thấy mối quan hệ trong cảnh phim này thế nào?”*

> [!NOTE]
> **Nguồn trọng tâm:** Planned Parenthood: *Talking About Sex and Relationships More Comfortably*  
> **Tài liệu đối chiếu:** [https://www.plannedparenthood.org/learn/parents/tips-talking](https://www.plannedparenthood.org/learn/parents/tips-talking)
""",
        "quiz_title": "Củng cố bài 4 — Một tin nhắn gây sốc: phản ứng đầu tiên quyết định điều gì?",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video gợi ý dùng điều gì để mở chuyện?",
                "options": [
                    "Bài hát, phim hoặc tình huống hằng ngày",
                    "Chỉ giấy kiểm tra",
                    "Tin đồn hàng xóm",
                    "Tra hỏi giữa lớp"
                ],
                "correct_index": 0,
                "explanation": "Tình huống đời thường là điểm mở."
            },
            {
                "question_text": "Khi con kể chuyện khó, phản ứng đầu?",
                "options": [
                    "La mắng ngay",
                    "Lắng nghe bình tĩnh và hỏi con có an toàn không",
                    "Công khai câu chuyện",
                    "Phủ nhận cảm xúc"
                ],
                "correct_index": 1,
                "explanation": "Bình tĩnh giữ kênh trợ giúp."
            },
            {
                "question_text": "Vì sao không nên hứa giữ bí mật tuyệt đối?",
                "options": [
                    "Vì cha mẹ luôn phải kể cho mọi người",
                    "Vì câu hỏi của con không quan trọng",
                    "Có thể cần tìm trợ giúp khi con gặp nguy hiểm",
                    "Vì con không có riêng tư"
                ],
                "correct_index": 2,
                "explanation": "An toàn đôi khi đòi hỏi chia sẻ với người hỗ trợ phù hợp."
            },
            {
                "question_text": "Lời nào thừa nhận sự khó nói?",
                "options": [
                    "“Con hỏi kỳ cục quá”",
                    "“Im đi”",
                    "“Bố mẹ luôn biết mọi chuyện”",
                    "“Chuyện này có thể ngượng; bố mẹ cũng thấy vậy, mình nói từng chút nhé”"
                ],
                "correct_index": 3,
                "explanation": "Video khuyến khích công nhận sự không thoải mái."
            },
            {
                "question_text": "Nếu lỡ nổi nóng, nên làm gì?",
                "options": [
                    "Nhận lỗi, xin lỗi và quay lại lắng nghe",
                    "Bảo con quên đi",
                    "Đổ lỗi cho con",
                    "Ngừng liên lạc"
                ],
                "correct_index": 0,
                "explanation": "Sửa cách phản ứng giúp nối lại đối thoại."
            },
            {
                "question_text": "Video nhấn mạnh hành động nào ngoài nói?",
                "options": [
                    "Chỉ đưa mệnh lệnh",
                    "Nghe và hiểu góc nhìn của teen",
                    "Giữ mọi câu hỏi cho riêng mình",
                    "Không nhắc quan hệ"
                ],
                "correct_index": 1,
                "explanation": "Lắng nghe là lời khuyên trực tiếp của video."
            },
            {
                "question_text": "Một câu hỏi mở về cảnh phim kiểm soát?",
                "options": [
                    "“Con có làm y như thế không, thú nhận đi”",
                    "“Con không được xem phim”",
                    "“Con nghĩ nhân vật có được tôn trọng không?”",
                    "“Ai sai, trả lời ngay”"
                ],
                "correct_index": 2,
                "explanation": "Nói về nhân vật bớt ép con tự tiết lộ."
            },
            {
                "question_text": "Nếu con nói đang bị ép buộc, nên ưu tiên gì?",
                "options": [
                    "Chỉ xét điểm số",
                    "Buộc con im lặng",
                    "Hỏi vì sao con làm sai",
                    "An toàn hiện tại và hỗ trợ chuyên môn phù hợp"
                ],
                "correct_index": 3,
                "explanation": "Nguy cơ ép buộc cần hỗ trợ bảo vệ."
            },
            {
                "question_text": "Cách đối xử với teen được video khuyên?",
                "options": [
                    "Tôn trọng như người đang trưởng thành",
                    "Chế giễu cảm xúc",
                    "Giả định con luôn nói dối",
                    "Cấm mọi bất đồng"
                ],
                "correct_index": 0,
                "explanation": "Video yêu cầu tôn trọng góc nhìn của teen."
            },
            {
                "question_text": "Sau câu trả lời đầu, cha mẹ nên?",
                "options": [
                    "Đóng cửa trò chuyện",
                    "Cho con biết có thể tiếp tục nói vào lúc khác",
                    "Đòi con kể toàn bộ ngay",
                    "Kể chuyện con cho cả nhà"
                ],
                "correct_index": 1,
                "explanation": "Đối thoại có thể diễn ra qua nhiều lần."
            }
        ]
    },
    {
        "order_index": 5,
        "title": "Bài 5 — Khi nào cha mẹ cần tìm chuyên gia cùng con?",
        "video_url": "https://www.youtube.com/watch?v=3Irkf1HGr6g",
        "duration_minutes": 14,
        "content_type": "HYBRID",
        "content_body": """### 1. Nhận ra thay đổi cần quan tâm
Video hướng dẫn quan sát dấu hiệu con có thể đang gặp khó khăn sức khỏe tinh thần; khó khăn này có thể điều trị và cần được xem nghiêm túc. Chú ý thay đổi kéo dài hoặc rõ rệt về tâm trạng, giấc ngủ, ăn uống, học tập, quan hệ và khả năng sinh hoạt.

### 2. Hỏi và kết nối
Hỏi con đang trải qua điều gì mà không tự chẩn đoán. Khi lo lắng, liên hệ chuyên gia sức khỏe tâm thần hoặc bác sĩ có chuyên môn về trẻ vị thành niên để được đánh giá; phối hợp với con theo mức phù hợp.

### 3. Tình huống cần trợ giúp ngay
Nếu con nói muốn tự làm hại bản thân, đang gặp bạo lực hoặc có nguy cơ tức thời, ở bên con và liên hệ cấp cứu hoặc dịch vụ bảo vệ phù hợp nơi cư trú ngay; không chờ quiz hay một buổi tư vấn thông thường.

### 4. Thực hành
*“Bố mẹ thấy gần đây con khó ngủ và bỏ nhiều hoạt động con thích. Bố mẹ quan tâm và muốn cùng con gặp người có chuyên môn để hiểu chuyện gì đang xảy ra.”*

> [!NOTE]
> **Nguồn trọng tâm:** Child Mind Institute: *How do I recognize signs and help my child struggling with mental health problems?*  
> **Tài liệu đối chiếu:** [https://childmind.org/positiveparenting/mental-health-problems/](https://childmind.org/positiveparenting/mental-health-problems/)
""",
        "quiz_title": "Củng cố bài 5 — Khi nào cha mẹ cần tìm chuyên gia cùng con?",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Video tập trung vào điều gì?",
                "options": [
                    "Nhận biết khó khăn tinh thần và cách hỗ trợ trẻ",
                    "Chẩn đoán qua quiz",
                    "Cách giấu triệu chứng",
                    "Quy tắc chấm điểm học"
                ],
                "correct_index": 0,
                "explanation": "Nguồn nói về dấu hiệu và hỗ trợ."
            },
            {
                "question_text": "Thay đổi nào đáng trao đổi với con?",
                "options": [
                    "Đổi một bài hát yêu thích",
                    "Tâm trạng và sinh hoạt thay đổi rõ, kéo dài",
                    "Thử một món ăn mới",
                    "Ngủ muộn một hôm"
                ],
                "correct_index": 1,
                "explanation": "Quan sát mẫu thay đổi có ảnh hưởng chức năng."
            },
            {
                "question_text": "Cha mẹ có thể tự chẩn đoán từ một biểu hiện không?",
                "options": [
                    "Có, chỉ cần xem một video",
                    "Có, từ một điểm quiz",
                    "Không; cần người có chuyên môn đánh giá khi lo lắng",
                    "Có, từ ý kiến bạn bè"
                ],
                "correct_index": 2,
                "explanation": "Video học tập không thay khám chuyên môn."
            },
            {
                "question_text": "Nếu con nói muốn tự làm hại bản thân?",
                "options": [
                    "Hẹn tháng sau hỏi lại",
                    "Bảo con đừng nghĩ nữa",
                    "Để con ở một mình",
                    "Ở bên con, tìm trợ giúp khẩn cấp tại địa phương"
                ],
                "correct_index": 3,
                "explanation": "Nguy cơ tức thời cần hỗ trợ ngay."
            },
            {
                "question_text": "Câu mở lời không phán xét?",
                "options": [
                    "“Bố mẹ thấy con đang khó khăn, con muốn kể điều gì không?”",
                    "“Con yếu đuối quá”",
                    "“Đây chỉ là làm quá”",
                    "“Con không có quyền buồn”"
                ],
                "correct_index": 0,
                "explanation": "Quan tâm cụ thể tạo điều kiện chia sẻ."
            },
            {
                "question_text": "Chuyên gia phù hợp là ai?",
                "options": [
                    "Bất kỳ tài khoản ẩn danh",
                    "Nhân viên y tế hoặc chuyên gia sức khỏe tâm thần đủ chuyên môn",
                    "Chỉ người chấm quiz",
                    "Người bán sản phẩm không rõ nguồn"
                ],
                "correct_index": 1,
                "explanation": "Cần đánh giá chuyên môn."
            },
            {
                "question_text": "Khó khăn tinh thần được nguồn mô tả thế nào?",
                "options": [
                    "Luôn do cha mẹ gây ra",
                    "Không đáng quan tâm",
                    "Có thật, thường gặp và có thể điều trị",
                    "Không thể cải thiện"
                ],
                "correct_index": 2,
                "explanation": "Nguồn khuyến khích nhận diện và hỗ trợ."
            },
            {
                "question_text": "Mục đích quan sát giấc ngủ, năng lượng, học tập?",
                "options": [
                    "Giám sát từng phút",
                    "Để công khai với hàng xóm",
                    "Để suy đoán danh tính của con",
                    "Nhận ra thay đổi để hỏi và hỗ trợ"
                ],
                "correct_index": 3,
                "explanation": "Quan sát phục vụ hỗ trợ, không bêu riếu."
            },
            {
                "question_text": "Nếu con lo sợ gặp chuyên gia, cha mẹ nên?",
                "options": [
                    "Giải thích mục đích, nghe băn khoăn và cùng tìm cách tiếp cận",
                    "Ép con im lặng",
                    "Trêu chọc con",
                    "Hứa chuyên gia sẽ không hỏi gì"
                ],
                "correct_index": 0,
                "explanation": "Hợp tác có thể giảm lo lắng."
            },
            {
                "question_text": "Quiz khóa học thay thế tư vấn được không?",
                "options": [
                    "Có, luôn luôn",
                    "Không; khi có dấu hiệu lo ngại, cần hỗ trợ phù hợp",
                    "Có nếu đạt 80%",
                    "Có nếu cha mẹ xem video"
                ],
                "correct_index": 1,
                "explanation": "Quiz là công cụ học tập, không chẩn đoán."
            }
        ]
    },
    {
        "order_index": 6,
        "title": "Bài 6 — Khi con gặp nội dung người lớn trên mạng: mở lời thế nào?",
        "video_url": None,
        "duration_minutes": 16,
        "content_type": "TEXT",
        "content_body": """### 1. Bình tĩnh trước nội dung nhạy cảm
Trẻ có thể vô tình thấy hoặc chủ động tìm nội dung tình dục. Mở chuyện không phán xét: *“Con có thấy nội dung nào làm con bối rối hoặc không thoải mái không?”*. Không suy đoán hành vi, bản dạng hay trải nghiệm của con.

### 2. Thông điệp cốt lõi
Nội dung khiêu dâm dành cho người lớn, thường không thể hiện thực tế đầy đủ về cơ thể, mối quan hệ, sự đồng thuận và an toàn. Phân biệt hình ảnh dàn dựng và thông tin giáo dục sức khỏe đáng tin cậy.

### 3. An toàn số
- Thỏa thuận cách thoát trang web lạ, chặn và báo cáo nội dung xấu độc.
- Tuyệt đối không chuyển tiếp hình ảnh riêng tư của người khác.
- Tìm người lớn tin cậy nếu bị ép gửi hoặc nhận hình ảnh nhạy cảm.
- Khi có dấu hiệu bóc lột hay đe dọa tống tiền/hình ảnh, ưu tiên bảo vệ con và tìm sự can thiệp từ cơ quan bảo vệ trẻ em ngay lập tức.

### 4. Lời khuyên đối thoại tích cực dành cho cha mẹ
- **Không quy chụp hay xấu hổ hóa:** Khi phát hiện con tiếp xúc với nội dung người lớn, phản ứng bình tĩnh và tìm hiểu xem con có cảm thấy bối rối hay bất an không sẽ hiệu quả hơn nhiều so với việc trừng phạt hay chỉ trích gay gắt.
- **Giải thích rõ tính dàn dựng của phim ảnh:** Giúp con hiểu rằng nội dung khiêu dâm là sản phẩm giải trí được phóng đại và dàn dựng, hoàn toàn khác biệt với các mối quan hệ tình cảm đời thực vốn cần sự tôn trọng, đồng thuận và an toàn.
- **Trang bị kỹ năng an toàn số:** Hướng dẫn con cách chủ động thoát khỏi trang web xấu, báo cáo nội dung độc hại và tuyệt đối không bao giờ chia sẻ hình ảnh riêng tư của mình hay của bạn bè.

> [!TIP]
> **Nguồn tài liệu tham khảo chuyên môn:**
> - [AMAZE #AskableParent — Hướng dẫn trao đổi về nội dung người lớn](https://amaze.org/parents/guides/porn/)
> - [Planned Parenthood — Những điều cần chia sẻ với học sinh trung học về tình dục](https://www.plannedparenthood.org/learn/parents/middle-school/what-should-i-teach-my-middle-schooler-about-sex-and-sex)
""",
        "quiz_title": "Củng cố bài 6 — Khi con gặp nội dung người lớn trên mạng: mở lời thế nào?",
        "quiz_description": "Bài tập kiểm tra 10 câu trắc nghiệm. Đạt từ 80% (8/10 câu đúng) để hoàn thành bài học.",
        "questions": [
            {
                "question_text": "Nếu con thấy nội dung tình dục trên mạng, phản ứng đầu?",
                "options": [
                    "Bình tĩnh hỏi con có thấy bối rối hay không an toàn không",
                    "Bêu con trước gia đình",
                    "Tự kết luận con đã quan hệ",
                    "Cắt mọi liên lạc"
                ],
                "correct_index": 0,
                "explanation": "Bình tĩnh giúp con nói về điều đã thấy."
            },
            {
                "question_text": "Nội dung khiêu dâm thay giáo dục giới tính được không?",
                "options": [
                    "Có, luôn luôn",
                    "Không; cần nguồn giáo dục sức khỏe đáng tin",
                    "Có nếu nhiều lượt xem",
                    "Có nếu con tự tìm"
                ],
                "correct_index": 1,
                "explanation": "Nguồn phân biệt giải trí người lớn với giáo dục."
            },
            {
                "question_text": "Khi con gặp hình ảnh riêng tư bị yêu cầu chuyển tiếp?",
                "options": [
                    "Chuyển tiếp cho bạn bè",
                    "Giữ kín dù bị đe dọa",
                    "Không chuyển tiếp; nói với người lớn tin cậy và tìm trợ giúp",
                    "Đăng lại để hỏi cộng đồng"
                ],
                "correct_index": 2,
                "explanation": "Không phát tán hình ảnh và ưu tiên trợ giúp."
            },
            {
                "question_text": "Câu mở không phán xét?",
                "options": [
                    "“Con hư vì dùng mạng”",
                    "“Đưa hết mật khẩu ngay”",
                    "“Con không được hỏi”",
                    "“Nếu có nội dung làm con khó chịu, mình có thể nói chuyện”"
                ],
                "correct_index": 3,
                "explanation": "Lời mời tạo đường hỗ trợ."
            },
            {
                "question_text": "Video cần nhấn mạnh thiếu sót nào của porn?",
                "options": [
                    "Có thể không phản ánh đúng sự đồng thuận và mối quan hệ thực",
                    "Luôn là giáo trình y khoa",
                    "Luôn là hình mẫu quan hệ",
                    "Đủ để hiểu tránh thai"
                ],
                "correct_index": 0,
                "explanation": "Nội dung dựng không thay thông tin sức khỏe."
            },
            {
                "question_text": "Khi bị ép gửi hình ảnh, bước ưu tiên?",
                "options": [
                    "Gửi ngay để khỏi mất lòng",
                    "Không làm theo, tìm người lớn tin cậy và hỗ trợ an toàn",
                    "Giữ hoàn toàn một mình",
                    "Tự đổ lỗi"
                ],
                "correct_index": 1,
                "explanation": "Ép buộc cần hỗ trợ bảo vệ."
            },
            {
                "question_text": "Khi muốn xử lý trang không phù hợp, nên?",
                "options": [
                    "Tự động chia sẻ rộng",
                    "Xem tiếp để chứng minh bản lĩnh",
                    "Thoát, chặn hoặc báo cáo và trò chuyện về an toàn số",
                    "Xóa mọi quy tắc an toàn"
                ],
                "correct_index": 2,
                "explanation": "Các thao tác an toàn giảm phơi nhiễm và tạo đường hỗ trợ."
            },
            {
                "question_text": "Cha mẹ nên tránh giả định nào?",
                "options": [
                    "Con có thể lo lắng",
                    "Con cần nguồn đáng tin",
                    "An toàn số cần đối thoại",
                    "Trẻ thấy nội dung nghĩa là trẻ đã có trải nghiệm tình dục"
                ],
                "correct_index": 3,
                "explanation": "Không suy diễn trải nghiệm cá nhân từ lịch sử xem."
            },
            {
                "question_text": "Trước khi xuất bản bài NotebookLM, cần làm gì?",
                "options": [
                    "Đối chiếu từng quiz với video thực tế",
                    "Chỉ kiểm tra tiêu đề",
                    "Bỏ qua nguồn",
                    "Xuất bản dù video thiếu nội dung"
                ],
                "correct_index": 0,
                "explanation": "Quiz phải khớp nội dung video cuối cùng."
            },
            {
                "question_text": "Khi nào cần tìm hỗ trợ ngay?",
                "options": [
                    "Khi con hỏi một câu bình thường",
                    "Khi có ép buộc, đe dọa hoặc dấu hiệu bóc lột",
                    "Khi con xem phim học đường",
                    "Khi con muốn biết nguồn giáo dục"
                ],
                "correct_index": 1,
                "explanation": "Tình huống nguy cơ cần bảo vệ kịp thời."
            }
        ]
    }
]

async def seed_course_5():
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
        print(f"Created Course 5: {course.title} (ID: {course_id})")

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
        print("SEEDING COURSE 5 COMPLETED SUCCESSFULLY!")
        print(f"Course: {COURSE_DATA['title']}")
        print(f"Target Audience: {COURSE_DATA['target_audience']}")
        print(f"Lessons: {len(LESSONS_DATA)}")
        print(f"Quizzes: {len(LESSONS_DATA)}")
        print(f"Total Questions: {total_questions}")
        print(f"Total Options: {total_options}")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(seed_course_5())
