import ollama
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramBadRequest
from config import TOKEN, whitelist

bot = Bot(token=TOKEN)
dp = Dispatcher()


def compat_format(text):
    special_chars = [".", ",", "!", "?", "-"]

    for char in special_chars:
        text = text.replace(char, f"\{char}")

    return text


@dp.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id in whitelist:
        try:
            start_message = """
Hello! This is a Private Ollama & Telegram Bot Integration.
It currently uses a [13B WizardLM-Uncensored Model](https://ollama.com/library/wizardlm-uncensored).
To generate a response, you should use the /ai command.
    """
            start_message = compat_format(start_message)
            await message.reply(start_message, parse_mode="MarkdownV2")
        except TelegramBadRequest:
            await message.answer(
                f"ERROR: TelegramBadRequest! Sending the response without formatting."
            )
            await message.reply(start_message)
        except Exception as e:
            await message.reply("Unknown error ocurred. Please refer to the logs.")
            print(e)
    else:
        await message.reply("You are not in the whitelist.")


@dp.message(Command("ai"))
async def generate_ai_response(message: Message):
    if message.from_user.id in whitelist:
        prompt = message.text.replace("/ai", "")
        prompt = prompt.strip()
        if prompt == "":
            await message.answer("The prompt is empty, can't generate anything.")
        else:
            await message.answer("Your response is currently generating, please wait.")
            print(f"IN: [{prompt}] FROM: [@{message.from_user.username}]")
            try:
                full_response = ollama.generate(
                    model="wizardlm-uncensored", prompt=prompt
                )
                response = full_response["response"]
                response_compat = compat_format(response)
                await message.answer(response_compat, parse_mode="MarkdownV2")
                print(f"OUT: [{response_compat}]")
            except TelegramBadRequest as e:
                await message.answer(
                    f"ERROR: TelegramBadRequest! Sending the response without formatting."
                )
                await message.answer(response)
                print(
                    "ERROR: TelegramBadRequest! Sending the response without formatting."
                )
                print(f"OUT: [{response}]")
            except Exception as e:
                await message.reply("Unknown error ocurred. Please refer to the logs.")
                print(e)
    else:
        await message.reply("You are not in the whitelist.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("The bot is ON.")
    asyncio.run(main())
