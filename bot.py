import requests
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bs4 import BeautifulSoup
import re
import aiohttp  # Using aiohttp for async HTTP requests
from web import keep_alive

# API endpoint and credentials
TERABOX_API_URL = "https://terabox-downloader3.p.rapidapi.com/get-final-response"
API_HEADERS = {
    "x-rapidapi-key": "0ec1d5fa9bmsh203fa2fef325774p1bdb48jsnce437790802e",
    "x-rapidapi-host": "terabox-downloader3.p.rapidapi.com",
    "Content-Type": "application/json"
}

# Telegram bot token
BOT_TOKEN = ""
BASE_URL = "https://terabox-downloader-direct-download-link-generator2.p.rapidapi.com/url="
TERABOX_PATTERN = r"https?://(?:\w+\.)?(terabox|1024terabox|freeterabox|teraboxapp|tera|teraboxlink|mirrorbox|nephobox|1024tera|momerybox|tibibox|terasharelink|teraboxshare|terafileshare)\.\w+"
LOG_CHANNEL_ID = "-1002107937108"  # Replace with your actual log channel's username or chat ID
FSUB_CHANNEL_ID = "-1001940661697"  # Replace with your force subscription channel ID or username
FSubLink = "https://t.me/+NfyWKdRHdsRhNWQ1"  # Replace with your actual channel link

# Current date and time
current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
# Current user's login
current_user = "monouj"

def get_download_link(url):
    """Get the download link for a given Terabox URL."""
    payload = { "url": url }
    try:
        print(f"Request initiated by {current_user} at {current_datetime}")
        response = requests.post(TERABOX_API_URL, json=payload, headers=API_HEADERS)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}

async def check_subscription(user_id, bot):
    """Check if a user is a member of the required channel."""
    try:
        member = await bot.get_chat_member(FSUB_CHANNEL_ID, user_id)
        print(f"User {user_id} subscription status: {member.status}")  # Debugging
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error in check_subscription: {e}")  # Debugging
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command to welcome the user with an image and button."""
    user_id = update.message.from_user.id
    is_subscribed = await check_subscription(user_id, context.bot)

    if not is_subscribed:
        button = InlineKeyboardButton("✨ Join Channel", url=FSubLink)
        reply_markup = InlineKeyboardMarkup([[button]])
        await update.message.reply_text(
            "❌ You must join our channel to use this bot.\n"
            "Click the button below to join and then try again.",
            reply_markup=reply_markup,
        )
        return

    image_url = "https://envs.sh/rhi.jpg"  # Replace with the URL or local path
    
    # Button that will be displayed below the image
    button = InlineKeyboardButton("✨ Join Channel", url="https://t.me/+NfyWKdRHdsRhNWQ1")  # Replace with your desired URL
    
    # Creating an inline keyboard with the button
    reply_markup = InlineKeyboardMarkup([[button]])

    # Reply with image and button
    await update.message.reply_photo(
        photo=image_url,
        caption="<b>👋 Hi! Welcome to the bot! Send a Terabox link, and I’ll create a stream link for you.Support Channel :- @AM_UPLOAD</b>",
    )

async def fetch_file_details(url):
    """Fetch file name, thumbnail, and size from the provided URL asynchronously."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                page_content = await response.text()

        soup = BeautifulSoup(page_content, "html.parser")

        file_name = soup.find("meta", {"property": "og:title"})
        file_name = file_name["content"] if file_name else "Unknown File"

        thumbnail = soup.find("meta", {"property": "og:image"})
        thumbnail_url = thumbnail["content"] if thumbnail else None

        file_size_tag = soup.find(string=lambda text: "MB" in text or "GB" in text)
        file_size = file_size_tag.strip() if file_size_tag else "Unknown Size"

        return {
            "file_name": file_name,
            "thumbnail_url": thumbnail_url,
            "file_size": file_size,
        }
    except aiohttp.ClientError as e:
        return {"error": f"Failed to fetch details: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

async def process_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process a Terabox link, fetch details, and create a new URL with a button."""
    user_id = update.message.from_user.id
    is_subscribed = await check_subscription(user_id, context.bot)

    if not is_subscribed:
        button = InlineKeyboardButton("✨ Join Channel", url=FSubLink)
        reply_markup = InlineKeyboardMarkup([[button]])
        await update.message.reply_text(
            "❌ You must join our channel to use this bot.\n"
            "Click the button below to join and then try again.",
            reply_markup=reply_markup,
        )
        return

    user_message = update.message.text.strip()

    if re.search(TERABOX_PATTERN, user_message):
        file_details = await fetch_file_details(user_message)

        if "error" in file_details:
            await update.message.reply_text(f"❌ Error fetching file details: {file_details['error']}")
            return

        file_name = file_details["file_name"]
        file_size = file_details["file_size"]
        thumbnail_url = file_details["thumbnail_url"]

        MAX_LENGTH = 100
        file_name = file_name[:MAX_LENGTH] + "..." if len(file_name) > MAX_LENGTH else file_name

        download_link_response = get_download_link(user_message)
        if "error" in download_link_response:
            await update.message.reply_text(f"❌ Error generating download link: {download_link_response['error']}")
            return

        new_url = download_link_response.get('download_link')
        button = InlineKeyboardButton("🌐 Watch Online", url=new_url)
        reply_markup = InlineKeyboardMarkup([[button]])

        reply_text = (
            f"✅ **Here is your stream Link:**\n\n"
            f"📄 **File Name:** {file_name}\n\n"
            f"By :- @AM_FILMS\n\n"
            f"🔗 Click the button below to open the link."
        )

        if thumbnail_url:
            await update.message.reply_photo(
                photo=thumbnail_url,
                caption=reply_text,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(reply_text, reply_markup=reply_markup)

        # Logging to channel
        if thumbnail_url:
            await context.bot.send_photo(
                chat_id=LOG_CHANNEL_ID,
                photo=thumbnail_url,
                caption=reply_text,
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=reply_text,
                reply_markup=reply_markup
            )
    else:
        await update.message.reply_text(
            "❌ That doesn't look like a valid Terabox link.\n"
            "💡 Please send a link from domains like *terabox.com* or *terabox.co*."
        )

def main():
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_link))

    application.run_polling()

if __name__ == "__main__":
    keep_alive()
    main()
