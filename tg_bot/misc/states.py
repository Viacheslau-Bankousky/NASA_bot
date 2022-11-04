from aiogram.dispatcher.filters.state import State, StatesGroup


class Conditions(StatesGroup):
    """A class of current states of the bot

    :param: yes_no_keyboard: the state in which only the keyboard
    with the question 'is the user ready to fly into the space' is available
    :type: yes_no_keyboard: State
    :param: rocket_button: the state in which only the keyboard with the
    rocket take-off button is available
    :type: rocket_button: State
    :param: menu_button: The state in which the menu button appears for
    the first time (it is necessary only at a certain stage of the program execution,
    to re-display the menu button, in case the user enters incorrect information)
    :type: menu_button: State
    :param: chose_place_keyboard: the state in which only a keyboard with a list
    of bot features is available
    :type: chose_place_keyboard: State
    :param: mars_chose_color: The state in which only a keyboard with the question about
    viewing photos of Mars in color/ uncolored mode is available
    :type: mars_chose_color: Stat
    :param: mars_chosen: It is set when the planet Mars is selected for viewing photos
    :type: mars_chosen:  State
    :param: working_with_mars: the state in which only the keyboard is displayed
    with a suggestion to continue viewing photos of Mars or its end
    :type: working_with_mars: State
    :param: earth_chosen: It is set when the planet Earth is selected for viewing photos
    :type: earth_chosen: State
    :param: working_with_earth: the state in which only the keyboard is displayed
    with a suggestion to continue viewing photos of the Earth or its end
    :type: working_with_earth: State
    :param: space_chosen: It is set when the space is selected for viewing photos
    :type: space_chosen: State
    :param: new_date_new_planet: It is set when only the keyboard is available with
    a question about continuing to view photos of the selected planet, but with
    a different date or choosing another planet for research
    :type: new_date_new_planet: State

    """
    yes_no_keyboard: State = State()
    rocket_button: State = State()
    menu_button: State = State()
    chose_place_keyboard: State = State()
    mars_chose_color = State()
    mars_chosen = State()
    working_with_mars: State = State()
    earth_chosen: State = State()
    working_with_earth: State = State()
    space_chosen = State()
    new_date_new_planet: State = State()


