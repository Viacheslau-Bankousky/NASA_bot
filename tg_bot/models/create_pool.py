from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from tg_bot.config import Config
from tg_bot.models.db_tables import Base
from tg_bot.services.logger.my_logger import get_logger

logger = get_logger(name=__name__)


async def create_pool(config: Config) -> sessionmaker:
    """Extracts the necessary parameters for connecting to the database from the config,
    adds them to the connection uri and passes it to the created asynchronous engine.
    Creates database tables. Creates a pool of database connections and
    passes the asynchronous engine to it

    :param: config: current user's config
    :type: config: Config
    :return: pool of connections to database
    :rtype: sessionmaker

    """
    user: str = config.database.user
    password: str = config.database.password
    host: str = config.database.host
    port: str = config.database.port
    database: str = config.database.database_name
    connection_uri: str = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
    engine = create_async_engine(
        url=make_url(connection_uri)
    )
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.drop_all)
        await connect.run_sync(Base.metadata.create_all)
    pool = sessionmaker(bind=engine,  class_=AsyncSession,
                        expire_on_commit=False, autoflush=False)
    logger.info(f'pool of connection is created')
    return pool
