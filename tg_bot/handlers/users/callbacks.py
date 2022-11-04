from aiogram.types import CallbackQuery
from tg_bot.keyboards.reply.menu_button import menu_button


async def start_callback(call: CallbackQuery) -> None:
    call.answer(text='Приготовьтесь)')
