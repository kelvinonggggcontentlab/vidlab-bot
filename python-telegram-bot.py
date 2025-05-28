import logging
import pytz
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIG ===
TOKEN = "7624965037:AAF9ZyfK_ZnbGhnwYMtDbGlV23n-SO_59qo"  # Replace with your real bot token
SPREADSHEET_ID = "1az2tADYNM2ARVWCPMspwUZdXMAmqe3nAYXnIgqEhvQ4"
TIMEZONE = pytz.timezone("Asia/Singapore")  # Must use pytz timezone for apscheduler compatibility

# Google Sheets scopes and credentials path
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENTIAL_PATH = "/Users/gggcapital/Desktop/VIDLAB PROJECT/final_data/script/DATA/vidlab-marketing-460409-f0e918ae72e2.json"

# === LOGGING SETUP ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# === GOOGLE SHEET HELPERS ===
def get_gsheet_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_PATH, SCOPE)
    client = gspread.authorize(creds)
    return client

def get_sheet(sheet_name: str):
    client = get_gsheet_client()
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
    return sheet

# === STAFF LIST SHEET ===
STAFF_LIST_SHEET = "Staff List"

# === FUNCTION: Get staff record by telegram id ===
def get_staff_by_telegram_id(telegram_id: int):
    try:
        sheet = get_sheet(STAFF_LIST_SHEET)
        all_records = sheet.get_all_records()
        for idx, record in enumerate(all_records, start=2):  # header row = 1
            if str(record.get("Telegram ID", "")).strip() == str(telegram_id):
                record["row"] = idx
                return record
    except Exception as e:
        logger.error(f"Error fetching staff by Telegram ID: {e}")
    return None

# === FUNCTION: Get staff record by Staff ID ===
def get_staff_by_staff_id(staff_id: str):
    try:
        sheet = get_sheet(STAFF_LIST_SHEET)
        all_records = sheet.get_all_records()
        for idx, record in enumerate(all_records, start=2):
            if record.get("Staff ID", "").strip().upper() == staff_id.upper():
                record["row"] = idx
                return record
    except Exception as e:
        logger.error(f"Error fetching staff by Staff ID: {e}")
    return None

# === FUNCTION: Bind telegram id to staff ===
def bind_telegram_id(staff_id: str, telegram_id: int, telegram_username: str):
    sheet = get_sheet(STAFF_LIST_SHEET)
    staff = get_staff_by_staff_id(staff_id)
    if not staff:
        return False, "Staff ID tidak dijumpai bossku."
    row = staff["row"]

    # Check if already bound
    col_telegram_id = sheet.find("Telegram ID").col
    col_telegram_username = sheet.find("Telegram Username").col
    col_login_time = sheet.find("Login Time").col

    current_telegram_id = sheet.cell(row, col_telegram_id).value
    if current_telegram_id and str(current_telegram_id) != "" and str(current_telegram_id) != str(telegram_id):
        return False, "Staff ID ni dah ada orang guna, tak boleh bind dua kali."

    # Check if telegram id already bind with other staff
    existing_staff = get_staff_by_telegram_id(telegram_id)
    if existing_staff and existing_staff["Staff ID"] != staff_id:
        return False, "Telegram ID ni dah bind dengan Staff ID lain."

    # Check STATUS aktif
    status = staff.get("STATUS", "").strip().upper()
    if status != "ACTIVE":
        return False, "Staff ID anda tak aktif, sila contact admin."

    # Bind Telegram ID & username and update login time
    try:
        sheet.update_cell(row, col_telegram_id, str(telegram_id))
        sheet.update_cell(row, col_telegram_username, telegram_username)
        now_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        sheet.update_cell(row, col_login_time, now_str)
    except Exception as e:
        logger.error(f"Error updating sheet bind info: {e}")
        return False, "Gagal update info, cuba semula."

    return True, "Yeay! Staff ID bind dengan Telegram berjaya bossku."

# === FUNCTION: Send role-based menu buttons ===
async def send_role_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, staff_role: str):
    buttons = [
        [InlineKeyboardButton("📤 Upload Footage", callback_data="upload_footage")],
        [InlineKeyboardButton("📜 My Submissions", callback_data="my_submissions")],
        [InlineKeyboardButton("🕵️ Review Status", callback_data="review_status")],
        [InlineKeyboardButton("🗣️ Feedback", callback_data="feedback")],
        [InlineKeyboardButton("📝 FAQ / Guide", callback_data="faq")],
        [InlineKeyboardButton("🏷️ My Profile", callback_data="my_profile")],
        [InlineKeyboardButton("💬 Leave Me a Msg", callback_data="leave_msg")],
        [InlineKeyboardButton("🔄 Refresh Menu", callback_data="refresh_menu")],
    ]

    if staff_role.upper() in ["ADMIN", "BIG BOSS"]:
        buttons.append([InlineKeyboardButton("📣 Push Notification", callback_data="push_notification")])
    if staff_role.upper() in ["EDITOR (SENIOR)", "EDITOR (JUNIOR)"]:
        buttons.append([InlineKeyboardButton("🎬 Video Edit Done", callback_data="video_edit_done")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Ini menu kau bossku! Pilih mana nak jalan kerja.", reply_markup=reply_markup)

# === COMMAND: /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello bossku! Sila guna /verify untuk bind Staff ID dengan Telegram.")

# === COMMAND: /verify ===
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sila taip Staff ID anda sekarang (contoh: SA1123).")
    context.user_data["awaiting_staff_id"] = True

# === HANDLE TEXT (for verify flow) ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    telegram_id = update.message.from_user.id
    telegram_username = update.message.from_user.username or ""

    if context.user_data.get("awaiting_staff_id", False):
        staff_id = text.upper()
        context.user_data["awaiting_staff_id"] = False

        success, msg = bind_telegram_id(staff_id, telegram_id, telegram_username)
        await update.message.reply_text(msg)

        if success:
            staff = get_staff_by_staff_id(staff_id)
            staff_name = staff.get("Staff Name", "Bossku")
            staff_role = staff.get("Role", "SA")
            await update.message.reply_text(f"Boom! Kau verified as {staff_name} (Staff ID: {staff_id}). Kita jalan kerja sekarang!")
            await send_role_menu(update, context, staff_role)
        else:
            await update.message.reply_text("Sila cuba lagi dengan Staff ID yang betul atau hubungi admin.")
    else:
        await update.message.reply_text("Saya tak faham bossku. Sila guna /verify untuk mula.")

# === CALLBACK QUERY BUTTON HANDLER ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "upload_footage":
        await query.edit_message_text("Feature Upload Footage coming soon, bossku!")
    elif data == "my_submissions":
        await query.edit_message_text("Feature My Submissions coming soon, bossku!")
    elif data == "review_status":
        await query.edit_message_text("Feature Review Status coming soon, bossku!")
    elif data == "feedback":
        await query.edit_message_text("Feature Feedback coming soon, bossku!")
    elif data == "faq":
        await query.edit_message_text("Feature FAQ / Guide coming soon, bossku!")
    elif data == "my_profile":
        await query.edit_message_text("Feature My Profile coming soon, bossku!")
    elif data == "leave_msg":
        await query.edit_message_text("Feature Leave Me a Msg coming soon, bossku!")
    elif data == "refresh_menu":
        staff = get_staff_by_telegram_id(update.effective_user.id)
        if staff:
            await send_role_menu(update, context, staff.get("Role", "SA"))
        else:
            await query.edit_message_text("Please /verify dulu, bossku!")
    elif data == "push_notification":
        await query.edit_message_text("Feature Push Notification coming soon, bossku!")
    elif data == "video_edit_done":
        await query.edit_message_text("Feature Video Edit Done coming soon, bossku!")
    else:
        await query.edit_message_text("Button belum implement, bossku!")

# === UNKNOWN COMMAND HANDLER ===
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Command tak dikenali bossku. Sila guna /verify untuk mula.")

# === MAIN FUNCTION ===
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("Bot started bossku, tunggu command dari user...")
    application.run_polling()

if __name__ == "__main__":
    main()
