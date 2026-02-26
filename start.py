
from aiogram.filters import CommandStart
from aiogram import Router,F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import asyncio
import logging
from datetime import datetime
from base import get_pending_posts,delete_post,add_post,update_status
KANAL_ID =-1003802620550
from main import bot

from aiogram.types import ReplyKeyboardMarkup,KeyboardButton





dminnn=ReplyKeyboardMarkup(
    keyboard=[

        [KeyboardButton(text="Телеграм "),KeyboardButton(text="Вк")],
        [KeyboardButton(text="Дабавит тг канал"),KeyboardButton(text="Дабавит вк группу")]

        ],
        resize_keyboard=True
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)



admin=Router()

@admin.message(CommandStart())
async def start (message:Message):
    name=message.from_user.full_name
    await message.answer(f"Здраствуйте {name}",reply_markup=dminnn)



class PostState(StatesGroup):
    photo = State()      # 1. rasm kutadi
    message = State()    # 2. matn kutadi
    time = State()       # 3. vaqt kutadi
    # 3. vaqt kutadi


@admin.message(F.text == "Телеграм")
async def add_post_start(message: Message, state: FSMContext):

    await state.set_state(PostState.photo)
    await message.answer("📸 Rasm yuboring\n\n(Rasm bo'lmasa /skip yozing)")

@admin.message(PostState.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo=file_id)
    await state.set_state(PostState.message)
    await message.answer("✍️ Post matnini yozing")

@admin.message(PostState.photo, F.text == "/skip")
async def skip_photo(message: Message, state: FSMContext):
    await state.update_data(photo=None)
    await state.set_state(PostState.message)
    await message.answer("✍️ Post matnini yozing")

@admin.message(PostState.message)
async def get_message(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    await state.set_state(PostState.time)
    await message.answer(
        "🕐 Qachon post qilinsin?\n\n"
        "Format: <code>2026-02-25 09:00</code>",
        parse_mode="HTML"
    )

@admin.message(PostState.time)
async def get_time(message: Message, state: FSMContext):
    # Vaqt formatini tekshirish
    try:
        post_time = datetime.strptime(message.text, '%Y-%m-%d %H:%M')
    except ValueError:
        return await message.answer(
            "❌ Format xato!\n"
            "To'g'ri format: <code>2026-02-25 09:00</code>",
            parse_mode="HTML"
        )

    data = await state.get_data()
    add_post(
        message=data.get("message"),
        post_time=message.text,
        photo=data.get("photo")
    )
    await state.clear()
    await message.answer(
        f"✅ Post saqlandi!\n\n"
        f"📅 Vaqt: <code>{message.text}</code>\n"
        f"📢 Kanal: {KANAL_ID}",
        parse_mode="HTML"
    )
    logger.info(f"Yangi post saqlandi → {message.text}")

# ========== SCHEDULER ==========
async def check_and_send():
    posts = get_pending_posts()
    for post_id, photo, message in posts:
        try:
            if photo and message:
                await bot.send_photo(chat_id=KANAL_ID, photo=photo, caption=message)
            elif photo:
                await bot.send_photo(chat_id=KANAL_ID, photo=photo)
            else:
                await bot.send_message(chat_id=KANAL_ID, text=message)

            update_status(post_id)   # status → 1
            delete_post(post_id)     # status=1 → o'chirish

            # Adminga xabar
            await bot.send_message(
              
                text=f"✅ Post #{post_id} kanalga yuborildi va o'chirildi!"
            )
            logger.info(f"Post #{post_id} yuborildi va o'chirildi")

        except Exception as e:
            logger.error(f"Post #{post_id} yuborishda xato: {e}")
            await bot.send_message(
                
                text=f"❌ Post #{post_id} yuborishda xato:\n{e}"
            )

async def scheduler():
    while True:
        await check_and_send()
        await asyncio.sleep(60)