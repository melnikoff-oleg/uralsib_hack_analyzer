from aiogram import Dispatcher, types


async def set_bot_commands(dp: Dispatcher) -> None:
    commands = [
        types.BotCommand(command="start", description="Start the bot"),
        types.BotCommand(command="cancel", description="Cancel"),
        types.BotCommand(command="restart", description="Restart"),
    ]

    await dp.bot.set_my_commands(commands)
