import traceback
from typing import Optional

from aiogram import Dispatcher
from aiogram.types import Update
from aiogram.utils.exceptions import TelegramAPIError, MessageToDeleteNotFound, BadRequest

from tg_bot.services.logger.my_logger import get_logger

logger = get_logger(name=__name__)


async def errors_handler(update: Update, exception: Exception) -> Optional[bool]:
    """Handler of the most frequent errors with full traceback of them

    :param: update: current update
    :type: call: Update
    :param: exception: current exception
    :type: exception: Exception
    :return: True, if the function is successfully executed or None if something
    went wrong

    """
    if isinstance(exception, MessageToDeleteNotFound):
        logger.error(f'Nothing to delete: {exception};'
                     f'\n{traceback.format_exc()};'
                     f'\nupdate: {update}')
        return True
    elif isinstance(exception, TelegramAPIError):
        logger.error(f'TelegramAPIError has occurred: {exception};'
                     f'\n{traceback.format_exc()};'
                     f'\n update: {update}')
        return True
    elif isinstance(exception, BadRequest):
        logger.error(f'\nCantParseEntities: {exception}; '
                     f'{traceback.format_exc()};'
                     f'\n update: {update}')
        return True
    else:
        logger.error(f'Something went wrong: {exception};'
                     f'\n {traceback.format_exc()};'
                     f'\n update: {update}')
        return True



def register_error_handler(dp: Dispatcher) -> None:
    """Registers an error handler

    :param: dp: current dispatcher
    :type: dp: Dispatcher
    :return: None

    """
    dp.register_errors_handler(callback=errors_handler)
