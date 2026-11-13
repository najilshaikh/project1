import asyncio
import json
import os
import warnings
from dotenv import load_dotenv
import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters

warnings.filterwarnings("ignore", message=".*inplace.*")

load_dotenv(os.path.expanduser("~/projects/tradingbot/.env"))

TOKEN = os.environ['TOKEN']
OWNER_ID = int(os.environ['OWNER_ID'])# your numeric Telegram user ID
CHECK_INTERVAL = 120  # seconds
SAVE_FILE = os.path.expanduser("~/projects/tradingbot/watchlist.json")

# {"NVDA": {"target": 130.0, "alerted": False}}
watchlist = {}


def load_watchlist():
    global watchlist
    try:
        with open(SAVE_FILE) as f:
            watchlist = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        watchlist = {}


def save_watchlist():
    with open(SAVE_FILE, "w") as f:
        json.dump(watchlist, f)


async def get_price(symbol: str):
    return await asyncio.to_thread(lambda: yf.Ticker(symbol).fast_info["lastPrice"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Stock server online.\n"
        "/price NVDA - current price\n"
        "/watch NVDA 130 - alert when price drops below 130\n"
        "/list - active alerts\n"
        "/stop NVDA - remove alert"
    )


async def price_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /price NVDA")
        return
    symbol = context.args[0].upper().strip()
    try:
        price = await get_price(symbol)
        if price is None:
            await update.message.reply_text(f"{symbol} is not a valid stock.")
        else:
            await update.message.reply_text(f"{symbol}: ${price:.2f}")
    except Exception:
        await update.message.reply_text(f"Could not fetch data for {symbol}.")


async def watch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /watch NVDA 130.50")
        return
    symbol = context.args[0].upper().strip()
    try:
        target = float(context.args[1])
    except ValueError:
        await update.message.reply_text("Target must be a number, e.g. /watch NVDA 130")
        return
    try:
        price = await get_price(symbol)
        if price is None:
            await update.message.reply_text(f"{symbol} is not a valid stock.")
            return
    except Exception:
        await update.message.reply_text(f"Could not verify {symbol}.")
        return

    watchlist[symbol] = {"target": target, "alerted": False}
    save_watchlist()
    await update.message.reply_text(
        f"Watching {symbol} (now ${price:.2f}). Alert below ${target:.2f}."
    )


async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not watchlist:
        await update.message.reply_text("No active alerts. Use /watch NVDA 130")
        return
    lines = [f"- {s}: below ${d['target']:.2f}" for s, d in watchlist.items()]
    await update.message.reply_text("Active alerts:\n" + "\n".join(lines))


async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /stop NVDA")
        return
    symbol = context.args[0].upper().strip()
    if symbol in watchlist:
        del watchlist[symbol]
        save_watchlist()
        await update.message.reply_text(f"Stopped watching {symbol}.")
    else:
        await update.message.reply_text(f"No alert found for {symbol}.")


async def background_check(context: ContextTypes.DEFAULT_TYPE):
    changed = False
    for symbol, data in list(watchlist.items()):
        try:
            price = await get_price(symbol)
            if price is None:
                continue
            if price < data["target"] and not data["alerted"]:
                await context.bot.send_message(
                    chat_id=OWNER_ID,
                    text=f"ALERT: {symbol} is ${price:.2f}, below ${data['target']:.2f}.",
                )
                data["alerted"] = True
                changed = True
            elif price >= data["target"] and data["alerted"]:
                data["alerted"] = False
                changed = True
        except Exception as e:
            print(f"Check failed for {symbol}: {e}", flush=True)
    if changed:
        save_watchlist()


def main():
    load_watchlist()
    owner = filters.User(user_id=OWNER_ID)
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start, filters=owner))
    app.add_handler(CommandHandler("price", price_cmd, filters=owner))
    app.add_handler(CommandHandler("watch", watch_cmd, filters=owner))
    app.add_handler(CommandHandler("list", list_cmd, filters=owner))
    app.add_handler(CommandHandler("stop", stop_cmd, filters=owner))
    app.job_queue.run_repeating(background_check, interval=CHECK_INTERVAL, first=10)
    app.run_polling()


if __name__ == "__main__":
    main()
