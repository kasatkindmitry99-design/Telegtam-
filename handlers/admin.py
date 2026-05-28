from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from config import ADMINS
from keyboards.inline import admin_keyboard, broadcast_keyboard
from utils.is_admin import AdminFilter
from database.services import *
from states.admin import AdminStates
import logging

router = Router()

def get_user_keyboard(user_id, index, total, filter_type):

    keyboard = []
    buttons = []

    if index > 0:

        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"prev_{index}_{filter_type}"))

    buttons.append(InlineKeyboardButton(text="❌ Удалить", callback_data=f"del_{user_id}_{index}"))
    buttons.append(InlineKeyboardButton(text="🟢 В работу", callback_data=f"work_{user_id}_{index}"))
    buttons.append(InlineKeyboardButton(text="🔴 Закрыть", callback_data=f"close_{user_id}_{index}"))

    if index < total - 1:

        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"next_{index}_{filter_type}"))

    keyboard.append(buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_status_text(status):

    statuses = {"new": "🟡 Новая", "work": "🟢 В работе", "closed": "🔴 Закрыта"}

    return statuses.get(status, status)

async def show_user_card(event, users, index=0, filter_type="all"):

    if not users:

        text = "<b>📭 Заявок нет</b>\n\nВы вернулись в админ панель"

        if isinstance(event, CallbackQuery):

            await event.message.answer(text, reply_markup=admin_keyboard)

        else:

            await event.answer(text, reply_markup=admin_keyboard)

        return

    user = users[index]
    user_id, name, phone, status, created_at, telegram_id = user

    keyboard = get_user_keyboard(user_id, index, len(users), filter_type)

    text = (
        f"<b>📋 Заявка {index + 1}/{len(users)}</b>\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"📱 <b>Телефон:</b> {phone}\n"
        f"📅 <b>Дата:</b> {created_at}\n"
        f"📅 <b>Телеграм id:</b> {telegram_id}\n"
        f"📌 <b>Статус:</b> {get_status_text(status)}"
    )

    if isinstance(event, CallbackQuery):

        await event.message.edit_text(text, reply_markup=keyboard)

    else:

        await event.answer(text, reply_markup=keyboard)

@router.callback_query(F.data == "show_all", AdminFilter())
async def show_all_users(callback: CallbackQuery):

    users = await get_users()

    await show_user_card(callback, users)
    await callback.answer()

@router.callback_query(F.data == "show_new", AdminFilter())
async def show_new_users(callback: CallbackQuery):

    users = await get_users_by_status("new")

    await show_user_card(callback, users)

@router.callback_query(F.data == "show_work", AdminFilter())
async def show_work_users(callback: CallbackQuery):

    users = await get_users_by_status("work")

    await show_user_card(callback, users)

@router.callback_query(F.data == "show_closed", AdminFilter())
async def show_closed_users(callback: CallbackQuery):

    users = await get_users_by_status("closed")

    await show_user_card(callback, users)

@router.callback_query(F.data.startswith("next_"), AdminFilter())
async def next_user(callback: CallbackQuery):

    data = callback.data.split("_")
    index = int(data[1]) + 1
    filter_type = data[2]

    if filter_type == "all":

        users = await get_users()

    else:

        users = await get_users_by_status(filter_type)

    if index >= len(users):

        index = 0

    await show_user_card(callback, users, index)
    await callback.answer()

@router.callback_query(F.data.startswith("prev_"), AdminFilter())
async def prev_user(callback: CallbackQuery):

    data = callback.data.split("_")
    index = int(data[1]) - 1
    filter_type = data[2]

    if filter_type == "all":

        users = await get_users()

    else:

        users = await get_users_by_status(filter_type)

    if index < 0:

        index = len(users) - 1

    await show_user_card(callback, users, index)
    await callback.answer()

@router.callback_query(F.data == "admin_stats", AdminFilter())
async def admin_stats(callback: CallbackQuery):

    stats = await get_stats()

    await callback.message.answer(
        "<b>📊 Статистика</b>\n\n"
        f"👥 Всего: {stats['total']}\n\n"
        f"🟡 Новые: {stats['new']}\n"
        f"🟢 В работе: {stats['work']}\n"
        f"🔴 Закрытые: {stats['closed']}"
    )

    await callback.answer()

@router.callback_query(F.data == "admin_find", AdminFilter())
async def admin_find(callback: CallbackQuery, state: FSMContext):

    await state.set_state(AdminStates.find_user)
    await callback.message.answer("<b>🔎 Введите имя или телефон</b>")
    await callback.answer()

@router.message(Command("admin"), AdminFilter())
async def admin_panel(message: Message):

    await message.answer(
        "<b>⚙️ Админ панель</b>",
        reply_markup=admin_keyboard
    )

@router.callback_query(F.data == "admin_send", AdminFilter())
async def admin_send(callback: CallbackQuery, state: FSMContext):

    await state.set_state(AdminStates.broadcast)
    await callback.message.answer("<b>📢 Введите текст рассылки</b>")
    await callback.answer()

@router.callback_query(F.data == "show_users", AdminFilter())
async def show_users(callback: CallbackQuery):

    users = await get_users()
    await show_user_card(callback,users)

@router.callback_query(F.data.startswith("work_"), AdminFilter())
async def set_work_status(callback: CallbackQuery):

    data = callback.data.split("_")
    user_id = int(data[1])
    index = int(data[2])

    cursor.execute("UPDATE users SET status = ? WHERE id = ?", ("work", user_id))
    conn.commit()

    await callback.answer("🟢 Статус обновлен")

@router.callback_query(F.data.startswith("close_"), AdminFilter())
async def set_closed_status(callback: CallbackQuery):

    data = callback.data.split("_")
    user_id = int(data[1])

    cursor.execute("UPDATE users SET status = ? WHERE id = ?", ("closed", user_id))
    conn.commit()

    await callback.answer("🔴 Заявка закрыта")

@router.message(AdminStates.find_user, AdminFilter())
async def process_find_user(message: Message, state: FSMContext):

    search = message.text
    users = await search_users(search)

    if not users:

        await message.answer("<b>📭 Ничего не найдено</b>")
        await state.clear()
        return

    for user in users:

        (
            user_id,
            telegram_id,
            name,
            phone,
            status,
            created_at
        ) = user

        await message.answer(
            f"<b>📋 Заявка #{user_id}</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"📱 <b>Телефон:</b> {phone}\n"
            f"📅 <b>Дата:</b> {created_at}\n"
            f"📌 <b>Статус:</b> "
            f"{get_status_text(status)}"
        )

    await state.clear()


@router.message(AdminStates.broadcast, AdminFilter())
async def process_broadcast(message: Message, state: FSMContext):

    text = message.text

    await state.update_data(broadcast_text=text)
    await state.set_state(AdminStates.confirm_broadcast)
    await message.answer(
        f"<b>📨 Предпросмотр</b>\n\n"
        f"{text}",
        reply_markup=broadcast_keyboard
    )

@router.callback_query(F.data == "confirm_send", AdminFilter())
async def confirm_send(callback: CallbackQuery, state: FSMContext, bot: Bot):

    data = await state.get_data()
    text = data.get("broadcast_text")
    users = await get_all_telegram_ids()

    success = 0
    failed = 0

    for user in users:

        telegram_id = user[0]

        if not telegram_id:

            continue

        try:

            await bot.send_message(telegram_id, text)

            success += 1

        except Exception:

            failed += 1

    await callback.message.answer(
        f"<b>✅ Рассылка завершена</b>\n\n"
        f"📨 Отправлено: {success}\n"
        f"❌ Ошибок: {failed}"
    )
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "cancel_send", AdminFilter())
async def cancel_send(callback: CallbackQuery, state: FSMContext):

    await state.clear()
    await callback.message.answer("<b>❌ Рассылка отменена</b>")
    await callback.answer()

@router.callback_query(F.data.startswith("del_"), AdminFilter())
async def delete_user_handler(callback: CallbackQuery):

    data = callback.data.split("_")
    user_id = int(data[1])
    index = int(data[2])

    try:

        await delete_user(user_id)
        users = await get_users()

        await show_user_card(callback, users)
        await callback.answer()

        await callback.answer("✅ Заявка удалена")

    except Exception as e:

        logging.error(e)

        await callback.answer("Ошибка удаления", show_alert=True)