import asyncio, os, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv
from google import genai

load_dotenv()
logging.basicConfig(level=logging.INFO)

google_api_key = os.getenv("GOOGLE_API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

client = genai.Client(api_key=google_api_key)
model_name = "gemini-3.5-flash-lite"
SYSTEM = "You are a helpful assistant."

# برای هر چت، id آخرین interaction را نگه می‌داریم (جایگزین کلاس reference)
last_interaction: dict[int, str] = {}

bot = Bot(token=telegram_bot_token)
dp = Dispatcher()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Hi\nI am a bot created by Hamed\nHow can I help you?")


@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.reply(
        "/start - شروع\n"
        "/clear - پاک کردن تاریخچهٔ گفتگو\n"
        "/help - راهنما\n"
        "هر سؤالی دارید بنویسید 🙂"
    )


@dp.message(Command("clear"))
async def clear(message: types.Message):
    last_interaction.pop(message.chat.id, None)
    await message.reply("تاریخچهٔ گفتگو پاک شد ✅")


def ask_gemini(text: str, previous_id: str | None):
    return client.interactions.create(
        model=model_name,
        input=text,
        system_instruction=SYSTEM,
        previous_interaction_id=previous_id,
    )


@dp.message(F.text)
async def chat(message: types.Message):
    chat_id = message.chat.id
    await bot.send_chat_action(chat_id, "typing")   # نمایش «در حال نوشتن...»

    try:
        # SDK همگام (sync) است؛ در thread جدا اجرا می‌کنیم تا ربات قفل نشود
        interaction = await asyncio.to_thread(
            ask_gemini, message.text, last_interaction.get(chat_id)
        )
        last_interaction[chat_id] = interaction.id
        await message.answer(interaction.output_text)
    except Exception as e:
        logging.exception("Gemini error")
        await message.answer("متأسفم، الان خطایی پیش آمد. کمی بعد دوباره امتحان کنید.")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())