import telegram
import random

def send_test_message():
    try:
        random_number = random.randint(0, 1000)
        telegram_notify = telegram.Bot("5910304360:AAGW_t3F1x9cATh7d6VUDCquJFX0dPC2W-M")
        message = "`Số random là {}`".format(random_number) 
    
        telegram_notify.send_message(chat_id="-895385211", text=message,
                                parse_mode='Markdown')
    except Exception as ex:
        print(ex)

send_test_message()