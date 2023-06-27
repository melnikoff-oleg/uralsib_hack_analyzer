import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from settings import Settings

settings = Settings()

loop = asyncio.get_event_loop()

# Initialize bot and dispatcher
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage(), loop=loop)
