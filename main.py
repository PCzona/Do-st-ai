import os
import asyncio
import random
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import openai

# ==========================================
# SOZLAMALAR VA TOKENLAR (GitHub Secrets'dan olinadi)
# ==========================================
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

CHANNEL_ID = "@pczona_off"
INSTAGRAM_URL = "https://www.instagram.com/pczona"
YOUTUBE_URL = "https://www.youtube.com/@PCzona"

# ==========================================
# BOT VA DISPATCHER INITIALIZATION
# ==========================================
bot = Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None
dp = Dispatcher()
openai.api_key = OPENAI_API_KEY

user_timers = {}

# Reaksiyalar uchun emojilar ro'yxati
REACTIONS = ["🔥", "❤️", "👍", "🤩", "⚡️", "🥳", "💥", "😎", "💯", "🎉"]

# ==========================================
# OBUNA TEKSHIRISH FUNKSIYASI
# ==========================================
async def check_sub(user_id: int) -> bool:
    if not bot:
        return True
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["creator", "administrator", "member"]
    except Exception as e:
        print(f"Obuna tekshirishda xatolik: {e}")
        return True

def get_sub_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish 🚀", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")],
        [InlineKeyboardButton(text="📸 Instagram ✨", url=INSTAGRAM_URL)],
        [InlineKeyboardButton(text="▶️ YouTube 🔥", url=YOUTUBE_URL)],
        [InlineKeyboardButton(text="✅ Obunani tekshirish 🔍", callback_data="check_subscription")]
    ])
    return keyboard

# ==========================================
# COMMAND HANDLERS
# ==========================================
@dp.message(F.text == "/start")
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if not await check_sub(user_id):
        await message.answer(
            "Salom! 👋✨ Botdan to'liq foydalanish va zo'r kayfiyat olish uchun kanalimizga obuna bo'ling! 🚀👇",
            reply_markup=get_sub_keyboard()
        )
        return

    await message.answer("Salom, do'stim! 🥳✨ Men juda xursandman! Menga istalgan narsani yoz, gaplashamiz! 💬🔥🎉")

@dp.callback_query(F.data == "check_subscription")
async def callback_check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await check_sub(user_id):
        await callback.message.edit_text("Uraaa! 🎉 Obuna tasdiqlandi! Endi mazza qilib gaplashamiz! 🚀💬💥")
    else:
        await callback.answer("Hali obuna bo'lmadingiz-ku! 😉👇 Kanalga kirib bosing!", show_alert=True)

# ==========================================
# AVTO-YAZISH MANTIGI (5 MINUTDAN KEYIN QAYTA YOZISH)
# ==========================================
async def auto_followup_task(chat_id: int, delay_seconds: int = 300):
    await asyncio.sleep(delay_seconds)
    try:
        if bot:
            messages = [
                "Eeeey, jigarim! Nega yo'q bo'lib ketding? 🤔💭 Qaydasan? 🕵️‍♂️✨",
                "Hoooy, do'stim! 😃 Nega jim bo'lib qolding? Kutyapman-ku! ⏳🔥",
                "Qayerlarga g'oyib bo'lding? 😱 Ketdik, gurungni davom ettiramiz! 🚀💬🎉",
                "Nega javob yo'q, do'stim? 😢 Zerikib qoldim-ku, yozvor! 🥺💬✨"
            ]
            await bot.send_message(chat_id=chat_id, text=random.choice(messages))
    except Exception as e:
        print(f"Avto-xabar yuborishda xatolik: {e}")

# ==========================================
# MAIN CHAT HANDLER (EMOJILAR VA REAKSIYA)
# ==========================================
@dp.message()
async def chat_handler(message: types.Message):
    user_id = message.from_user.id
    
    # 1. Obuna tekshirish
    if not await check_sub(user_id):
        await message.answer(
            "Kanalimizga obuna bo'lishingiz kerak! 👇✨",
            reply_markup=get_sub_keyboard()
        )
        return

    # 2. Xabarga avtomatik emotsional reaksiya (Stiker/Emoji) qoldirish
    try:
        chosen_reaction = random.choice(REACTIONS)
        await message.react([types.ReactionTypeEmoji(emoji=chosen_reaction)])
    except Exception as e:
        print(f"Reaksiya qo'yishda xatolik: {e}")

    # 3. Oldingi taymerni bekor qilish
    if user_id in user_timers:
        user_timers[user_id].cancel()

    # 4. Sun'iy intellekt orqali emojilarga boy javob qaytarish
    user_text = message.text
    try:
        if OPENAI_API_KEY and OPENAI_API_KEY != "YOUR_OPENAI_API_KEY":
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "Siz judayam emotsional, quvnoq, xushchaqchaq va do'stona AI yordamchisiz. Har bir javobingizda ko'plab mos emojilar (🔥, 🎉, 🤩, 🚀, ❤️, 😂, ✨ va h.k.) va stiker kayfiyatini beruvchi so'zlardan foydalaning!"
                    },
                    {"role": "user", "content": user_text}
                ]
            )
            reply_text = response.choices[0].message.content
        else:
            reply_text = f"Vauuu! 🤩 '{user_text}' dedingmi?! Zaybal/Zo'r gap bo'ldi-ku! 🔥 Hali yana ko'p gaplashamiz! 🚀💬🎉"
    except Exception as e:
        reply_text = f"Ajoyib xabar uchun rahmat! 🥳 Yana nimalar haqida gaplashamiz, do'stim? ✨💬🔥"

    await message.answer(reply_text)

    # 5. 5 daqiqa (300 soniya) dan keyin avto-yozish taymerini yoqish
    timer_task = asyncio.create_task(auto_followup_task(chat_id=message.chat.id, delay_seconds=300))
    user_timers[user_id] = timer_task

# ==========================================
# ASOSIY ISHGA TUSHIRISH
# ==========================================
async def main():
    if not TELEGRAM_BOT_TOKEN:
        print("XATOLIK: BOT_TOKEN topilmadi!")
        return
    
    print("Bot emojilar va vaqt taymeri bilan muvaffaqiyatli ishga tushdi... 🚀🔥")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
