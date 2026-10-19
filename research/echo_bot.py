import asyncio, os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start", "help"))
async def send_welcome(message: types.Message):
    await message.reply("سلام به ربات من خوش آمدید")

from aiogram import F

@dp.message(F.text)
async def echo(message: types.Message):
    """
    This will return echo
    """
    await message.answer(message.text)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)  # معادل skip_updates=True
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())