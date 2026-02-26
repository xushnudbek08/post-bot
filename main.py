import asyncio
import logging
import os


from aiogram import Bot, Dispatcher, F


from headnlers.chanel import scheduler, Chanel


#  CONFIG 


BOT_TOKEN = os.getenv("BOT_TOKEN")
KANAL_ID = int(os.getenv("KANAL_ID"))
ADMIN_ID = int(os.getenv("admin"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(Chanel)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





# ================= FSM =================
  # har 30 sekund

# ================= MAIN =================
async def main():
    
    # start scheduler with bot instance
    asyncio.create_task(scheduler(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())