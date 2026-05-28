from aiogram.types import (ReplyKeyboardMarkup,KeyboardButton)

contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📱 Отправить контакт",
                request_contact=True
            )
        ],
        [
            KeyboardButton(
                text="❌ Отмена"
            )
        ]
    ],
    resize_keyboard=True
)