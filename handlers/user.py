from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from states.form import Form
from keyboards.inline import main_menu
from config import ADMINS
from utils.antiflood import check_flood
from keyboards.reply import contact_keyboard
from aiogram.types import ReplyKeyboardRemove
from database.services import add_user, user_exists
import re
import logging

router = Router()

@router.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message,state: FSMContext):

    await state.clear()
    await message.answer("<b>❌ Действие отменено</b>", reply_markup=ReplyKeyboardRemove())
    await message.answer("<b>Главное меню</b>",reply_markup=main_menu)

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "<b>👋 Добро пожаловать!</b>\n\n"
        "Выберите действие ниже 👇",
        reply_markup=main_menu
    )

@router.callback_query(F.data == "new_order")
async def new_order(callback: CallbackQuery, state: FSMContext):

    if await user_exists(
        callback.from_user.id
    ):

        await callback.message.answer(
            "❌ Вы уже отправляли заявку"
        )

        return

    await callback.message.answer("Введите имя", reply_markup=contact_keyboard)
    await state.set_state(Form.name)

@router.message(Form.name)
async def get_name(message: Message, state: FSMContext):

    name = message.text.strip()

    if len(name) < 3:
        await message.answer("<b>❌ Имя должно быть минимум 3 символа</b>")
        return

    if not re.match(r"^[А-Яа-яA-Za-zЁё\s-]+$", name):
        await message.answer("<b>❌ Имя должно содержать только буквы</b>")
        return

    await state.update_data(name=name)
    await message.answer("📱 Отправьте номер телефона", reply_markup=contact_keyboard)
    await state.set_state(Form.phone)

@router.message(Form.phone)
async def get_phone(message: Message, state: FSMContext):

    if message.contact:

        phone = message.contact.phone_number

    else:

        phone = message.text.strip()
        phone = (
            phone
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

        pattern = r'^\+?\d{10,15}$'

        if not re.match(pattern, phone):

            await message.answer(
                "<b>❌ Неверный номер</b>\n"
                "<b>Пример: +77001234567</b>"
            )

            return

    await state.update_data(phone=phone)

    data = await state.get_data()

    name = data["name"]

    if not check_flood(message.from_user.id):

        await message.answer("<b>⏳ Подождите немного перед новой заявкой</b>")
        return

    try:

        await add_user(message.from_user.id, name, phone)

        logging.info(f"Новая заявка от {name} | {phone}")

        username = message.from_user.username or "нет"

        for admin in ADMINS:

            await message.bot.send_message(
                admin,
                "<b>🔔 Новая заявка!</b>\n\n"
                f"👤 <b>Имя:</b> {name}\n"
                f"📱 <b>Телефон:</b> {phone}\n"
                f"🆔 <b>User ID:</b> {message.from_user.id}\n"
                f"👤 <b>Username:</b> @{username}"
            )

        await message.answer(
            "<b>✅ Заявка сохранена!</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"📱 <b>Телефон:</b> {phone}",
            reply_markup=ReplyKeyboardRemove()
        )

    except Exception as e:

        logging.error(e)

        await message.answer("<b>❌ Ошибка при сохранении заявки</b>")

    await state.clear()

@router.callback_query(F.data == "help")
async def help_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("<b>Это бот для заявок по вопросам сотрудничества писать на мой email: kasatkin.dmitry.99@gmail.com</b>")