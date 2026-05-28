from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📝 Оставить заявку", callback_data="new_order")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ]
)

broadcast_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Отправить",
                callback_data="confirm_send"
            ),

            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="cancel_send"
            )
        ]
    ]
)

admin_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[

        [
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="admin_stats"
            ),

            InlineKeyboardButton(
                text="🔎 Поиск",
                callback_data="admin_find"
            )
        ],

        [
            InlineKeyboardButton(
                text="📢 Рассылка",
                callback_data="admin_send"
            )
        ],

        [
            InlineKeyboardButton(
                text="📋 Все",
                callback_data="show_all"
            ),

            InlineKeyboardButton(
                text="🟡 Новые",
                callback_data="show_new"
            )
        ],

        [
            InlineKeyboardButton(
                text="🟢 В работе",
                callback_data="show_work"
            ),

            InlineKeyboardButton(
                text="🔴 Закрытые",
                callback_data="show_closed"
            )
        ]
    ]
)