import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from sqlalchemy.orm import sessionmaker

from tg_bot.config import get_config
from tg_bot.handlers.errors.errors import register_error_handler
from tg_bot.handlers.users.actions import register_basic_handlers
from tg_bot.handlers.users.callbacks import register_callbacks_handlers
from tg_bot.middlewares.data_middleware import DataMiddleware
from tg_bot.middlewares.db_middleware import DbMiddleware
from tg_bot.middlewares.throttling_middleware import ThrottlingMiddleware
from tg_bot.models.create_pool import create_pool
from tg_bot.services.logger.my_logger import get_logger

logger = get_logger(name=__name__)


def register_all_middlewares(dp: Dispatcher, pool:  sessionmaker) -> None:
    """Registers all available middlewares from modules

    :param: dp: current dispatcher
    :type: dp: Dispatcher
    :param: pool: current pool of database connections
    :type: pool: sessionmaker
    :return: None

    """
    dp.setup_middleware(DbMiddleware(pool=pool))
    dp.setup_middleware(DataMiddleware())
    dp.setup_middleware(LoggingMiddleware(logger=logger))
    dp.setup_middleware(ThrottlingMiddleware())



def register_all_handlers(dp: Dispatcher) -> None:
    """Registers all available handlers from modules

    :param: dp: current dispatcher
    :type: dp: Dispatcher
    :return: None

    """
    register_basic_handlers(dp=dp)
    register_callbacks_handlers(dp=dp)
    register_error_handler(dp=dp)


async def main() -> None:
    """The main function that gets the user's config, initializes the bot, dispatcher,
    storage, pool of database connections objects, calls the general registrar of all
    handlers and middlewares, and performs polling to receive updates from the Telegram
    server. At the end of the work of bot, the current storage is closed, it is expected
    to be completely closed and the current bot session is closed

    :return: None

    """
    logger.info("Starting bot")
    config = get_config(path='.env')
    my_bot = Bot(token=config.bot.token, parse_mode='HTML')
    if config.bot.use_redis:
        storage = RedisStorage2(pool_size=50)
    else:
        storage = MemoryStorage()
    dp = Dispatcher(bot=my_bot, storage=storage)
    pool = await create_pool(config=config)
    my_bot['config'] = config

    register_all_middlewares(dp=dp, pool=pool)
    register_all_handlers(dp=dp)

    # start
    try:
        await dp.start_polling(timeout=0)
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await my_bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.critical("Bot stopped!")