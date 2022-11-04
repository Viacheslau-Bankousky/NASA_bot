from io import BytesIO
from random import randint, choice
# from typing import List, Optional, Any, Generator

from PIL import Image
from aiogram.types import Message
from aiohttp import ClientSession

from tg_bot.config import get_config
from tg_bot.loader import my_bot
from tg_bot.keyboards.inline.inline_keyboards import show_more_mars_photo
from tg_bot.misc.states import Conditions


async def get_all_mars_photos(message: Message) -> str:
    while True:
        ROVER_URL = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'
        params = dict(sol=randint(0, 1722),
                      api_key=get_config().api.nasa_api_token)
        async with ClientSession() as session:
            async with session.get(url=ROVER_URL, params=params) as response:
                response_dictionary = await response.json()
                if 'photos' not in response_dictionary:
                    await message.answer('Вы исчерпали лимит попыток,'
                                         ' попробуйте воспользоваться мной немного позже')
                    break
                elif not response_dictionary['photos']:
                    await message.answer('Подождите еще чуть-чуть)')
                    continue
                else:
                    return choice(response_dictionary['photos'])['img_src']



async def get_mars_photo_bytes(message: Message) -> bytes:
    while True:
        current_url = await get_all_mars_photos(message=message)
        if not current_url:
            break
        async with ClientSession() as session:
            async with session.get(url=current_url) as response:
                bytes_image = await response.read()
        if await validate_image(image_bytes=bytes_image):
            break
    return bytes_image


async def validate_image(image_bytes) -> bool:
    image = Image.open(BytesIO(initial_bytes=image_bytes))
    return image.width >= 1024 and image.height >= 1024 and image.mode != 'L'


async def show_mars_photo(message: Message) -> None:
    await Conditions.working_with_mars.set()
    gif = await my_bot.send_animation(chat_id=message.chat.id,
                                animation='https://vgif.ru/gifs/166/vgif-ru-37964.gif')
    image = await get_mars_photo_bytes(message=message)
    if image:
        await my_bot.send_photo(chat_id=message.chat.id, photo=image,
                                caption='Вот, что я нашел')
        await message.answer('\nНу что, останемся еще немного на этой планете '
                             'или выберем что-то другое?)', reply_markup=show_more_mars_photo())
    await gif.delete()





# async def get_all_mars_photos(message: Message) -> List[str]:
#     while True:
#         ROVER_URL = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'
#         params = dict(sol=randint(0, 1722),
#                       api_key=get_config().api.nasa_api_token)
#         async with ClientSession() as session:
#             async with session.get(url=ROVER_URL, params=params) as response:
#                 response_dictionary = await response.json()
#                 if 'photos' not in response_dictionary:
#                     await message.answer('Вы исчерпали лимит попыток,'
#                                          ' попробуйте воспользоваться мной немного позже')
#                     break
#                 elif not response_dictionary['photos']:
#                     await message.answer('Подождите еще чуть-чуть)')
#                     continue
#                 else:
#                     return [i_element['img_src'] for i_element in response_dictionary['photos']]
#
#
#
# async def get_good_mars_photo(message: Message) -> List[str]:
#     all_urls = await get_all_mars_photos(message=message)
#     return [i_url for i_url in all_urls if await get_mars_photo_bytes(url=i_url)]
#
#
# async def get_mars_photo_bytes(url: str) -> Optional[bool]:
#     async with ClientSession() as session:
#         async with session.get(url=url) as response:
#             bytes_image = await response.read()
#             if await validate_image(image_bytes=bytes_image):
#                 return True
#
#
#
# async def validate_image(image_bytes) -> bool:
#     image = Image.open(BytesIO(initial_bytes=image_bytes))
#     return image.width >= 1024 and image.height >= 1024 and image.mode != 'L'
#
#
# async def show_mars_photo(message: Message) -> None:
#     gif = await my_bot.send_animation(chat_id=message.chat.id,
#                                 animation='https://vgif.ru/gifs/166/vgif-ru-37964.gif')
#     image = await get_good_mars_photo(message=message)
#     if image:
#         await my_bot.send_photo(chat_id=message.chat.id, photo=choice(image), caption='Вот, что я нашел')
#     await gif.delete()
#
#
#


