import os
import logging
import time

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

from bot.bulbs_commands import *

load_dotenv()
TOKEN = os.getenv('TOKEN_TG_BOT')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
scheduler = AsyncIOScheduler()

ENTRYTEXT = """
Привет, {}, я бот, который умеет управлять светом в твоём умном доме.
Для того, чтобы ты мог мною пользоваться, тебе необходимо узнать какие команды у меня есть.
Введи /help, чтобы сделать это.
"""

HELPTEXT = """
Доступные команды:
/start - Запуск бота
/help - Вызов справки по всем командам
/all_on - Включить все лампочки
/all_off - Выключить все лампочки
/show_all - Показать все лампочки
/bright % - настройка яркости. Прим. /bright 100 - установить яркость 100%, если вызвать команду без аргумментов, то покажет клавиатуру с выбором
/dif_on num- включить выбранную лампочку. Прим. /dif_on №num включить лампочку №num
/dif_off num- выключить  выбранную лампочку. Прим. /dif_off №num вsключить лампочку №num
/cute_blink - включить мигание на 15 секунд, полезно, чтобы показать знакомым насколько ваши лампочки "умные"
/very_smart - включить режим, когда бот спрашивает в комнате ли вы раз в 10 минут, чтобы выключить лампы, если нет. (в разработке)
"""


class Smart(StatesGroup):
    wait_for_user = State()
    exit_from_smart = State()


class Brightness(StatesGroup):
    wait_for_brightness = State()


keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("/help"))

keyboard_brightness = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_brightness.add(KeyboardButton("0 %"), KeyboardButton("25 %"), KeyboardButton("50 %"), KeyboardButton("75 %"), KeyboardButton("100 %"))


storage = MemoryStorage()


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    """
    Стартовый хендлер для всех пользователей
    :param message:
    :return:
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'%{time.asctime()} %{user_id=}'
                 f' {user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    await bot.send_message(user_id,
                           ENTRYTEXT.format(message.from_user.username), reply_markup=keyboard)  # прислать сообщение


@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    """
    Функция, обрабатывающая запрос на вывод справки по боту
    :param message:
    :return:
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} '
                 f'{user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    await bot.send_message(user_id,
                           HELPTEXT.format(message.from_user.username))  # прислать сообщение


@dp.message_handler(commands="all_on")
async def all_on_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} '
                 f'{user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    my_bulbs = connection()
    try:
        all_on(my_bulbs)
    except Exception as e:
        print(e)
        await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.")
        return
    await message.answer('Все лампочки включены')


@dp.message_handler(commands="all_off")
async def all_off_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} '
                 f'{user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    my_bulbs = connection()
    try:
        all_off(my_bulbs)
    except Exception as e:
        print(e)
        await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.")
        return
    await message.answer('Все лампочки выключены')


@dp.message_handler(commands="show_all")
async def show_all_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} '
                 f'{user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    my_bulbs = connection()
    try:
        bulbs = show_all(my_bulbs)
    except Exception as e:
        print(e)
        await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.")
        return
    show_message = "Все Ваши лампочки: \n"
    for bulb in bulbs:
        show_message += bulb + '\n'
    await message.answer(show_message)


@dp.message_handler(commands="bright")
async def bright_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} '
                 f'{user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    my_bulbs = connection()
    args = message.text.split(sep=" ")
    if len(args) < 2:
        if str(my_bulbs) == "Can't connect":
            await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.", reply_markup=keyboard)
            return 1
        await message.answer("Выберите яркость", reply_markup=keyboard_brightness)
        await Brightness.wait_for_brightness.set()
        return
    if not (100 >= int(args[1]) >= 0):
        args[1] = "100"
    try:
        set_brightness(my_bulbs, args[1])
    except Exception as e:
        print(e)
        await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.", reply_markup=keyboard)
        return
    await message.answer("Яркость установлена на " + args[1] + "%", reply_markup=keyboard)


@dp.message_handler(state=Brightness.wait_for_brightness)
async def bright_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} '
                 f'{user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    my_bulbs = connection()
    args = message.text.split(sep=" ")
    try:
        value = int(args[0])
    except Exception as e:
        print(e)
        await message.answer("Вы ввели не число, введите команду сначала.", reply_markup=keyboard)
        await state.finish()
        return
    if not (100 >= value >= 0):
        value = "100"
    try:
        set_brightness(my_bulbs, value)
    except Exception as e:
        print(e)
        await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.", reply_markup=keyboard)
        return
    await message.answer("Яркость установлена на " + str(value) + "%", reply_markup=keyboard)
    await state.finish()


@dp.message_handler(commands="dif_on")
async def dif_on_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} '
                 f'{user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    my_bulbs = connection()
    args = message.text.split(sep=" ")
    if len(args) < 2:
        if str(my_bulbs) == "Can't connect":
            await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.")
            return 1
        await message.answer("Вы не выбрали лампочку, попробуйте снова")
        return 1
    try:
        dif_on(my_bulbs, args[1])
    except Exception as e:
        print(e)
        await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.")
        return
    await message.answer('Лампочка №' + args[1] + ' включена')


@dp.message_handler(commands="dif_off")
async def dif_off_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} '
                 f'{user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    my_bulbs = connection()
    args = message.text.split(sep=" ")
    if len(args) < 2:
        if str(my_bulbs) == "Can't connect":
            await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.")
            return 1
        await message.answer("Вы не выбрали лампочку, попробуйте снова")
        return 1
    try:
        dif_off(my_bulbs, args[1])
    except Exception as e:
        print(e)
        await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.")
        return
    await message.answer('Лампочка №' + args[1] + ' выключена')


@dp.message_handler(commands="cute_blink")
async def cute_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} '
                 f'{user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    my_bulbs = connection()
    try:
        set_mode(my_bulbs)
    except Exception as e:
        print(e)
        await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.")
        return
    await message.answer('Мигание завершено')


async def smart_func(state: FSMContext):
    data = await state.get_data()
    message = data.get('mes')
    await message.answer(message.from_user.id, "Вы всё ещё в комнате?")
    await Smart.wait_for_user.set()


@dp.message_handler(commands="very_smart")
async def very_smart_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} '
                 f'{user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    my_bulbs = connection()
    try:
        if is_all_off(my_bulbs):
            await message.answer("Все ваши лампочки уже выключены")
            return 1
    except Exception as e:
        print(e)
        await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.")
        return
    scheduler.add_job(Smart.wait_for_user.set, "interval", minutes=10)
    scheduler.start()


@dp.message_handler(state=Smart.wait_for_user)
async def is_room(message: types.Message):
    await message.answer("Вы всё ещё в комнате?")
    answer = message.text.lower()
    await message.answer(answer)
    if answer == 'нет' or answer == 'выход':
        my_bulbs = connection()
        try:
            all_off(my_bulbs)
        except Exception as e:
            print(e)
            await message.answer("Не удалось подключить лампочки, проверьте их подключение к сети Wi-Fi.")
            return
        await message.answer("Выход из режима")
        await Smart.exit_from_smart.set()
        scheduler.shutdown()
        return 1
    else:
        await Smart.wait_for_user.set()


if __name__ == '__main__':
    executor.start_polling(dp)
