from aiogram import asyncio, types

from loader import bot


async def send_typing_periodically(chat_id: int, delay=4.5):
    while True:
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        await asyncio.sleep(delay)
