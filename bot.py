#!/usr/bin/env python3
import logging
import os

from typing import Awaitable, Callable

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from commands import set_bot_commands
from loader import bot, dp
from model import process_query
from aiogram import executor

logging.basicConfig(level=logging.INFO)


class UserSession(StatesGroup):
    SendingFile = State()
    Processing = State()
    QueryProcessing = State()
    Idle = State()

    file_path = State()
    file_description = State()


def get_status_callback(chat_id: int) -> Callable[[str], Awaitable]:
    async def callback(status: str) -> None:
        await bot.send_message(chat_id, status)
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)

    return callback


@dp.message_handler(commands="start")
async def start(message: types.Message, state: FSMContext):
    await message.answer(
        "Отправьте мне файл с данными и текстовое описание данных одним сообщением. Доступные форматы: CSV, JSON и XLSX."
    )

    await UserSession.SendingFile.set()


@dp.message_handler(commands="restart", state="*")
async def restart(message: types.Message, state: FSMContext):
    await state.finish()
    await start(message, state)


@dp.message_handler(commands="cancel", state="*")
async def cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer("Cancelled.")


@dp.message_handler(
    content_types=types.ContentType.DOCUMENT, state=UserSession.SendingFile
)
async def process_file(message: types.Message, state: FSMContext):
    chat_id = message.chat.id

    # Check if message has document
    if not message.document:
        await message.reply("Отправьте файл с расширением CSV, JSON или XLSX.")
        return

    # Check if message has text and text length > 30
    if not message.caption:
        await message.reply(
            "Отправьте файл с описанием. Описание должно быть не менее 30 символов"
        )
        return

    if len(message.caption) < 30:
        await message.reply("Описание должно быть не менее 30 символов.")
        return

    document_id = message.document.file_id
    file_info = await bot.get_file(document_id)

    await UserSession.Processing.set()

    # Pass file path
    file_path = file_info.file_path
    file_extension = message.document.file_name.split(".")[-1]
    if file_extension in ["csv", "json", "xlsx"]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_file_path = f"{current_dir}/{message.document.file_name}"

        await bot.download_file(file_path, destination=local_file_path)
        async with state.proxy() as data:
            data["file_path"] = local_file_path
            data["file_description"] = message.caption

        await message.reply("Ваш файл успешно загружен. Какой вопрос вы хотите задать?")

        # await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        # process_model_result = await process_file_with_model(
        #     local_file_path, get_status_callback(chat_id)
        # )

        # await message.reply(f"Обработка файла завершена. Отправляю результат...")
        # await bot.send_message(chat_id, process_model_result)

        await UserSession.QueryProcessing.set()
    else:
        await message.reply(
            "Такой формат не поддерживается. Попробуйте еще раз. Отправьте файл с расширением CSV, JSON или XLSX."
        )
        await UserSession.Idle.set()


@dp.message_handler(state=UserSession.Processing)
async def ignore_messages_while_processing(message: types.Message):
    await message.reply("Я занят обработкой предыдущего файла. Пожалуйста, подождите.")


@dp.message_handler(state=UserSession.QueryProcessing)
async def query_processing(message: types.Message, state: FSMContext):
    question = message.text

    data = await state.get_data()
    data_path = data.get("file_path")
    data_description = data.get("file_description")
    print(
        "starting query...\ndata_path: ",
        data_path,
        "\ndata_description:",
        data_description,
        "\nquestion:",
        question,
    )

    await process_query(
        data_path,
        data_description,
        question,
        message=message,
    )


async def on_startup(dp: Dispatcher) -> None:
    await set_bot_commands(dp)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
