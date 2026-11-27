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
    "title": "Nhà Mình Nói Chuyện Về Cơ Thể Được Mà!",
    "slug": "nha-minh-noi-chuyen-ve-co-the-duoc-ma",
    "short_description": "Khóa học đồng hành dành cho phụ huynh và học sinh (10–15 tuổi): cùng gọi đúng tên các bộ phận cơ thể, tôn trọng nhịp dậy thì riêng biệt, đối thoại cởi mở, thiết lập ranh giới riêng tư số và kiểm chứng tin đồn sức khỏe.",
    "description": (
        "**Đối tượng:** Phụ huynh và học sinh cùng học (độ tuổi khuyến nghị: 10–15 tuổi).\n\n"
        "Khóa học được thiết kế đặc biệt như một cầu nối đồng hành giữa cha mẹ và con cái, tạo dựng không gian gia đình cởi mở, an toàn và tôn trọng lẫn nhau khi trao đổi về cơ thể và sự trưởng thành: "
        "từ việc xóa bỏ ngại ngùng để gọi đúng tên giải phẫu cơ thể, thấu hiểu nhịp độ dậy thì đa dạng mà không phán xét hay so sánh, mở ra kênh trò chuyện về giới tính và tình dục ngay tại nhà, "
        "cân bằng giữa quyền riêng tư của con và sự bảo vệ của cha mẹ trên không gian số, rèn luyện tư duy phản biện kiểm chứng tin đồn sức khỏe, "
        "cho đến việc thiết lập tín hiệu giao tiếp linh hoạt (giấy nhắn, tin nhắn) khi con chưa sẵn sàng đối thoại trực tiếp.\n\n"
        "**Lưu ý:** Bài học mang tính chất giáo dục kỹ năng giao tiếp và kiến thức khoa học thường thức, không thay thế việc chẩn đoán hay điều trị y tế chuyên biệt."
    ),
    "learning_objectives": (
        "- Cùng nhau gọi tên chính xác các cơ quan giải phẫu bên ngoài và bên trong một cách tự nhiên, khoa học và không trêu chọc.\n"
        "- Thấu hiểu và tôn trọng rằng mỗi cơ thể đều lớn lên theo nhịp sinh học riêng biệt, không dùng bạn bè làm thước đo giá trị bản thân.\n"
        "- Xây dựng quy ước đối thoại hai chiều thoải mái, lắng nghe và tìm kiếm lời giải đáp khoa học cho những câu hỏi khó về giới tính.\n"
        "- Thỏa thuận minh bạch ranh giới giữa quyền riêng tư của con và sự hỗ trợ an toàn của cha mẹ trong kỷ nguyên số.\n"
        "- Rèn luyện kỹ năng 3 bước của Khan Academy để phát hiện và ngăn chặn tin giả, lời đồn thất thiệt về sức khỏe và dậy thì.\n"
        "- Thống nhất các tín hiệu mở lời gián tiếp (tin nhắn, giấy hẹn) và quy trình xử lý khẩn cấp khi gặp nguy cơ mất an toàn."
    ),
    "thumbnail_url": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=1200&q=80",
    "target_audience": "BOTH",
    "is_published": True,
}

LESSONS_DATA = [
    {
        "order_index": 1,
        "title": "Bài 1 — Tên gọi đúng giúp ta bớt ngại",
        "video_url": "https://www.youtube.com/watch?v=EinNeciMgpQ",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Cùng gọi tên
Video minh họa cho cha mẹ cách nói tên các bộ phận cơ thể và an toàn cơ thể với trẻ nhỏ (*Planned Parenthood — How To Talk To Preschoolers About Anatomy & Body Safety*). Nếu cùng xem với học sinh lớn hơn, hãy xem như một ví dụ trực quan về cách nói rõ ràng, thẳng thắn, rồi cùng nhau dùng từ ngữ giải phẫu phù hợp với lứa tuổi; không xem trẻ lớn như trẻ mẫu giáo.

### 2. Nói chính xác, không trêu chọc
Có thể gọi tên chính xác các cơ quan bên ngoài như âm hộ, dương vật, bìu/tinh hoàn, hoặc các cơ quan bên trong như tử cung, buồng trứng khi cần. Các đặc điểm cơ thể không quyết định giá trị hay phẩm giá của một con người; mọi người học đều có quyền thắc mắc và được giải đáp với thái độ tôn trọng, không chê cười.

### 3. Bài tập đôi: Mô tả nhu cầu sức khỏe
Mỗi người thực hành nói một câu mô tả nhu cầu sức khỏe bằng từ ngữ rõ ràng:
> *“Con thấy khó chịu/đau ở vùng...; con muốn hỏi ý kiến nhân viên y tế.”*
> Người kia lắng nghe và đáp lại: *“Cảm ơn vì đã chia sẻ, mình cùng tìm hiểu nguồn tin cậy nhé.”*

*(Lưu ý: Không ai bị bắt buộc phải tiết lộ tình trạng cơ thể thực tế của bản thân).*

### 4. An toàn và quyền riêng tư
Trẻ có quyền từ chối các đụng chạm không mong muốn và tìm đến người lớn tin cậy. Khi thăm khám y tế, người chăm sóc cần giải thích rõ ràng lý do, tôn trọng ranh giới và luôn đồng hành hỗ trợ trẻ.

> [!NOTE]
> **Tài liệu tham khảo đối chiếu:** [Planned Parenthood — How do I talk to my preschooler about their body?](https://www.plannedparenthood.org/learn/parents/preschool/how-do-i-talk-my-preschooler-about-their-body)
""",
        "quiz_title": "Củng cố bài 1 — Tên gọi đúng giúp ta bớt ngại",
        "quiz_description": "Bài trắc nghiệm 10 câu kiểm tra khả năng sử dụng thuật ngữ giải phẫu chính xác, thái độ tôn trọng và nguyên tắc an toàn thân thể.",
        "questions": [
            {
                "question_text": "Vì sao cần biết tên đúng của các bộ phận cơ thể?",
                "options": [
                    "Để mô tả thắc mắc hoặc khó chịu rõ ràng",
                    "Để chế giễu cơ thể khác",
                    "Để bắt ai cũng phải tiết lộ",
                    "Để thay khám y tế",
                ],
                "correct_index": 0,
                "explanation": "Tên đúng giúp giao tiếp về sức khỏe và an toàn.",
            },
            {
                "question_text": "Lời đáp nào phù hợp khi trẻ nêu câu hỏi về cơ thể?",
                "options": [
                    "“Đừng nói tên đó”",
                    "“Mình cùng tìm tên đúng và giải thích nhé”",
                    "“Con thật kỳ lạ”",
                    "“Cơ thể con phải giống người khác”",
                ],
                "correct_index": 1,
                "explanation": "Lắng nghe không xấu hổ.",
            },
            {
                "question_text": "Cơ thể có đặc điểm khác nhau nghĩa là?",
                "options": [
                    "Có người không được học",
                    "Chỉ một giới được hỏi",
                    "Vẫn cần được tôn trọng và học các nguyên tắc an toàn như nhau",
                    "Cơ thể khác là sai",
                ],
                "correct_index": 2,
                "explanation": "Quyền an toàn áp dụng cho mọi học sinh.",
            },
            {
                "question_text": "Nếu đau ở một vùng cơ thể, cách nói hữu ích?",
                "options": [
                    "Chỉ nói “đau chỗ đó” dù có thể diễn đạt rõ",
                    "Giấu mọi triệu chứng",
                    "Hỏi người lạ ẩn danh thay vì chăm sóc",
                    "Dùng từ rõ ràng để mô tả vùng đau với người tin cậy/y tế",
                ],
                "correct_index": 3,
                "explanation": "Diễn đạt chính xác hỗ trợ tìm trợ giúp.",
            },
            {
                "question_text": "Bài tập xem chung có yêu cầu kể tình trạng riêng?",
                "options": [
                    "Không; có thể dùng tình huống giả định",
                    "Có, bắt buộc kể",
                    "Có, phải cho xem hình",
                    "Có, phải kể trước lớp",
                ],
                "correct_index": 0,
                "explanation": "Thực hành không ép tiết lộ riêng tư.",
            },
            {
                "question_text": "Khi người chăm sóc cần đụng chạm phục vụ y tế, điều gì quan trọng?",
                "options": [
                    "Không giải thích gì",
                    "Giải thích và tôn trọng trẻ, bảo đảm an toàn",
                    "Cấm trẻ hỏi",
                    "Luôn làm ở chỗ đông người",
                ],
                "correct_index": 1,
                "explanation": "Trẻ cần hiểu chăm sóc đang diễn ra.",
            },
            {
                "question_text": "Câu nào nên tránh?",
                "options": [
                    "“Con có thể hỏi người tin cậy”",
                    "“Mọi cơ thể đáng tôn trọng”",
                    "“Tên bộ phận này đáng xấu hổ, không được nhắc”",
                    "“Mình cùng đọc nguồn y tế”",
                ],
                "correct_index": 2,
                "explanation": "Xấu hổ hóa cản trở giao tiếp.",
            },
            {
                "question_text": "Video gốc nhắm đến nhóm tuổi nào?",
                "options": [
                    "Chỉ bác sĩ chuyên khoa",
                    "Chỉ sinh viên đại học",
                    "Chỉ trẻ đã trưởng thành",
                    "Cha mẹ trò chuyện với trẻ mẫu giáo",
                ],
                "correct_index": 3,
                "explanation": "Phải điều chỉnh hoạt động khi dùng cho trẻ lớn hơn.",
            },
            {
                "question_text": "Ai có quyền đặt câu hỏi về cơ thể?",
                "options": [
                    "Mọi học sinh bất kể giới và đặc điểm cơ thể",
                    "Chỉ học sinh nam",
                    "Chỉ học sinh nữ",
                    "Chỉ người đã dậy thì",
                ],
                "correct_index": 0,
                "explanation": "Kiến thức sức khỏe dành cho tất cả.",
            },
            {
                "question_text": "Nếu không chắc thuật ngữ, hai bên nên?",
                "options": [
                    "Đoán và khẳng định chắc chắn",
                    "Tra nguồn giáo dục sức khỏe đáng tin cùng nhau",
                    "Đổi thành biệt danh gây hiểu nhầm",
                    "Cấm hỏi",
                ],
                "correct_index": 1,
                "explanation": "Kiểm tra nguồn giúp tránh sai kiến thức.",
            },
        ],
    },
    {
        "order_index": 2,
        "title": "Bài 2 — Mỗi cơ thể lớn lên theo nhịp riêng",
        "video_url": "https://www.youtube.com/watch?v=IAIpqX5V2Jg",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Nhịp lớn lên khác nhau
Video từ AMAZE (*Puberty: Am I Normal? #AskAMAZE*) giải đáp băn khoăn phổ biến: *“Liệu mình có bình thường không?”* và chứng minh rằng các thay đổi sinh học trong tuổi dậy thì không đến cùng một thời điểm với tất cả mọi người. Tuyệt đối không lấy bạn bè đồng trang lứa làm thước đo giá trị bản thân.

### 2. Cùng hiểu nhiều kiểu thay đổi
Dậy thì có thể bao gồm những biến đổi về chiều cao, da tiết dầu, mụn, mùi cơ thể, cảm xúc thăng trầm, kinh nguyệt hoặc hiện tượng xuất tinh trong khi ngủ (mộng tinh). Cả phụ huynh lẫn học sinh đều nên hiểu biết toàn diện về các thay đổi này để tự chăm sóc cơ thể và biết tôn trọng người khác; không phân biệt kiến thức theo nam/nữ.

### 3. Khi nào cần tìm tư vấn chuyên môn?
Nếu cảm thấy quá lo lắng về sức khỏe, đau đớn dữ dội kéo dài hoặc thay đổi sinh lý làm cản trở sinh hoạt thường ngày, hãy cùng nhau tìm đến bác sĩ hoặc nhân viên y tế có chuyên môn. Video mang tính giáo dục phổ quát và không thay thế chẩn đoán y khoa cá nhân.

### 4. Bài tập chung: Khẳng định không so sánh
Mỗi bên cùng viết ra một câu khẳng định tích cực, ví dụ:
> *“Cơ thể mỗi người thay đổi theo một nhịp điệu sinh học riêng và đều đáng được tôn trọng.”*

*(Quy tắc quan trọng: Không bình luận hay phán xét về đặc điểm ngoại hình thực tế của nhau).*

> [!NOTE]
> **Tài liệu tham khảo đối chiếu:** [AMAZE — Puberty: Am I Normal?](https://amaze.org/video/puberty-am-i-normal/)
""",
        "quiz_title": "Củng cố bài 2 — Mỗi cơ thể lớn lên theo nhịp riêng",
        "quiz_description": "Bài trắc nghiệm 10 câu về sự đa dạng trong tiến trình dậy thì, cách nhìn nhận tích cực về cơ thể và chăm sóc sức khỏe.",
        "questions": [
            {
                "question_text": "Thông điệp chính của video “Am I Normal?” là gì?",
                "options": [
                    "Dậy thì có thể diễn ra theo nhịp khác nhau",
                    "Mọi người thay đổi cùng ngày",
                    "Chậm hơn bạn nghĩa là sai",
                    "Chỉ một kiểu cơ thể là chuẩn",
                ],
                "correct_index": 0,
                "explanation": "Nhịp dậy thì khác nhau.",
            },
            {
                "question_text": "Khi con so sánh chiều cao với bạn, phụ huynh nên?",
                "options": [
                    "Chê con yếu",
                    "Công nhận lo lắng và nhắc sự khác nhau về nhịp lớn lên",
                    "So sánh thêm với nhiều bạn",
                    "Coi video là chẩn đoán",
                ],
                "correct_index": 1,
                "explanation": "Tránh so sánh mang tính đánh giá.",
            },
            {
                "question_text": "Ai nên học kiến thức về kinh nguyệt và xuất tinh trong khi ngủ?",
                "options": [
                    "Chỉ người có kinh nguyệt",
                    "Chỉ người có xuất tinh",
                    "Mọi học sinh",
                    "Không ai trước 18 tuổi",
                ],
                "correct_index": 2,
                "explanation": "Hiểu biến đổi cơ thể giúp tôn trọng nhau.",
            },
            {
                "question_text": "Nếu thay đổi cơ thể gây đau hoặc ảnh hưởng sinh hoạt, nên?",
                "options": [
                    "Dựa vào bình luận mạng",
                    "Giữ kín dù lo lắng",
                    "So chiều cao với bạn",
                    "Hỏi nhân viên y tế có chuyên môn",
                ],
                "correct_index": 3,
                "explanation": "Lo lắng y tế cần đánh giá cụ thể.",
            },
            {
                "question_text": "Điều nào không nên làm trong bài tập đôi?",
                "options": [
                    "Bình phẩm ngoại hình thực của người cùng học",
                    "Nói về khác biệt giữa người",
                    "Hỏi câu hỏi chung",
                    "Tìm nguồn y tế",
                ],
                "correct_index": 0,
                "explanation": "Không bình phẩm giúp giữ không gian an toàn.",
            },
            {
                "question_text": "Da và mùi cơ thể thay đổi có thể là?",
                "options": [
                    "Bằng chứng mọi người giống nhau",
                    "Một số thay đổi liên quan dậy thì",
                    "Dấu hiệu người đó xấu",
                    "Lý do để trêu bạn",
                ],
                "correct_index": 1,
                "explanation": "Các thay đổi cơ thể thường gặp cần cách chăm sóc phù hợp.",
            },
            {
                "question_text": "Nếu con hỏi “Tại sao mình chưa giống bạn?”, nên?",
                "options": [
                    "Khẳng định con có bệnh",
                    "Bắt con giống bạn",
                    "Trả lời rằng thời điểm và biểu hiện thay đổi đa dạng",
                    "Không cho con hỏi",
                ],
                "correct_index": 2,
                "explanation": "Trấn an có căn cứ và sẵn sàng tìm y tế khi cần.",
            },
            {
                "question_text": "Dậy thì tác động đến khía cạnh nào?",
                "options": [
                    "Chỉ điểm số",
                    "Chỉ giọng nói tất cả mọi người",
                    "Chỉ bạn bè",
                    "Cơ thể và có thể cả cảm xúc",
                ],
                "correct_index": 3,
                "explanation": "Thay đổi có thể đa dạng.",
            },
            {
                "question_text": "Đạt điểm quiz có thay thế tư vấn y tế cá nhân?",
                "options": [
                    "Không",
                    "Có",
                    "Có nếu 100%",
                    "Có nếu xem hai lần",
                ],
                "correct_index": 0,
                "explanation": "Quiz củng cố kiến thức chung.",
            },
            {
                "question_text": "Một câu khẳng định tôn trọng là?",
                "options": [
                    "“Bạn phát triển không đúng”",
                    "“Mỗi cơ thể có nhịp phát triển riêng”",
                    "“Chỉ một giới cần biết”",
                    "“Không hỏi người lớn”",
                ],
                "correct_index": 1,
                "explanation": "Không gắn giá trị người với thời điểm dậy thì.",
            },
        ],
    },
    {
        "order_index": 3,
        "title": "Bài 3 — Câu hỏi khó cũng được hỏi ở nhà",
        "video_url": "https://www.youtube.com/watch?v=1wg_a0HCqvA",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Ngượng vẫn có thể hỏi
Video của AMAZE (*Talking With Your Parents About Sex*) ghi nhận cảm giác ngại ngùng, lúng túng rất tự nhiên khi con cái hỏi cha mẹ về dậy thì và tình dục. Tuy nhiên, người lớn tin cậy luôn là nguồn hỗ trợ quan trọng. Học sinh không cần phải thú nhận hay kể hết mọi chi tiết riêng tư mới có quyền nhận thông tin khoa học, chính xác.

### 2. Hai cách bắt đầu câu chuyện
- **Trực tiếp:** *“Con muốn tìm hiểu về...”* hoặc *“Dạo này con thấy có thông tin này trên mạng...”*.
- **Gián tiếp:** Gửi mẩu giấy nhắn hoặc tin nhắn hẹn trước: *“Khi nào rảnh bố/mẹ nói chuyện với con một lát nhé?”*.
- **Phản hồi từ phụ huynh:** *“Cảm ơn con đã tin tưởng hỏi bố mẹ. Bố mẹ sẽ lắng nghe, nếu điều gì chưa rõ mình sẽ cùng tra cứu tài liệu rồi nói tiếp nhé.”*

### 3. Thỏa thuận nhịp độ đối thoại
Nên trao đổi từng chủ đề ngắn, cho phép tạm dừng nếu cảm thấy ngượng và hẹn quay lại sau. Nếu câu hỏi liên quan đến sức khỏe sinh sản khẩn cấp hoặc an toàn cá nhân, hãy cùng tìm đến chuyên gia y tế hoặc người lớn tin cậy ngay.

### 4. Thực hành hai vai
Một bên đóng vai người hỏi: *“Con nghe bạn nói rằng dậy thì ai cũng phát triển giống hệt nhau, có đúng không?”*, bên kia trả lời ngắn gọn, chân thành và hỏi lại con đang băn khoăn hay lo lắng điều gì nhất.

> [!NOTE]
> **Tài liệu tham khảo đối chiếu:** [AMAZE — Talking With Your Parents About Sex](https://amaze.org/parents/)
""",
        "quiz_title": "Củng cố bài 3 — Câu hỏi khó cũng được hỏi ở nhà",
        "quiz_description": "Bài trắc nghiệm 10 câu về cách mở lời trao đổi giữa cha mẹ và con cái về dậy thì, giới tính và tình dục.",
        "questions": [
            {
                "question_text": "Video nêu cảm giác thường gặp khi hỏi cha mẹ?",
                "options": [
                    "Có thể thấy ngượng hoặc khó mở lời",
                    "Luôn hoàn toàn dễ dàng",
                    "Luôn vô ích",
                    "Lúc nào cũng phải kể bí mật",
                ],
                "correct_index": 0,
                "explanation": "AMAZE thừa nhận sự ngại ngùng.",
            },
            {
                "question_text": "Người lớn tin cậy có thể làm gì?",
                "options": [
                    "Chỉ trách mắng",
                    "Lắng nghe và giúp tìm thông tin phù hợp",
                    "Đòi kể toàn bộ chi tiết",
                    "Thay mọi bác sĩ",
                ],
                "correct_index": 1,
                "explanation": "Người lớn có thể hỗ trợ trong dậy thì.",
            },
            {
                "question_text": "Cách hỏi không trực tiếp có thể là?",
                "options": [
                    "Giữ mọi câu hỏi vĩnh viễn",
                    "Chỉ hỏi tài khoản lạ",
                    "Viết giấy hoặc nhắn xin thời gian nói chuyện",
                    "Đăng danh tính lên mạng",
                ],
                "correct_index": 2,
                "explanation": "Có thể chọn hình thức mở lời.",
            },
            {
                "question_text": "Khi cha mẹ chưa biết, nên nói gì?",
                "options": [
                    "“Đoán vậy chắc đúng”",
                    "“Cấm hỏi nữa”",
                    "“Con tự lo”",
                    "“Mình cùng kiểm tra nguồn, rồi nói tiếp”",
                ],
                "correct_index": 3,
                "explanation": "Thừa nhận chưa biết và quay lại.",
            },
            {
                "question_text": "Trẻ phải kể hết chuyện riêng mới được hỏi kiến thức?",
                "options": [
                    "Không",
                    "Có",
                    "Chỉ khi điểm kém",
                    "Chỉ nếu người lớn muốn",
                ],
                "correct_index": 0,
                "explanation": "Quyền hỏi không phụ thuộc tiết lộ đời tư.",
            },
            {
                "question_text": "Nếu câu hỏi liên quan nguy cơ an toàn ngay, nên?",
                "options": [
                    "Chờ đến quiz tuần sau",
                    "Tìm người tin cậy hoặc hỗ trợ phù hợp kịp thời",
                    "Bỏ qua",
                    "Chỉ hỏi diễn đàn ẩn danh",
                ],
                "correct_index": 1,
                "explanation": "An toàn không nên trì hoãn.",
            },
            {
                "question_text": "Một câu hỏi mở tốt từ phụ huynh là?",
                "options": [
                    "“Ai dạy con hỏi chuyện đó?”",
                    "“Con hỏi vì đã làm sai à?”",
                    "“Con đang muốn hiểu phần nào?”",
                    "“Con phải kể ngay”",
                ],
                "correct_index": 2,
                "explanation": "Hỏi để hiểu nhu cầu, tránh quy kết.",
            },
            {
                "question_text": "Nếu lần đầu nói chuyện lúng túng, gia đình nên?",
                "options": [
                    "Bỏ luôn chủ đề",
                    "Chê người hỏi",
                    "Đòi nói hết ngay",
                    "Cho phép tạm dừng và quay lại",
                ],
                "correct_index": 3,
                "explanation": "Đối thoại có thể chia nhiều lần.",
            },
            {
                "question_text": "Bài tập hai vai có thể dùng gì?",
                "options": [
                    "Câu hỏi giả định về dậy thì",
                    "Buộc kể chuyện riêng",
                    "Đưa hồ sơ y tế cá nhân",
                    "Đọc tin nhắn của nhau",
                ],
                "correct_index": 0,
                "explanation": "Giả định giúp thực hành an toàn.",
            },
            {
                "question_text": "Mục tiêu chính của bài là?",
                "options": [
                    "Chấm điểm sự vâng lời",
                    "Tạo đường hỏi đáp với người lớn tin cậy",
                    "Loại bỏ hoàn toàn ngượng",
                    "Buộc cha mẹ biết mọi thứ",
                ],
                "correct_index": 1,
                "explanation": "Mở kênh hỏi đáp đáng tin.",
            },
        ],
    },
    {
        "order_index": 4,
        "title": "Bài 4 — Quyền riêng tư của con, sự quan tâm của cha mẹ",
        "video_url": "https://www.youtube.com/watch?v=t1axo8Sz3_g",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Cân bằng hai nhu cầu
Dựa trên hướng dẫn từ Child Mind Institute (*How do I promote my child’s healthy use of technology?*), video phân tích sự cân bằng tinh tế giữa nhu cầu kết nối xã hội của trẻ và trách nhiệm bảo vệ an toàn của phụ huynh. Gia đình cần cùng nhau xây dựng các quy tắc rõ ràng về thiết bị, thời lượng, thiết lập bảo mật và các ngoại lệ an toàn bắt buộc phải thông báo.

### 2. Minh bạch về quyền riêng tư
Cha mẹ giải thích rõ lý do cần có các biện pháp an toàn thay vì âm thầm đọc trộm tin nhắn; con có quyền được hỏi về phạm vi giám sát và thẳng thắn bày tỏ cảm xúc khi thấy ranh giới riêng tư bị xâm phạm. Việc thống nhất trước các trường hợp can thiệp giúp xây dựng sự tin tưởng vững chắc giữa hai bên.

### 3. Dấu hiệu cần báo ngay lập tức
Khi bị đe dọa, quấy rối, tống tiền, ép gửi hình ảnh nhạy cảm, bắt giữ bí mật gây lo sợ hoặc đối mặt với bất kỳ nguy cơ tổn hại nào, con cần báo ngay cho cha mẹ hoặc người lớn tin cậy. Phụ huynh cam kết phản hồi bằng sự thấu hiểu, bình tĩnh và tuyệt đối không đổ lỗi.

### 4. Bài tập chung: Bảng thỏa thuận hai cột
Hai bên cùng lập bảng thỏa thuận:
- **Cột 1: Con có thể tự quyết:** Tự chọn thời gian trò chuyện với bạn bè, quản lý sở thích cá nhân phù hợp lứa tuổi.
- **Cột 2: Bố mẹ sẽ hỗ trợ khi:** Con gặp đe dọa trên mạng, tiếp xúc nội dung độc hại, hoặc cần báo cáo nền tảng / liên hệ Tổng đài 111 bảo vệ trẻ em.

> [!NOTE]
> **Tài liệu tham khảo đối chiếu:** [Child Mind Institute — Healthy Technology Use](https://childmind.org/positiveparenting/healthy-technology-use/)
""",
        "quiz_title": "Củng cố bài 4 — Quyền riêng tư của con, sự quan tâm của cha mẹ",
        "quiz_description": "Bài trắc nghiệm 10 câu về ranh giới riêng tư số, sự đồng hành của phụ huynh và kỹ năng ứng phó nguy cơ trực tuyến.",
        "questions": [
            {
                "question_text": "Video Child Mind nói về cân bằng nào?",
                "options": [
                    "Kết nối công nghệ và an toàn số",
                    "Cấm mọi công nghệ",
                    "Cho toàn bộ thời gian màn hình tùy ý",
                    "Chỉ điểm số",
                ],
                "correct_index": 0,
                "explanation": "Nguồn nêu cân bằng kết nối và bảo vệ.",
            },
            {
                "question_text": "Quy tắc gia đình tốt cần gì?",
                "options": [
                    "Giữ bí mật tuyệt đối với con",
                    "Thống nhất rõ mục đích, phạm vi và ngoại lệ an toàn",
                    "Thay đổi tùy cảm xúc",
                    "Không cần lý do",
                ],
                "correct_index": 1,
                "explanation": "Minh bạch giúp hợp tác.",
            },
            {
                "question_text": "Nếu trẻ bị ép gửi hình, điều nào cần ưu tiên?",
                "options": [
                    "Làm theo người ép",
                    "Giữ một mình",
                    "Báo người lớn tin cậy và tìm hỗ trợ an toàn",
                    "Đổ lỗi cho bản thân",
                ],
                "correct_index": 2,
                "explanation": "Nguy cơ trực tuyến cần hỗ trợ.",
            },
            {
                "question_text": "Cha mẹ hỗ trợ riêng tư bằng cách?",
                "options": [
                    "Đọc lén mọi cuộc trò chuyện mặc định",
                    "Đăng ảnh con để hỏi",
                    "Chê con ngại",
                    "Giải thích trước các biện pháp an toàn và lắng nghe",
                ],
                "correct_index": 3,
                "explanation": "Quan tâm đi cùng minh bạch.",
            },
            {
                "question_text": "Trong bài tập chung, cột “Bố mẹ hỗ trợ khi” nên ghi?",
                "options": [
                    "Tình huống bị đe dọa hoặc không an toàn",
                    "Mọi suy nghĩ riêng của con",
                    "Bất cứ khi nào bố mẹ tò mò",
                    "Chỉ khi con đạt điểm tốt",
                ],
                "correct_index": 0,
                "explanation": "Ngoại lệ liên quan an toàn cần nêu rõ.",
            },
            {
                "question_text": "Quyền riêng tư của trẻ có nghĩa là?",
                "options": [
                    "Không cần người lớn nào",
                    "Có không gian phù hợp tuổi và đường nhờ trợ giúp",
                    "Có thể tự xử mọi nguy hiểm",
                    "Không ai được hỏi con có an toàn",
                ],
                "correct_index": 1,
                "explanation": "Quyền riêng tư và an toàn cùng được tôn trọng.",
            },
            {
                "question_text": "Khi con không đồng ý phạm vi kiểm tra, nên?",
                "options": [
                    "Bắt im lặng",
                    "Đăng tranh cãi",
                    "Lắng nghe và giải thích lý do, điều chỉnh thỏa thuận",
                    "Bỏ hết quy tắc",
                ],
                "correct_index": 2,
                "explanation": "Thỏa thuận cần trao đổi hai chiều.",
            },
            {
                "question_text": "Câu trả lời đầu khi trẻ báo bị đe dọa?",
                "options": [
                    "“Tại con thôi”",
                    "“Đừng kể nữa”",
                    "“Đưa mọi mật khẩu cho mọi người”",
                    "“Cảm ơn con đã nói, mình cùng xử lý”",
                ],
                "correct_index": 3,
                "explanation": "Không đổ lỗi giữ kênh bảo vệ.",
            },
            {
                "question_text": "Biện pháp an toàn số cần điều chỉnh theo gì?",
                "options": [
                    "Độ tuổi và khả năng tự quản của trẻ",
                    "Chỉ theo giới",
                    "Chỉ theo sở thích người lớn",
                    "Không bao giờ thay đổi",
                ],
                "correct_index": 0,
                "explanation": "Nhu cầu thay đổi khi trẻ lớn.",
            },
            {
                "question_text": "Sản phẩm bài tập chung là gì?",
                "options": [
                    "Bản công khai nhật ký chat",
                    "Một thỏa thuận có quyền tự chủ và kênh hỗ trợ",
                    "Danh sách phải khai đời tư",
                    "Bài kiểm tra bí mật",
                ],
                "correct_index": 1,
                "explanation": "Thỏa thuận giúp hai bên hiểu mong đợi.",
            },
        ],
    },
    {
        "order_index": 5,
        "title": "Bài 5 — Lời đồn lan nhanh: nhà mình kiểm chứng thế nào?",
        "video_url": "https://www.youtube.com/watch?v=-b8fceyd-ik",
        "duration_minutes": 13,
        "content_type": "HYBRID",
        "content_body": """### 1. Ba câu hỏi kiểm chứng từ Khan Academy
Video từ Khan Academy (*How to spot misinformation*) hướng dẫn quy trình 3 bước cốt lõi để xác thực thông tin số:
1. **Ai là người đưa ra tuyên bố?** Tác giả/tổ chức có uy tín, chuyên môn và danh tính rõ ràng không?
2. **Bằng chứng nào hỗ trợ cho tuyên bố đó?** Có số liệu nghiên cứu, trích dẫn khoa học hay chỉ là phán đoán cá nhân?
3. **Các nguồn độc lập đáng tin cậy khác nói gì?** So sánh chéo với các tổ chức y tế, khoa học chính thống.

Quy trình này áp dụng trực tiếp để sàng lọc các lời đồn thất thiệt về tuổi dậy thì và cơ thể.

### 2. Thử nghiệm với một lời đồn giả định
- **Tuyên bố:** *“Ai dậy thì muộn hơn bạn bè đồng trang lứa đều là bị mắc bệnh lý nghiêm trọng.”*
- **Kiểm chứng:** Tìm nguồn phát ngôn, xem xét bằng chứng và đối chiếu tài liệu từ các cơ quan y tế (WHO, Bộ Y tế, các viện nhi khoa).
- **Kết luận khoa học:** Thời điểm dậy thì diễn ra trong một khung sinh học rất rộng và chịu ảnh hưởng của nhiều yếu tố; nếu có băn khoăn cá nhân, cần tham vấn bác sĩ chuyên khoa chứ không tự ý lo sợ hay chẩn đoán qua mạng.

### 3. Nguyên tắc ngăn chặn tin sai
Nếu thông tin chưa được kiểm chứng, tuyệt đối không bấm nút chia sẻ. Ảnh chụp màn hình mờ ảo, số lượng lượt xem/like khủng hay giọng điệu hùng hồn giật tít không thể thay thế cho bằng chứng khoa học.

### 4. Bài tập đôi: Sàng lọc thông tin sức khỏe
Hai người cùng chọn một khẳng định về cơ thể đang lan truyền trên mạng, áp dụng 3 câu hỏi trên và tra cứu từ 2 nguồn chính thống. Nếu chưa đủ căn cứ chứng minh, hãy cùng ghi chú lại trạng thái: *“Chưa xác minh”* thay vì vội vàng tin tưởng.

> [!NOTE]
> **Tài liệu tham khảo đối chiếu:** [UNICEF — A quick guide to spotting misinformation](https://www.unicef.org/eca/stories/quick-guide-spotting-misinformation)
""",
        "quiz_title": "Củng cố bài 5 — Lời đồn lan nhanh: nhà mình kiểm chứng thế nào?",
        "quiz_description": "Bài trắc nghiệm 10 câu về kỹ năng tư duy phản biện, 3 bước kiểm chứng tin đồn sức khỏe và văn hóa chia sẻ an toàn.",
        "questions": [
            {
                "question_text": "Video Khan Academy gợi ý hỏi gì đầu tiên?",
                "options": [
                    "Ai là người đưa ra tuyên bố?",
                    "Có bao nhiêu lượt thích?",
                    "Ảnh nền có đẹp không?",
                    "Bạn bè có gửi không?",
                ],
                "correct_index": 0,
                "explanation": "Tác giả là một yếu tố kiểm chứng.",
            },
            {
                "question_text": "Tiếp theo cần xem?",
                "options": [
                    "Số biểu tượng cảm xúc",
                    "Bằng chứng nào hỗ trợ tuyên bố",
                    "Màu giao diện",
                    "Nhạc nền",
                ],
                "correct_index": 1,
                "explanation": "Bằng chứng quan trọng hơn hình thức.",
            },
            {
                "question_text": "Bước đối chiếu cần gì?",
                "options": [
                    "Một bình luận duy nhất",
                    "Tin nhắn không nguồn",
                    "Nguồn độc lập đáng tin khác",
                    "Tài khoản ẩn danh",
                ],
                "correct_index": 2,
                "explanation": "So sánh nguồn đáng tin giúp kiểm chứng.",
            },
            {
                "question_text": "Nếu chưa có chứng cứ cho lời đồn sức khỏe?",
                "options": [
                    "Kết luận chắc chắn đúng",
                    "Đăng nhanh",
                    "Chỉ hỏi số lượt xem",
                    "Ghi chưa xác minh và không vội chia sẻ",
                ],
                "correct_index": 3,
                "explanation": "Tạm dừng giảm lan tin sai.",
            },
            {
                "question_text": "Lượt xem lớn có là bằng chứng y tế?",
                "options": [
                    "Không",
                    "Có, luôn luôn",
                    "Có nếu video ngắn",
                    "Có nếu nhiều bình luận",
                ],
                "correct_index": 0,
                "explanation": "Sự phổ biến không chứng minh độ đúng.",
            },
            {
                "question_text": "Nguồn tốt cho câu hỏi dậy thì thường là?",
                "options": [
                    "Quảng cáo giấu tác giả",
                    "Tổ chức y tế/giáo dục sức khỏe có trách nhiệm và thông tin cập nhật",
                    "Tài khoản không ghi nguồn",
                    "Bài đăng chỉ có ảnh",
                ],
                "correct_index": 1,
                "explanation": "Cần nguồn xác định và có căn cứ.",
            },
            {
                "question_text": "Nếu con đưa lời đồn “dậy thì muộn là bệnh”, cha mẹ nên?",
                "options": [
                    "Cười nhạo người hỏi",
                    "Khẳng định có bệnh ngay",
                    "Cùng tra nguồn và hỏi chuyên môn khi có lo lắng riêng",
                    "Phát tán lời đồn",
                ],
                "correct_index": 2,
                "explanation": "Kiểm chứng rồi mới đánh giá cá nhân.",
            },
            {
                "question_text": "Quy trình video áp dụng trực tiếp cho kiến thức giới tính?",
                "options": [
                    "Là chẩn đoán y khoa",
                    "Là hướng dẫn điều trị",
                    "Không thể áp dụng",
                    "Là phương pháp kiểm tra chung, sau đó dùng nguồn y tế chuyên môn",
                ],
                "correct_index": 3,
                "explanation": "Cần phân biệt phương pháp với nội dung chuyên ngành.",
            },
            {
                "question_text": "Khi hai nguồn đáng tin mâu thuẫn, nên?",
                "options": [
                    "Xem ngày, phạm vi và hỏi chuyên môn nếu liên quan sức khỏe",
                    "Chọn nguồn nhiều lượt xem",
                    "Chọn nguồn giật tít",
                    "Bỏ mọi nguồn",
                ],
                "correct_index": 0,
                "explanation": "Bối cảnh và cập nhật quan trọng.",
            },
            {
                "question_text": "Đầu ra bài tập đôi là gì?",
                "options": [
                    "Chỉ lượt xem",
                    "Tuyên bố, tác giả, bằng chứng và nguồn đối chiếu",
                    "Chỉ ảnh chụp",
                    "Chỉ ý kiến một người",
                ],
                "correct_index": 1,
                "explanation": "Ghi lại cách kiểm chứng có thể xem lại.",
            },
        ],
    },
    {
        "order_index": 6,
        "title": "Bài 6 — Chưa sẵn sàng nói trực tiếp: nhà mình chọn tín hiệu nào?",
        "video_url": None,
        "duration_minutes": 16,
        "content_type": "TEXT",
        "content_body": """### 1. Cùng thiết kế kênh giao tiếp linh hoạt
Không phải lúc nào phụ huynh và học sinh cũng cảm thấy sẵn sàng để bắt đầu một cuộc trò chuyện trực diện mặt-đối-mặt. Học sinh hoàn toàn có thể lựa chọn các kênh gián tiếp: để lại mẩu giấy nhắn trên bàn làm việc, gửi một tin nhắn riêng, hoặc sử dụng một câu tín hiệu đã quy ước trước:
> *“Con muốn hỏi bố/mẹ một chuyện nhưng hiện tại con chưa tiện nói trực tiếp ngay.”*
Phụ huynh nhận tín hiệu, xác nhận đã tiếp nhận và hai bên hẹn trước một thời điểm cụ thể, thư thả để cùng trao đổi.

### 2. Quy ước đối thoại 3 bước an toàn
1. **Bước 1 — Người hỏi chủ động:** Chọn phương thức mở lời (nhắn tin/viết giấy) và nêu chủ đề muốn tìm hiểu mà không bị ép buộc phải tiết lộ đời tư cá nhân.
2. **Bước 2 — Người nghe xác nhận:** Phản hồi ghi nhận, hỏi xem có điều gì cấp bách đe dọa an toàn không, và đề xuất một khung giờ thuận tiện để trao đổi.
3. **Bước 3 — Cùng nhau thực hiện:** Đúng thời điểm đã hẹn, hai bên ngồi lại trò chuyện với thái độ cởi mở; có thể cùng tìm kiếm thêm sự hỗ trợ từ chuyên gia nếu cần.

### 3. Ngoại lệ an toàn khẩn cấp
Nếu phát hiện tình huống bị đe dọa, xâm hại thân thể, quấy rối tình dục hoặc có nguy cơ tự gây hại, quy trình hẹn lịch phải được gác lại; lập tức liên hệ người lớn tin cậy, dịch vụ y tế khẩn cấp hoặc gọi đến **Tổng đài Quốc gia Bảo vệ Trẻ em 111** (miễn phí 24/7 tại Việt Nam).

### 4. Lời khuyên xây dựng cầu nối đối thoại gia đình
- **Linh hoạt các hình thức trò chuyện:** Mỗi gia đình và từng đứa trẻ đều có tính cách khác nhau. Việc cho phép sử dụng tin nhắn, giấy nhắn hay tín hiệu quy ước trước giúp giảm bớt cảm giác ngượng ngùng ban đầu và mở ra cánh cửa cho những cuộc trao đổi sâu sắc hơn sau này.
- **Lắng nghe chân thành và tôn trọng ranh giới:** Người lớn cần thể hiện sự đón nhận bình tĩnh, ghi nhận sự can đảm của con khi đặt câu hỏi và không ép con phải kể toàn bộ chi tiết riêng tư mới giải đáp thắc mắc.
- **Cùng nhau đồng hành tìm kiếm câu trả lời:** Nếu gặp những vấn đề chưa rõ, cha mẹ và con cái có thể cùng nhau tra cứu từ các nguồn giáo dục sức khỏe chính thống, biến quá trình học tập thành trải nghiệm gắn kết tình cảm gia đình.

> [!TIP]
> **Nguồn tài liệu tham khảo chuyên môn:**
> - [Planned Parenthood — Cẩm nang hướng dẫn cha mẹ trò chuyện cùng con](https://www.plannedparenthood.org/learn/parents/tips-talking)
> - [AMAZE — Nguồn tài liệu giáo dục giới tính dành cho phụ huynh](https://amaze.org/parents/)
> - [Child Mind Institute — Kỹ năng giao tiếp thấu cảm với trẻ tuổi teen](https://childmind.org/article/tips-communicating-with-teen/)
""",
        "quiz_title": "Củng cố bài 6 — Chưa sẵn sàng nói trực tiếp: nhà mình chọn tín hiệu nào?",
        "quiz_description": "Bài trắc nghiệm 10 câu củng cố quy ước tín hiệu mở lời gián tiếp, thỏa thuận đối thoại gia đình và nguyên tắc bảo vệ khẩn cấp.",
        "questions": [
            {
                "question_text": "Nếu con muốn hỏi nhưng chưa sẵn sàng nói, có thể?",
                "options": [
                    "Dùng giấy nhắn hoặc tin nhắn riêng",
                    "Không được hỏi",
                    "Chỉ đăng công khai",
                    "Bắt phải nói trước lớp",
                ],
                "correct_index": 0,
                "explanation": "Kênh thay thế giúp bắt đầu.",
            },
            {
                "question_text": "Phụ huynh nhận tin nhắn nên?",
                "options": [
                    "Giả vờ không đọc",
                    "Xác nhận đã nhận và hẹn lúc cùng nói",
                    "Chuyển tiếp cho họ hàng",
                    "Bắt trả lời ngay mọi điều",
                ],
                "correct_index": 1,
                "explanation": "Xác nhận và giữ lời hẹn xây tin cậy.",
            },
            {
                "question_text": "Cần hỏi trước khi trì hoãn cuộc nói chuyện?",
                "options": [
                    "Điểm kiểm tra gần nhất",
                    "Ai đang theo dõi mạng xã hội",
                    "Có tình huống nào khẩn cấp hoặc không an toàn không",
                    "Con có vâng lời không",
                ],
                "correct_index": 2,
                "explanation": "Ngoại lệ an toàn phải xử lý ngay.",
            },
            {
                "question_text": "Người hỏi có phải kể toàn bộ chuyện riêng để được giải đáp?",
                "options": [
                    "Có",
                    "Chỉ khi cha mẹ yêu cầu",
                    "Chỉ khi cả lớp xem",
                    "Không",
                ],
                "correct_index": 3,
                "explanation": "Có thể hỏi một phần thông tin.",
            },
            {
                "question_text": "Hẹn nói tiếp nên thế nào?",
                "options": [
                    "Nêu thời điểm cụ thể và thực sự quay lại",
                    "Chỉ nói “để sau” vô hạn",
                    "Luôn hủy khi ngượng",
                    "Không phản hồi",
                ],
                "correct_index": 0,
                "explanation": "Lời hẹn đáng tin cần thực hiện.",
            },
            {
                "question_text": "Nếu người đầu không giúp được, học sinh có thể?",
                "options": [
                    "Dừng mọi tìm trợ giúp",
                    "Tìm người lớn tin cậy khác hoặc chuyên gia phù hợp",
                    "Chỉ hỏi tài khoản ẩn danh",
                    "Chịu đựng một mình",
                ],
                "correct_index": 1,
                "explanation": "Nhiều kênh hỗ trợ tạo an toàn.",
            },
            {
                "question_text": "Thỏa thuận có nên dùng cho tình huống nguy hiểm tức thời?",
                "options": [
                    "Có, đợi vài tuần",
                    "Có, chỉ nhắn giấy",
                    "Không chờ lịch; tìm trợ giúp ngay",
                    "Có, đợi quiz",
                ],
                "correct_index": 2,
                "explanation": "Ngoại lệ an toàn cần can thiệp kịp thời.",
            },
            {
                "question_text": "Trong thỏa thuận, ai được chọn cách mở lời?",
                "options": [
                    "Chỉ người ngoài",
                    "Chỉ hệ thống quiz",
                    "Chỉ mạng xã hội",
                    "Học sinh và phụ huynh cùng trao đổi để chọn kênh phù hợp",
                ],
                "correct_index": 3,
                "explanation": "Cùng chọn tăng khả năng sử dụng.",
            },
            {
                "question_text": "Video NotebookLM cần tránh điều gì?",
                "options": [
                    "Ép kể chuyện riêng hoặc phân nội dung theo giới",
                    "Có tình huống thực hành",
                    "Dẫn nguồn",
                    "Cho phép nói tiếp",
                ],
                "correct_index": 0,
                "explanation": "Khóa cùng học phải tôn trọng mọi người học.",
            },
            {
                "question_text": "Trước xuất bản quiz bài NotebookLM, cần?",
                "options": [
                    "Chỉ nhìn tên file",
                    "Đối chiếu từng câu với lời thoại video cuối",
                    "Tin mọi nội dung AI",
                    "Không kiểm tra nguồn",
                ],
                "correct_index": 1,
                "explanation": "Quiz phải bám video thực tế.",
            },
        ],
    },
]

async def seed_course_7():
    async with AsyncSessionLocal() as session:
        print("Starting seed for Course 7: Nhà Mình Nói Chuyện Về Cơ Thể Được Mà!...")

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
        print(f"Created Course 7: {course.title} (ID: {course_id})")

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
        print("SEEDING COURSE 7 COMPLETED SUCCESSFULLY!")
        print(f"Course: {COURSE_DATA['title']}")
        print(f"Target Audience: {COURSE_DATA['target_audience']}")
        print(f"Lessons: {len(LESSONS_DATA)}")
        print(f"Quizzes: {len(LESSONS_DATA)}")
        print(f"Total Questions: {total_questions}")
        print(f"Total Options: {total_options}")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(seed_course_7())
