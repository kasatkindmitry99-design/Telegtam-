import logging

from aiogram import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler,
        event,
        data
    ):

        user = event.from_user

        logging.info(
            f"USER: {user.id} | "
            f"USERNAME: @{user.username} | "
            f"TEXT: {getattr(event, 'text', 'NO TEXT')}"
        )

        return await handler(event, data)