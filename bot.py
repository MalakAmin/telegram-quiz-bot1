# 🧮 بوت اختبارات رياضيات النهايات (Limits) - صح/خطأ + خيارات متعددة
# 👨🏫 للمرحلة الثانوية والجامعية

import os
import asyncio
import json
import random
import math
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔐 التوكن من متغيرات البيئة
TOKEN = os.environ.get('TELEGRAM_TOKEN', 'ضع_توكنك_هنا')

# 👨🏫 رقم المعلم
TEACHER_ID = 123456789  # غير هذا الرقم!

# 📊 قاعدة البيانات
class MathDatabase:
    def __init__(self):
        self.data_file = 'math_limits_data.json'
        self.data = self.load_data()
    
    def load_data(self):
        """تحميل البيانات"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                'students': {},
                'stats': {
                    'total_true_false': 0,
                    'total_mcqs': 0,
                    'correct_true_false': 0,
                    'correct_mcqs': 0,
                    'topics': {}
                },
                'created_at': datetime.now().isoformat()
            }
    
    def save_data(self):
        """حفظ البيانات"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def register_student(self, user_id, name):
        """تسجيل طالب جديد"""
        user_id = str(user_id)
        if user_id not in self.data['students']:
            self.data['students'][user_id] = {
                'name': name,
                'joined': datetime.now().isoformat(),
                'true_false': {'correct': 0, 'total': 0},
                'mcqs': {'correct': 0, 'total': 0},
                'last_active': datetime.now().isoformat(),
                'level': 'مبتدئ',
                'topics': {}
            }
            self.save_data()
            return True
        return False
    
    def update_score(self, user_id, question_type, is_correct, topic=None):
        """تحديث النتيجة"""
        user_id = str(user_id)
        
        if user_id not in self.data['students']:
            return {'correct': 0, 'total': 0}
        
        student = self.data['students'][user_id]
        student['last_active'] = datetime.now().isoformat()
        
        # تحديث إحصاءات الطالب
        student[question_type]['total'] += 1
        if is_correct:
            student[question_type]['correct'] += 1
        
        # تحديث إحصاءات الموضوع
        if topic:
            if topic not in student['topics']:
                student['topics'][topic] = {'correct': 0, 'total': 0}
            student['topics'][topic]['total'] += 1
            if is_correct:
                student['topics'][topic]['correct'] += 1
        
        # تحديث الإحصائيات العامة
        self.data['stats'][f'total_{question_type}'] += 1
        if is_correct:
            self.data['stats'][f'correct_{question_type}'] += 1
        
        # تحديث إحصائيات الموضوع العام
        if topic:
            if topic not in self.data['stats']['topics']:
                self.data['stats']['topics'][topic] = {'correct': 0, 'total': 0}
            self.data['stats']['topics'][topic]['total'] += 1
            if is_correct:
                self.data['stats']['topics'][topic]['correct'] += 1
        
        # تحديث مستوى الطالب
        total_questions = student['true_false']['total'] + student['mcqs']['total']
        total_correct = student['true_false']['correct'] + student['mcqs']['correct']
        
        if total_questions >= 10:
            percentage = (total_correct / total_questions * 100)
            if percentage >= 80:
                student['level'] = 'ممتاز'
            elif percentage >= 60:
                student['level'] = 'جيد جداً'
            elif percentage >= 40:
                student['level'] = 'متوسط'
            else:
                student['level'] = 'مبتدئ'
        
        self.save_data()
        
        return student[question_type]

# إنشاء قاعدة البيانات
db = MathDatabase()

# 📚 بنك أسئلة النهايات (Limits) في الرياضيات

### 🔵 أسئلة صح/خطأ في النهايات (5 أسئلة)
TRUE_FALSE_LIMITS = [
    {
        "id": 1,
        "question": "lim┬(x→0)〖sin(x)/x = 1〗",
        "correct": True,
        "explanation": "نعم، هذه نهاية أساسية معروفة: lim┬(x→0)〖sin(x)/x = 1〗",
        "difficulty": "متوسط",
        "topic": "النهايات الأساسية"
    },
    {
        "id": 2,
        "question": "lim┬(x→∞)〖1/x = ∞〗",
        "correct": False,
        "explanation": "خطأ، lim┬(x→∞)〖1/x = 0〗 لأن مقام الكسر يكبر بلا حدود",
        "difficulty": "سهل",
        "topic": "النهايات عند اللانهاية"
    },
    {
        "id": 3,
        "question": "إذا lim┬(x→a)〖f(x)〗 موجودة، فإن f(a) يجب أن تكون معرفة",
        "correct": False,
        "explanation": "خطأ، النهاية عند نقطة لا تتطلب أن تكون الدالة معرفة عند تلك النقطة",
        "difficulty": "متوسط",
        "topic": "مفهوم النهاية"
    },
    {
        "id": 4,
        "question": "lim┬(x→0)〖(1 + x)^(1/x) = e〗",
        "correct": True,
        "explanation": "نعم، هذه صيغة النهاية الأساسية للعدد e",
        "difficulty": "صعب",
        "topic": "العدد النيبيري e"
    },
    {
        "id": 5,
        "question": "lim┬(x→2)〖(x² - 4)/(x - 2) = 4〗",
        "correct": True,
        "explanation": "نعم، (x² - 4)/(x - 2) = x + 2 عندما x ≠ 2، والنهاية = 4",
        "difficulty": "سهل",
        "topic": "النهايات الجبرية"
    }
]

### 🔴 أسئلة خيارات متعددة في النهايات (10 أسئلة)
MCQ_LIMITS = [
    {
        "id": 1,
        "question": "ما قيمة: lim┬(x→3)〖(x² - 9)/(x - 3)〗 ؟",
        "options": ["0", "3", "6", "غير موجودة"],
        "correct": 2,
        "explanation": "الحل: (x² - 9)/(x - 3) = x + 3 عندما x ≠ 3، والنهاية = 6",
        "difficulty": "سهل",
        "topic": "النهايات الجبرية"
    },
    {
        "id": 2,
        "question": "ما قيمة: lim┬(x→0)〖(e^x - 1)/x〗 ؟",
        "options": ["0", "1", "e", "∞"],
        "correct": 1,
        "explanation": "هذه نهاية أساسية: lim┬(x→0)〖(e^x - 1)/x = 1〗",
        "difficulty": "متوسط",
        "topic": "النهايات الأسية"
    },
    {
        "id": 3,
        "question": "lim┬(x→∞)〖(3x² + 2x + 1)/(x² + 5)〗 = ?",
        "options": ["0", "1", "3", "∞"],
        "correct": 2,
        "explanation": "النهاية = معامل أعلى درجة في البسط/المقام = 3/1 = 3",
        "difficulty": "سهل",
        "topic": "النهايات عند اللانهاية"
    },
    {
        "id": 4,
        "question": "ما قيمة: lim┬(x→π/2)〖tan(x)〗 ؟",
        "options": ["0", "1", "π/2", "∞"],
        "correct": 3,
        "explanation": "tan(π/2) غير معرفة، والنهاية من اليمين = ∞، ومن اليسار = -∞",
        "difficulty": "متوسط",
        "topic": "النهايات المثلثية"
    },
    {
        "id": 5,
        "question": "lim┬(x→1)〖(√x - 1)/(x - 1)〗 = ?",
        "options": ["0", "1/2", "1", "2"],
        "correct": 1,
        "explanation": "بضرب البسط والمقام في (√x + 1): النهاية = 1/2",
        "difficulty": "متوسط",
        "topic": "النهايات الجذرية"
    },
    {
        "id": 6,
        "question": "ما قيمة: lim┬(x→0)〖(ln(1 + x))/x〗 ؟",
        "options": ["0", "1", "e", "∞"],
        "correct": 1,
        "explanation": "نهاية أساسية: lim┬(x→0)〖ln(1 + x)/x = 1〗",
        "difficulty": "متوسط",
        "topic": "النهايات اللوغاريتمية"
    },
    {
        "id": 7,
        "question": "lim┬(x→∞)〖(1 + 1/x)^x〗 = ?",
        "options": ["0", "1", "e", "∞"],
        "correct": 2,
        "explanation": "هذا تعريف العدد النيبيري e: lim┬(n→∞)〖(1 + 1/n)^n = e〗",
        "difficulty": "صعب",
        "topic": "العدد النيبيري e"
    },
    {
        "id": 8,
        "question": "ما قيمة: lim┬(x→0)〖(1 - cos(x))/x²〗 ؟",
        "options": ["0", "1/2", "1", "2"],
        "correct": 1,
        "explanation": "باستخدام متطابقة مثلثية: النهاية = 1/2",
        "difficulty": "صعب",
        "topic": "النهايات المثلثية"
    },
    {
        "id": 9,
        "question": "lim┬(x→2)〖|x - 2|/(x - 2)〗 = ?",
        "options": ["-1", "0", "1", "غير موجودة"],
        "correct": 3,
        "explanation": "النهاية من اليمين = 1، ومن اليسار = -1، إذن غير موجودة",
        "difficulty": "متوسط",
        "topic": "النهايات بالقيمة المطلقة"
    },
    {
        "id": 10,
        "question": "ما قيمة: lim┬(x→0)〖(sin(3x))/x〗 ؟",
        "options": ["0", "1", "3", "∞"],
        "correct": 2,
        "explanation": "باستخدام lim┬(x→0)〖sin(ax)/(ax) = 1〗: النهاية = 3",
        "difficulty": "متوسط",
        "topic": "النهايات المثلثية"
    }
]

# 🎯 ردود وتقييمات
CORRECT_RESPONSES = [
    "🎯 إجابة صحيحة!",
    "✅ ممتاز! أجبت بشكل صحيح",
    "🏆 أحسنت! هذه الإجابة الصحيحة",
    "⭐ رائع! فهمك دقيق",
    "👏 برافو! إجابة دقيقة"
]

INCORRECT_RESPONSES = [
    "📚 دعني أوضح لك الحل",
    "💡 هذه فرصة للتعلم",
    "🔍 دعنا نراجع المفهوم معاً",
    "🎓 كل خطأ يقربنا من الفهم",
    "🌟 لا تيأس، الرياضيات تحتاج تمرين"
]

# ==================== دوال البوت ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start - بداية المحادثة"""
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name
    
    # تسجيل الطالب
    is_new = db.register_student(user_id, user_name)
    
    if is_new:
        welcome = f"""
🧮 **أهلاً {user_name}!**

مرحباً بك في **بوت اختبارات رياضيات النهايات**!

📚 **الموضوع:** حساب النهايات (Limits)
🎯 **المستوى:** من المبتدئ إلى المتقدم

📋 **أنواع الأسئلة:**
1️⃣ **صح/خطأ** - 5 أسئلة
2️⃣ **خيارات متعددة** - 10 أسئلة

🚀 **ابدأ الآن بالأوامر التالية:**
"""
    else:
        student = db.data['students'][str(user_id)]
        tf_correct = student['true_false']['correct']
        tf_total = student['true_false']['total']
        mcq_correct = student['mcqs']['correct']
        mcq_total = student['mcqs']['total']
        
        tf_percent = (tf_correct/tf_total*100) if tf_total > 0 else 0
        mcq_percent = (mcq_correct/mcq_total*100) if mcq_total > 0 else 0
        
        welcome = f"""
👋 **أهلاً بعودتك {user_name}!**

📊 **إحصائياتك:**
• ✅ صح/خطأ: {tf_correct}/{tf_total} ({tf_percent:.1f}%)
• 🔘 خيارات: {mcq_correct}/{mcq_total} ({mcq_percent:.1f}%)
• 📈 مستواك: **{student['level']}**

🎯 **استمر في التقدم!**
"""
    
    welcome += """
📝 **قائمة الأوامر:**

/start - البداية
/help - المساعدة
/truefalse - 5 أسئلة صح/خطأ في النهايات
/mcq - 10 أسئلة خيارات متعددة في النهايات
/mix - خليط من النوعين
/score - نتيجتك وتقرير مفصل
/top - المتصدرين
/stats - إحصائيات الفصل (للمعلم)
"""
    
    await update.message.reply_text(welcome)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help - المساعدة"""
    help_text = """
🆘 **دليل استخدام بوت النهايات**

🧮 **عن البوت:**
بوت متخصص في اختبارات **رياضيات النهايات (Limits)**
يساعد في فهم مفاهيم النهايات وحسابها

📋 **أنواع الاختبارات:**
/truefalse - 5 أسئلة صح/خطأ
/mcq - 10 أسئلة خيارات متعددة
/mix - خليط من النوعين (15 سؤال)

🎯 **مستويات الصعوبة:**
• 🟢 سهل - أساسيات النهايات
• 🟡 متوسط - نهايات مثلثية وأسية
• 🔴 صعب - نهايات متقدمة

📊 **متابعة التقدم:**
/score - عرض نتيجتك المفصلة
/top - قائمة المتصدرين
/stats - إحصائيات الفصل (للمعلم)

💡 **نصائح:**
1. اقرأ كل سؤال بعناية
2. تأكد من فهم المطلوب
3. استخدم الورقة والقلم إذا احتجت
4. راجع الشرح بعد كل إجابة

📞 **للدعم:** راسل المعلم على حسابه
"""
    
    await update.message.reply_text(help_text)

async def truefalse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/truefalse - أسئلة صح/خطأ"""
    # اختيار 5 أسئلة عشوائية
    questions = random.sample(TRUE_FALSE_LIMITS, min(5, len(TRUE_FALSE_LIMITS)))
    
    # حفظ الأسئلة في سياق المستخدم
    context.user_data['truefalse_questions'] = questions
    context.user_data['current_question'] = 0
    context.user_data['truefalse_answers'] = []
    context.user_data['quiz_type'] = 'truefalse'
    
    await send_truefalse_question(update, context)

async def send_truefalse_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال سؤال صح/خطأ"""
    questions = context.user_data.get('truefalse_questions', [])
    current = context.user_data.get('current_question', 0)
    
    if current >= len(questions):
        await finish_truefalse_quiz(update, context)
        return
    
    question = questions[current]
    
    # أزرار صح/خطأ
    buttons = [
        [InlineKeyboardButton("✅ صحيح", callback_data=f"tf_{question['id']}_true")],
        [InlineKeyboardButton("❌ خطأ", callback_data=f"tf_{question['id']}_false")]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    question_text = f"""
🔵 **سؤال {current + 1} من {len(questions)}**
📚 الموضوع: {question['topic']}
⚡ الصعوبة: {question['difficulty']}

❓ **{question['question']}**

🎯 **اختر الإجابة:**
    """
    
    await update.message.reply_text(question_text, reply_markup=keyboard)

async def handle_truefalse_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إجابة صح/خطأ"""
    query = update.callback_query
    await query.answer()
    
    _, q_id, answer = query.data.split('_')
    q_id = int(q_id)
    user_answer = (answer == 'true')
    
    # البحث عن السؤال
    questions = context.user_data.get('truefalse_questions', [])
    current_q = context.user_data.get('current_question', 0)
    
    question = None
    for q in questions:
        if q['id'] == q_id:
            question = q
            break
    
    if not question:
        await query.edit_message_text("⚠️ حدث خطأ في السؤال")
        return
    
    # التحقق من الإجابة
    is_correct = (user_answer == question['correct'])
    
    # حفظ الإجابة
    if 'truefalse_answers' not in context.user_data:
        context.user_data['truefalse_answers'] = []
    
    context.user_data['truefalse_answers'].append({
        'question_id': q_id,
        'user_answer': user_answer,
        'correct_answer': question['correct'],
        'is_correct': is_correct,
        'explanation': question['explanation'],
        'topic': question['topic']
    })
    
    # تحديث النتيجة
    db.update_score(query.from_user.id, 'true_false', is_correct, question['topic'])
    
    # عرض التقييم
    if is_correct:
        response = f"✅ {random.choice(CORRECT_RESPONSES)}"
        emoji = "🟢"
    else:
        response = f"❌ {random.choice(INCORRECT_RESPONSES)}"
        emoji = "🔴"
    
    feedback = f"""
{emoji} **{response}**

📌 **التوضيح:**
{question['explanation']}

📚 **الموضوع:** {question['topic']}
"""
    
    await query.edit_message_text(feedback)
    
    # الانتقال للسؤال التالي
    context.user_data['current_question'] = current_q + 1
    
    # انتظر قليلاً ثم أرسل السؤال التالي
    await asyncio.sleep(2)
    await send_truefalse_question(update, context)

async def finish_truefalse_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إنهاء اختبار صح/خطأ"""
    answers = context.user_data.get('truefalse_answers', [])
    
    if not answers:
        await update.message.reply_text("📭 لم تجب على أي سؤال!")
        return
    
    # حساب النتيجة
    total = len(answers)
    correct = sum(1 for a in answers if a['is_correct'])
    percentage = (correct / total * 100) if total > 0 else 0
    
    # تحليل المواضيع
    topics = {}
    for answer in answers:
        topic = answer['topic']
        if topic not in topics:
            topics[topic] = {'correct': 0, 'total': 0}
        topics[topic]['total'] += 1
        if answer['is_correct']:
            topics[topic]['correct'] += 1
    
    # بناء تقرير النتيجة
    report = f"""
📊 **نتيجة اختبار صح/خطأ**

✅ **الإجابات الصحيحة:** {correct} من {total}
🎯 **النسبة:** {percentage:.1f}%

📈 **تحليل المواضيع:**
"""
    
    for topic, stats in topics.items():
        topic_percent = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        report += f"• {topic}: {stats['correct']}/{stats['total']} ({topic_percent:.1f}%)\n"
    
    # نصيحة حسب النسبة
    if percentage >= 80:
        report += "\n🏆 **ممتاز!** مستواك متقدم في النهايات"
    elif percentage >= 60:
        report += "\n👍 **جيد جداً!** تحتاج لمراجعة بعض النقاط"
    elif percentage >= 40:
        report += "\n💪 **مستوى مقبول!** واصل التدريب"
    else:
        report += "\n📚 **يحتاج مذاكرة!** راجع أساسيات النهايات"
    
    report += "\n\n🔁 **جرب اختباراً آخر:**"
    report += "\n/truefalse - صح/خطأ جديد"
    report += "\n/mcq - خيارات متعددة"
    report += "\n/score - تفاصيل نتيجتك"
    
    await update.message.reply_text(report)
    
    # مسح بيانات الاختبار
    context.user_data.clear()

async def mcq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/mcq - أسئلة خيارات متعددة"""
    # اختيار 10 أسئلة عشوائية
    questions = random.sample(MCQ_LIMITS, min(10, len(MCQ_LIMITS)))
    
    # حفظ الأسئلة في سياق المستخدم
    context.user_data['mcq_questions'] = questions
    context.user_data['current_mcq'] = 0
    context.user_data['mcq_answers'] = []
    context.user_data['quiz_type'] = 'mcq'
    
    await send_mcq_question(update, context)

async def send_mcq_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال سؤال خيارات متعددة"""
    questions = context.user_data.get('mcq_questions', [])
    current = context.user_data.get('current_mcq', 0)
    
    if current >= len(questions):
        await finish_mcq_quiz(update, context)
        return
    
    question = questions[current]
    
    # تحضير الأزرار
    buttons = []
    letters = ['أ', 'ب', 'ج', 'د']
    
    for i, option in enumerate(question['options']):
        buttons.append([
            InlineKeyboardButton(
                f"{letters[i]}. {option}",
                callback_data=f"mcq_{question['id']}_{i}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    question_text = f"""
🔴 **سؤال {current + 1} من {len(questions)}**
📚 الموضوع: {question['topic']}
⚡ الصعوبة: {question['difficulty']}

❓ **{question['question']}**

🎯 **اختر الإجابة الصحيحة:**
    """
    
    await update.message.reply_text(question_text, reply_markup=keyboard)

async def handle_mcq_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إجابة خيارات متعددة"""
    query = update.callback_query
    await query.answer()
    
    _, q_id, answer_idx = query.data.split('_')
    q_id = int(q_id)
    answer_idx = int(answer_idx)
    
    # البحث عن السؤال
    questions = context.user_data.get('mcq_questions', [])
    current_q = context.user_data.get('current_mcq', 0)
    
    question = None
    for q in questions:
        if q['id'] == q_id:
            question = q
            break
    
    if not question:
        await query.edit_message_text("⚠️ حدث خطأ في السؤال")
        return
    
    # التحقق من الإجابة
    is_correct = (answer_idx == question['correct'])
    
    # حفظ الإجابة
    if 'mcq_answers' not in context.user_data:
        context.user_data['mcq_answers'] = []
    
    letters = ['أ', 'ب', 'ج', 'د']
    context.user_data['mcq_answers'].append({
        'question_id': q_id,
        'user_answer': answer_idx,
        'user_answer_text': question['options'][answer_idx],
        'correct_answer': question['correct'],
        'correct_answer_text': question['options'][question['correct']],
        'is_correct': is_correct,
        'explanation': question['explanation'],
        'topic': question['topic']
    })
    
    # تحديث النتيجة
    db.update_score(query.from_user.id, 'mcqs', is_correct, question['topic'])
    
    # عرض التقييم
    if is_correct:
        response = f"✅ {random.choice(CORRECT_RESPONSES)}"
        emoji = "🟢"
        explanation = f"\n📌 **الإجابة الصحيحة:** {letters[question['correct']]}. {question['options'][question['correct']]}"
    else:
        response = f"❌ {random.choice(INCORRECT_RESPONSES)}"
        emoji = "🔴"
        explanation = f"""
📌 **إجابتك:** {letters[answer_idx]}. {question['options'][answer_idx]}
✅ **الإجابة الصحيحة:** {letters[question['correct']]}. {question['options'][question['correct']]}

🔍 **التوضيح:**
{question['explanation']}"""
    
    feedback = f"""
{emoji} **{response}**
{explanation}

📚 **الموضوع:** {question['topic']}
"""
    
    await query.edit_message_text(feedback)
    
    # الانتقال للسؤال التالي
    context.user_data['current_mcq'] = current_q + 1
    
    # انتظر قليلاً ثم أرسل السؤال التالي
    await asyncio.sleep(2)
    await send_mcq_question(update, context)

async def finish_mcq_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إنهاء اختبار خيارات متعددة"""
    answers = context.user_data.get('mcq_answers', [])
    
    if not answers:
        await update.message.reply_text("📭 لم تجب على أي سؤال!")
        return
    
    # حساب النتيجة
    total = len(answers)
    correct = sum(1 for a in answers if a['is_correct'])
    percentage = (correct / total * 100) if total > 0 else 0
    
    # تحليل المواضيع
    topics = {}
    for answer in answers:
        topic = answer['topic']
        if topic not in topics:
            topics[topic] = {'correct': 0, 'total': 0}
        topics[topic]['total'] += 1
        if answer['is_correct']:
            topics[topic]['correct'] += 1
    
    # بناء تقرير النتيجة
    report = f"""
📊 **نتيجة اختبار الخيارات المتعددة**

✅ **الإجابات الصحيحة:** {correct} من {total}
🎯 **النسبة:** {percentage:.1f}%

📈 **تحليل المواضيع:**
"""
    
    for topic, stats in topics.items():
        topic_percent = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        report += f"• {topic}: {stats['correct']}/{stats['total']} ({topic_percent:.1f}%)\n"
    
    # نصيحة حسب النسبة
    if percentage >= 80:
        report += "\n🏆 **متفوق!** لديك فهم ممتاز للنهايات"
    elif percentage >= 60:
        report += "\n⭐ **جيد جداً!** قريب من التميز"
    elif percentage >= 40:
        report += "\n📚 **مستوى جيد!** واصل التدريب"
    else:
        report += "\n🎯 **يحتاج تركيز!** راجع الأساسيات"
    
    report += "\n\n🔁 **جرب اختباراً آخر:**"
    report += "\n/mcq - خيارات جديدة"
    report += "\n/truefalse - صح/خطأ"
    report += "\n/score - تفاصيل نتيجتك"
    
    await update.message.reply_text(report)
    
    # مسح بيانات الاختبار
    context.user_data.clear()

async def mix_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/mix - خليط من النوعين"""
    # اختيار 3 صح/خطأ و 7 خيارات متعددة
    tf_questions = random.sample(TRUE_FALSE_LIMITS, min(3, len(TRUE_FALSE_LIMITS)))
    mcq_questions = random.sample(MCQ_LIMITS, min(7, len(MCQ_LIMITS)))
    
    # دمج الأسئلة
    all_questions = tf_questions + mcq_questions
    random.shuffle(all_questions)
    
    await update.message.reply_text(
        "🔀 **اختبار مختلط - 10 أسئلة**\n"
        "مزيج من أسئلة صح/خطأ وخيارات متعددة\n\n"
        "📚 ابدأ الآن بـ:\n"
        "/truefalse - لأسئلة صح/خطأ فقط\n"
        "/mcq - لأسئلة خيارات متعددة فقط"
    )

async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/score - عرض النتيجة"""
    user_id = str(update.effective_user.id)
    
    if user_id not in db.data['students']:
        await update.message.reply_text("⚠️ اكتب /start أولاً للتسجيل")
        return
    
    student = db.data['students'][user_id]
    
    tf_correct = student['true_false']['correct']
    tf_total = student['true_false']['total']
    mcq_correct = student['mcqs']['correct']
    mcq_total = student['mcqs']['total']
    
    tf_percent = (tf_correct/tf_total*100) if tf_total > 0 else 0
    mcq_percent = (mcq_correct/mcq_total*100) if mcq_total > 0 else 0
    
    total_correct = tf_correct + mcq_correct
    total_questions = tf_total + mcq_total
    overall_percent = (total_correct/total_questions*100) if total_questions > 0 else 0
    
    # بناء التقرير
    report = f"""
📈 **تقرير أداء: {student['name']}**

🎯 **المستوى:** {student['level']}
📅 **انضم منذ:** {student['joined'][:10]}

📊 **الإحصائيات العامة:**
• ✅ **الإجمالي:** {total_correct}/{total_questions} ({overall_percent:.1f}%)

🔵 **أسئلة صح/خطأ:**
• النسبة: {tf_percent:.1f}%
• الصحيحة: {tf_correct} من {tf_total}

🔴 **أسئلة خيارات متعددة:**
• النسبة: {mcq_percent:.1f}%
• الصحيحة: {mcq_correct} من {mcq_total}
"""
    
    # إضافة تحليل المواضيع
    if student['topics']:
        report += "\n📚 **تحليل المواضيع:**\n"
        
        # ترتيب المواضيع حسب عدد الأسئلة
        sorted_topics = sorted(
            student['topics'].items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )
        
        for topic, stats in sorted_topics[:5]:  # أول 5 مواضيع
            topic_percent = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            report += f"• {topic}: {stats['correct']}/{stats['total']} ({topic_percent:.1f}%)\n"
    
    # توصيات
    report += "\n💡 **التوصيات:**\n"
    
    if total_questions < 5:
        report += "• ابدأ بالإجابة على المزيد من الأسئلة\n"
    elif overall_percent < 50:
        report += "• راجع أساسيات النهايات\n• تدرب على الأسئلة السهلة أولاً\n"
    elif overall_percent < 75:
        report += "• ممتاز! واصل التدريب\n• حاول حل أسئلة أصعب\n"
    else:
        report += "• مذهل! مستواك متقدم\n• يمكنك مساعدة زملائك\n"
    
    report += "\n🚀 **واصل التقدم!**"
    
    await update.message.reply_text(report)

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/top - أفضل الطلاب"""
    if not db.data['students']:
        await update.message.reply_text("🏆 لا توجد نتائج بعد!")
        return
    
    rankings = []
    for user_id, student in db.data['students'].items():
        tf_total = student['true_false']['total']
        mcq_total = student['mcqs']['total']
        total_questions = tf_total + mcq_total
        
        if total_questions >= 5:  # من أجاب على 5 أسئلة على الأقل
            tf_correct = student['true_false']['correct']
            mcq_correct = student['mcqs']['correct']
            total_correct = tf_correct + mcq_correct
            
            percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0
            
            rankings.append({
                'name': student['name'],
                'percentage': percentage,
                'total_correct': total_correct,
                'total_questions': total_questions,
                'level': student['level']
            })
    
    if not rankings:
        await update.message.reply_text("🏆 لم يكمل أي طالب 5 أسئلة بعد!")
        return
    
    # ترتيب حسب النسبة
    rankings.sort(key=lambda x: x['percentage'], reverse=True)
    
    leaderboard = """
🏆 **متصدرين النهايات** 🏆
━━━━━━━━━━━━━━━━━━━━━━

"""
    
    medals = ["🥇", "🥈", "🥉", "🎖️", "🎖️", "🎖️", "🎖️", "🎖️", "🎖️", "🎖️"]
    
    for i, student in enumerate(rankings[:10]):
        medal = medals[i] if i < len(medals) else "🔸"
        leaderboard += f"{medal} **{student['name']}** - {student['level']}\n"
        leaderboard += f"   النسبة: {student['percentage']:.1f}% "
        leaderboard += f"({student['total_correct']}/{student['total_questions']})\n\n"
    
    leaderboard += "━━━━━━━━━━━━━━━━━━━━━━\n"
    leaderboard += "🎯 **تحدى أصدقاءك واصعد للقمة!**"
    
    await update.message.reply_text(leaderboard)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/stats - إحصائيات الفصل"""
    if update.effective_user.id != TEACHER_ID:
        await update.message.reply_text("🔒 هذا الأمر للمعلم فقط!")
        return
    
    stats = db.data['stats']
    
    # حساب النسب
    tf_percent = (stats['correct_true_false'] / stats['total_true_false'] * 100) if stats['total_true_false'] > 0 else 0
    mcq_percent = (stats['correct_mcqs'] / stats['total_mcqs'] * 100) if stats['total_mcqs'] > 0 else 0
    
    total_questions = stats['total_true_false'] + stats['total_mcqs']
    total_correct = stats['correct_true_false'] + stats['correct_mcqs']
    overall_percent = (total_correct / total_questions * 100) if total_questions > 0 else 0
    
    # بناء التقرير
    stats_report = f"""
👨🏫 **تقرير المعلم - بوت النهايات**
━━━━━━━━━━━━━━━━━━━━━━

📊 **إحصائيات الفصل:**
• 👥 **الطلاب المسجلين:** {len(db.data['students'])}
• 📝 **إجمالي الأسئلة المجابة:** {total_questions}
• ✅ **الإجابات الصحيحة:** {total_correct}
• 🎯 **نسبة النجاح العامة:** {overall_percent:.1f}%

🔵 **أسئلة صح/خطأ:**
• المجابة: {stats['total_true_false']}
• الصحيحة: {stats['correct_true_false']}
• النسبة: {tf_percent:.1f}%

🔴 **أسئلة خيارات متعددة:**
• المجابة: {stats['total_mcqs']}
• الصحيحة: {stats['correct_mcqs']}
• النسبة: {mcq_percent:.1f}%
"""
    
    # إحصائيات المواضيع
    if stats['topics']:
        stats_report += "\n📚 **إحصائيات المواضيع:**\n"
        
        # ترتيب المواضيع حسب عدد الأسئلة
        sorted_topics = sorted(
            stats['topics'].items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )
        
        for topic, topic_stats in sorted_topics:
            topic_percent = (topic_stats['correct'] / topic_stats['total'] * 100) if topic_stats['total'] > 0 else 0
            stats_report += f"• {topic}: {topic_stats['correct']}/{topic_stats['total']} ({topic_percent:.1f}%)\n"
    
    # الطلاب النشطين
    active_students = []
    for user_id, student in db.data['students'].items():
        total_q = student['true_false']['total'] + student['mcqs']['total']
        if total_q >= 3:
            active_students.append((student['name'], total_q, student['level']))
    
    if active_students:
        stats_report += f"\n🎯 **الطلاب النشطين ({len(active_students)}):**\n"
        for name, total_q, level in sorted(active_students, key=lambda x: x[1], reverse=True)[:10]:
            stats_report += f"• {name}: {total_q} سؤال ({level})\n"
    
    stats_report += f"\n📅 **منذ:** {db.data['created_at'][:10]}"
    
    await update.message.reply_text(stats_report)

async def main():
    """الدالة الرئيسية"""
    print("=" * 60)
    print("🧮 بوت اختبارات رياضيات النهايات (Limits)")
    print("=" * 60)
    print(f"📅 بدأ التشغيل: {datetime.now()}")
    print(f"👥 الطلاب المسجلين: {len(db.data['students'])}")
    print(f"📝 الأسئلة المجابة: {db.data['stats']['total_true_false'] + db.data['stats']['total_mcqs']}")
    print("✅ البوت يعمل 24/7!")
    print("=" * 60)
    
    # إنشاء التطبيق
    app = Application.builder().token(TOKEN).build()
    
    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("truefalse", truefalse_command))
    app.add_handler(CommandHandler("mcq", mcq_command))
    app.add_handler(CommandHandler("mix", mix_command))
    app.add_handler(CommandHandler("score", score_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    # إضافة معالجات الاستجابات
    app.add_handler(CallbackQueryHandler(handle_truefalse_answer, pattern="^tf_"))
    app.add_handler(CallbackQueryHandler(handle_mcq_answer, pattern="^mcq_"))
    
    print("\n📱 **تعليمات التشغيل:**")
    print("1. اذهب إلى Telegram وابحث عن البوت")
    print("2. اكتب /start للتسجيل")
    print("3. اكتب /truefalse لأسئلة صح/خطأ")
    print("4. اكتب /mcq لأسئلة خيارات متعددة")
    print("5. اكتب /score لمتابعة تقدمك")
    
    print("\n🎯 **المعلم:** اكتب /stats لمشاهدة إحصائيات الفصل")
    print("=" * 60)
    
    # بدء البوت
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
