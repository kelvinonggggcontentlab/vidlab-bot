def send_push_notification_to_editor(editor, count, goal, new=False):
    png_path = '/Users/gggcapital/Desktop/VIDLAB PROJECT/final_data/script/ASSETS/masa habis.png'
    msg = (
        f"Hai {editor['STAFF NAME']}! Calvin nak {'info' if new else 'remind'}:\n"
        f"{'Kamu telah dapat tugas baru A CODE video untuk diedit hari ini.' if new else f'Today you have only sent back {count}/{goal} videos.'}\n"
        f"Min daily is {goal}. Kalau kurang, monthly performance report akan effect, Boss Aroon will check every month."
    )
    # TG推送接口（正式上线需补token与chat_id）
    # from telegram import Bot
    # bot = Bot(token="7624965037:AAF9ZyfK_ZnbGhnwYMtDbGlV23n-SO_59qo")
    # bot.send_photo(chat_id=editor['TELEGRAM ID'], photo=open(png_path, 'rb'), caption=msg)
    print(f"[发通知] 给{editor['STAFF NAME']} | 内容: {msg} | PNG: {png_path}")

