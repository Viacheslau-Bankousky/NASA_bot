from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types.base import TelegramObject
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from tg_bot.services.logger.my_logger import get_logger

logger = get_logger(name=__name__)


class DbMiddleware(LifetimeControllerMiddleware):
    """
    Middleware to get the session (from the database connection pool) at all stages
    of the bot's operation
    """
    skip_patterns = ['error', 'update']

    def __init__(self, pool: sessionmaker) -> None:
        """constructor of the middleware class

        :param: pool: current pool of database connections
        :type: time_limit: sessionmaker
        :return: None

        """
        super(DbMiddleware, self).__init__()
        self.pool = pool


    async def pre_process(self, obj: TelegramObject, data: dict, *args) -> None:
        """when a message was received, gets a current session from the pool of database
        connections (from a class attribute),  and assigns it as a dictionary value for
        contextual data (for later access to it in the necessary places)

         :param: obj: received object
         :type: obj: TelegramObject
         :param: data: contextual data
         :type: data: dictionary
         :param: *args: other things
         :type: *args: Any
         :return: None

         """
        session = self.pool()
        data['session']: Session = session

    async def post_process(self, obj: TelegramObject, data: dict, *args) -> None:
        """retrieves the current session (from the context data dictionary) and closes it

         :param: obj: received object
         :type: obj: TelegramObject
         :param: data: contextual data
         :type: data: dictionary
         :param: *args: other things
         :type: *args: Any
         :return: None

         """
        if session := data.get('session', None):
            await session.close()