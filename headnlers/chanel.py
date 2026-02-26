import asyncio
import os
from datetime import datetime
import logging
# bot is imported inside functions to prevent circular import with main
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router,F
from dotenv import load_dotenv
from base import  add_post, get_pending_posts, update_status,delete_post ,add_channel



from aiogram.types import ReplyKeyboardMarkup,KeyboardButton





Admin=ReplyKeyboardMarkup(
    keyboard=[

        [KeyboardButton(text="Телеграм "),KeyboardButton(text="Вк")],
        [KeyboardButton(text="Показать все посты"),KeyboardButton(text="Удалить посты")],
        [KeyboardButton(text="Дабавит тг канал и админ ид"),KeyboardButton(text="Дабавит вк группу")],
        [KeyboardButton(text="Показать все каналы"),KeyboardButton(text="Удалить канал")]

        ],
        resize_keyboard=True
)


load_dotenv()
KANAL_ID = int(os.getenv("KANAL_ID"))
ADMIN_ID = int(os.getenv("admin"))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)






Chanel = Router()
class Chanel(StatesGroup):
    chanel_id = State()
    admin_id = State()

class PostState(StatesGroup):
    photo = State()
    message = State()
    time = State()


# start handler
@Chanel.message(CommandStart())
async def start(message: Message):
    name=message.from_user.full_name
    await message.answer(f"Здраствуйте {name}  🚀",reply_markup=Admin)


# add post handlers
@Chanel.message(F.text == "Телеграм")
async def add_post_start(message: Message, state: FSMContext):
    await state.set_state(PostState.photo)
    await message.answer("📸 Отправте изображения /skip")


@Chanel.message(PostState.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(PostState.message)
    await message.answer("✍️ напишите текст поста 1024 символов")


@Chanel.message(PostState.photo, F.text == "/skip")
async def skip_photo(message: Message, state: FSMContext):
    await state.update_data(photo=None)
    await state.set_state(PostState.message)
    await message.answer("✍️ напишите текст поста 1024 символов")


@Chanel.message(PostState.message)
async def get_message(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    await state.set_state(PostState.time)
    await message.answer("🕐 Формат: 2026-02-25 18:30")


@Chanel.message(PostState.time)
async def get_time(message: Message, state: FSMContext):
    try:
        post_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")

        if post_time <= datetime.now():
            return await message.answer("❌ пашедшая время!")

    except ValueError:
        return await message.answer("❌ формат  не то!")

    data = await state.get_data()

    add_post(
        message=data.get("message"),
        post_time=message.text,
        photo=data.get("photo")
    )

    await state.clear()
    await message.answer("✅ Пост добавлен!")

# add channel handler
@Chanel.message(F.text == "Дабавит тг канал и админ ид")
async def add_channel_handler(message: Message):
    await message.answer("Введите ID канала ")
    await Chanel.chanel_id.set() 

@Chanel.message(Chanel.chanel_id)
async def process_channel_info(message: Message, state: FSMContext):
    channel_id = message.text.strip()
    await state.update_data(channel_id=channel_id)
    await message.answer("Введите ID админа канала")
    await Chanel.admin_id.set() 


@Chanel.message(Chanel.admin_id)
async def process_admin_info(message: Message, state: FSMContext):
    admin_id = message.text.strip()
    data = await state.get_data()
    channel_id = data.get("channel_id")
    add_channel(channel_id, admin_id)
    await state.clear()
    await message.answer("✅ Канал и админ добавлены!")




# ================= SCHEDULER =================
async def check_and_send(bot):
    # bot is passed from main to avoid importing __main__ as a module
    posts = get_pending_posts()

    for post_id, photo, message in posts:
        try:
            if photo and message:
                await bot.send_photo(KANAL_ID, photo=photo, caption=message)
                await bot.send_message(ADMIN_ID,"Ваш пост атправлен канал")
            elif photo:
                await bot.send_photo(KANAL_ID, photo=photo)
            else:
                await bot.send_message(KANAL_ID, message)

            update_status(post_id)
            delete_post(post_id)

            logger.info(f"Post {post_id} yuborildi")

        except Exception as e:
            logger.error(f"Post {post_id} xato: {e}")


async def scheduler(bot):
    while True:
        await check_and_send(bot)
        await asyncio.sleep(30)