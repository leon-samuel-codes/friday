"""Telegram remote control — Phase 13.

Run it from FRIDAY with /telegram. Incoming messages go
through the same CommandRouter.process_command() the
terminal uses, so both front-ends behave the same.

Setup (one time):
  1. On Telegram, message @BotFather -> /newbot, copy the token
  2. Message @userinfobot to get YOUR user id
  3. Set environment variables:
       FRIDAY_TELEGRAM_TOKEN=<the token>
       FRIDAY_TELEGRAM_USER_ID=<your id>

Security: the bot answers only to your user ID — nobody
else can drive FRIDAY through it.
"""

import os

import commands
from ai import build_system_prompt, trim


def run(memory, router, chat_with_model):
    """Start the bot. Blocks until Ctrl+C.

    chat_with_model(messages, echo) is the same streaming
    function the terminal uses (stream_chat in main.py);
    telegram passes an echo that throws the text away, so
    tokens aren't printed to the terminal.
    """
    try:
        from telegram.ext import (Application, CommandHandler,
                                  MessageHandler, filters)
    except ImportError:
        return ("Needs python-telegram-bot — "
                "run: pip install python-telegram-bot")

    token = os.environ.get("FRIDAY_TELEGRAM_TOKEN")
    allowed_raw = os.environ.get("FRIDAY_TELEGRAM_USER_ID")
    if not token or not allowed_raw:
        return ("Set FRIDAY_TELEGRAM_TOKEN and "
                "FRIDAY_TELEGRAM_USER_ID first "
                "(see this file's docstring).")
    try:
        allowed_id = int(allowed_raw)
    except ValueError:
        return "FRIDAY_TELEGRAM_USER_ID must be a number."

    # Telegram keeps its own conversation, separate from
    # the terminal's.
    messages = [{"role": "system",
                 "content": build_system_prompt(memory)}]

    async def send(update, text):
        await update.message.reply_text(text or "(no reply)")

    async def on_start(update, context):
        await send(update, "FRIDAY remote is online.")

    async def on_help(update, context):
        await send(update, router.process_command("help"))

    async def on_text(update, context):
        if update.effective_user.id != allowed_id:      # security gate
            await send(update, "Not authorized.")
            return
        text = update.message.text
        low = text.lower()

        if low == "/new":                # reset THIS chat's history
            messages[:] = messages[:1]
            await send(update, "Fresh conversation.")
            return

        reply = router.process_command(text)
        if reply is not None:
            await send(update, reply)
            return

        if low.startswith("ask "):       # live web answer
            question = text[4:].strip()
            results = commands.ask(question)
            content = (f"Live search results for '{question}':\n"
                       + results
                       + f"\n\nUsing only these results, answer: {question}")
        else:
            content = text

        messages.append({"role": "user", "content": content})
        messages[:] = trim(messages, 10)
        answer = chat_with_model(messages, echo=lambda piece: None)
        if answer is None:
            messages.pop()
            await send(update, "FRIDAY: the model call failed.")
            return
        messages.append({"role": "assistant", "content": answer.strip()})
        await send(update, answer.strip())

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", on_start))
    app.add_handler(CommandHandler("help", on_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    print("FRIDAY Telegram remote: listening for messages... "
          "(Ctrl+C to stop)")
    app.run_polling()
    return "Telegram remote stopped."
