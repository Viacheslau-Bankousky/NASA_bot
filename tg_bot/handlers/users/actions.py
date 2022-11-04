from typing import Optional

import emoji
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.handler import ctx_data
from aiogram.types import Message, ContentType

import tg_bot.keyboards.inline.inline_keyboards as inline
from tg_bot.keyboards.reply.menu_button import menu_button
from tg_bot.misc.calendar import DialogCalendar
from tg_bot.misc.limit_for_throttling import rate_limit
from tg_bot.misc.states import Conditions
from tg_bot.services.logger.my_logger import get_logger

logger = get_logger(name=__name__)


async def user_greeting(message: Message) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Sets the state in which only the keyboard
    with answers to the question about 'the user's readiness to fly into space'
    will be displayed. Displays the user's greeting together with the above keyboard.

    :param: message: current message
    :type: message: Message
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} joined us')
    await Conditions.yes_no_keyboard.set()
    await message.answer(text=emoji.emojize(f'Приветствую {message.from_user.first_name},\n '
                                            f'готовы совершить путешествие в космос? '
                                            f':ringed_planet:'
                                            ':sun_with_face::sun:'),
                         reply_markup=inline.answer_about_trip())
    return True


async def re_greeting(message: Message) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Warns a user that incorrect information
    has been entered, after which the question is asked again 'whether the user
    is ready to fly into space' and a keyboard with multiple answers (yes/no)
    is displayed again. The previous inline keyboard is being deleted.

    :param: message: current message
    :type: message: Message
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} entered incorrect '
                f'answer about flying into space')
    await message.bot.delete_message(chat_id=message.chat.id,
                                     message_id=message.message_id - 1)
    await message.answer(text='Кажется я вас не понимаю)\n'
                              ' Так полетим в космос или нет?',
                         reply_markup=inline.answer_about_trip())
    return True


async def flight_beginning(message: Message) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Sets the state in which only the keyboard
    with the rocket button (flight readiness) will be displayed and displays it after
    the countdown.

    :param: message: current message
    :type: message: Message
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} flies into space')
    await Conditions.rocket_button.set()
    await message.answer(text=emoji.emojize(':keycap_5:' + ' ' * 17 + ':keycap_4:'
                                            + ' ' * 17 + ':keycap_3:' + ' ' * 17 +
                                            ':keycap_2:' + ' ' * 17 + ':keycap_1:' +
                                            ' ' * 17 + ':keycap_0:'),
                         reply_markup=inline.rocket_button())
    return True


async def re_flight_beginning(message: Message) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Warns the user that a message was entered
    incorrectly, after which the countdown starts and the button with a rocket appears
    again (the corresponding function is called). The previous inline keyboard is being
    deleted.

    :param: message: current message
    :type: message: Message
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} entered incorrect answer about the takeoff')
    await message.bot.delete_message(chat_id=message.chat.id,
                                     message_id=message.message_id - 1)
    await message.answer(text='Кажется появились какие-то технические проблемы\n'
                              'Пробуем взлететь еще раз)')
    await flight_beginning(message=message)
    return True


async def show_actions(message: Message) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Sets the state in which the menu button
    appears for the first time. The message is displayed, which explaining how
    the user can view the list of features of the bot (with menu button or /help
    command).

    :param: message: current message
    :type: message: Message
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f"{name} is thinking about the answer"
                f" about viewing the capabilities of the bot")
    await Conditions.menu_button.set()
    await message.answer(text='Для просмотра перечня моих возможностей, '
                              'воспользуйтесь кнопкой МЕНЮ или введите '
                              'команду /help',
                         reply_markup=menu_button())
    return True


async def re_show_actions(message: Message) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Warns the user that an incorrect message
    has been entered, and then displays the menu button again together with an
    explanatory message (it is necessary only when the menu button is displayed
    for the first time).

    :param: message: current message
    :type: message: Message
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name = ctx_data.get()['user'].user_name
    logger.info(f"{name} entered incorrect answer"
                f" about the viewing of the bot's capabilities")
    await message.answer('Кажется вы ввели что-то не то, попробуйте еще раз)\n')
    await show_actions(message=message)
    return True


@rate_limit(limit=3)
async def help_answer(message: Message, state: FSMContext) -> Optional[bool]:
    """With the help of a special decorator, a time limit is set on the use of
    the menu button (using the ThrottlingMiddleware). Retrieves the necessary
    user from the database (via DataMiddleware) to use his name when recording
    log message. Resets the current state to its original condition along with
    all the data. Sets the state in which only the keyboard with available
    capabilities to the bot will be displayed. It shows the above keyboard
    with the appropriate message.

    :param: message: current message
    :type: message: Message
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f"{name} is looking at the bot's capabilities")
    await state.reset_state(with_data=True)
    await Conditions.chose_place_keyboard.set()
    await message.answer(text='Сейчас я вам помогу)\n'
                              'Фотографии каких планет желаете посмотреть?',
                         reply_markup=inline.show_commands())
    return True


async def re_help_answer(message: Message) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Warns a user that an incorrect message
    has been entered, after which the keyboard with the capabilities available
    to the bot is displayed again (using appropriate function). The previous
    inline keyboard is being deleted.

    :param: message: current message
    :type: message: Message
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f"{name} entered incorrect answer"
                f" about using of the bot's capabilities")
    await message.bot.delete_message(chat_id=message.chat.id,
                                     message_id=message.message_id - 1)
    await message.answer(text='Кажется вы ввели что-то не то\n')
    await help_answer(message=message)
    return True


async def re_send_color_decision(message: Message) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware)
    to use his name when recording log message. Deletes the previous inline
    keyboard (with the question, about of viewing color or uncolor photos
    of Mars) if an incorrect message was entered and displays it again

    :param: message: current message
    :type: message: Message
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f"{name} entered incorrect answer"
                f" when when the color selection of Mars photos was expected")
    await message.bot.delete_message(chat_id=message.chat.id,
                                     message_id=message.message_id - 1)
    await message.answer(text='Я вас не понимаю, воспользуйтесь экранной клавиатурой '
                              'и выберите цвет фото)',
                         reply_markup=inline.mars_photos_color())
    return True


async def re_send_mars_photo(message: Message) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Warns the user that an incorrect message
    has been entered (after displaying the found photo of Mars and a keyboard
    offering to continue viewing the photo or stop it). Deletes the previous
    inline keyboard and displays it again.

    :param: message: current message
    :type: message: Message
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name = ctx_data.get()['user'].user_name
    logger.info(f"{name} entered incorrect answer"
                f" about continue of viewing photos of Mars")
    await message.bot.delete_message(chat_id=message.chat.id,
                                     message_id=message.message_id - 1)
    await message.answer(text='Я вас не понимаю, подумайте еще)\n',
                         reply_markup=inline.show_more_mars_photo())
    return True


async def re_send_earth_photo(message: Message) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Warns the user that an incorrect message
    has been entered (after displaying the found photo of Earth and a keyboard
    offering to continue viewing the photo or stop it). Deletes the previous
    inline keyboard and displays it again.

    :param: message: current message
    :type: message: Message
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f"{name} entered incorrect answer"
                f" about continue of viewing photos of Earth")
    await message.bot.delete_message(chat_id=message.chat.id,
                                     message_id=message.message_id - 1)
    await message.answer(text='Я вас не понимаю, подумайте еще)\n',
                         reply_markup=inline.show_more_earth_photo())
    return True


async def re_send_new_date_new_planet(message: Message) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Warns the user that an incorrect message
    has been entered, deletes the previous inline keyboard (with a question about
    choosing a new date and continuing to view photos of the previously selected
    planet, or switching to choosing another planet) and displays it again.

    :param: message: current message
    :type: message: Message
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f"{name} entered incorrect answer"
                f" when he had to enter new date of the chosen planet or"
                f"chose new planet")
    await message.bot.delete_message(chat_id=message.chat.id,
                                     message_id=message.message_id - 1)
    await message.answer(text='Я вас не понимаю, воспользуйтесь экранной клавиатурой '
                              'для ответа)',
                         reply_markup=inline.new_date_new_planet())
    return True


async def re_send_calendar(message: Message) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Warns the user that an incorrect message
    has been entered, then deletes the previous calendar and displays it again.

    :param: message: current message
    :type: message: Message
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f"{name} entered incorrect answer"
                f" when he had to enter the date")
    await message.bot.delete_message(chat_id=message.chat.id,
                                     message_id=message.message_id - 1)
    await message.answer(text='Я вас не понимаю, попробуйте ввести дату '
                              'при помощи экранной клавиатуры)',
                         reply_markup=await DialogCalendar().start_calendar())
    return True


def register_basic_handlers(dp: Dispatcher) -> None:
    """Registers handlers:
    1.The 'user_greeting' function is called when entered the /start command in any
    state
    2.The function of displaying the list of features of the bot ('help_answer')
    is called when entered the /help command or press the menu button in any state
    3.If incorrect information is entered (any content type) in the state when the
    keyboard with the question "is the user ready to fly to the space" ('yes_no_keyboard
    state') is displayed, a warning function (re_greeting) is called
    4.If incorrect information is entered (any content type) in the state when the keyboard
    with the rocket (rocket_button state) is displayed, the function (re_flight_beginning)
    is called that reports this
    5.If incorrect information is entered (any content type) in the state when the menu
    button (menu_button state) is displayed in the first time, the function that reports
    this (re_show_actions) is called
    6.If incorrect information is entered (any content type) in the state when the keyboard
    with the available bot capabilities is displayed (chose_place_keyboard state), the
    function that reports this (re_help_answer) is called
    7. If incorrect information is entered (any content type) in the state when the keyboard
    with variants for viewing photos of Mars (color / black and white) is displayed
    (mars_chose_color state),the function that reports this (re_send_color_decision) is called
    8. If incorrect information is entered (any content type) in the state when only the
    keyboard with a question about continuing to view photos of Mars or stopping doing this
    (the working_with_mars state) is available, the function (re_send_mars_photo) is called,
    that warns about this and displays keyboard from above again.
    9. If incorrect information is entered (any content type)  in the state when only the
    keyboard with a question about continuing to view photos of Earth or stopping doing
    this (the working_with_earth state) is available, the function (re_send_earth_photo)
    is called, that warns about this and displays keyboard from above again.
    10. If incorrect information (any content type) is entered in the state when only
    the keyboard, with a question about choosing a new date for photos of the same planet
    or choosing a new planet (new_date_new_planet state) is available, the function
    (re_send_new_date_new_planet) is called, that warns about this and displays keyboard
    from above again.
    11. If an incorrect information (any content type) is entered in the states (mars_chosen,
    earth_chosen, space_chosen) when only the calendar is displayed (after selecting the planet
    to view). the function that reports this (re_send_calendar) is called, that warns about this
    and displays keyboard from above again

    :param: dp: current dispatcher
    :type: dp: aiogram.Dispatcher
    :return: None

    """
    dp.register_message_handler(callback=user_greeting,
                                commands=['start'],
                                state='*')
    dp.register_message_handler(callback=help_answer,
                                commands=['help'],
                                state='*')
    dp.register_message_handler(help_answer,
                                Text(equals='Меню  🔭'),
                                state='*')
    dp.register_message_handler(callback=re_greeting,
                                state=Conditions.yes_no_keyboard,
                                content_types=ContentType.ANY)
    dp.register_message_handler(callback=re_flight_beginning,
                                state=Conditions.rocket_button,
                                content_types=ContentType.ANY)
    dp.register_message_handler(callback=re_show_actions,
                                state=Conditions.menu_button,
                                content_types=ContentType.ANY)
    dp.register_message_handler(callback=re_help_answer,
                                state=Conditions.chose_place_keyboard,
                                content_types=ContentType.ANY)
    dp.register_message_handler(callback=re_send_color_decision,
                                state=Conditions.mars_chose_color,
                                content_types=ContentType.ANY)
    dp.register_message_handler(callback=re_send_mars_photo,
                                state=Conditions.working_with_mars,
                                content_types=ContentType.ANY)
    dp.register_message_handler(callback=re_send_earth_photo,
                                state=Conditions.working_with_earth,
                                content_types=ContentType.ANY)
    dp.register_message_handler(callback=re_send_new_date_new_planet,
                                state=Conditions.new_date_new_planet,
                                content_types=ContentType.ANY)
    dp.register_message_handler(callback=re_send_calendar,
                                state=[Conditions.mars_chosen,
                                       Conditions.earth_chosen,
                                       Conditions.space_chosen],
                                content_types=ContentType.ANY)
