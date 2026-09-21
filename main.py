import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import ReactionTypeEmoji

BOT_TOKEN = "YOUR_BOT_TOKEN"  # Bu yerga bot tokeningizni kiriting

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Har bir foydalanuvchining oxirgi faollik vaqtini saqlash uchun
user_tasks = {}

async def check_inactivity(chat_id: int):
    """ Foydalanuvchi 1 kun (86400 sek) yozmasa, o'zi birinchi bo'lib yozadi """
    await asyncio.sleep(86400) # Sinash uchun buni 60 (1 minut) qilib ko'rsangiz bo'ladi
    await bot.send_message(
        chat_id, 
        "Eee, yo'q bo'lib ketdingmi? Tirikmisan o'zi? Nimalar qilyapsan? 😄"
    )

@dp.message()
async def handle_user_messages(message: types.Message):
    chat_id = message.chat.id

    # 1. Eski eslatma taymerini bekor qilish va yangisini o'rnatish
    if chat_id in user_tasks:
        user_tasks[chat_id].cancel()
    user_tasks[chat_id] = asyncio.create_task(check_inactivity(chat_id))

    # 2. Xabarga avtomatik reaksiyalar bosish
    try:
        await message.react([
            ReactionTypeEmoji(emoji="👍"),
            ReactionTypeEmoji(emoji="❤️"),
            ReactionTypeEmoji(emoji="🔥"),
            ReactionTypeEmoji(emoji="🎉")
        ])
    except Exception as e:
        print(f"Reaksiya xatoligi: {e}")

    # 3. Foydalanuvchi xabariga mos ravishda do'stona javob qaytarish
    text = message.text.lower() if message.text else ""

    if "salom" in text:
        await message.reply("Salom! Ishlaring yaxshimi? Nimalar bilan bandsan?")
    elif "yaxshimi" in text or "qalaysan" in text:
        await message.reply("Zo'r, rahmat! O'zingda nima gaplar?")
    else:
        # Boshqa har qanday gapga do'stona javob
        await message.reply(f"Tushundim! Siz dedingiz: '{message.text}'. Yana nimalar haqida gaplashamiz?")
