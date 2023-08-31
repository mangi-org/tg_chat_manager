import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import config

API_TOKEN = config.API_TOKEN
# Замените на ID пользователя, которому будут пересылаться сообщения
TARGET_USER_ID = config.TARGET_USER_ID

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    author = State()  # добавил новое состояние
    name = State()
    picture = State()
    video = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await Form.author.set()
    await message.answer("Напишите автора:")


@dp.message_handler(state=Form.author, content_types=types.ContentTypes.TEXT)
async def process_author(message: types.Message, state: FSMContext):  # добавил state
    await state.update_data(author=message.text)  # сохраняю автора в состояние
    await Form.next()
    await message.answer("Пришлите текст:")


@dp.message_handler(state=Form.name, content_types=types.ContentTypes.TEXT)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await Form.next()
    await message.answer("Пришлите картинку (не файл):")


async def send_next_button(message: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Next", callback_data="next"))
    await message.answer("Если есть ещё, пришлите. Иначе нажмите Next.", reply_markup=markup)


@dp.message_handler(state=Form.picture, content_types=types.ContentTypes.PHOTO)
async def process_picture(message: types.Message, state: FSMContext):
    current_data = await state.get_data()
    pictures = current_data.get("pictures", [])
    pictures.append(message.photo[-1].file_id)
    await state.update_data(pictures=pictures)

    await asyncio.sleep(0.5)

    updated_data = await state.get_data()
    updated_pictures = updated_data.get("pictures", [])
    if pictures == updated_pictures:
        await send_next_button(message)


@dp.callback_query_handler(lambda c: c.data == 'next', state=Form.picture)
async def process_callback_next_picture(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await Form.next()
    await bot.send_message(callback_query.from_user.id, "Пришлите видео (не файл):")


@dp.message_handler(state=Form.video, content_types=types.ContentTypes.VIDEO)
async def process_video(message: types.Message, state: FSMContext):
    current_data = await state.get_data()
    videos = current_data.get("videos", [])
    videos.append(message.video.file_id)
    await state.update_data(videos=videos)

    await asyncio.sleep(0.5)

    updated_data = await state.get_data()
    updated_videos = updated_data.get("videos", [])
    if videos == updated_videos:
        await send_next_button(message)


@dp.callback_query_handler(lambda c: c.data == 'next', state=Form.video)
async def process_callback_next_video(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    data = await state.get_data()

    await bot.send_message(TARGET_USER_ID, f"From user {callback_query.from_user.first_name}:")
    await bot.send_message(TARGET_USER_ID, f"Author: {data.get('author')}")
    await bot.send_message(TARGET_USER_ID, f"Text: {data.get('name')}")

    pictures = data.get("pictures", [])
    if pictures:
        media = [types.InputMediaPhoto(p) for p in pictures]
        await bot.send_media_group(TARGET_USER_ID, media)

    videos = data.get("videos", [])
    for video in videos:
        await bot.send_video(TARGET_USER_ID, video)

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
