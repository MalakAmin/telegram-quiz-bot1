# 🚀 بوت اختبارات مدرسي - يعمل 24/7 على Render
# 👨🏫 إعداد: معلم المدرسة

import os
import asyncio
import json
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔐 التوكن من متغيرات البيئة (ساضيفه في Render)
TOKEN = os.environ.get('TELEGRAM_TOKEN', 'ضع_توكنك_هنا')

# 👨🏫 رقم المعلم (ضع رقمك من @userinfobot)
TEACHER_ID = 123456789  # غير هذا الرقم!

# 📊 قاعدة بيانات بسيطة في ملف
class Database:
    def __init__(self):
        self.data_file = 'data.json'
        self.data = self.load_data()
    
    def load_data(self):
        """تحميل البيانات"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                'students': {},
                'questions_answered': 0,
                'correct_answers': 0,
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
                'correct': 0,
                'total': 0,
                'last_active': datetime.now().isoformat()
            }
            self.save_data()
            return True
        return False
    
    def update_score(self, user_id, is_correct):
        """تحديث النتيجة"""
        user_id = str(user_id)
        
        if user_id not in self.data['students']:
            return {'correct': 0, 'total': 0}
        
        self.data['students'][user_id]['total'] += 1
        self.data['students'][user_id]['last_active'] = datetime.now().isoformat()
        
        if is_correct:
            self.data['students'][user_id]['correct'] += 1
        
        # تحديث الإحصائيات العامة
        self.data['questions_answered'] += 1
        if is_correct:
            self.data['correct_answers'] += 1
        
        self.save_data()
        
        return {
            'correct': self.data['students'][user_id]['correct'],
            'total': self.data['students'][user_id]['total']
        }

# إنشاء قاعدة البيانات
db = Database()

# 📚 الأسئلة
QUESTIONS = [
    {
        "id": 1,
        "subject": "الرياضيات",
        "question": "ما هو ناتج ٨ × ٧؟",
        "options": ["٥٦", "٦٤", "٤٨", "٥٠"],
        "correct": 0
    },
    {
        "id": 2,
        "subject": "العلوم",
        "question": "ما هو الغاز الذي نتنفسه؟",
        "options": ["الأكسجين", "ثاني أكسيد الكربون", "النيتروجين", "الهيدروجين"],
        "correct": 0
    },
    {
        "id": 3,
        "subject": "اللغة العربية",
        "question": "ما جمع كلمة 'كتاب'؟",
        "options": ["كتب", "كتابون", "كتابات", "كتيب"],
        "correct": 0
    },
    {
        "id": 4,
        "subject": "التاريخ",
        "question": "متى توحدت المملكة العربية السعودية؟",
        "options": ["١٩٣٢", "١٩٤٥", "١٩٥٠", "١٩٢٠"],
        "correct": 0
    },
    {
        "id": 5,
        "subject": "الجغرافيا",
        "question": "ما هي عاصمة مصر؟",
        "options": ["القاهرة", "الإسكندرية", "الجيزة", "بورسعيد"],
        "correct": 0
    }
]

# 🎯 ردود
CORRECT_MESSAGES = ["أحسنت! 🎯", "ممتاز! 🔥", "صحيح! ✅", "برافو! 👏"]
WRONG_MESSAGES = ["حاول مرة أخرى! 💪", "لا تيأس! 🌟", "تعلم من الخطأ! 📚"]

# ==================== دوال البوت ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عند /start"""
    user = update.effective_user
    is_new = db.register_student(user.id, user.first_name)
    
    if is_new:
        msg = f"🎉 أهلاً {user.first_name}!\nتم تسجيلك في نظام الاختبارات."
    else:
        student = db.data['students'][str(user.id)]
        msg = f"👋 أهلًا بعودتك {user.first_name}!\nنتيجتك: {student['correct']}/{student['total']}"
    
    msg += "\n\n📋 الأوامر:\n/start - البداية\n/quiz - اختبار\n/score - نتيجتك\n/top - المتصدرين\n/help - المساعدة"
    
    await update.message.reply_text(msg)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عند /help"""
    help_text = """
🆘 دليل الاستخدام:

📋 الأوامر:
/start - تسجيل الدخول
/quiz - اختبار عشوائي
/score - عرض نتيجتك
/top - أفضل الطلاب
/stats - للمعلم فقط

🎮 طريقة اللعب:
1. اكتب /quiz
2. اختر الإجابة
3. احصل على التقييم
4. تابع تقدمك

⏰ البوت يعمل 24/7!
"""
    await update.message.reply_text(help_text)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عند /quiz"""
    question = random.choice(QUESTIONS)
    
    buttons = []
    for i, option in enumerate(question['options']):
        # تحويل للأرقام العربية
        arabic_num = str(i+1).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))
        buttons.append([
            InlineKeyboardButton(
                f"{arabic_num}. {option}",
                callback_data=f"ans_{question['id']}_{i}"
            )
        ])
    
    text = f"📚 {question['subject']}\n\n❓ {question['question']}"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الإجابات"""
    query = update.callback_query
    await query.answer()
    
    _, q_id, ans_idx = query.data.split('_')
    q_id, ans_idx = int(q_id), int(ans_idx)
    
    question = next((q for q in QUESTIONS if q['id'] == q_id), None)
    
    if question:
        is_correct = (ans_idx == question['correct'])
        scores = db.update_score(query.from_user.id, is_correct)
        
        if is_correct:
            message = f"✅ {random.choice(CORRECT_MESSAGES)}"
        else:
            correct_answer = question['options'][question['correct']]
            message = f"❌ {random.choice(WRONG_MESSAGES)}\n📌 الإجابة: {correct_answer}"
        
        percentage = (scores['correct'] / scores['total'] * 100) if scores['total'] > 0 else 0
        
        response = f"{message}\n\n📊 نتيجتك: {scores['correct']}/{scores['total']} ({percentage:.1f}%)\n\n🔁 /quiz لسؤال جديد"
        
        await query.edit_message_text(response)

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عند /score"""
    user_id = str(update.effective_user.id)
    
    if user_id not in db.data['students']:
        await update.message.reply_text("⚠️ اكتب /start أولاً")
        return
    
    student = db.data['students'][user_id]
    
    if student['total'] == 0:
        await update.message.reply_text("📭 لم تجب على أسئلة بعد!\n/quiz لتبدأ")
        return
    
    percentage = (student['correct'] / student['total'] * 100)
    
    report = f"""
📊 تقرير {student['name']}:

✅ صحيح: {student['correct']}
❌ خطأ: {student['total'] - student['correct']}
📝 المجموع: {student['total']}
🎯 النسبة: {percentage:.1f}%

📅 انضم: {student['joined'][:10]}
"""
    
    await update.message.reply_text(report)

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عند /top"""
    if not db.data['students']:
        await update.message.reply_text("🏆 لا توجد نتائج بعد!")
        return
    
    rankings = []
    for user_id, student in db.data['students'].items():
        if student['total'] >= 3:  # من أجاب على 3 أسئلة على الأقل
            percentage = (student['correct'] / student['total'] * 100)
            rankings.append((student['name'], percentage, student['correct'], student['total']))
    
    if not rankings:
        await update.message.reply_text("🏆 لم يكمل أحد 3 أسئلة بعد!")
        return
    
    rankings.sort(key=lambda x: x[1], reverse=True)
    
    leaderboard = "🏆 المتصدرون:\n\n"
    medals = ["🥇", "🥈", "🥉", "🎖️", "🎖️"]
    
    for i, (name, perc, correct, total) in enumerate(rankings[:5]):
        medal = medals[i] if i < len(medals) else "🔸"
        leaderboard += f"{medal} {name}: {perc:.1f}% ({correct}/{total})\n"
    
    await update.message.reply_text(leaderboard)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عند /stats (للمعلم فقط)"""
    if update.effective_user.id != TEACHER_ID:
        await update.message.reply_text("🔒 للمعلم فقط!")
        return
    
    total_students = len(db.data['students'])
    active_students = sum(1 for s in db.data['students'].values() if s['total'] > 0)
    total_questions = db.data['questions_answered']
    total_correct = db.data['correct_answers']
    
    percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0
    
    stats_text = f"""
👨🏫 إحصائيات المعلم:

👥 الطلاب: {total_students}
🎯 النشطين: {active_students}
📝 الأسئلة: {total_questions}
✅ الصحيحة: {total_correct}
📈 النسبة: {percentage:.1f}%

📅 منذ: {db.data['created_at'][:10]}
"""
    
    await update.message.reply_text(stats_text)

async def main():
    """الدالة الرئيسية"""
    print("=" * 50)
    print("🚀 بوت الاختبارات المدرسي")
    print("=" * 50)
    print(f"📅 بدأ التشغيل: {datetime.now()}")
    print(f"👥 الطلاب المسجلين: {len(db.data['students'])}")
    print(f"📝 الأسئلة المجابة: {db.data['questions_answered']}")
    print("✅ البوت يعمل 24/7 على Render!")
    print("=" * 50)
    
    # إنشاء التطبيق
    app = Application.builder().token(TOKEN).build()
    
    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(handle_answer))
    
    print("\n📱 يمكنك الآن:")
    print("1. البحث عن البوت في Telegram")
    print("2. كتابة /start")
    print("3. كتابة /quiz للاختبار")
    print("\n⚡ البوت يعمل بشكل دائم!")
    
    # بدء البوت
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
