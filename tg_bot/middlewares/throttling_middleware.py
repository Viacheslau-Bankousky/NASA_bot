import asyncio

from aiogram import Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from aiogram.utils.exceptions import Throttled

from tg_bot.services.logger.my_logger import get_logger
from aiogram.dispatcher.handler import ctx_data

logger = get_logger(name=__name__)



class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for throttling clicks on the inline keyboard (menu button)
    """
    def __init__(self, time_limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_') -> None:
        """constructor of the middleware class

        :param: time_limit: current time limit of current handler (set by default)
        :type: time_limit: integer
        :param: key_prefix: prefix of name of current hanller
        :type: key_prefix: string
        :return: None

        """
        self.rate_limit = time_limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: Message, data: dict) -> None:
        """This handler is called when dispatcher receives a message

        :param: message: current message
        :type: message: Message
        :param: data: data of current message
        :type: data: Dictionary
        :return: None

        """
        # gets current handler
        handler = current_handler.get()
        # gets current dispatcher from context
        dispatcher = Dispatcher.get_current()
        # If handler was configured, get rate limit and key from handler
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        # Use Dispatcher.throttle method.
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:  # if current handler was throttled
            name: str = ctx_data.get()['user'].user_name
            logger.info(f'{name} have pushed the menu button many times')
            # Execute action
            await self.message_throttled(message=message, throttled=t, dp=dispatcher, key=key)
            # Cancel current handler
            raise CancelHandler()

    @staticmethod
    async def message_throttled(message: Message, throttled: Throttled,
                                dp: Dispatcher, key: str) -> None:
        """Notify user only on first exceed and notify about unlocking only on last exceed

        :param: message: current message
        :type: message: Message
        :param: throttled: an exception that occurred when the keyboard pressing limit was exceeded
        :type: throttled: Throttled (inherits from TelegramAPIError)
        :param: dp: current dispatcher:
        :type: dp: Dispatcher
        :param: key: specific key for a throttling
        :type: key: string
        :return: None

        """
        # Calculate how much time is left till the block ends
        delta = throttled.rate - throttled.delta
        # Prevent flooding
        if throttled.exceeded_count <= 2:
            await message.reply('Не стоит так часто жать на кнопку,\n'
                                'я вас понял с первого раза)')
        # Sleep.
        await asyncio.sleep(delta)
        # Check lock status
        thr = await dp.check_key(key)
        # If current message is not last with current key - do not send message
        if thr.exceeded_count == throttled.exceeded_count:
            await message.reply('Ладно, можете продолжать)')
