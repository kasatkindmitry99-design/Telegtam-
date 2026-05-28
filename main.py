import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.user import router as user_router
from handlers.admin import router as admin_router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from middlewares.logging import LoggingMiddleware
from database.db import create_db

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

dp.message.middleware(LoggingMiddleware())

dp.include_router(user_router)
dp.include_router(admin_router)

async def main():

    try:

        logging.info("Бот запущен")

        await create_db()
        await dp.start_polling(bot)

    finally:

        await bot.session.close()

        logging.info("Бот остановлен")

if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        logging.info("Выключение бота")