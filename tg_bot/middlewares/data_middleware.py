from sqlite3 import Row
from typing import Dict, List, Union

from aiogram import types
from aiogram.dispatcher.handler import ctx_data
from aiogram.dispatcher.middlewares import BaseMiddleware
from sqlalchemy import select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.models.db_tables import User, UserFavoritePhotos
from tg_bot.services.logger.my_logger import get_logger

logger = get_logger(name=__name__)


class DataMiddleware(BaseMiddleware):
    """
    Middleware for adding information to the database and extracting it from it
    """
    @staticmethod
    async def setup_user(data: dict, user: types.User = None) -> None:
        """Retrieves the user's name and ID from the received update; extracts the current
        session from the contextual data dictionary; extracts (by the user id key) from the
        database of the required user (or adds to the database if the user uses the bot for
        the first time); adds the current user to the dictionary of contextual data for
        subsequent use in a various places of the program

        :param: data: contextual data
        :type: data: dictionary
        :param: user: current user
        :type: user: as a standard value it assigned as None (in the future it will be
        set as message.from_user)
        :return: None

        """
        user_id = int(user.id)
        user_name: str = user.full_name
        session: AsyncSession = data['session']
        async with session.begin():
            if not (user := await session.get(User, user_id)):
                session.add(user := User(user_id=user_id, user_name=user_name))
            await session.flush()

        data['user'] = user

    @staticmethod
    async def add_url_to_database() -> None:
        """Retrieves the url of the viewed photo from the contextual data dictionary;
        if the url is received, extracts the current user and session from the above
        dictionary; extracts a photo with the current url from the database and if there
        is no such, then adds it to the database (if the photo is found, then the duplicate
        is not added)

        :return: None

        """
        data: Dict[str: str] = ctx_data.get()
        url: str = data.get('photo_url')
        if url:
            user: User = data['user']
            session: AsyncSession = data['session']
            async with session.begin():
                url_exist: ChunkedIteratorResult = await session.execute(select(UserFavoritePhotos).where(
                    UserFavoritePhotos.photo_url == url))
                if not url_exist.all():
                    session.add(UserFavoritePhotos(
                        relation_user_id=user.user_id,
                        photo_url=url)
                    )
                await session.flush()

    @staticmethod
    async def get_photo_from_database() -> None:
        """Retrieves a value from the contextual data dictionary indicating the need
        to view previously displayed photos; if the above value is True, extracts
        the current user and session from the contextual data dictionary, extracts
        all photos from the database viewed by this user earlier and adds them to
        the contextual data dictionary as a value. The photos will be viewed through
        another method of the class

        :return: None

        """
        data: Dict[str: str] = ctx_data.get()
        viewing_photo: bool = data.get('show_photo')
        if viewing_photo:
            user: User = data['user']
            session: AsyncSession = data['session']
            async with session.begin():
                result: ChunkedIteratorResult = await session.execute(
                    select(UserFavoritePhotos).where(
                        UserFavoritePhotos.relation_user_id == user.user_id)
                )
                data['all_photos'] = result
                await session.flush()

    @staticmethod
    async def create_media_group(loaded_photos: List[Row], update: types.Update) -> None:
        """displays the viewed photos as a media group

        :param: loaded_photos: 9 first photos (not processed) extracted from the database
        :type: loaded_photos: list with database rows
        :param: update: current update
        :type: update: Update
        :return: None

        """
        photos_urls: List[Union[str]] = list(map(lambda x: x[0].photo_url, loaded_photos))
        processed_photos: List[Union[types.InputMediaPhoto]] = [
            types.InputMediaPhoto(url) for url in photos_urls
        ]
        await update.callback_query.message.answer('Вот, где мы успели побывать)')
        await update.callback_query.bot.send_media_group(
            chat_id=update.callback_query.message.chat.id,
            media=processed_photos)


    @staticmethod
    async def show_photos(update: types.Update) -> None:
        """Extracts all the photos viewed by the user (ChunkedIteratorResult) from the
        dictionary of contextual data; until the above iterator is exhausted, it takes
        9 photos from it and displays them as a media group using the special method

        :param: update: current update
        :type: update: Update
        :return: None

        """
        data: Dict[str: str] = ctx_data.get()
        photos: ChunkedIteratorResult = data.get('all_photos')
        if photos and update.callback_query:
            while True:
                loaded_photos: List[Row] = photos.fetchmany(9)
                if not loaded_photos:
                    await update.callback_query.message.answer('Упс, кажется фотографии закончились)')
                    break
                await DataMiddleware.create_media_group(loaded_photos=loaded_photos,
                                                        update=update)



    async def on_pre_process_message(self, message: types.Message,
                                     data: dict) -> None:
        """when a message is received, retrieves the user from the database using
        a special method

        :param: message: current message
        :type: message: Message
        :param: data: contextual data:
        :type: data: dictionary
        :return: None

        """
        await self.setup_user(data=data, user=message.from_user)

    async def on_pre_process_callback_query(self, query: types.CallbackQuery,
                                            data: dict) -> None:
        """when a callback query is received, retrieves the user from the database using
        a special method

        :param: message: current qb query
        :type: message: CallbackQuery
        :param: data: contextual data:
        :type: data: dictionary
        :return: None

        """
        await self.setup_user(data, query.from_user)

    async def on_post_process_callback_query(self, *args) -> None:
        """when the callback query is processed, it adds the url of the viewed photo
        to the database using a special method (if the photo has already been displayed
        and the url has already been added to the contextual data dictionary)

        :param: *args: other parameters that need for normal work of this method
        :type: Any
        :return: None

        """
        await self.add_url_to_database()

    async def on_post_process_update(self, update: types.Update, *args) -> None:
        """when the callback query is processed, using the special methods, retrieves viewed
        photos from the database and displays them (if the history view button is pressed)

        :param: update: current update
        :type: update: Update
        :param: *args: other parameters that need for normal work of this method
        :type: Any
        :return: None

        """
        await self.get_photo_from_database()
        await self.show_photos(update=update)
