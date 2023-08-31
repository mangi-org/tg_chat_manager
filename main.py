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
    name = State()
    picture = State()
    video = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await Form.name.set()
    await message.answer("Пришлите текст:")


@dp.message_handler(state=Form.name, content_types=types.ContentTypes.TEXT)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await Form.next()
    await message.answer("Пришлите картинку:")


@dp.message_handler(state=Form.picture, content_types=types.ContentTypes.PHOTO)
async def process_picture(message: types.Message, state: FSMContext):
    current_data = await state.get_data()
    pictures = current_data.get("pictures", [])
    pictures.append(message.photo[-1].file_id)
    await state.update_data(pictures=pictures)
    await message.answer("Если есть ещё картинки, пришлите. Иначе напишите /next.")


@dp.message_handler(state=Form.picture, commands='next')
async def next_picture(message: types.Message, state: FSMContext):
    await Form.next()
    await message.answer("Пришлите видео:")


@dp.message_handler(state=Form.video, content_types=types.ContentTypes.VIDEO)
async def process_video(message: types.Message, state: FSMContext):
    current_data = await state.get_data()
    videos = current_data.get("videos", [])
    videos.append(message.video.file_id)
    await state.update_data(videos=videos)
    await message.answer("Если есть ещё видео, пришлите. Иначе напишите /next.")


@dp.message_handler(state=Form.video, commands='next')
async def next_video(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await bot.send_message(TARGET_USER_ID, f"From user {message.from_user.first_name}:")
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
