import calendar
from datetime import datetime
from typing import Optional, Tuple

from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

# setting callback_data prefix and parts
calendar_callback = CallbackData('dialog_calendar', 'act', 'year', 'month', 'day')
ignore_callback = calendar_callback.new('IGNORE', -1, -1, -1)  # for buttons with no answer


class DialogCalendar:
    """Custom Calendar class

    :param: month: all month of year
    :type: month: list with strings
    :param: year: current year
    :type: year: integer
    :param: month: current month
    :type: month: integer"""

    months = ['Январь', 'Февраль', 'Март',
              'Апрель', 'Май', 'Июнь',
              'Июль', 'Август', 'Сентябрь',
              'Октябрь', 'Ноябрь', 'Декабрь']

    def __init__(self, year: int = datetime.now().year,
                 month: int = datetime.now().month):
        self.year = year
        self.month = month


    @staticmethod
    async def start_calendar(year: int = datetime.now().year) -> InlineKeyboardMarkup:
        """Creates a part of the calendar that displays variants of possible years

        :param: year: current year
        :type: year: integer
        :return: keyboard with the variants of possible years
        :rtype: InlineKeyboardMarkup"""

        inline_keyboard = InlineKeyboardMarkup(row_width=5)
        # first row - years
        inline_keyboard.row()
        for value in range(year - 2, year + 1):
            inline_keyboard.insert(InlineKeyboardButton(
                str(value),
                callback_data=calendar_callback.new(act='SET-YEAR', year=value,
                                                    month=-1, day=-1)
            ))
        # nav buttons
        inline_keyboard.row()
        inline_keyboard.insert(InlineKeyboardButton(
            "⬅️",
            callback_data=calendar_callback.new(act='PREV-YEARS', year=year,
                                                month=-1, day=-1)
        ))
        inline_keyboard.insert(InlineKeyboardButton(
            "➡️",
            callback_data=calendar_callback.new(act='NEXT-YEARS', year=year,
                                                month=-1, day=-1)
        ))

        return inline_keyboard

    async def _get_month_keyboard(self, year: int) -> InlineKeyboardMarkup:
        """Creates a part of the calendar that displays possible months

        :param: year: current year
        :type: year: integer
        :return: keyboard with the variants of possible months
        :rtype: InlineKeyboardMarkup"""

        inline_keyboard = InlineKeyboardMarkup(row_width=6)
        # first row with year button
        inline_keyboard.row()
        inline_keyboard.insert(InlineKeyboardButton(' ', callback_data=ignore_callback))
        inline_keyboard.insert(InlineKeyboardButton(
            str(year),
            callback_data=calendar_callback.new('START', year, -1, -1)
        ))
        inline_keyboard.insert(InlineKeyboardButton(' ', callback_data=ignore_callback))
        # two rows with 6 months buttons
        inline_keyboard.row()
        for month in self.months[0:6]:
            inline_keyboard.insert(InlineKeyboardButton(
                month,
                callback_data=calendar_callback.new(act='SET-MONTH', year=year,
                                                    month=self.months.index(month) + 1, day=-1)
            ))
        inline_keyboard.row()
        for month in self.months[6:12]:
            inline_keyboard.insert(InlineKeyboardButton(
                month,
                callback_data=calendar_callback.new(act='SET-MONTH', year=year,
                                                    month=self.months.index(month) + 1, day=-1)
            ))
        return inline_keyboard

    async def _get_days_keyboard(self, year: int, month: int) -> InlineKeyboardMarkup:
        """Creates a part of the calendar that displays possible days

        :param: year: current year
        :type: year: integer
        :param: month: current month
        :type: month: integer
        :return: keyboard with the variants of possible days
        :rtype: InlineKeyboardMarkup"""

        inline_keyboard = InlineKeyboardMarkup(row_width=7)
        inline_keyboard.row()
        inline_keyboard.insert(InlineKeyboardButton(
            str(year),
            callback_data=calendar_callback.new(act='START', year=year,
                                                month=-1, day=-1)
        ))
        inline_keyboard.insert(InlineKeyboardButton(
            self.months[month - 1],
            callback_data=calendar_callback.new(act='SET-YEAR', year=year,
                                                month=-1, day=-1)
        ))
        inline_keyboard.row()
        for day in ['Пн', 'Вт', 'Ср',
                    'Чт', 'Пт', 'Сб',
                    'Вс']:
            inline_keyboard.insert(InlineKeyboardButton(day, callback_data=ignore_callback))

        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            inline_keyboard.row()
            for day in week:
                if day == 0:
                    inline_keyboard.insert(InlineKeyboardButton(' ', callback_data=ignore_callback))
                    continue
                inline_keyboard.insert(InlineKeyboardButton(
                    str(day), callback_data=calendar_callback.new(act='SET-DAY', year=year,
                                                                  month=month, day=day)
                ))
        return inline_keyboard

    async def process_selection(self, query: CallbackQuery,
                                data: CallbackData) -> Tuple[bool, Optional[datetime.date]]:
        """Handles callbacks of pressed calendar buttons
        :param: query: current callback
        :type: query: aiogram.types.CallbackQuery
        :param: data: it collects the current data of pushed buttons (year, month, day)
        :type: data: aiogram.utils.callback_data.CallbackData
        :return: the date, entered of user (if year, month and day was chosen) or tuple(False, None),
        if not all data was chosen
        :rtype: Tuple[bool, Optional[datetime.date]]"""

        return_data = (False, None)
        if data['act'] == "IGNORE":
            await query.answer(cache_time=60)
        if data['act'] == "SET-YEAR":
            await query.message.edit_reply_markup(await self._get_month_keyboard(int(data['year'])))
        if data['act'] == "PREV-YEARS":
            new_year = int(data['year']) - 5
            await query.message.edit_reply_markup(await self.start_calendar(new_year))
        if data['act'] == "NEXT-YEARS":
            new_year = int(data['year']) + 5
            await query.message.edit_reply_markup(await self.start_calendar(new_year))
        if data['act'] == "START":
            await query.message.edit_reply_markup(await self.start_calendar(int(data['year'])))
        if data['act'] == "SET-MONTH":
            await query.message.edit_reply_markup(await self._get_days_keyboard(int(data['year']),
                                                                                int(data['month'])))
        if data['act'] == "SET-DAY":
            await query.message.delete_reply_markup()   # removing inline keyboard
            return_data = True, datetime(int(data['year']), int(data['month']), int(data['day']))
        return return_data