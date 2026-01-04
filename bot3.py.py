# -*- coding: utf-8 -*-
"""
Created on Sat Dec 27 00:31:37 2025

@author: Umidjon
"""

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import os

# .env faylni yuklaymiz
load_dotenv()

# Tokenni .env fayldan olamiz
TOKEN = os.getenv("BOT_TOKEN")

print(TOKEN)
# Foydalanuvchi ma’lumotlarini saqlash uchun lug‘at
users_data = {}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users_data[update.effective_user.id] = {
        "son_oddiy": 0,
        "son_pitilka": 0,
        "stage": "choose_type"
    }
    await update.message.reply_text(
        "Siz oyligingizni hisoblovchi dasturdan foydalanmoqdasiz.\n"
        "Oddiy va pitilka sochiqlardan qancha ishlab chiqqaningizni kiriting.\n"
        "Siz qanday sochiq ishlab chiqardingiz? (oddiy/pitilka)"
    )

# Foydalanuvchi javoblarini qabul qilish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()

    # Agar foydalanuvchi start qilmagan bo‘lsa
    if user_id not in users_data:
        await update.message.reply_text("Iltimos, avval /start buyrug‘ini yuboring.")
        return

    data = users_data[user_id]
    narx_oddiy = 14.2
    narx_pitilka = 28.4

    stage = data["stage"]

    # Foydalanuvchi turini tanlaydi
    if stage == "choose_type":
        if text in ["oddiy", "pitilka"]:
            data["current_type"] = text
            data["stage"] = "enter_amount"
            await update.message.reply_text(f"{text.capitalize()} sochiqdan qancha ishlab chiqdingiz? (stop tugatish uchun)")
        else:
            await update.message.reply_text("Faqat 'oddiy' yoki 'pitilka' sochiqni kiriting.")
    
    # Foydalanuvchi son kirityapti
    elif stage == "enter_amount":
        if text == "stop":
            data["stage"] = "ask_another"
            await update.message.reply_text("Boshqa turdagi sochiqlarni kiritasizmi? (ha/yoq)")
        else:
            try:
                son = int(text)
                if data["current_type"] == "oddiy":
                    data["son_oddiy"] += son
                else:
                    data["son_pitilka"] += son
                await update.message.reply_text("Ma’lumot saqlandi. Yana qancha ishlab chiqdingiz? (stop tugatish uchun)")
            except:
                await update.message.reply_text("Iltimos, raqam kiriting!")

    # Boshqa turdagi sochiqlarni kiritish
    elif stage == "ask_another":
        if text == "ha":
            data["stage"] = "choose_type"
            await update.message.reply_text("Qaysi tur: oddiy yoki pitilka?")
        elif text == "yoq":
            # Natijalarni chiqarish
            son_oddiy = data["son_oddiy"]
            son_pitilka = data["son_pitilka"]
            total = son_oddiy * narx_oddiy + son_pitilka * narx_pitilka
            await update.message.reply_text(
                f"\nNatijalar:\n"
                f"Oddiy sochiqlar soni: {son_oddiy}, jami narxi: {son_oddiy * narx_oddiy}\n"
                f"Pitilka sochiqlar soni: {son_pitilka}, jami narxi: {son_pitilka * narx_pitilka}\n"
                f"Umumiy ishlab chiqarilgan sochiqlar soni: {son_oddiy + son_pitilka}\n"
                f"Umumiy narx: {total}"
            )
            # Ma’lumotlarni tozalash
            del users_data[user_id]
        else:
            await update.message.reply_text("Faqat 'ha' yoki 'yoq' deb javob bering.")

# Botni ishga tushirish
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()

