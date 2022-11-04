import emoji
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def answer_about_trip() -> InlineKeyboardMarkup:
    """Displays buttons with the answer to the question, whether the user
     wants to travel to space

    :return: keyboard with available buttons
    :rtype: InlineKeyboardMarkup"""

    buttons = [
        InlineKeyboardButton(text=emoji.emojize('ДА :slightly_smiling_face:'),
                             callback_data='yes'),
        InlineKeyboardButton(text=emoji.emojize('НЕТ :upside-down_face:'),
                             callback_data='no')
    ]
    keyboard = InlineKeyboardMarkup().add(*buttons)
    return keyboard


def rocket_button() -> InlineKeyboardMarkup:
    """Displays a keyboard with one button in the form of a rocket
    (flight readiness)

    :return: keyboard with available button
    :rtype: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text=emoji.emojize(string='Стартуем :rocket:'),
                             callback_data='go'))
    return keyboard


def show_commands() -> InlineKeyboardMarkup:
    """Displays buttons with available planets or space, photos of which can be viewed

    :return: keyboard with available buttons
    :rtype: InlineKeyboardMarkup
    """

    buttons = [
        InlineKeyboardButton(text=emoji.emojize('Земля :globe_showing_Europe-Africa:'),
                             callback_data='Earth'),
        InlineKeyboardButton(text=emoji.emojize('Марс 🔴🌌'),
                             callback_data='Mars'),
        InlineKeyboardButton(text=emoji.emojize('Исследовать космос :shooting_star:'),
                             callback_data='Space'),
        InlineKeyboardButton(text=emoji.emojize('Завершить работу :check_mark_button:'),
                             callback_data='finish_work'),
        InlineKeyboardButton(text=emoji.emojize('История путешествий :shopping_cart:'),
                             callback_data='history')

    ]
    keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
    return keyboard


def show_more_mars_photo() -> InlineKeyboardMarkup:
    """It is displayed after each found photo of Mars and offers
     to continue exploring Mars or stop

    :return: keyboard with available buttons
    :rtype: InlineKeyboardMarkup"""

    buttons = [
        InlineKeyboardButton(text=emoji.emojize('Еще фото :bellhop_bell:'),
                             callback_data='mars_continue'),
        InlineKeyboardButton(text=emoji.emojize('Достаточно :construction:'),
                             callback_data='mars_stop')
    ]
    keyboard = InlineKeyboardMarkup().add(*buttons)
    return keyboard


def mars_photos_color() -> InlineKeyboardMarkup:
    """Offers to choose to view color or black-and-white photos of Mars

    :return: keyboard with available buttons
    :rtype: InlineKeyboardMarkup"""

    buttons = [
        InlineKeyboardButton(text=emoji.emojize('Цветные :sun_with_face:'),
                             callback_data='Color_photos'),
        InlineKeyboardButton(text=emoji.emojize('Черно-белые :new_moon_face:'),
                             callback_data='Black_white_photos')
    ]
    keyboard = InlineKeyboardMarkup().add(*buttons)
    return keyboard


def show_more_earth_photo() -> InlineKeyboardMarkup:
    """It is displayed after each found photo of Earth and offers
     to continue exploring Earth or stop

    :return: keyboard with available buttons
    :rtype: InlineKeyboardMarkup"""

    buttons = [
        InlineKeyboardButton(text=emoji.emojize('Еще фото :bellhop_bell:'),
                             callback_data='earth_continue'),
        InlineKeyboardButton(text=emoji.emojize('Достаточно :construction:'),
                             callback_data='earth_stop')
    ]
    keyboard = InlineKeyboardMarkup().add(*buttons)
    return keyboard


def new_date_new_planet() -> InlineKeyboardMarkup:
    """It is displayed after no photos with the previously specified date have been
    found and offers to select a new date and continue viewing photos of the same planet
    or select a new planet

    :return: keyboard with available buttons
    :rtype: InlineKeyboardMarkup"""

    buttons = [
        InlineKeyboardButton(text=emoji.emojize('Новая дата :closed_book:'),
                             callback_data='new_date'),
        InlineKeyboardButton(text=emoji.emojize('Новая планета :full_moon_face:'),
                             callback_data='new_planet')
    ]
    keyboard = InlineKeyboardMarkup().add(*buttons)
    return keyboard
