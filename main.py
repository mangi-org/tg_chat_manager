import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import config

API_TOKEN = config.API_TOKEN
TARGET_USER_ID = config.TARGET_USER_ID


storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    author = State()
    name = State()
    picture = State()
    video = State()


@dp.message_handler(commands='help')
async def cmd_help(message: types.Message) -> None:
    """
    Обработчик команды 'help' в Telegram боте.
    
    Агрументы:
        (types.Message): Объект сообщения, представляющий команду.
    """
    commands = [
        '/start - Начать бота',
        '/help - Вывести список доступных команд'
    ]

    response = "Доступные команды:\n" + "\n".join(commands)
    await message.answer(response)

@dp.message_handler(commands='start')
async def cmd_start(message: types.Message) -> None:
    """
    Обработчик команды 'start' в Telegram боте.

    Аргументы:
        (types.Message): Объект сообщения, представляющий команду.
    """
    await Form.author.set()
    await message.answer("Напишите автора:")


@dp.message_handler(state=Form.author, content_types=types.ContentTypes.TEXT)
async def process_author(message: types.Message, state: FSMContext) -> None:
    """
    A message handler that processes the author state and updates the data accordingly.

    Args:
        message (types.Message): The message object received.
        state (FSMContext): The FSM context object.

    Returns:
        None
    """
    await state.update_data(author=message.text)
    await Form.next()
    await message.answer("Пришлите текст:")


@dp.message_handler(state=Form.name, content_types=types.ContentTypes.TEXT)
async def process_name(message: types.Message, state: FSMContext) -> None:
    """
    Handles the message received during the "Form.name" state, when the content type is text.

    Args:
        message (types.Message): The message received.
        state (FSMContext): The current state of the conversation.

    Returns:
        None

    Raises:
        None
    """
    await state.update_data(name=message.text)
    await Form.next()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Далее", callback_data="next"))
    await message.answer("Пришлите картинку:", reply_markup=markup)


@dp.message_handler(state=Form.picture, content_types=types.ContentTypes.PHOTO)
async def process_picture(message: types.Message, state: FSMContext) -> None:
    """
    Process a picture message and update the state with the new picture.

    Args:
        message (types.Message): The message containing the picture.
        state (FSMContext): The current state of the conversation.

    Returns:
        None
    """
    current_data = await state.get_data()
    pictures = current_data.get("pictures", [])
    pictures.append(message.photo[-1].file_id)
    await state.update_data(pictures=pictures)

    await asyncio.sleep(0.5)

    updated_data = await state.get_data()
    updated_pictures = updated_data.get("pictures", [])
    if pictures == updated_pictures:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Далее", callback_data="next"))
        await message.answer("Если есть ещё картинки, пришлите.", reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data == 'next', state=Form.picture)
async def process_callback_next_picture(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Process the callback for the 'next' button in the picture form.

    Args:
        callback_query (types.CallbackQuery): The callback query object.
        state (FSMContext): The FSM context object.

    Returns:
        None
    """
    await bot.answer_callback_query(callback_query.id)
    await Form.next()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Отправить", callback_data="next"))
    await bot.send_message(callback_query.from_user.id, "Пришлите видео:", reply_markup=markup)


@dp.message_handler(state=Form.video, content_types=types.ContentTypes.VIDEO)
async def process_video(message: types.Message, state: FSMContext) -> None:
    """
    Process video message and update the state data with the video file ID.

    Args:
        message (types.Message): The video message received.
        state (FSMContext): The current state of the conversation.

    Returns:
        None
    """
    current_data = await state.get_data()
    videos = current_data.get("videos", [])
    videos.append(message.video.file_id)
    await state.update_data(videos=videos)

    await asyncio.sleep(0.5)

    updated_data = await state.get_data()
    updated_videos = updated_data.get("videos", [])
    if videos == updated_videos:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Отправить", callback_data="next"))
        await message.answer("Если есть ещё видео, пришлите.", reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data == 'next', state=Form.video)
async def process_callback_next_video(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Process callback for the next video.

    Args:
        callback_query (types.CallbackQuery): The callback query.
        state (FSMContext): The state of the conversation.

    Returns:
        None: This function does not return anything.
    """
    await bot.answer_callback_query(callback_query.id)
    data = await state.get_data()

    await bot.send_message(TARGET_USER_ID, f"From {callback_query.from_user.first_name}:")
    await bot.send_message(TARGET_USER_ID, f"Author: {data.get('author')}")
    await bot.send_message(TARGET_USER_ID, f"Text: {data.get('name')}")

    pictures = data.get("pictures", [])
    if pictures:
        media = [types.InputMediaPhoto(p) for p in pictures]
        await bot.send_media_group(TARGET_USER_ID, media)

    videos = data.get("videos", [])
    for video in videos:
        await bot.send_video(TARGET_USER_ID, video)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)\
        .add(KeyboardButton('/start'))

    await bot.send_message(callback_query.from_user.id,
                           "Чтобы запустить снова, нажмите /start",
                           reply_markup=markup)

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
