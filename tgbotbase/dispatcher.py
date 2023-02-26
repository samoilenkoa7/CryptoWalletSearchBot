import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import settings

# Configure logging
logging.basicConfig(level=logging.WARNING, filename='../log.log', filemode='w')

# init
storage = MemoryStorage()
bot = Bot(token=settings.bot_token, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
