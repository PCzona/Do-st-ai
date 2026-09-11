import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import openai

# =========================================================
# SOZLAMALAR VA TOKENLAR
# =========================================================
TELEGRAM_BOT_TOKEN = "8737137144:AAHj2K3ylZvr6oPSylHIhBuIE27U2usww-w"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"  # OpenAI kalitingizni shu yerga yozasiz

CHANNEL_ID = "@pczona_off"
INSTAGRAM_URL = "https://www.instagram.com/pczona_off"
YOUTUBE_URL = "https://www.youtube.com/@PCzona_off"
# =========================================================

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
openai.api_key = OPENAI_API_KEY

user_timers = {}


# Obunani tekshirish funksiyasi
async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["creator", "administrator", "member"]
    except Exception:
        return False


# Obuna tugmalari
def get_sub_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                text="📢 Telegram Kanal", url=f"https://t.me/{CHANNEL_ID[1:]}"
            )
        ],
        [InlineKeyboardButton(text="📸 Instagram", url=INSTAGRAM_URL)],
        [InlineKeyboardButton(text="▶️ YouTube", url=YOUTUBE_URL)],
        [
            InlineKeyboardButton(
                text="✅ Obunani tekshirish", callback_data="check_subscription"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# AI (Do'st) javobi
async def get_ai_response(user_text, is_followup=False):
    system_instruction = (
        "Siz foydalanuvchining eng yaqin, samimiy va mehrli do'stisiz. "
        "O'zbek tilida juda tabiiy, og'zaki so'zlashuv uslubida, o'rtoqlarcha va hazilkashlik bilan muloqot qiling. "
        "Rasmiy gaplar ishlatmang, do'stona va qisqa javob bering."
    )

    prompt = (
        "Do'stingiz bir oz vaqtdan beri jim bo'lib qoldi. Unga hol-ahvol so'rab samimiy va qiziqarli xabar yozing."
        if is_followup
        else user_text
    )

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


# Inactivity Timer (5 daqiqa jim tursa AI birinchi yozadi)
async def check_inactivity(user_id):
    await asyncio.sleep(300)
    follow_up_message = await get_ai_response("", is_followup=True)
    await bot.send_message(user_id, follow_up_message)


# Foydalanuvchidan xabar kelganda
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id

    is_subscribed = await check_sub(user_id)
    if not is_subscribed:
        await message.answer(
            "Botdan va AI do'stingizdan foydalanish uchun quyidagi kanallarga obuna bo'ling va **'Obunani tekshirish'** tugmasini bosing:",
            reply_markup=get_sub_keyboard(),
            parse_mode="Markdown",
        )
        return

    if user_id in user_timers:
        user_timers[user_id].cancel()

    ai_response = await get_ai_response(message.text)
    await message.answer(ai_response)

    user_timers[user_id] = asyncio.create_task(check_inactivity(user_id))


# Tekshirish tugmasi bosilganda
@dp.callback_query(F.data == "check_subscription")
async def process_check(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    is_subscribed = await check_sub(user_id)

    if is_subscribed:
        await callback_query.message.delete()
        await bot.send_message(
            user_id,
            "Rahmat! Obuna tasdiqlandi. Endi menga bemalol xabar yozishingiz mumkin, men sizning AI do'stingizman!",
        )
    else:
        await callback_query.answer(
            "Siz hali Telegram kanalimizga obuna bo'lmadingiz!",
            show_alert=True,
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
