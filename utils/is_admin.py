import logging

from aiogram.filters import BaseFilter

from config import ADMINS

class AdminFilter(BaseFilter):

    async def __call__(self, obj):

        user_id = obj.from_user.id

        if user_id not in ADMINS:

            logging.warning(f"Попытка доступа к админке | ID: {user_id}")

            return False

        logging.info(f"Админ вошел | ID: {user_id}")

        return True