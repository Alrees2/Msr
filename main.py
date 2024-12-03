import logging
import sqlite3
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from PIL import Image, ImageDraw, ImageFont
import random

# إعداد تسجيل الدخول
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# إعداد قاعدة البيانات
def init_db():
		conn = sqlite3.connect('reports.db')
		c = conn.cursor()
		c.execute('''CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, title TEXT, content TEXT, pages INTEGER, type TEXT)''')
		conn.commit()
		conn.close()

# دالة لإنشاء محتوى التقرير تلقائيًا
def generate_report_content(title: str) -> dict:
		return {
				"Abstract": f"This is a generated abstract for the research titled '{title}'.",
				"Introduction": f"The main problem addressed in '{title}' is detailed in this section.",
				"Objectives": "These are the objectives generated for the research.",
				"Literature Review": "A summary of related works and their impact on the research.",
				"Methodology": "Details of the methodology used to conduct this research.",
				"Results and Discussion": "Results of the research and a detailed discussion.",
				"Conclusion": "The main conclusions drawn from this research.",
				"References": "References used to support the research.",
				"Appendix": "Additional materials and resources."
		}

# دالة لإنشاء تقرير
def create_report(title: str, content: dict, pages: int, report_type: str) -> str:
		# إعداد صورة خلفية
		img = Image.new('RGB', (800, 1200), color=(255, 255, 255))
		d = ImageDraw.Draw(img)

		# إعداد الخط
		font = ImageFont.load_default()

		# إضافة النص إلى الصورة
		y_offset = 10
		d.text((10, y_offset), f"Report Type: {report_type}", fill=(0, 0, 0), font=font)
		y_offset += 30
		d.text((10, y_offset), f"Pages: {pages}", fill=(0, 0, 0), font=font)
		y_offset += 30
		d.text((10, y_offset), f"Title: {title}", fill=(0, 0, 0), font=font)
		y_offset += 50

		for section, text in content.items():
				d.text((10, y_offset), f"{section}: {text}", fill=(0, 0, 0), font=font)
				y_offset += 30 + len(text.splitlines()) * 15  # تغيير المسافة بناءً على طول النص

		# حفظ الصورة
		img_path = f'report_{random.randint(1000, 9999)}.png'
		img.save(img_path)
		return img_path

# دالة لحفظ التقرير في قاعدة البيانات
def save_report(title: str, content: str, pages: int, report_type: str):
		conn = sqlite3.connect('reports.db')
		c = conn.cursor()
		c.execute("INSERT INTO reports (title, content, pages, type) VALUES (?, ?, ?, ?)", (title, content, pages, report_type))
		conn.commit()
		conn.close()

# دالة لمعالجة الأوامر
def start(update: Update, context: CallbackContext) -> None:
		update.message.reply_text('مرحبًا! اختر نوع التقرير:\n1- /free_report (تقرير مجاني 10-40 صفحة)\n2- /full_report (تقرير كامل أكثر من 50 صفحة)')

def set_report_type(update: Update, context: CallbackContext) -> None:
		if update.message.text == '/free_report':
				context.user_data['report_type'] = 'مجاني'
				context.user_data['max_pages'] = 40
				update.message.reply_text('لقد اخترت تقريرًا مجانيًا. أرسل عنوان البحث:')
		elif update.message.text == '/full_report':
				context.user_data['report_type'] = 'كامل'
				context.user_data['min_pages'] = 50
				update.message.reply_text('لقد اخترت تقريرًا كاملاً. أرسل عنوان البحث:')

def handle_message(update: Update, context: CallbackContext) -> None:
		user_data = context.user_data
		text = update.message.text

		if 'report_type' not in user_data:
				update.message.reply_text('يرجى اختيار نوع التقرير باستخدام /start.')
				return

		# إنشاء محتوى التقرير تلقائيًا بناءً على العنوان
		title = text
		content = generate_report_content(title)

		# إعداد الصفحات بناءً على نوع التقرير
		report_type = user_data['report_type']
		max_pages = user_data.get('max_pages', 10)
		min_pages = user_data.get('min_pages', 50)
		pages = random.randint(10, max_pages) if report_type == 'مجاني' else random.randint(min_pages, 100)

		# إنشاء التقرير
		report_image = create_report(title, content, pages, report_type)
		save_report(title, str(content), pages, report_type)

		update.message.reply_photo(photo=open(report_image, 'rb'))
		update.message.reply_text('تم إنشاء التقرير بنجاح!')

def main() -> None:
		TOKEN = os.getenv("7828961178:AAHAgs6w_PbWqUPG0bfhckIb6qamomJYEsk")  # جلب التوكن من متغيرات البيئة
		init_db()

		updater = Updater(TOKEN)

		# إضافة المعالجات
		updater.dispatcher.add_handler(CommandHandler('start', start))
		updater.dispatcher.add_handler(CommandHandler('free_report', set_report_type))
		updater.dispatcher.add_handler(CommandHandler('full_report', set_report_type))
		updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

		# بدء البوت
		updater.start_polling()
		updater.idle()

if __name__ == '__main__':
		main()
