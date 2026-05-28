from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMINS
from database.db import cursor, conn
from keyboards.inline import admin_keyboard
from utils.is_admin import AdminFilter
from database.services import get_users, delete_user, search_users, get_stats
import logging

router = Router()

def get_user_keyboard(user_id, index, total):

    keyboard = []
    buttons = []

    if index > 0:

        buttons.append(InlineKeyboardButton(text="⬅️",callback_data=f"prev_{index}"))

    buttons.append(InlineKeyboardButton(text="❌ Удалить",callback_data=f"del_{user_id}_{index}"))
    buttons.append(InlineKeyboardButton(text="🟢 В работу",callback_data=f"work_{user_id}_{index}"))
    buttons.append(InlineKeyboardButton(text="🔴 Закрыть",callback_data=f"close_{user_id}_{index}"))

    if index < total - 1:

        buttons.append(InlineKeyboardButton(text="➡️",callback_data=f"next_{index}"))

    keyboard.append(buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_status_text(status):

    statuses = {"new": "🟡 Новая","work": "🟢 В работе","closed": "🔴 Закрыта"}

    return statuses.get(status, status)

async def show_user_card(callback,users,index=0):

    if not users:

        await callback.message.edit_text("<b>📭 Заявок нет</b>")
        return

    user = users[index]
    user_id, name, phone, status, created_at = user

    keyboard = get_user_keyboard(user_id,index,len(users))

    await callback.message.edit_text(
        f"<b>📋 Заявка {index + 1}/{len(users)}</b>\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"📱 <b>Телефон:</b> {phone}\n"
        f"📅 <b>Дата:</b> {created_at}\n"
        f"📌 <b>Статус:</b> {get_status_text(status)}",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "show_new",AdminFilter())
async def show_new_users(callback: CallbackQuery):

    users = get_users_by_status("new")

    await show_user_card(callback,users)

@router.callback_query(F.data.startswith("next_"),AdminFilter())
async def next_user(callback: CallbackQuery):

    index = int(callback.data.split("_")[1]) + 1
    users = get_users()
    user = users[index]
    user_id, name, phone, status, created_at = user

    keyboard = get_user_keyboard(user_id,index,len(users))

    await callback.message.edit_text(
        f"<b>📋 Заявка {index + 1}/{len(users)}</b>\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"📱 <b>Телефон:</b> {phone}\n"
        f"📅 <b>Дата:</b> {created_at}\n"
        f"📌 <b>Статус:</b> {get_status_text(status)}",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("prev_"),AdminFilter())
async def prev_user(callback: CallbackQuery):

    index = int(callback.data.split("_")[1]) - 1
    users = get_users()
    user = users[index]
    user_id, name, phone, status, created_at = user
    keyboard = get_user_keyboard(user_id,index,len(users))

    await callback.message.edit_text(
        f"<b>📋 Заявка {index + 1}/{len(users)}</b>\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"📱 <b>Телефон:</b> {phone}\n"
        f"📅 <b>Дата:</b> {created_at}\n"
        f"📌 <b>Статус:</b> {get_status_text(status)}",
        reply_markup=keyboard
    )
    await callback.answer()

@router.message(Command("stats"),AdminFilter())
async def show_stats(message: Message):

    stats = get_stats()

    await message.answer(
        "<b>📊 Статистика заявок</b>\n\n"
        f"👥 <b>Всего:</b> {stats['total']}\n\n"
        f"🟡 <b>Новые:</b> {stats['new']}\n"
        f"🟢 <b>В работе:</b> {stats['work']}\n"
        f"🔴 <b>Закрытые:</b> {stats['closed']}"
    )

@router.message(Command("find"),AdminFilter())
async def find_user(message: Message):

    text = message.text.split(maxsplit=1)

    if len(text) < 2:

        await message.answer(
            "<b>❌ Укажите запрос</b>\n\n"
            "Пример:\n"
            "<code>/find Алекс</code>"
        )
        return

    search = text[1]
    users = search_users(search)

    if not users:

        await message.answer("<b>📭 Ничего не найдено</b>")
        return

    for user in users:

        user_id, name, phone, status, created_at = user

        await message.answer(
            f"<b>📋 Заявка #{user_id}</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"📱 <b>Телефон:</b> {phone}\n"
            f"📅 <b>Дата:</b> {created_at}\n"
            f"📌 <b>Статус:</b> {get_status_text(status)}"
        )

@router.message(Command("admin"), AdminFilter())
async def admin_panel(message: Message):

    await message.answer(
        "<b>👤Админ панель</b>",
        reply_markup=admin_keyboard
    )

@router.callback_query(F.data == "show_users", AdminFilter())
async def show_users(callback: CallbackQuery):

    users = get_users()

    if not users:

        await callback.message.answer("Заявок нет")

        return

    user = users[0]
    user_id, name, phone, status, created_at = user

    keyboard = get_user_keyboard(user_id,0,len(users))

    await callback.message.answer(
        f"<b>📋 Заявка 1/{len(users)}</b>\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"📱 <b>Телефон:</b> {phone}\n"
        f"📅 <b>Дата:</b> {created_at}\n"
        f"📌 <b>Статус:</b> {get_status_text(status)}",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("work_"),AdminFilter())
async def set_work_status(callback: CallbackQuery):

    data = callback.data.split("_")
    user_id = int(data[1])
    index = int(data[2])

    cursor.execute("UPDATE users SET status = ? WHERE id = ?",("work", user_id))
    conn.commit()

    await callback.answer("🟢 Статус обновлен")

@router.callback_query(F.data.startswith("close_"),AdminFilter())
async def set_closed_status(callback: CallbackQuery):

    data = callback.data.split("_")
    user_id = int(data[1])

    cursor.execute("UPDATE users SET status = ? WHERE id = ?",("closed", user_id))
    conn.commit()

    await callback.answer("🔴 Заявка закрыта")

@router.callback_query(F.data.startswith("del_"), AdminFilter())
async def delete_user(callback: CallbackQuery):

    data = callback.data.split("_")
    user_id = int(data[1])
    index = int(data[2])

    try:

        delete_user(user_id)
        users = get_users()

        if not users:

            await callback.message.edit_text("<b>📭 Заявок больше нет</b>")
            await callback.answer()

            return

        index = min(index, len(users) - 1)
        user = users[index]
        new_user_id, name, phone, status, created_at = user

        keyboard = get_user_keyboard(new_user_id,index,len(users))

        await callback.message.edit_text(
            f"<b>📋 Заявка {index + 1}/{len(users)}</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"📱 <b>Телефон:</b> {phone}\n"
            f"📅 <b>Дата:</b> {created_at}\n"
            f"📌 <b>Статус:</b> {get_status_text(status)}",
            reply_markup=keyboard
        )
        await callback.answer()

        await callback.answer("✅ Заявка удалена")

    except Exception as e:

        logging.error(e)

        await callback.answer("Ошибка удаления", show_alert=True)



@router.message(Command("stats"),AdminFilter())
async def show_stats(message: Message):

    stats = get_stats()

    await message.answer(
        "<b>📊 Статистика заявок</b>\n\n"
        f"👥 <b>Всего:</b> {stats['total']}\n\n"
        f"🟡 <b>Новые:</b> {stats['new']}\n"
        f"🟢 <b>В работе:</b> {stats['work']}\n"
        f"🔴 <b>Закрытые:</b> {stats['closed']}"
    )


@router.message(Command("find"),AdminFilter())
async def find_user(message: Message):

    text = message.text.split(maxsplit=1)

    if len(text) < 2:

        await message.answer(
            "<b>❌ Укажите запрос</b>\n\n"
            "Пример:\n"
            "<code>/find Алекс</code>"
        )
        return

    search = text[1]
    users = search_users(search)

    await show_user_card(callback,users)


@router.message(Command("send"),AdminFilter())
async def broadcast(message: Message,bot: Bot):
    text = message.text.split(maxsplit=1)

    if len(text) < 2:

        await message.answer("❌ Укажите текст")
        return

    broadcast_text = text[1]

    users = get_all_telegram_ids()
    success = 0
    failed = 0

    for user in users:

        telegram_id = user[0]

        try:

            await bot.send_message(telegram_id,broadcast_text)

            success += 1

        except Exception:

            failed += 1

    await message.answer(
        f"✅ Отправлено: {success}\n"
        f"❌ Ошибок: {failed}"
    )