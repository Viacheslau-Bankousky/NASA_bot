import emoji
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def menu_button() -> ReplyKeyboardMarkup:
    """Displays the menu button

    :return: keyboard with available button
    :rtype: ReplyKeyboardMarkup"""

    keyboard = ReplyKeyboardMarkup(one_time_keyboard=False,
                                   resize_keyboard=True)
    button = KeyboardButton(emoji.emojize(string='Меню  :telescope:'))
    keyboard.add(button)
    return keyboard