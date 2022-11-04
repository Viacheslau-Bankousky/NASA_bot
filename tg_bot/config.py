import os
from dataclasses import dataclass

from dotenv import find_dotenv, load_dotenv


@dataclass
class TelegramBot:
    """
    Parameters of Telegram bot

    :param: token: bot token
    :type: token: string
    :param: use_redis: will Redis be used as a cache
    :type: use_redis: bool
    """
    token: str
    use_redis: bool


@dataclass
class Database:
    """
    Parameters of Database

    :param: database_name: name of the current database
    :type: database_name: string
    :param: user: user of the current database
    :type: user: string
    :param: password: password of the current  database
    :type: password: string
    :param: host: host of the current database
    :type: host: string
    :param: port: port of the current database
    :type: port: string
    """
    database_name: str
    user: str
    password: str
    host: str
    port: str


@dataclass
class Api:
    """
    Parameters of NASA api

    :param: nasa_api_token: your private API token
    :type: nasa_api_token: string
    """
    nasa_api_token: str


@dataclass
class Config:
    """
    Telegram bot config

    :param: bot: current bot
    :type: bot: instance of TelegramBot class
    :param: database: current database
    :type: database: instance of Database class
    :param: api: NASA api
    :type: api: instance of APi class
    """
    bot: TelegramBot
    database: Database
    api: Api


def get_config(path: str) -> Config:
    """Returns the config with the main parameters. If the environment variables
     are not loaded information about this is displayed

     """
    if not find_dotenv(path):
        exit('Переменные окружения не загружены')
    else:
        load_dotenv(dotenv_path=path)

    return Config(
        bot=TelegramBot(token=os.getenv('BOT_TOKEN'),
                        use_redis=True if os.getenv(
                            'USE_REDIS') == 'True' else False),
        database=Database(database_name=os.getenv('DB_NAME'),
                          user=os.getenv('DB_USER'),
                          password=os.getenv('DB_PASSWORD'),
                          host=os.getenv('DB_HOST'),
                          port=os.getenv('DB_PORT')),
        api=Api(nasa_api_token=os.getenv('NASA_API_TOKEN'))
    )
