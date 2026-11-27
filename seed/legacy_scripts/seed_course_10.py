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
    "title": "Đừng Để Lời Đồn Quyết Định Sức Khỏe Của Bạn",
    "slug": "dung-de-loi-don-quyet-dinh-suc-khoe-cua-ban",
    "short_description": "Khóa học giáo dục sức khỏe giới tính khoa học dành cho học sinh 15–18 tuổi: phân biệt sự thật và lời đồn về các bệnh lây truyền qua đường tình dục (STI), hiểu đúng về xét nghiệm, các biện pháp chắn bảo vệ, tránh thai và xử lý sự cố an toàn.",
    "description": (
        "**Đối tượng:** Học sinh THPT (15–18 tuổi) thuộc mọi giới tính.\n\n"
        "Khóa học trang bị kiến thức y khoa nền tảng, chính xác và cởi mở giúp người học tự tin bảo vệ sức khỏe sinh sản và tình dục của bản thân, không để những lời đồn thổi vô căn cứ hay tâm lý e ngại định đoạt sức khỏe:\n"
        "- Hiểu rõ bản chất của các nhiễm trùng lây truyền qua đường tình dục (STI), các con đường lây truyền thực tế và sự thật về những ca nhiễm không hề có biểu hiện hay triệu chứng ra bên ngoài.\n"
        "- Tầm quan trọng của xét nghiệm STI định kỳ và đúng thời điểm (thời kỳ cửa sổ), cách trao đổi cởi mở với nhân viên y tế thay vì tự chẩn đoán qua mạng hay hỏi người không có chuyên môn.\n"
        "- Phân biệt rành mạch giữa hai mục tiêu sức khỏe hoàn toàn khác nhau: phòng tránh mang thai ngoài ý muốn và phòng chống lây nhiễm STI.\n"
        "- Kỹ năng sử dụng đúng cách các biện pháp chắn: bao cao su ngoài và bao cao su trong (internal condom), các nguyên tắc an toàn về ma sát và việc tuyệt đối không dùng lồng hai bao cùng lúc.\n"
        "- Các phương án xử trí sự cố khẩn cấp (như rách hoặc tuột bao cao su) kịp thời, hành động sớm và tìm kiếm sự hỗ trợ y tế chuyên môn tin cậy tại địa phương.\n\n"
        "**Lưu ý an toàn & y tế:** Nội dung khóa học mang tính chất giáo dục nâng cao nhận thức sức khỏe cộng đồng, không thay thế cho việc thăm khám, xét nghiệm hay chẩn đoán và điều trị y khoa trực tiếp từ các bác sĩ chuyên khoa. "
        "Khi có lo ngại về phơi nhiễm hay nguy cơ sức khỏe, hãy liên hệ ngay với cơ sở y tế địa phương uy tín."
    ),
    "learning_objectives": (
        "- Hiểu đúng định nghĩa STI và nhận biết các con đường lây truyền có thể xảy ra (âm đạo, hậu môn, miệng, tiếp xúc da vùng sinh dục).\n"
        "- Nhận thức rõ ràng rằng người nhiễm STI có thể không có triệu chứng bề ngoài; từ đó nhận biết vai trò then chốt của xét nghiệm y khoa.\n"
        "- Nắm vững quy trình và lưu ý quan trọng khi sử dụng bao cao su ngoài như một biện pháp chắn bảo vệ kép (ngừa thai và giảm nguy cơ STI).\n"
        "- Phân biệt rõ sự khác nhau giữa các phương pháp tránh thai nội tiết/vật lý và việc phòng ngừa STI (không đánh đồng hai mục tiêu).\n"
        "- Biết cách hành động sớm, bình tĩnh khi gặp sự cố quan hệ không an toàn và hiểu đúng về các phương án tránh thai khẩn cấp.\n"
        "- Nắm bắt kiến thức về bao cao su trong (internal condom), cách sử dụng theo cấu tạo giải phẫu và nguyên tắc an toàn không dùng chồng hai bao."
    ),
    "thumbnail_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1200&q=80",
    "target_audience": "CHILD",
    "is_published": True,
}

LESSONS_DATA = [
    {
        "order_index": 1,
        "title": "Bài 1 — Lời đồn im lặng, STI vẫn có thể lây",
        "video_url": "https://www.youtube.com/watch?v=PBb-EKA8xFo",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Bản chất của nhiễm trùng lây truyền qua đường tình dục (STI)
Nhiễm trùng lây truyền qua đường tình dục (Sexually Transmitted Infections - STI) là các bệnh nhiễm do vi khuẩn, virus hoặc ký sinh trùng gây ra, có khả năng lây truyền qua các hoạt động tình dục:
- Quan hệ tình dục qua đường âm đạo.
- Quan hệ tình dục qua đường hậu môn.
- Quan hệ tình dục qua đường miệng (tùy thuộc vào tác nhân vi sinh).
- Tiếp xúc trực tiếp giữa da với da ở vùng sinh dục (đối với một số tác nhân như HPV hay Herpes).

### 2. Sự thật: Không có triệu chứng không đồng nghĩa với không có nguy cơ
Một trong những lời đồn nguy hiểm nhất là: *“Người trông khỏe mạnh, sạch sẽ thì chắc chắn không mắc bệnh”*.
- Rất nhiều loại STI trong giai đoạn đầu hoặc suốt thời gian dài **không hề gây ra biểu hiện rõ ràng** (không đau rát, không sốt, không nổi mụn).
- Bằng mắt thường, không ai có thể xác định được một người có đang mang mầm bệnh STI hay không. Do đó, việc phán đoán tình trạng sức khỏe qua vẻ ngoài là hoàn toàn sai lầm.

### 3. Biện pháp chắn và sự bảo vệ cần thiết
- **Biện pháp chắn vật lý:** Sử dụng bao cao su đúng cách và đều đặn mỗi lần quan hệ giúp giảm thiểu đáng kể nguy cơ lây truyền nhiều loại STI phổ biến.
- **Xét nghiệm y khoa:** Là phương thức khoa học duy nhất để xác định chính xác tình trạng sức khỏe sinh dục của một người.

### 4. Ứng xử văn minh và không kỳ thị
Người mắc STI xứng đáng nhận được sự chăm sóc y tế chu đáo, điều trị khoa học và sự thấu hiểu từ cộng đồng, không phải sự phán xét hay kỳ thị. Nếu bạn có băn khoăn về sức khỏe của mình, hãy chủ động tìm gặp nhân viên y tế để được tư vấn xét nghiệm bảo mật.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [Planned Parenthood — What Are STDs and How Are They Transmitted?](https://www.plannedparenthood.org/learn/stds-hiv-safer-sex/get-tested)
""",
        "quiz_title": "Củng cố bài 1 — Lời đồn im lặng, STI vẫn có thể lây",
        "quiz_description": "Bài trắc nghiệm 10 câu giúp củng cố kiến thức nền tảng về khái niệm STI, các con đường lây truyền và nhận thức không đánh giá qua vẻ ngoài.",
        "questions": [
            {
                "question_text": "STI là gì?",
                "options": [
                    "Nhiễm trùng có thể lây qua hoạt động tình dục",
                    "Một kiểu tính cách",
                    "Bệnh chỉ xuất hiện ở người lớn tuổi",
                    "Một hình thức tránh thai",
                ],
                "correct_index": 0,
                "explanation": "Nhiễm trùng có thể lây qua hoạt động tình dục. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Người không có triệu chứng có thể có STI không?",
                "options": [
                    "Không bao giờ",
                    "Có, nhiều STI không gây triệu chứng rõ",
                    "Chỉ nếu bị sốt",
                    "Chỉ khi da đổi màu",
                ],
                "correct_index": 1,
                "explanation": "Có, nhiều STI không gây triệu chứng rõ. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Con đường nào có thể làm lây STI?",
                "options": [
                    "Ngồi cạnh bạn học",
                    "Dùng chung bút",
                    "Quan hệ tình dục đường miệng tùy tác nhân",
                    "Bắt tay thông thường",
                ],
                "correct_index": 2,
                "explanation": "Quan hệ tình dục đường miệng tùy tác nhân. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Có thể xác định STI chỉ bằng vẻ ngoài không?",
                "options": [
                    "Có, luôn nhìn thấy được",
                    "Có, nhìn màu tóc",
                    "Có, hỏi bạn bè là đủ",
                    "Không, cần xét nghiệm và tư vấn phù hợp",
                ],
                "correct_index": 3,
                "explanation": "Không, cần xét nghiệm và tư vấn phù hợp. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Biện pháp chắn như bao cao su có tác dụng nào?",
                "options": [
                    "Giảm nguy cơ lây một số STI khi dùng đúng",
                    "Loại bỏ mọi nguy cơ tuyệt đối",
                    "Thay xét nghiệm",
                    "Chữa khỏi STI",
                ],
                "correct_index": 0,
                "explanation": "Giảm nguy cơ lây một số STI khi dùng đúng. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "STI có thể lây qua tiếp xúc da vùng sinh dục không?",
                "options": [
                    "Không với bất kỳ tác nhân nào",
                    "Có, với một số tác nhân",
                    "Chỉ qua hắt hơi",
                    "Chỉ qua thức ăn",
                ],
                "correct_index": 1,
                "explanation": "Có, với một số tác nhân. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Nếu lo về nguy cơ STI, bước phù hợp là gì?",
                "options": [
                    "Tự kết luận từ ảnh mạng",
                    "Giấu và tự dùng thuốc",
                    "Tìm tư vấn y tế về xét nghiệm",
                    "Chờ triệu chứng chắc chắn xuất hiện",
                ],
                "correct_index": 2,
                "explanation": "Tìm tư vấn y tế về xét nghiệm. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Nói gì với người có STI?",
                "options": [
                    "Đổ lỗi công khai",
                    "Xua đuổi",
                    "Chia sẻ thông tin cá nhân của họ",
                    "Khuyến khích khám và tránh kỳ thị",
                ],
                "correct_index": 3,
                "explanation": "Khuyến khích khám và tránh kỳ thị. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Một người có STI luôn biết ngay không?",
                "options": [
                    "Không, có thể không có triệu chứng",
                    "Có, luôn đau ngay",
                    "Có, luôn phát ban",
                    "Có, luôn sốt",
                ],
                "correct_index": 0,
                "explanation": "Không, có thể không có triệu chứng. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Điều nào tóm tắt video đúng nhất?",
                "options": [
                    "Đoán qua ngoại hình",
                    "Hiểu đường lây, giảm nguy cơ và xét nghiệm khi cần",
                    "Tin lời đồn",
                    "Tránh tiếp xúc xã hội thông thường",
                ],
                "correct_index": 1,
                "explanation": "Hiểu đường lây, giảm nguy cơ và xét nghiệm khi cần. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
        ],
    },
    {
        "order_index": 2,
        "title": "Bài 2 — Không thấy dấu hiệu ≠ không có nguy cơ",
        "video_url": "https://www.youtube.com/watch?v=_EKnKJ-Wb-g",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Tại sao không thể chỉ chờ đợi triệu chứng?
Nhiều người trẻ mang tâm lý: *“Khi nào thấy đau, ngứa hay có vết loét thì mới cần đi khám”*. Thực tế y khoa chứng minh:
- Đa số các ca nhiễm Chlamydia hay Gonorrhea (lậu) ở nữ giới và một phần ở nam giới hoàn toàn không có triệu chứng lâm sàng ở giai đoạn đầu.
- Tuy không biểu hiện, mầm bệnh vẫn có thể âm thầm gây tổn thương hệ sinh sản lâu dài và tiếp tục lây truyền cho bạn tình.

### 2. Xét nghiệm — Cách duy nhất để biết chính xác
- Xét nghiệm STI là việc kiểm tra mẫu dịch, nước tiểu hoặc máu để tìm sự hiện diện của tác nhân gây bệnh hoặc kháng thể.
- Việc xét nghiệm nhanh chóng, đơn giản và được bảo mật tuyệt đối tại các cơ sở y tế chuyên khoa.

### 3. Yếu tố thời điểm và loại xét nghiệm
- **Thời kỳ cửa sổ (Window period):** Là khoảng thời gian từ lúc có nguy cơ tiếp xúc với mầm bệnh đến khi xét nghiệm có thể phát hiện được chính xác.
- Mỗi loại mầm bệnh (HIV, Giang mai, Lậu, Chlamydia...) có thời kỳ cửa sổ và hình thức xét nghiệm khác nhau. Do đó, hãy nói thật với nhân viên y tế về thời điểm xảy ra sự cố để được chỉ định thời gian xét nghiệm tối ưu.

### 4. Tôn trọng quyền riêng tư
- Khi đi khám, bạn có toàn quyền yêu cầu bảo mật thông tin cá nhân.
- Tương tự, nếu biết kết quả của người khác, hãy tôn trọng quyền riêng tư tuyệt đối của họ, không lan truyền hay dùng để phán xét.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [Planned Parenthood — STI Testing: How to Know If You Have an STD](https://www.plannedparenthood.org/learn/stds-hiv-safer-sex/get-tested)
""",
        "quiz_title": "Củng cố bài 2 — Không thấy dấu hiệu ≠ không có nguy cơ",
        "quiz_description": "Bài trắc nghiệm 10 câu về tầm quan trọng của xét nghiệm STI, thời điểm xét nghiệm và thái độ bảo mật y tế.",
        "questions": [
            {
                "question_text": "Muốn biết chắc tình trạng STI nên làm gì?",
                "options": [
                    "Trao đổi với cơ sở y tế về xét nghiệm",
                    "Soi gương",
                    "Hỏi người lạ",
                    "Dùng ứng dụng đoán bệnh",
                ],
                "correct_index": 0,
                "explanation": "Trao đổi với cơ sở y tế về xét nghiệm. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Không có triệu chứng nghĩa là gì?",
                "options": [
                    "Chắc chắn không có STI",
                    "Không loại trừ STI",
                    "Không cần tư vấn",
                    "Đã khỏi mọi STI",
                ],
                "correct_index": 1,
                "explanation": "Không loại trừ STI. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Ai tư vấn loại xét nghiệm phù hợp?",
                "options": [
                    "Bình luận trên mạng",
                    "Người bán hàng không chuyên",
                    "Nhân viên y tế",
                    "Một bài trắc nghiệm tính cách",
                ],
                "correct_index": 2,
                "explanation": "Nhân viên y tế. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Thời điểm xét nghiệm có quan trọng không?",
                "options": [
                    "Không, mọi lúc như nhau",
                    "Chỉ quan trọng vào thứ hai",
                    "Chỉ liên quan đến chiều cao",
                    "Có, tùy tác nhân và thời điểm phơi nhiễm",
                ],
                "correct_index": 3,
                "explanation": "Có, tùy tác nhân và thời điểm phơi nhiễm. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Nếu kết quả dương tính, nên làm gì?",
                "options": [
                    "Hỏi nhân viên y tế về điều trị và theo dõi",
                    "Tự mua thuốc bất kỳ",
                    "Giấu mọi thông tin với cơ sở y tế",
                    "Đăng kết quả người khác",
                ],
                "correct_index": 0,
                "explanation": "Hỏi nhân viên y tế về điều trị và theo dõi. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Xét nghiệm STI có ích cho ai?",
                "options": [
                    "Chỉ một giới",
                    "Người cần đánh giá nguy cơ sau phơi nhiễm",
                    "Chỉ người có phát ban",
                    "Chỉ người đã kết hôn",
                ],
                "correct_index": 1,
                "explanation": "Người cần đánh giá nguy cơ sau phơi nhiễm. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Triệu chứng có thay thế xét nghiệm được không?",
                "options": [
                    "Luôn luôn",
                    "Chỉ khi tự tìm trên mạng",
                    "Không",
                    "Nếu bạn bè đồng ý",
                ],
                "correct_index": 2,
                "explanation": "Không. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Câu hỏi hữu ích khi đi khám là gì?",
                "options": [
                    "Tôi trông có khỏe không?",
                    "Ai nổi tiếng từng mắc?",
                    "Có thể bỏ qua kết quả không?",
                    "Khi nào cần xét nghiệm và nhận kết quả?",
                ],
                "correct_index": 3,
                "explanation": "Khi nào cần xét nghiệm và nhận kết quả?. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Sau nguy cơ phơi nhiễm, hành động có trách nhiệm là gì?",
                "options": [
                    "Xin tư vấn xét nghiệm thích hợp",
                    "Đoán rồi quên",
                    "Lan truyền tin đồn",
                    "Uống thuốc theo quảng cáo",
                ],
                "correct_index": 0,
                "explanation": "Xin tư vấn xét nghiệm thích hợp. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Cần đối xử với kết quả xét nghiệm của người khác thế nào?",
                "options": [
                    "Đăng lên nhóm lớp",
                    "Giữ riêng tư, tôn trọng",
                    "Kể cho mọi người",
                    "Dùng để trêu chọc",
                ],
                "correct_index": 1,
                "explanation": "Giữ riêng tư, tôn trọng. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
        ],
    },
    {
        "order_index": 3,
        "title": "Bài 3 — Một lớp chắn, hai mục tiêu khác nhau",
        "video_url": "https://www.youtube.com/watch?v=Eh5HK3F42IU",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Cơ chế bảo vệ kép của bao cao su ngoài
Bao cao su (external condom) là một trong những biện pháp chắn vật lý phổ biến và hiệu quả nhất, đảm nhiệm cùng lúc hai mục tiêu bảo vệ:
1. **Phòng tránh mang thai ngoài ý muốn:** Ngăn cản tinh dịch xâm nhập vào đường âm đạo.
2. **Giảm thiểu nguy cơ lây truyền STI:** Tạo màng ngăn giữa dịch sinh dục và niêm mạc.

### 2. Các bước kiểm tra an toàn trước khi sử dụng
- **Hạn sử dụng:** Kiểm tra ngày hết hạn in trên vỏ bao; tuyệt đối không dùng bao đã quá hạn vì chất liệu cao su bị thoái hóa dễ rách.
- **Tình trạng túi bọc:** Bóp nhẹ gói bao xem có cảm giác đệm không khí (air cushion) bên trong hay không. Nếu gói bị xẹp hoặc rách thủng từ trước, hãy bỏ đi và dùng gói khác.
- **Mở bao cẩn thận:** Xé bao bằng tay ở mép khía, không dùng răng, kéo hay vật sắc nhọn vì rất dễ làm thủng bao.

### 3. Nguyên tắc vàng trong sử dụng
- **Luôn dùng một bao mới cho mỗi lần quan hệ.**
- **Tuyệt đối KHÔNG đeo hai bao cao su cùng lúc:** Đeo hai bao ngoài chồng lên nhau sẽ sinh ra lực ma sát mạnh giữa hai lớp cao su, khiến bao cực kỳ dễ rách và tuột.
- **Đúng chiều:** Đặt mặt bao đúng chiều để có thể cuộn xuống dễ dàng đến gốc dương vật.

### 4. Phạm vi bảo vệ thực tế
Mặc dù rất hiệu quả, bao cao su không thể bảo vệ 100% đối với những mầm bệnh lây qua tiếp xúc da ở những vùng mà bao không che phủ được (chẳng hạn như mụn rộp sinh dục hoặc sùi mào gà ở bẹn). Nếu bao bị rách hoặc tuột trong lúc quan hệ, cần dừng lại ngay và xin tư vấn y tế về các biện pháp khẩn cấp tiếp theo.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [Planned Parenthood — Condoms: How to Use and Effectiveness](https://www.plannedparenthood.org/learn/birth-control/condom)
""",
        "quiz_title": "Củng cố bài 3 — Một lớp chắn, hai mục tiêu khác nhau",
        "quiz_description": "Bài trắc nghiệm 10 câu về cách dùng bao cao su ngoài đúng quy cách, các bước kiểm tra an toàn và sai lầm thường gặp.",
        "questions": [
            {
                "question_text": "Bao cao su ngoài là gì?",
                "options": [
                    "Một biện pháp chắn",
                    "Một loại kháng sinh",
                    "Một xét nghiệm",
                    "Một vắc xin",
                ],
                "correct_index": 0,
                "explanation": "Một biện pháp chắn. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Bao cao su có thể giúp giảm nguy cơ nào?",
                "options": [
                    "Mọi nguy cơ xuống 0",
                    "Mang thai và một số STI",
                    "Chỉ cảm cúm",
                    "Chỉ dị ứng",
                ],
                "correct_index": 1,
                "explanation": "Mang thai và một số STI. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Trước khi dùng bao cần kiểm tra gì?",
                "options": [
                    "Màu áo",
                    "Giá giày",
                    "Hạn dùng và vỏ còn nguyên",
                    "Ngày trong tuần",
                ],
                "correct_index": 2,
                "explanation": "Hạn dùng và vỏ còn nguyên. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Mỗi lần sử dụng cần mấy bao mới?",
                "options": [
                    "Một bao đã dùng",
                    "Hai bao ngoài chồng nhau",
                    "Không cần bao",
                    "Một bao mới đúng cách",
                ],
                "correct_index": 3,
                "explanation": "Một bao mới đúng cách. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Dùng hai bao ngoài chồng nhau có nên không?",
                "options": [
                    "Không, có thể làm tăng ma sát và rách",
                    "Luôn tốt hơn",
                    "Bắt buộc",
                    "Không liên quan",
                ],
                "correct_index": 0,
                "explanation": "Không, có thể làm tăng ma sát và rách. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Nếu bao rách hoặc tuột thì sao?",
                "options": [
                    "Coi như không có gì",
                    "Dừng lại và hỏi tư vấn về bước tiếp theo",
                    "Dùng lại bao đó",
                    "Chờ triệu chứng mới xử lý",
                ],
                "correct_index": 1,
                "explanation": "Dừng lại và hỏi tư vấn về bước tiếp theo. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Bao cao su có bảo vệ tuyệt đối khỏi mọi STI không?",
                "options": [
                    "Có, tuyệt đối",
                    "Chỉ khi bao có màu đen",
                    "Không, còn tùy đường lây và vùng che phủ",
                    "Không bao giờ giảm nguy cơ",
                ],
                "correct_index": 2,
                "explanation": "Không, còn tùy đường lây và vùng che phủ. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Điều nào giúp biện pháp hiệu quả hơn?",
                "options": [
                    "Chỉ mang theo mà không dùng",
                    "Dùng bao hết hạn",
                    "Dùng lại",
                    "Dùng đúng và đều đặn",
                ],
                "correct_index": 3,
                "explanation": "Dùng đúng và đều đặn. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Bao cao su ngoài có thể được dùng bởi cặp đôi thuộc giới nào?",
                "options": [
                    "Bất kỳ cặp đôi nào có hoạt động phù hợp",
                    "Chỉ học sinh nam",
                    "Chỉ người đã kết hôn",
                    "Chỉ người lớn tuổi",
                ],
                "correct_index": 0,
                "explanation": "Bất kỳ cặp đôi nào có hoạt động phù hợp. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Nếu chưa rõ cách sử dụng an toàn nên làm gì?",
                "options": [
                    "Tự đoán",
                    "Xem hướng dẫn sản phẩm và hỏi chuyên gia",
                    "Tin thử thách trên mạng",
                    "Bỏ qua hướng dẫn",
                ],
                "correct_index": 1,
                "explanation": "Xem hướng dẫn sản phẩm và hỏi chuyên gia. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
        ],
    },
    {
        "order_index": 4,
        "title": "Bài 4 — Tránh thai không đồng nghĩa tránh STI",
        "video_url": "https://www.youtube.com/watch?v=ypbxZQ8wEFY",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Phân biệt rành mạch hai mục tiêu sức khỏe
Một ngộ nhận rất phổ biến ở lứa tuổi học sinh là cho rằng *“Đã dùng thuốc tránh thai rồi thì hoàn toàn an toàn, không lo bệnh tật gì nữa”*. Cần phân định rõ:
- **Ngừa thai:** Là ngăn chặn sự thụ tinh giữa tinh trùng và trứng hoặc ngăn trứng làm tổ.
- **Phòng chống STI:** Là ngăn chặn sự tiếp xúc và trao đổi mầm bệnh (vi khuẩn, virus) qua dịch cơ thể hoặc niêm mạc.

### 2. Các phương pháp tránh thai phổ biến hiện nay
Khoa học y tế cung cấp nhiều biện pháp tránh thai với cơ chế hoạt động khác nhau:
- **Phương pháp nội tiết (Hormone):** Thuốc viên uống hàng ngày, miếng dán tránh thai, que cấy tránh thai, mũi tiêm tránh thai.
- **Dụng cụ tử cung (IUD / Vòng tránh thai):** Vòng đồng hoặc vòng nội tiết đặt trong tử cung.
- **Biện pháp chắn:** Bao cao su ngoài, bao cao su trong.

### 3. Tại sao các biện pháp hormone không phòng được STI?
Các biện pháp nội tiết hay que cấy chỉ tác động lên chu kỳ rụng trứng hoặc làm đặc chất nhầy cổ tử cung để chặn tinh trùng, **hoàn toàn không tạo ra lớp rào cản vật lý** để ngăn virus hay vi khuẩn lây lan. Do đó:
> *Chỉ có các biện pháp chắn (như bao cao su) mới đồng thời giúp giảm thiểu nguy cơ lây truyền STI.*

### 4. Quyết định có hiểu biết và sự tôn trọng
- Lựa chọn không quan hệ tình dục (abstinence) là một quyết định hoàn toàn bình thường, lành mạnh và đáng được tôn trọng tuyệt đối ở lứa tuổi học đường.
- Việc tìm hiểu kiến thức này giúp các bạn trẻ có hiểu biết vững vàng để tự bảo vệ mình, không phải là sự cổ súy hay thúc ép quan hệ tình dục sớm.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [AMAZE Org — Birth Control: What Is It?](https://amaze.org/)
> - [Planned Parenthood — Birth Control Options](https://www.plannedparenthood.org/learn/birth-control)
""",
        "quiz_title": "Củng cố bài 4 — Tránh thai không đồng nghĩa tránh STI",
        "quiz_description": "Bài trắc nghiệm 10 câu phân biệt rõ ràng giữa mục tiêu tránh thai và phòng chống STI, các nhóm biện pháp khoa học.",
        "questions": [
            {
                "question_text": "Mục đích chính của tránh thai là gì?",
                "options": [
                    "Giảm khả năng mang thai",
                    "Chữa STI",
                    "Thay khám bệnh",
                    "Tăng chiều cao",
                ],
                "correct_index": 0,
                "explanation": "Giảm khả năng mang thai. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Phương pháp nào là biện pháp chắn được video đề cập?",
                "options": [
                    "Thuốc kháng sinh",
                    "Bao cao su",
                    "Vitamin",
                    "Nước rửa",
                ],
                "correct_index": 1,
                "explanation": "Bao cao su. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Thuốc tránh thai có bảo vệ khỏi mọi STI không?",
                "options": [
                    "Có, tuyệt đối",
                    "Chỉ khi uống buổi tối",
                    "Không",
                    "Chỉ nếu uống với nước lạnh",
                ],
                "correct_index": 2,
                "explanation": "Không. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Video nhắc đến phương pháp nào khác?",
                "options": [
                    "Thuốc chữa cảm",
                    "Kính áp tròng",
                    "Máy đo huyết áp",
                    "Que cấy tránh thai",
                ],
                "correct_index": 3,
                "explanation": "Que cấy tránh thai. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Các phương pháp tránh thai có giống nhau hoàn toàn không?",
                "options": [
                    "Không, khác cách sử dụng và đặc điểm",
                    "Có, cùng một cách dùng",
                    "Chỉ khác tên gọi",
                    "Chỉ khác màu hộp",
                ],
                "correct_index": 0,
                "explanation": "Không, khác cách sử dụng và đặc điểm. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Vì sao cần phân biệt tránh thai với phòng STI?",
                "options": [
                    "Vì STI luôn nhìn thấy",
                    "Vì không phải mọi cách tránh thai đều phòng STI",
                    "Vì phương pháp nào cũng như nhau",
                    "Vì xét nghiệm làm tránh thai",
                ],
                "correct_index": 1,
                "explanation": "Vì không phải mọi cách tránh thai đều phòng STI. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Muốn chọn phương pháp phù hợp nên hỏi ai?",
                "options": [
                    "Bình luận ngẫu nhiên",
                    "Bạn chưa tìm hiểu",
                    "Nhân viên y tế đủ chuyên môn",
                    "Người bán sản phẩm bất kỳ",
                ],
                "correct_index": 2,
                "explanation": "Nhân viên y tế đủ chuyên môn. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Không quan hệ tình dục có là lựa chọn hợp lệ không?",
                "options": [
                    "Không, luôn bị ép",
                    "Chỉ với một giới",
                    "Chỉ sau xét nghiệm",
                    "Có",
                ],
                "correct_index": 3,
                "explanation": "Có. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Điều nào thể hiện dùng thông tin đúng cách?",
                "options": [
                    "Xem mục tiêu tránh thai và phòng STI riêng biệt",
                    "Cho rằng một viên thuốc xử lý mọi rủi ro",
                    "Chọn theo tin đồn",
                    "Tự kê đơn",
                ],
                "correct_index": 0,
                "explanation": "Xem mục tiêu tránh thai và phòng STI riêng biệt. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Một ví dụ về phương pháp video nêu là gì?",
                "options": [
                    "Thuốc hạ sốt",
                    "Vòng tránh thai",
                    "Khẩu trang",
                    "Thuốc nhỏ mắt",
                ],
                "correct_index": 1,
                "explanation": "Vòng tránh thai. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
        ],
    },
    {
        "order_index": 5,
        "title": "Bài 5 — Sau một sự cố: hành động sớm, hỏi đúng người",
        "video_url": "https://www.youtube.com/watch?v=Z1LTban3Z84",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Tránh thai khẩn cấp (Emergency Contraception - EC) là gì?
Tránh thai khẩn cấp là phương án hỗ trợ nhằm giảm thiểu khả năng mang thai sau khi đã xảy ra quan hệ tình dục đường âm đạo không có bảo vệ, hoặc khi biện pháp tránh thai thông thường gặp sự cố (ví dụ: rách bao cao su, tuột bao, quên uống thuốc tránh thai hàng ngày).

### 2. Yếu tố thời gian sống còn: Càng sớm càng hiệu quả
- Hiệu quả của thuốc tránh thai khẩn cấp suy giảm nhanh theo thời gian sau khi xảy ra quan hệ không an toàn.
- Phần lớn các loại thuốc khẩn cấp có hiệu quả cao nhất nếu được sử dụng trong vòng **24–72 giờ đầu** (tùy thuộc vào loại hoạt chất như Levonorgestrel hay Ulipristal Acetate).
- Vì vậy, việc **hành động sớm và tham khảo ý kiến dược sĩ/bác sĩ ngay** là yếu tố quyết định.

### 3. Những điều tránh thai khẩn cấp KHÔNG THỂ làm:
- **KHÔNG PHẢI là thuốc phá thai:** Thuốc tránh thai khẩn cấp hoạt động chủ yếu bằng cách trì hoãn sự rụng trứng; thuốc hoàn toàn không có tác dụng chấm dứt thai kỳ nếu trứng đã làm tổ trong tử cung.
- **KHÔNG BẢO VỆ khỏi STI:** Thuốc không có khả năng chống lại bất kỳ mầm bệnh lây truyền qua đường tình dục nào. Nếu có nguy cơ phơi nhiễm STI, cần tìm tư vấn xét nghiệm hoặc điều trị dự phòng (như PEP với HIV trong vòng 72 giờ).
- **Không dùng thay thế biện pháp thường xuyên:** Đây chỉ là phương án ứng phó sự cố, không nên lạm dụng định kỳ vì có thể gây rối loạn kinh nguyệt và hiệu quả kém hơn các biện pháp lâu dài.

### 4. Giữ bình tĩnh và tìm kiếm sự hỗ trợ an toàn
Nếu bạn ở trong tình huống bị ép buộc hoặc bạo lực tình dục, hãy ưu tiên sự an toàn của bản thân, tìm đến người lớn đáng tin cậy hoặc cơ sở y tế địa phương để được bảo vệ và hỗ trợ tâm lý y tế kịp thời.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [Planned Parenthood — Emergency Contraception (Morning-After Pill)](https://www.plannedparenthood.org/learn/morning-after-pill-emergency-contraception)
""",
        "quiz_title": "Củng cố bài 5 — Sau một sự cố: hành động sớm, hỏi đúng người",
        "quiz_description": "Bài trắc nghiệm 10 câu về bản chất của tránh thai khẩn cấp, mốc thời gian vàng và cách xử trí sự cố trách nhiệm.",
        "questions": [
            {
                "question_text": "Tránh thai khẩn cấp nhằm mục đích gì?",
                "options": [
                    "Giảm nguy cơ mang thai sau một tình huống có nguy cơ",
                    "Chữa STI",
                    "Thay mọi phương pháp thường xuyên",
                    "Chẩn đoán có thai",
                ],
                "correct_index": 0,
                "explanation": "Giảm nguy cơ mang thai sau một tình huống có nguy cơ. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Khi nào nên tìm tư vấn về tránh thai khẩn cấp?",
                "options": [
                    "Sau vài tháng",
                    "Càng sớm càng tốt sau sự cố có nguy cơ",
                    "Chỉ khi đã sốt",
                    "Chỉ sau khi đăng mạng",
                ],
                "correct_index": 1,
                "explanation": "Càng sớm càng tốt sau sự cố có nguy cơ. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Bao cao su rách khi quan hệ đường âm đạo thì sao?",
                "options": [
                    "Chắc chắn không cần làm gì",
                    "Tự kết luận không nguy cơ",
                    "Hỏi sớm về tránh thai khẩn cấp và nguy cơ STI",
                    "Dùng lại bao rách",
                ],
                "correct_index": 2,
                "explanation": "Hỏi sớm về tránh thai khẩn cấp và nguy cơ STI. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Tránh thai khẩn cấp có phòng STI không?",
                "options": [
                    "Có, mọi STI",
                    "Chỉ nếu uống nhiều",
                    "Có trong một năm",
                    "Không",
                ],
                "correct_index": 3,
                "explanation": "Không. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Tránh thai khẩn cấp có chấm dứt thai đã hình thành không?",
                "options": [
                    "Không, đây không phải thuốc phá thai",
                    "Có, luôn luôn",
                    "Chỉ qua tin nhắn",
                    "Không liên quan mục đích",
                ],
                "correct_index": 0,
                "explanation": "Không, đây không phải thuốc phá thai. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Ai có thể tư vấn lựa chọn phù hợp?",
                "options": [
                    "Bài quảng cáo ẩn danh",
                    "Nhân viên y tế hoặc dược sĩ",
                    "Người không có chuyên môn",
                    "Trò chơi trực tuyến",
                ],
                "correct_index": 1,
                "explanation": "Nhân viên y tế hoặc dược sĩ. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Mọi phương án khẩn cấp có cùng mốc thời gian không?",
                "options": [
                    "Có, luôn giống nhau",
                    "Chỉ phụ thuộc thời tiết",
                    "Không, cần hỏi về từng lựa chọn",
                    "Không có giới hạn nào",
                ],
                "correct_index": 2,
                "explanation": "Không, cần hỏi về từng lựa chọn. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Có nên coi tránh thai khẩn cấp là cách dùng thường xuyên thay tư vấn không?",
                "options": [
                    "Có, vì phòng STI",
                    "Có, vì không cần hướng dẫn",
                    "Có, vì chữa STI",
                    "Không, cần tìm phương pháp phù hợp lâu dài",
                ],
                "correct_index": 3,
                "explanation": "Không, cần tìm phương pháp phù hợp lâu dài. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Nếu lo ngại bị ép buộc nên làm gì?",
                "options": [
                    "Tìm hỗ trợ an toàn từ cơ sở y tế và người tin cậy",
                    "Tự nhận lỗi",
                    "Chia sẻ ảnh lên mạng",
                    "Bỏ qua an toàn",
                ],
                "correct_index": 0,
                "explanation": "Tìm hỗ trợ an toàn từ cơ sở y tế và người tin cậy. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Tình huống nào video tập trung giải thích?",
                "options": [
                    "Chế độ ăn",
                    "Phương án tránh thai sau quan hệ có nguy cơ",
                    "Vệ sinh răng",
                    "Bài tập thể thao",
                ],
                "correct_index": 1,
                "explanation": "Phương án tránh thai sau quan hệ có nguy cơ. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
        ],
    },
    {
        "order_index": 6,
        "title": "Bài 6 — Bao cao su trong: thêm lựa chọn, vẫn cần dùng đúng",
        "video_url": "https://www.youtube.com/watch?v=P0gd7kUf1bo",
        "duration_minutes": 15,
        "content_type": "HYBRID",
        "content_body": """### 1. Bao cao su trong (Internal Condom) là gì?
Bao cao su trong (tên tiếng Anh trước đây thường gọi là *female condom*) là một túi mỏng bằng chất liệu tổng hợp (như nitrile hoặc polyurethane), có hai vòng mềm ở hai đầu:
- Vòng kín bên trong dùng để đưa sâu vào đáy âm đạo để cố định.
- Vòng hở bên ngoài bao phủ một phần âm hộ bên ngoài.
Phương pháp này giúp tạo rào cản vật lý ngăn tinh dịch và giảm thiểu nguy cơ lây truyền một số bệnh lây qua đường tình dục.

### 2. Ý nghĩa của tên gọi trung tính theo cấu tạo giải phẫu
Tên gọi khoa học chuẩn mực hiện nay là **“Bao cao su trong” (Internal Condom)** thay vì “bao cao su nữ”:
- Thuật ngữ này dựa trên vị trí sử dụng và cơ chế hoạt động thực tế của sản phẩm.
- Nhấn mạnh rằng kiến thức sức khỏe sinh sản dành cho học sinh thuộc mọi giới tính để hiểu biết và chủ động bảo vệ sức khỏe cho nhau, không gán định kiến giới tính vào dụng cụ y tế.

### 3. Cảnh báo quan trọng: Tuyệt đối không dùng chung hai loại bao
Một sai lầm rất nguy hiểm là nghĩ rằng *“Dùng cả bao ngoài lẫn bao trong sẽ an toàn gấp đôi”*:
- Khi hai bao cao su cọ xát trực tiếp vào nhau trong quá trình quan hệ, lực ma sát sẽ làm cả hai bao **rất dễ bị rách, xô lệch hoặc tuột ra ngoài**, làm mất hoàn toàn hiệu quả bảo vệ.
- **Quy tắc:** Chỉ chọn một trong hai phương án (hoặc bao ngoài, hoặc bao trong) cho mỗi lần quan hệ.

### 4. Đọc kỹ hướng dẫn và chủ động tham khảo chuyên gia
Bao cao su trong có thể được đặt trước khi quan hệ và không phụ thuộc vào trạng thái cương cứng. Tuy nhiên, việc đưa vào và lấy ra cần làm theo đúng hướng dẫn của nhà sản xuất. Nếu gặp sự cố bao bị tuột vào trong hoặc bị rách, hãy bình tĩnh tìm đến nhân viên y tế để được hỗ trợ kịp thời.

> [!NOTE]
> **Tài liệu tham khảo chuyên môn:**
> - [Planned Parenthood — Internal Condom: How to Use and Benefits](https://www.plannedparenthood.org/learn/birth-control/internal-condom)
> - [Planned Parenthood — STI Testing & Safer Sex](https://www.plannedparenthood.org/learn/stds-hiv-safer-sex/get-tested)
> - [Planned Parenthood — Emergency Contraception Overview](https://www.plannedparenthood.org/learn/morning-after-pill-emergency-contraception)
""",
        "quiz_title": "Củng cố bài 6 — Bao cao su trong: thêm lựa chọn, vẫn cần dùng đúng",
        "quiz_description": "Bài trắc nghiệm 10 câu về bao cao su trong, vị trí sử dụng, nguyên tắc an toàn chống ma sát và kiến thức y khoa không gán giới.",
        "questions": [
            {
                "question_text": "Bao cao su trong thuộc nhóm nào?",
                "options": [
                    "Biện pháp chắn",
                    "Kháng sinh",
                    "Vắc xin",
                    "Xét nghiệm",
                ],
                "correct_index": 0,
                "explanation": "Biện pháp chắn. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Vị trí sử dụng được bài này đề cập là đâu?",
                "options": [
                    "Trong tai",
                    "Bên trong âm đạo",
                    "Trên cánh tay",
                    "Trong mắt",
                ],
                "correct_index": 1,
                "explanation": "Bên trong âm đạo. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Bao cao su trong có thể giảm những nguy cơ nào?",
                "options": [
                    "Mọi nguy cơ tuyệt đối",
                    "Chỉ cảm lạnh",
                    "Mang thai và một số STI khi dùng đúng",
                    "Chỉ đau đầu",
                ],
                "correct_index": 2,
                "explanation": "Mang thai và một số STI khi dùng đúng. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Có nên dùng đồng thời bao trong và bao ngoài không?",
                "options": [
                    "Có, bắt buộc",
                    "Có, luôn an toàn hơn",
                    "Không ảnh hưởng gì",
                    "Không, ma sát có thể gây tuột hoặc rách",
                ],
                "correct_index": 3,
                "explanation": "Không, ma sát có thể gây tuột hoặc rách. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Nên tìm hướng dẫn cách sử dụng ở đâu?",
                "options": [
                    "Hướng dẫn sản phẩm hoặc nhân viên y tế",
                    "Tin đồn",
                    "Bình luận ngẫu nhiên",
                    "Một bài bói",
                ],
                "correct_index": 0,
                "explanation": "Hướng dẫn sản phẩm hoặc nhân viên y tế. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Tên gọi “bao cao su trong” nhấn mạnh điều gì?",
                "options": [
                    "Chỉ một giới có thể học",
                    "Vị trí và cách dùng, không gán giới cho người học",
                    "Sản phẩm chữa bệnh",
                    "Là thuốc uống",
                ],
                "correct_index": 1,
                "explanation": "Vị trí và cách dùng, không gán giới cho người học. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Nếu bao bị tuột cần làm gì?",
                "options": [
                    "Giấu sự cố",
                    "Tiếp tục dùng bao đó",
                    "Hỏi tư vấn phù hợp về nguy cơ và bước tiếp theo",
                    "Chắc chắn không có nguy cơ",
                ],
                "correct_index": 2,
                "explanation": "Hỏi tư vấn phù hợp về nguy cơ và bước tiếp theo. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Bao cao su trong có thay xét nghiệm STI không?",
                "options": [
                    "Có, hoàn toàn",
                    "Chỉ khi mua online",
                    "Chỉ khi còn mới",
                    "Không",
                ],
                "correct_index": 3,
                "explanation": "Không. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Đối tượng nào có thể học nội dung video này?",
                "options": [
                    "Học sinh mọi giới, để hiểu cách bảo vệ sức khỏe",
                    "Chỉ một giới",
                    "Chỉ người đã kết hôn",
                    "Chỉ nhân viên bán hàng",
                ],
                "correct_index": 0,
                "explanation": "Học sinh mọi giới, để hiểu cách bảo vệ sức khỏe. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
            {
                "question_text": "Thông điệp thực hành đúng là gì?",
                "options": [
                    "Dùng đồng thời hai loại bao",
                    "Chọn biện pháp phù hợp, làm theo hướng dẫn và tìm tư vấn khi cần",
                    "Bỏ qua sự cố",
                    "Cho rằng nguy cơ luôn bằng không",
                ],
                "correct_index": 1,
                "explanation": "Chọn biện pháp phù hợp, làm theo hướng dẫn và tìm tư vấn khi cần. Đây là ý chính được giới thiệu trong video và nội dung bài.",
            },
        ],
    },
]

async def seed_course_10():
    async with AsyncSessionLocal() as session:
        print("Starting seed for Course 10: Đừng Để Lời Đồn Quyết Định Sức Khỏe Của Bạn...")

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
        print(f"Created Course 10: {course.title} (ID: {course_id})")

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
        print("SEEDING COURSE 10 COMPLETED SUCCESSFULLY!")
        print(f"Course: {COURSE_DATA['title']}")
        print(f"Target Audience: {COURSE_DATA['target_audience']}")
        print(f"Lessons: {len(LESSONS_DATA)}")
        print(f"Quizzes: {len(LESSONS_DATA)}")
        print(f"Total Questions: {total_questions}")
        print(f"Total Options: {total_options}")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(seed_course_10())
