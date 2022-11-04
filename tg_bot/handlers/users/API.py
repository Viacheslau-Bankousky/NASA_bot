import json
import traceback
from io import BytesIO
from random import randint
from typing import Optional, List, Dict, Any

from PIL import Image
from aiogoogletrans import Translator
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import ctx_data
from aiogram.types import Message
from aiogram.utils.exceptions import TelegramAPIError
from aiohttp import ClientSession

import tg_bot.keyboards.inline.inline_keyboards as inline
from tg_bot.misc.states import Conditions
from tg_bot.services.logger.my_logger import get_logger

logger = get_logger(name=__name__)


async def get_all_mars_photos(message: Message, state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use his name
    when recording log message. Takes the current data (dictionary of the current state).
    Sends a request to the API and performs deserialization of the received json (the
    response contains all photos of the rover on the selected day). If there is not
    'photos' key in the dictionary (deserialized json), then this indicates that the
    number of api requests made has been exceeded and should be tried again a little later.
    If nothing is found in the dictionary by the key 'photos', then this indicates that on
    this day the rover did not take any photos, and you need to choose a different date
    or place. Sets the state in which only the keyboard with the selection of a new date
    (continue viewing of chosen place) or the selection of a new planet is available. If the
    connection fails,the request is repeated (3 times). If the number of connection
    attempts to the api reaches the specified limit, the function returns. If all photos
    of the Mars are received, they are processed and the necessary information (photo id)
    is extracted (using 'process_mars_data' function), after this True is returned.

    :param: message: current message
    :type: message: Message
    :param: state: current state
    :type: state: FSMContext
    :return: True, If photos of the Mars are received or None (if the total number
    of requests to the api or connection attempts is exceeded or something went wrong)
    :rtype: Optional[bool]

    """
    current_data: Dict[str: Any] = await state.get_data()
    name: str = ctx_data.get()['user'].user_name
    connection_attempts: int = 0
    ROVER_URL: str = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'
    params: Dict[str: str] = dict(earth_date=current_data.get('calendar_date'),
                        api_key=message.bot.get('config').api.nasa_api_token)
    while True:
        if connection_attempts == 3:
            await message.answer('Попробуйте воспользоваться мной немного позже')
            logger.critical(f'In the process of getting all Mars photos, after three attempts '
                            f'of connection to the API, {name} finished his work'
                            f' with the bot')
            return
        async with ClientSession() as session:
            async with session.get(url=ROVER_URL, params=params) as response:
                if response.status == 200:
                    response_dictionary: json = await response.json()
                    if 'photos' not in response_dictionary:
                        logger.critical(f'{name} in the process of receiving Mars photos'
                                        f' has exhausted the daily limit of the API connections')
                        await message.answer('Вы исчерпали лимит попыток,'
                                             ' попробуйте воспользоваться мной немного позже')
                        return
                    elif not response_dictionary.get('photos'):
                        logger.warning(f"{name} couldn't find any photos of Mars "
                                       f"on the specified date")
                        await Conditions.new_date_new_planet.set()
                        await message.answer('В этот день марсоход не сделал ни одного фото)\n'
                                             'Хотите изменить свое решение?',
                                             reply_markup=inline.new_date_new_planet())
                        return
                    else:
                        logger.info(f'{name} have received all photos of Mars '
                                    f'(not processed)')
                        await process_mars_data(initial_mars_data=response_dictionary, state=state)
                        return True
                else:
                    await message.answer('Кажется появились какие-то проблемы с подключением\n'
                                         'Сейчас попробуем еще раз')
                    connection_attempts += 1
                    logger.warning(f'{name} has an unsuccessful connection attempt to the API '
                                   f'at the stage of getting all photos of Mars')


async def process_mars_data(initial_mars_data: json, state: FSMContext) -> None:
    """Retrieves the necessary user from the database (via DataMiddleware) to use his
    name when recording log message. Creates an iterator from a deserialized json,
    passed to the function as an argument (contains all photos of Mars). Iterate over
    it and extracts photo IDs from nested dictionaries and adds them to the list that
    is assigned as the value of the dictionary of the current state data (key - 'mars_photos')

    :param: initial_mars_data: all information about the Mars photos
    :type: initial_mars_data: deserialized json
    :param: state: current state
    :type: state: FSMContext
    :return: None

    """
    final_mars_data: List = list()
    for i_dictionary in iter(initial_mars_data.get('photos')):
        final_mars_data.append(i_dictionary['img_src'])
    async with state.proxy() as data:
        data['mars_photos']: List[str] = final_mars_data
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} have processed all photos of Mars')



async def mars_request(message: Message, state: FSMContext) -> Optional[bytes]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use his name
    when recording log message. Takes the current data (dictionary of the current state).
    Executes an API request, using the ID (random) of the Mars photo from the  list, assigned as
    the value of the dictionary of the current state data (key - 'mars_photos'). If the connection
    fails, the request is repeated (3 times). If the number of connection attempts to the API
    reaches the specified limit, the function returns. A successful response is transformed
    into bytes and passed to the validator function, which checks whether the photo matches
    the specified parameters. If the photo is high resolution, it is returned. The url of the
    Mars photo is recorded as the value of the contextual data dictionary for later addition
    to the database using DataMiddleware. If all photos are shown (or None are found), it is
    suggested to select a new date and continue exploring the selected place or choose another
    (the state is set, in which only calendar is available).

    :param: message: current message
    :type: message: Message
    :param: state: current state
    :type: state: FSMContext
    :exception: The IndexError, AttributeError, ValueError exceptions occur if there are
    no more photos of Mars in the list (the value of the 'mars_photos' key of the dictionary of
    the current state).
    :return: high-resolution photo transformed into bytes or None (if the total number
    of requests to the api / connection attempts is exceeded or something went wrong)
    :rtype: Optional[bytes]

    """
    connection_attempts: int = 0
    name: str = ctx_data.get().get('user').user_name
    current_data: Dict[str: Any] = await state.get_data()
    while True:
        if connection_attempts == 3:
            logger.critical(f'In the process of getting one Mars photo, after three attempts '
                            f'of connection to the API, {name} finished his work '
                            f'with the bot')
            await message.answer('Попробуйте воспользоваться мной немного позже')
            return
        try:
            current_photo: str = current_data.get('mars_photos').pop(
                randint(0, len(current_data.get('mars_photos')) - 1))
            async with ClientSession() as session:
                async with session.get(url=current_photo) as response:
                    if response.status == 200:
                        logger.info(f'{name} have received some picture of Mars, '
                                    f'and is going to check its quality')
                        bytes_image: bytes = await response.read()
                        if await validate_mars_image(image_bytes=bytes_image, state=state):
                            data: Dict = ctx_data.get()
                            data['photo_url']: str = str(response.url)
                            ctx_data.set(data)
                            return bytes_image
                    else:
                        await message.answer('Кажется появились какие-то проблемы с подключением\n'
                                             'Сейчас попробуем еще раз')
                        connection_attempts += 1
                        logger.warning(f'{name} has an unsuccessful connection attempt'
                                       f' to the API at the stage of receiving one photo of Mars')
        except (IndexError, AttributeError, ValueError):
            logger.warning(f'{name} did not find any photos of Mars on the specified day '
                           f'in the list of photos\n {traceback.format_exc()}')
            await Conditions.new_date_new_planet.set()
            await message.answer('Кажется фото с высоким разрешением в этот день больше нет\n'
                                 'Хотите изменить свое решение?',
                                 reply_markup=inline.new_date_new_planet())
            return


async def validate_mars_image(image_bytes: bytes, state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use his name
    when recording log message. Performs a check of the photo of Mars, translated into
    bytes, for compliance with the specified size and color.

    :param: image_bytes: transformed current image of Mars
    :type: image_bytes: bytes
    :param: state: current state
    :type: state: FSMContext
    :return: True, if the photo meets the specified standard, else False;
    (None if something went wrong)
    :rtype: Optional[bool]

    """
    name: str = ctx_data.get().get('user').user_name
    image: image_bytes = Image.open(BytesIO(initial_bytes=image_bytes))
    current_data: Dict[str: str] = await state.get_data()
    if current_data.get('mars_color_chosen') == 'yes':
        if image.width >= 1024 and image.height >= 1024 and image.mode != 'L':
            logger.info(f'{name} have received the photo of Mars with high resolution')
            return True
        else:
            logger.info(f'{name} have received the photo of Mars with a low resolution')
            return False
    elif current_data.get('mars_color_chosen') == 'no':
        if image.width >= 1024 and image.height >= 1024:
            logger.info(f'{name} have received the photo of Mars with high resolution')
            return True
        else:
            logger.info(f'{name} have received the photo of Mars with a low resolution')
            return False



async def get_mars_photo_bytes(message: Message, state: FSMContext) -> Optional[bytes]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use his name
    when recording log message. Takes the current data (dictionary of the current state).
    If the first api request is not executed and there are no photos of Mars yet, using
    the 'get_all_mars_photos' function gets all photos of Mars (idetifiers of photos in
    the list), writes them as the value of  the dictionary of the current state (in the
    future, photos are taken from here, bypassing the first request to the api). If the
    number of api requests or the number of connection attempts is exceeded, the function
    returns. In all cases, a request is sent to the api and receives a high-resolution photo
    of Mars in the form of bytes (using the mars_request function).

    :param: message: current message
    :type: message: Message
    :param: state: current state
    :type: state: FSMContext
    :return: high-resolution photo transformed into bytes or None (if the total number
    of requests to the api / connection attempts is exceeded or something went wrong)
    :rtype: Optional[bytes]

    """
    name: str = ctx_data.get()['user'].user_name
    current_data: Dict[str: Any] = await state.get_data()
    if not current_data.get('mars_photos'):
        logger.info(f'{name} is sending a request to the API at the first time'
                    f'(in the process of receiving of Mars photos)')
        current_urls: bool = await get_all_mars_photos(message=message, state=state)
        if not current_urls:
            return
        mars_photo_bytes: bytes = await mars_request(message=message, state=state)
    else:
        logger.info(f'{name} is sending a following request to the API '
                    f'(in the process of receiving of Mars photos)')
        mars_photo_bytes: bytes = await mars_request(message=message, state=state)
    return mars_photo_bytes


async def show_mars_photo(message: Message, state: FSMContext) -> None:
    """Sets the state (working_with_mars) in which only the keyboard offering "view photos
    of Mars or stop" is available. Sends a gif message to the user, which is displayed until
    the photo of Mars with the above keyboard appears or the message appears stating that the
    api connection limit or the number of connection attempts has been exceeded. Retrieves the
    necessary user from the database (via DataMiddleware) to use his name when recording log message.

    :param: message: current message
    :type: message: Message
    :param: state: current state
    :type: state: FSMContext
    :return: None

    """
    await Conditions.working_with_mars.set()
    gif: Message = await message.bot.send_animation(
        chat_id=message.chat.id,
        animation='https://vgif.ru/gifs/166/vgif-ru-37964.gif')
    image: bytes = await get_mars_photo_bytes(message=message, state=state)
    if image:
        current_data: Dict[str: Any] = await state.get_data()
        await message.bot.send_photo(chat_id=message.chat.id,
                                     photo=image,
                                     caption=f'Актуальное фото Марса на {current_data["calendar_date"]}')
        await message.answer('\nНу что, останемся еще немного на этой планете '
                             'или выберем что-то другое?)', reply_markup=inline.show_more_mars_photo())
        name: str = ctx_data.get()['user'].user_name
        logger.info(f'{name} have watched one photo of Mars')
    await gif.delete()


async def get_all_earth_photos(message: Message, state: FSMContext) -> Optional[bool]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use his name
    when recording log message. Takes the current data (dictionary of the current state).
    Sends a request to the API and performs deserialization of the received json (the
    response contains all photos of Earth on the selected day). If the deserialized json
    does not contain any data inside, the user is informed that no photos were found on
    the specified date and using the special inline keyboard, it suggests to choose another
    date or place. The state (new_date_new_planet) is set, when only this keyboard is available.
    The dictionary containing all photos of Earth (deserialized json) is passed into the
    function ('process_earth_data') which process it and transform to the proper form (dictionary,
    containing the image ID and its date as the values)  and writes this dict as the value of
    dictionary of the current state (in this case, True is returned). If the connection fails,
    the request is repeated. If the number of connection attempts to the api reaches the specified
    limit, the function returns.

    :param: message: current message
    :type: message: Message
    :param: state: current state
    :type: state: FSMContext
    :return: True (if all photos of Earth was received) or None (if the total number
    of requests to the api / connection attempts is exceeded or something went wrong)
    :rtype: Optional[bool]

    """
    connection_attempts: int = 0
    current_data: Dict[str: Any] = await state.get_data()
    URL: str = f'https://api.nasa.gov/EPIC/api/natural/date/{current_data["calendar_date"]}'
    params: Dict = dict(api_key=message.bot.get('config').api.nasa_api_token)
    name: str = ctx_data.get()['user'].user_name
    while True:
        if connection_attempts == 3:
            await message.answer('Попробуйте воспользоваться мной немного позже')
            logger.critical(f'In the process of getting all Earth photos, after three attempts '
                            f'of connection to the  API, {name} finished his work '
                            f'with the bot')
            return
        async with ClientSession() as session:
            async with session.get(url=URL, params=params) as response:
                if response.status == 200:
                    all_earth_photos: json = await response.json()
                    if not all_earth_photos:
                        logger.warning(f"{name} couldn't find any photos of Earth"
                                       f" on the specified date")
                        await Conditions.new_date_new_planet.set()
                        await message.answer('В выбранную вами дату нет ни одного фото\n'
                                             'Измените сове решение?',
                                             reply_markup=inline.new_date_new_planet())
                        return
                    else:
                        logger.info(f'{name} have received all photos of Earth '
                                    f'(not processed)')
                        await process_earth_data(initial_earth_data=all_earth_photos, state=state)
                        return True
                else:
                    await message.answer('Кажется появились какие-то проблемы с соединением\n'
                                         'пробуем подключиться еще раз')
                    connection_attempts += 1
                    logger.warning(f'{name} has an unsuccessful connection attempt '
                                   f'to the API at the stage of getting all photos of Earth')


async def process_earth_data(initial_earth_data: json, state: FSMContext) -> None:
    """Processes the json passed as the argument (total information about all photos of Earth),
    and generates the list with dictionaries containing basic information about photos (the
    specifier of each photo and the current date of the snapshots as values of the dictionary).
    Converts the date to the YY/mm/dd format. Writes the list of dictionaries with data for each
    photo as the value of the dictionary of the current state. Retrieves the necessary user from
    the database (via DataMiddleware) to use his name when recording log message.

    :param: initial_earth_data: total information about all Earth photos
    :type: initial_earth_data: json
    :param: state: current state
    :type: state: FSMContext
    :return: None

    """
    final_earth_data: List = list()
    for i_dictionary in iter(initial_earth_data):
        final_earth_data.append(dict(image=i_dictionary['image'],
                                     date=i_dictionary['date'].split(' ')[0]))
    for j_dictionary in final_earth_data:
        for symbol in j_dictionary['date']:
            if symbol == '-':
                j_dictionary['date'] = j_dictionary['date'].replace(symbol, '/')
    async with state.proxy() as data:
        data['earth_photos'] = final_earth_data
    name: str = ctx_data.get()['user'].user_name
    logger.info(f'{name} have processed all photos of Earth')


async def earth_request(message: Message, state: FSMContext) -> Optional[str]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use his name when
    recording log message. Takes the current data (dictionary of the current state). Executes
    an api request using the ID of Earth photo and the date of its snapshot from the dictionary
    that was extracted from the list with dictionaries from dictionary of the current state
    (when data about all Earth photos is collected). If the connection fails, the request is
    repeated. If the number of connection attempts to the api reaches the specified limit,
    the function returns. A successful response is transformed into bytes and will be returned.
    If all photos are shown (or none are found), it is suggested to select a new date and continue
    exploring the selected place or choose another place (a state is set in which only this keyboard
    is available).

    :param: message: current message
    :type: message: Message
    :param: state: current state
    :type: state: FSMContext
    :exception: The IndexError, AttributeError, ValueError exceptions occur if there
    are no more photos of Earth in the list with dictionaries (the value
    of the dictionary of the current state)
    # :return:  url of the photo of Earth or None (if the total number of requests to
    the api / connection attempts is exceeded or something went wrong)
    :rtype: Optional[string]

    """
    connection_attempts: int = 0
    name: str = ctx_data.get()['user'].user_name
    current_data: Dict[str: Any] = await state.get_data()
    while True:
        if connection_attempts == 3:
            logger.critical(f'In the process of getting one Earth photo, after '
                            f'three attempts of connection to the API, {name} '
                            f'finished his work with the bot')
            await message.answer('Попробуйте воспользоваться мной немного позже')
            return
        try:
            current_photo_dict: Dict[str: str] = current_data['earth_photos'].pop(
                randint(0, len(current_data['earth_photos']) - 1))
            current_date: str = current_photo_dict['date']
            current_image: str = current_photo_dict['image']
            URL: str = f'https://api.nasa.gov/EPIC/archive/natural/{current_date}/png/{current_image}.png'
            params: Dict[str: str] = dict(api_key=message.bot.get('config').api.nasa_api_token)
            async with ClientSession() as session:
                async with session.get(url=URL, params=params) as response:
                    if response.status == 200:
                        current_photo = str(response.url)
                        logger.info(f'{name} have received one photo of Earth')
                        return current_photo
                    else:
                        await message.answer('Кажется появились какие-то проблемы с подключением\n'
                                             'Сейчас попробуем еще раз')
                        connection_attempts += 1
                        logger.warning(f'{name} has an unsuccessful connection attempt'
                                       f' to the API at the stage of receiving one photo of Earth')
        except (IndexError, AttributeError, ValueError):
            logger.warning(f'{name} did not find any photos of Earth on the specified '
                           f'day in list of photos\n {traceback.format_exc()}')
            await Conditions.new_date_new_planet.set()
            await message.answer('Кажется на указанную вами дату больше нет ни одной фотографии\n '
                                 'Желаете изменить решение?',
                                 reply_markup=inline.new_date_new_planet())
            return


async def get_one_earth_photo(message: Message, state: FSMContext) -> Optional[str]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use his name when
    recording log message. Takes the current data (dictionary of the current state). If the
    first api request is not executed and there are no photos of Earth yet, using the
    'get_all_earth_photos' function gets all photos of Earth (dictionaries with main
    parameters of each Earth photo in list), writes them as the value of the dictionary
    of the current state  (in the future, photos are taken from here, bypassing the first
    request to the api). If the number of api requests or the number of connection attempt
    is exceeded, the function exits. In all cases, a request is sent to the api and receives
    a photo of Mars in the form of bytes (using the earth_request function).

    :param: message: current message
    :type: message: Message
    :param: state: current state
    :type: state: FSMContext
    :return: url of the photo of Earth or None (if the total number of requests
    to the api / connection attempts is exceeded or something went wrong)
    :rtype: Optional[string]

    """
    name: str = ctx_data.get()['user'].user_name
    current_data: Dict[str: Any] = await state.get_data()
    if not current_data.get('earth_photos'):
        logger.info(f'{name} is sending a request to the API at the first time'
                    f'(in a process of receiving Earth photos)')
        current_urls: bool = await get_all_earth_photos(message=message, state=state)
        if not current_urls:
            return
        earth_photo: str = await earth_request(message=message, state=state)
    else:
        logger.info(f'{name} is sending a following request to the API '
                    f'(in a process of receiving Earth photos)')
        earth_photo: str = await earth_request(message=message, state=state)
    return earth_photo


async def show_earth_photo(message: Message, state: FSMContext) -> None:
    """Takes the current data (dictionary of the current state). Sets the state in which only
    the keyboard offering "view photos of Earth or stop" is available. Sends a gif message to
    the user, which is displayed until a photo of Earth with the above keyboard appears or
    a message appears, stating that the api connection limit or the number of connection
    attempts has been exceeded. Retrieves the necessary user from the database (via DataMiddleware)
    to use his name when recording log message. Writes the url of the photo of Earth as the
    dictionary value of the context data (for later addition to the database via DataMiddleware)

    :param: message: current message
    :type: message: Message
    :param: state: current state
    :type: state: FSMContext
    :return: None

    """
    current_data: Dict[str: Any] = await state.get_data()
    await Conditions.working_with_earth.set()
    gif: Message = await message.bot.send_animation(
        chat_id=message.chat.id,
        animation='https://vgif.ru/gifs/166/vgif-ru-37964.gif')
    image: str = await get_one_earth_photo(message=message, state=state)
    if image:
        await message.bot.send_photo(chat_id=message.chat.id,
                                     photo=image,
                                     caption=f'Актуальное фото земли на {current_data["calendar_date"]}\n')
        await message.answer('\nНу что, останемся еще немного на этой планете '
                             'или выберем что-то другое?)',
                             reply_markup=inline.show_more_earth_photo())
        name: str = ctx_data.get()['user'].user_name
        logger.info(f'{name} have watched one photo of Earth')
        data: Dict = ctx_data.get()
        data['photo_url']: str = image
        ctx_data.set(data)
    await gif.delete()


async def get_all_space_data_from_api(message: Message, state: FSMContext) -> Optional[Dict]:
    """Retrieves the necessary user from the database (via DataMiddleware) to use his name when
    recording log message. Takes the current data (dictionary of the current state). Executes
    an api request using the date of the space snapshot from 'current data'. If the connection
    fails, the request is repeated. If the number of connection attempts to the api reaches
    the specified limit, the function returns. A successful response is deserialized to the
    dictionary

    :param: message: current message
    :type: message: Message
    :param: state: current state
    :type: state: FSMContext
    :return: dictionary (deserialized json) with the main parameters of the space object
    (url, description, etc.) on the selected date, or None (if the total number of requests
    to the api / connection attempts is exceeded or something went wrong)
    :return: Optional[Dictionary]

    """
    connection_attempts: int = 0
    current_data: Dict[str: Any] = await state.get_data()
    URL: str = f'https://api.nasa.gov/planetary/apod'
    params: Dict[str: str] = dict(date=current_data['calendar_date'],
                        api_key=message.bot.get('config').api.nasa_api_token)
    name: str = ctx_data.get()['user'].user_name
    while True:
        if connection_attempts == 3:
            logger.critical(f'In the process of getting one photo of the space, after '
                            f'three attempts of connection to the API, {name} '
                            f'finished his work with the bot')
            await message.answer('Попробуйте воспользоваться мной немного позже')
            return
        async with ClientSession() as session:
            async with session.get(url=URL, params=params) as response:
                if response.status == 200:
                    current_photo: json = await response.json()
                    logger.info(f'{name} have received one photo of Earth')
                    return current_photo
                else:
                    await message.answer('Кажется появились какие-то проблемы с подключением\n'
                                         'Сейчас попробуем еще раз')
                    connection_attempts += 1
                    logger.warning(f'{name} has an unsuccessful connection attempt'
                                   f' to the API at the stage of receiving one photo of the space')


async def show_space_photo(message: Message, state: FSMContext) -> None:
    """Displays a GIF message that will be active until the photo with a description
    of it is displayed. The api request is executed using the get_all_space_data_from_api
    function, which returns a dictionary (deserialized json) with the main parameters of
    the space object (url, description, etc.) on the selected date. Retrieves the necessary
    user from the database (via DataMiddleware) to use his name when recording log message.
    The text with the description of the current photo is translated using aiogoogletrans.
    After the photo with description is displayed. The state is set, in which only the
    keyboard is available, offering to select a new date and continue exploring space
    or choose another place. The above keyboard is displayed with the corresponding message.
    Writes the url of the photo of Space as the dictionary value of the context data
    (for later addition to the database via DataMiddleware)

    :param: message: current message
    :type: message: aiogram.types.Message
    :exception: TelegramAPIError: If the user received a bad photo (you will be prompted
    to select a different date. The state in which only the inline calendar is available
    will be set)
    :return: None

    """
    gif: Message = await message.bot.send_animation(
        chat_id=message.chat.id,
        animation='https://vgif.ru/gifs/166/vgif-ru-37964.gif')
    space_data: json = await get_all_space_data_from_api(message=message, state=state)

    if space_data:
        name: str = ctx_data.get()['user'].user_name
        translator = Translator()
        data_for_translation: List[str] = [space_data.get("title"), space_data.get("explanation")]
        result = await translator.translate(text=data_for_translation, dest='ru')
        try:
            await message.bot.send_photo(chat_id=message.chat.id,
                                         photo=space_data.get('hdurl'),
                                         caption=f'Фотография на {space_data.get("date")}\n'
                                                 f'Название: {result[0].text}\n')
            await message.answer(f'Описание: {result[1].text}')
            await Conditions.new_date_new_planet.set()
            await message.answer('Хотите продолжить исследовать космос?\n'
                                 'Можете выбрать другую дату или все же полетим на другую планету?',
                                 reply_markup=inline.new_date_new_planet())
            logger.info(f"{name} have received a good photo of space")
            data: Dict = ctx_data.get()
            data['photo_url']: str = space_data.get('hdurl')
            ctx_data.set(data)
        except TelegramAPIError:
            await Conditions.new_date_new_planet.set()
            logger.warning(f'{name} have received a bad  photo of space \n {traceback.format_exc()}')
            await message.answer('Получена не качественная фотография, можете выбрать другую дату или планету',
                                 reply_markup=inline.new_date_new_planet())
    await gif.delete()