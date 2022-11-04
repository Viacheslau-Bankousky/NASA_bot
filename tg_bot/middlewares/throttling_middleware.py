import asyncio

from aiogram import Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from aiogram.utils.exceptions import Throttled

from tg_bot.misc.states import Conditions
from tg_bot.services.logger.my_logger import get_logger

logger = get_logger(name=__name__)



class ThrottlingMiddleware(BaseMiddleware):
    # TODO написать докстринг

    def __init__(self, time_limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = time_limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: Message, data: dict):
        # TODO написать докстринг
        # Get current handler
        handler = current_handler.get()

        # Get dispatcher from context
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
        except Throttled as t:
            logger.info(f'{Conditions.name} have pushed the menu button many times')
            # Execute action
            await self.message_throttled(message=message, throttled=t, dp=dispatcher, key=key)
            # Cancel current handler
            raise CancelHandler()

    @staticmethod
    async def message_throttled(message: Message, throttled: Throttled,
                                dp: Dispatcher, key: str):
        # TODO написать докстринг

        # Calculate how much time is left till the block ends
        delta = throttled.rate - throttled.delta
        # Prevent flooding
        if throttled.exceeded_count <= 2:
            await message.reply('Не стоит так торопиться,\n'
                                'я вас понял с первого раза)')
        # Sleep.
        await asyncio.sleep(delta)
        # Check lock status
        thr = await dp.check_key(key)
        # If current message is not last with current key - do not send message
        if thr.exceeded_count == throttled.exceeded_count:
            await message.reply('Ладно, можете продолжать)')
