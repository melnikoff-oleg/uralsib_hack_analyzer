import time
from typing import Callable, Awaitable
from data_analyst import use_data_assistant
from aiogram import types


# async def process_file_with_model(
#     file_path: str, callback: Callable[[str], Awaitable]
# ) -> str:
#     start = time.time()
#     for _ in range(0, 51, 10):
#         time.sleep(1)

#         await callback(f"Processed time: {time.time() - start} seconds")

#     return "Done"


async def process_query(
    data_path: str,
    data_description: str,
    question: str,
    message: types.Message,
) -> str:
    response = use_data_assistant(
        data_path,
        data_description=data_description,
        question=question,
    )
    await message.reply(
        response
        + "\n\nЗадайте следующий вопрос, либо воспользуйтесь командой /restart чтобы начать работу с новым набором данных."
    )
