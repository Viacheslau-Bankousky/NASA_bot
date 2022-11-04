# NASA_shizoid_bot

![my_bot](https://fotogaleri.star.com.tr/fotogaleri/act/2020/01/16/1601202015791813192c6a0012.jpg)

***
### This bot shows photos of various objects in space on the specified date using the public API of NASA
***

#### There are 2 commands available:
* `/start` - starts/ restarts the bot
* `/help` - displays a list of places in space whose photos are available for viewing (Mars, Earth, various constellations and so on)

###### note:
    The "MENU" button, which performs the same functions as the /start command, is available at all stages 
    of the program execution
***

### Getting started
#### To launch the bot, you need:
* Clone the current repo, using `git clone`
* `cd` into the `NASA_bot` directory 
* Create a new virtual environment `venv` in this directory using follow command: `python -m virtualenv venv`
* Activate the new environment (`source venv/bin/activate`)
* Install dependencies in the new environment (`pip install -r requirements.txt`);
* Create a file `.env` in the project directory where you have to save the NASA_API_TOKEN, BOT_TOKEN,
the need to use Redis and parameters of database 
* Install the Redis server (if necessary) and the Postgresql database (locally or on the server)
and specify the connection parameters in `.env` (see example file in `.env.template`)
