from typing import Dict, Any, Optional

import emoji
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.handler import ctx_data
from aiogram.types import CallbackQuery
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from tg_bot.handlers.users.API import show_mars_photo, show_earth_photo, show_space_photo
from tg_bot.handlers.users.actions import flight_beginning, help_answer, show_actions
from tg_bot.keyboards.inline.inline_keyboards import mars_photos_color
from tg_bot.misc.calendar import calendar_callback as dialog_cal_callback, DialogCalendar
from tg_bot.misc.states import Conditions
from tg_bot.services.logger.my_logger import get_logger

logger = get_logger(name=__name__)


async def yes_answer(call: CallbackQuery) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log messageProcesses the callback when pressing the
    "yes" button of the keyboard with the question 'is the user ready to fly into
    space' and the flight start function is called.

    :param: call: current callback
    :type: call: CallbackQuery
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} answered yes for question about flying ito space')
    await call.message.edit_text(text=emoji.emojize(
        'Отлично)\n'
        'Приcтегните ремни, начинаем взлетать :seat:')
    )
    await flight_beginning(message=call.message)
    return True


async def no_answer(call: CallbackQuery) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log messageProcesses the callback when pressing the
    "no" button of the keyboard with the question 'is the user ready to fly into
    space' and displays the words of farewell.

    :param: call: current callback
    :type: call: CallbackQuery
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} answered no for question about flying ito space')
    await call.message.edit_text(text='Ну что же, в таком случае я с вами прощаюсь)\n'
                                      'Полетаем в другой раз.\n'
                                      'Если вдруг передумаете воспользуйтесь командой /start\n')
    return True


async def start_flight(call: CallbackQuery) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log messageHandles the callback when the button with
    a rocket is pressed and the function that displays a list of the bot's
    capabilities is called.

    :param: call: current callback
    :type: call: CallbackQuery
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} soared high')
    await call.message.edit_text(text=emoji.emojize(
        ':airplane:' + '\n\nПрекрасно, мы набрали '
                       'достаточную высоту для работы :satellite:')
    )
    await show_actions(message=call.message)
    return True


async def mars_chosen(call: CallbackQuery, state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Handles a callback when the button with
    Mars is pressed. Remembers the selected place to visit as the dictionary
    value of the current state. Sets the state indicating that work with photos
    of Mars will be carried out in the future. Inline keyboard, with  a question
    about viewing photos of Mars in color or black and white is displayed

    :param: call: current callback
    :type: call: CallbackQuery
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} have chosen Mars')
    async with state.proxy() as data:
        data['explored_place'] = 'Mars'
    await Conditions.mars_chose_color.set()
    await call.message.edit_text('Хорошо, будем исследовать Марс)')
    await call.message.answer(emoji.emojize(':grinning_face:'))
    await call.message.answer('Какие фотографии желаете просмотреть?\n Имейте ввиду, '
                              'что черно-белый Марс\n некоторым может показаться слишком'
                              ' депрессивным, а поиск цветных фото\n иногда выполняется '
                              'очень долго (а иногда и вовсе в выбранный день я'
                              'не смогу найти ни одной цветной фотографии).\n '
                              'Так что подумайте хорошенько прежде чем выбрать)',
                              reply_markup=mars_photos_color())
    return True


async def processing_mars_color_decision(call: CallbackQuery,
                                         state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Records the selected decision to view
    color photos of Mars as the dictionary value of the current state. Sets next
    state, indicating that viewing photos of Mars has been selected. Displays
    a message prompting the user to select a date and the inline keyboard for
    this is displayed

    :param: call: current callback
    :type: call: CallbackQuery
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} have chosen viewing color photos of Mars')
    async with state.proxy() as data:
        data['mars_color_chosen'] = 'yes'
    await Conditions.mars_chosen.set()
    await call.message.edit_text('Хорошо, поищем цветное фото)\n'
                              'Теперь приступим к выбору даты для просмотра его фотографий\n'
                              'Если вы ввели что-то не то, смело нажимайте на кнопку'
                              'с выбранным вами параметром\n(год, месяц, день) и начинайте с начала',
                              reply_markup=await DialogCalendar().start_calendar())
    return True


async def processing_mars_uncolored_decision(call: CallbackQuery,
                                             state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Records the selected decision to view
    uncolored photos of Mars as the dictionary value of the current state. Sets
    next state, indicating that viewing photos of Mars has been selected.
    Displays the message prompting the user to select a date and the inline
    keyboard for this is displayed

    :param: call: current callback
    :type: call: CallbackQuery
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} have chosen viewing uncolored photos of Mars')
    async with state.proxy() as data:
        data['mars_color_chosen'] = 'no'
    await Conditions.mars_chosen.set()
    await call.message.edit_text('Хорошо поищем черно-белые фото)\n'
                              'Теперь приступим к выбору даты для просмотра его фотографий\n'
                              'Если вы ввели что-то не то, смело нажимайте на кнопку'
                              'с выбранным вами параметром\n(год, месяц, день) и начинайте с начала',
                              reply_markup=await DialogCalendar().start_calendar())
    return True


async def earth_chosen(call: CallbackQuery, state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Records the selected decision to view
    photos of Earth as the dictionary value of the current state. Sets
    next state, indicating that viewing photos of Earth has been selected.
    Displays the message prompting the user to select a date and the inline
    keyboard for this is displayed

    :param: call: current callback
    :type: call: CallbackQuery
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} have chosen Earth')
    async with state.proxy() as data:
        data['explored_place'] = 'Earth'
    await Conditions.earth_chosen.set()
    await call.message.edit_text('Хорошо, будем исследовать Землю)')
    await call.message.answer(emoji.emojize(':grinning_face:'))
    await call.message.answer('Приступим к выбору даты для просмотра ее фотографий)\n'
                              'Если вы ввели что-то не то, смело нажимайте на кнопку '
                              'с выбранным вами параметром\n(год, месяц, день) и начинайте '
                              'с начала',
                              reply_markup=await DialogCalendar().start_calendar())
    return True


async def space_chosen(call: CallbackQuery, state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Records the selected decision to view
    photos of space as the dictionary value of the current state. Sets
    next state, indicating that viewing photos of space has been selected.
    Displays the message prompting the user to select a date and the inline
    keyboard for this is displayed

    :param: call: current callback
    :type: call: CallbackQuery
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} have chosen to explore the space')
    async with state.proxy() as data:
        data['explored_place'] = 'Space'
    await Conditions.space_chosen.set()
    await call.message.edit_text('Хорошо, будем исследовать Космос)')
    await call.message.answer(emoji.emojize(':grinning_face:'))
    await call.message.answer('Приступим к выбору даты для просмотра его фотографий)\n'
                              'Если ввели что-то не то, смело нажимайте на кнопку '
                              'с выбранным вами параметром\n(год, месяц, день) и начинайте с начала',
                              reply_markup=await DialogCalendar().start_calendar())
    return True


async def process_dialog_calendar(call: CallbackQuery, callback_data: CallbackData,
                                  state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. displays the date entered by the user
    and records it as the dictionary value of the current state. Depending on
    the selected location for viewing photos at the previous stage, the
    corresponding functions are called that show photos of planets or space

    :param: call: current callback
    :type: call: CallbackQuery
    :param: callback_data: data of current callback query
    :type: callback_data: CallbackData (Dict)
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} is entering the date')
    selected, date = await DialogCalendar().process_selection(call, callback_data)
    selected: bool
    date: date
    if selected:
        await call.message.edit_text(
            f'Вы выбрали {date.strftime("%d-%m-%Y")}'
        )
        await state.update_data(calendar_date=date.strftime('%Y-%m-%d'))
        current_data: Dict[str: Any] = await state.get_data()
        if current_data['explored_place'] == 'Mars':
            await show_mars_photo(message=call.message, state=state)
        elif current_data['explored_place'] == 'Earth':
            await show_earth_photo(message=call.message, state=state)
        elif current_data['explored_place'] == 'Space':
            await show_space_photo(message=call.message, state=state)
    return True


async def more_mars_photo(call: CallbackQuery, state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Informs the user that the exploration
    of Mars is ongoing and calls the function to display its photo

    :param: call: current callback
    :type: call: CallbackQuery
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} is continuing of Mars exploring')
    await call.message.edit_text('Продолжаем исследовать Марс')
    await show_mars_photo(message=call.message, state=state)
    return True


async def no_more_mars_photo(call: CallbackQuery, state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Processes a callback when the button
    to stop viewing photos of Mars is pressed and displays a keyboard with
    a list of bot features

    :param: call: current callback
    :type: call: CallbackQuery
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} dont wont to explore Mars anymore')
    await call.message.edit_text('В самом деле, Марс уже поднадоел)')
    await help_answer(message=call.message, state=state)
    return True


async def more_earth_photo(call: CallbackQuery, state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Processes a callback when the user
    pressed the button to continue exploring Earth and would want to see more
    of its photo

    :param: call: current callback
    :type: call: CallbackQuery
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} is continuing of Earth exploring')
    await call.message.edit_text('Продолжаем исследовать Землю')
    await show_earth_photo(message=call.message, state=state)
    return True


async def no_more_earth_photo(call: CallbackQuery, state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Processes a callback when the button
    to stop viewing photos of Earth is pressed and displays a keyboard with
    a list of bot features.

    :param: call: current callback
    :type: call: CallbackQuery
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} dont wont to explore Ears anymore')
    await call.message.edit_text('В самом деле, Земля уже поднадоела)')
    await help_answer(message=call.message, state=state)
    return True


async def new_date(call: CallbackQuery, state: FSMContext) -> bool:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Processes a callback when the button is
    pressed to select another date to view photos of the corresponding planet/space
    Depending on the location visited at the previous stage (stored as dictionary
    values of the current state), the corresponding state is re-set. Displays
    a calendar for selecting a new date. The previous inline keyboard is being
    deleted.

    :param: call: current callback
    :type: call: CallbackQuery
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} have chosen a new date of viewing photos '
                f'of the current planet')
    if call:
        current_data: Dict[str: Any] = await state.get_data()
        if current_data['explored_place'] == 'Mars':
            await Conditions.mars_chosen.set()
        elif current_data['explored_place'] == 'Earth':
            await Conditions.earth_chosen.set()
        elif current_data['explored_place'] == 'Space':
            await Conditions.space_chosen.set()
    await call.message.edit_text('Выберите новую дату',
                                 reply_markup=await DialogCalendar().start_calendar())
    return True


async def new_planet(call: CallbackQuery, state: FSMContext) -> bool:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Processes a callback when the button
    for selecting a new planet is pressed, after which a function is called
    that will display a list of the bot's capabilities.The previous inline
    keyboard is being deleted.

    :param: call: current callback
    :type: call: CallbackQuery
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} have chosen a new planet ')
    await call.message.edit_text('Меняем курс)')
    await help_answer(message=call.message, state=state)
    return True


async def history(call: CallbackQuery) -> bool:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Sets the dictionary value of the context
    variable to true. Further extraction of photos from the database is carried
    out via DbMiddleware

    :param: call: current callback
    :type: call: CallbackQuery
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} looks at the history of space travel')
    await call.message.edit_text('Хорошо, посмотрим историю наших путешествий)\n')
    data: Dict[str: Any] = ctx_data.get()
    data['show_photo']: bool = True
    ctx_data.set(data)
    return True


async def finish_work(call: CallbackQuery, state: FSMContext) -> bool:
    """Retrieves the necessary user from the database (via DataMiddleware) to use
    his name when recording log message. Handles a callback when the button
    'finish_work' is pressed and displays the words of farewell. Resets the
    current state to its original condition along with all the data.

    :param: call: current callback
    :type: call: CallbackQuery
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} does not want to see any photos that the bot can show')
    await call.message.edit_text('Тогда на сегодня закончим\n')
    await call.message.answer('Обращайтесь при любой необходимости)',
                              reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=True)
    await call.answer()
    return True


def register_callbacks_handlers(dp: Dispatcher) -> None:
    """Registers callback query handlers:
    1. the 'yes_answer' function is called when the 'yes' button of the keyboard with
    the question 'is the user ready to fly into space' is pressed (only in the state
    'yes_no_keyboard'). CallbackData (text filter) == 'yes'
    2. the 'no_answer' function is called when the 'no' button of the keyboard with
    the question 'is the user ready to fly into space' is pressed (only in the state
    'yes_no_keyboard'). CallbackData (text filter) == 'no'
    3.the 'start_flight' function is called when the rocket button is pressed and the
    user "flew into space" (only in the state 'rocket_button'). CallbackData (text
    filter) == 'go'
    4. the 'mars_chosen' function is called when the 'Mars' button of keyboard with
    available capabilities of the bot is pressed (only in the state
    'chose_place_keyboard'). CallbackData (text filter) == 'Mars'
    5. the 'processing_mars_color_decision' function is called when the button to
    view color photos of Mars is pressed (only in the state 'mars_chose_color').
    CallbackData (text filter) == 'Color_photos'.
    6. the 'processing_mars_uncolored_decision' function is called when the button
    to view uncolored photos of Mars is pressed (only in the state 'mars_chose_color').
    CallbackData (text filter) == 'Black_white_photos'.
    7. the 'more_mars_photo' function is called when the button 'continue exploring
    Mars and getting its photos' is pressed (only in the state 'working_with_mars').
    CallbackData (text filter) == 'mars_continue'
    8. the 'no_more_mars_photo' function is called when the 'stop Mars exploration'
    button is pressed (only in the state 'working_with_mars').
    CallbackData (text filter) == 'mars_stop'
    9.the 'earth_chosen' function is called when the 'Earth' button of keyboard with
    available capabilities of the bot is pressed (only in the state 'chose_place_keyboard').
    CallbackData (text filter) == 'Earth'
    10. the 'more_earth_photo' function is called when the button 'continue exploring
    the Earth and getting its photos' is pressed (only in the state 'working_with_earth').
    CallbackData (text filter) == 'earth_continue'
    11. the 'no_more_earth_photo' function is called when the 'stop Earth exploration'
    button is pressed (only in the state 'working_with_earth'). CallbackData == 'earth_stop'
    12. the 'space_chosen' function is called when the 'Space' button of keyboard with
    available capabilities of the bot is pressed (only in the state 'chose_place_keyboard').
    CallbackData (text filter) == 'Space'
    13. the 'new_date' function is called when the button 'new date' is pressed
    (only in the state 'new_date_new_planet'). CallbackData (text filter) == 'new_date'
    14. the 'new_planet' function is called when the button 'new planet' is pressed
    (only in the state 'new_date_new_planet'). CallbackData (text filter) == 'new_planet'
    15. the 'process_dialog_calendar' function is called when the date of viewing
    the photo is entered and the result corresponds to the dialog_cal_callback.filter()
    (in the next states: mars_chosen, earth_chosen, space_chosen)
    16. the 'history' function is called when  the history button is pressed (only in
    the state 'chose_place_keyboard'). CallbackData (text filter) == 'history'
    17. the 'finish_work' function is called when the stop working with the bot button
    is pressed (in the state 'chose_place_keyboard'). CallbackData (text filter) == 'finish_work'

    :param: dp: current dispatcher
    :type: dp: Dispatcher
    :return: None

    """
    dp.register_callback_query_handler(yes_answer,
                                       Text(equals='yes'),
                                       state=Conditions.yes_no_keyboard)
    dp.register_callback_query_handler(no_answer,
                                       Text(equals='no'),
                                       state=Conditions.yes_no_keyboard)
    dp.register_callback_query_handler(start_flight,
                                       Text(equals='go'),
                                       state=Conditions.rocket_button)
    dp.register_callback_query_handler(mars_chosen,
                                       Text(equals='Mars'),
                                       state=Conditions.chose_place_keyboard)
    dp.register_callback_query_handler(processing_mars_color_decision,
                                       Text(equals='Color_photos'),
                                       state=Conditions.mars_chose_color)
    dp.register_callback_query_handler(processing_mars_uncolored_decision,
                                       Text(equals='Black_white_photos'),
                                       state=Conditions.mars_chose_color)
    dp.register_callback_query_handler(more_mars_photo,
                                       Text(equals='mars_continue'),
                                       state=Conditions.working_with_mars),
    dp.register_callback_query_handler(no_more_mars_photo,
                                       Text(equals='mars_stop'),
                                       state=Conditions.working_with_mars)
    dp.register_callback_query_handler(earth_chosen,
                                       Text(equals='Earth'),
                                       state=Conditions.chose_place_keyboard),
    dp.register_callback_query_handler(more_earth_photo,
                                       Text(equals='earth_continue'),
                                       state=Conditions.working_with_earth)
    dp.register_callback_query_handler(no_more_earth_photo,
                                       Text(equals='earth_stop'),
                                       state=Conditions.working_with_earth)
    dp.register_callback_query_handler(space_chosen,
                                       Text(equals='Space'),
                                       state=Conditions.chose_place_keyboard)
    dp.register_callback_query_handler(new_date,
                                       Text(equals='new_date'),
                                       state=Conditions.new_date_new_planet)
    dp.register_callback_query_handler(new_planet,
                                       Text(equals='new_planet'),
                                       state=Conditions.new_date_new_planet)
    dp.register_callback_query_handler(process_dialog_calendar,
                                       dialog_cal_callback.filter(),
                                       state=[Conditions.mars_chosen,
                                              Conditions.earth_chosen,
                                              Conditions.space_chosen]),
    dp.register_callback_query_handler(history,
                                       Text(equals='history'),
                                       state=Conditions.chose_place_keyboard)
    dp.register_callback_query_handler(finish_work,
                                       Text(equals='finish_work'),
                                       state=Conditions.chose_place_keyboard)
