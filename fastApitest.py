from fastapi import FastAPI
from fastapi import FastAPI, Header, Request, Response
import telegram

def send_test_message(message):
    try:
        telegram_notify = telegram.Bot("5910304360:AAGW_t3F1x9cATh7d6VUDCquJFX0dPC2W-M")
    
        telegram_notify.send_message(chat_id="-895385211", text=message,
                                parse_mode='Markdown')
    except Exception as ex:
        print(ex)
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/phuong')
async def phuongEvent(request: Request):
    body = await request.body()
    send_test_message(body.decode("utf8"))
    return "ok"