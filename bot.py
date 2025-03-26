from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bs4 import BeautifulSoup
import re
import aiohttp  # Using aiohttp for async HTTP requests
from web import keep_alive

BOT_TOKEN = "6880096605:AAGP6---YcXDdPYtYlqrlxRbSmmhrfcMo9c"
BASE_URL = "https://opabhik.serv00.net/Watch.php?url="
TERABOX_PATTERN = r"https?://(?:\w+\.)?(terabox|1024terabox|freeterabox|teraboxapp|tera|teraboxlink|mirrorbox|nephobox|1024tera|momerybox|tibibox|terasharelink|teraboxshare|terafileshare)\.\w+"
LOG_CHANNEL_ID = "-1002107937108"  # Replace with your actual log channel's username or chat ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command to welcome the user with an image and button."""
    
    # URL or path to the image
    image_url = "https://envs.sh/ozm.jpg"  # Replace with the URL or local path
    
    # Button that will be displayed below the image
    button = InlineKeyboardButton("✨ Join Channel", url="https://t.me/+Q8sRUuL-hzUwZGM1")  # Replace with your desired URL
    
    # Creating an inline keyboard with the button
    reply_markup = InlineKeyboardMarkup([[button]])

    # Reply with image and button
    await update.message.reply_photo(
        photo=image_url,  # Use an image URL or local file path
        caption="<b>👋 Hi! Welcome to the bot! Send a Terabox link, and I’ll create a stream link for you.Support Channel :- @AM_UPLOAD</b>",
        reply_markup=reply_markup
    )

async def fetch_file_details(url):
    """Fetch file name, thumbnail, and size from the provided URL asynchronously."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()  # Raise error for bad status
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
    user_message = update.message.text.strip()

    if re.search(TERABOX_PATTERN, user_message):
        # Fetch file details (ensure to await the coroutine)
        file_details = await fetch_file_details(user_message)

        # Handle error if any
        if "error" in file_details:
            await update.message.reply_text(f"❌ Error fetching file details: {file_details['error']}")
            return

        # Format the details
        file_name = file_details["file_name"]
        file_size = file_details["file_size"]
        thumbnail_url = file_details["thumbnail_url"]

        # Truncate file name if it's too long
        MAX_LENGTH = 100  # Adjust based on your needs
        file_name = file_name[:MAX_LENGTH] + "..." if len(file_name) > MAX_LENGTH else file_name

        # Create the new URL
        new_url = f"{BASE_URL}{user_message}"
 # Create a button   
        button = InlineKeyboardButton("🌐 Watch Online", url=new_url)
        reply_markup = InlineKeyboardMarkup([[button]])

        # Format the reply text
        reply_text = (
            f"✅ Here is your stream Link:**\n\n"
            f"📄 **File Name: {file_name}\n\n"
            f"By :- @AM_FILMS\n\n"
            f"🔗 Click the button below to open the link."
        )

        # Send message with photo or just text depending on size for the user
        if thumbnail_url:
            if len(reply_text) > 4096:
                # If the text is too long, split it
                await update.message.reply_text(reply_text[:4096])
                await update.message.reply_photo(photo=thumbnail_url, caption=reply_text[4096:], reply_markup=reply_markup)
            else:
                await update.message.reply_photo(
                    photo=thumbnail_url,
                    caption=reply_text,
                    reply_markup=reply_markup
                )
        else:
            await update.message.reply_text(reply_text, reply_markup=reply_markup)

        # Send the same message to the log channel (exact same message with thumbnail and button)
        if thumbnail_url:
            # Send the same message (including the button) to the log channel
            await context.bot.send_photo(
                chat_id=LOG_CHANNEL_ID,
                photo=thumbnail_url,
                caption=reply_text,
                reply_markup=reply_markup  # Sending the button
            )
        else:
            # If no thumbnail, send only the text with the button to the log channel
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=reply_text,
                reply_markup=reply_markup  # Sending the button
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

    # Start polling
    application.run_polling()

if name == "main":
    keep_alive()
    main()
