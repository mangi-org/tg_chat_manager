from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import config

API_TOKEN = config.API_TOKEN
TARGET_USER_ID = config.TARGET_USER_ID

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(f"Привет, {message.from_user.first_name}!\nТвой ID: {message.from_user.id}")


@dp.message_handler()
async def forward_message(message: types.Message):
    await bot.send_message(TARGET_USER_ID, f"From user {message.from_user.id}:")
    await message.forward(TARGET_USER_ID)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
