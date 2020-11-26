from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

import paho.mqtt.publish as publish
app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
YOUR_BEEBOTTE_TOKEN = os.environ['YOUR_BEEBOTTE_TOKEN']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

def publish_cam_control(msg):
    publish.single('pitest/button', \
                    msg, \
                    hostname='mqtt.beebotte.com', \
                    port=8883, \
                    auth = {'username':'token:{}'.format(YOUR_BEEBOTTE_TOKEN)}, \
                    tls={'ca_certs':'mqtt.beebotte.com.pem'})



@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text=event.message.text
    if text == "camera-on":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="ONにしますよ"))
        publish_cam_control("on")
            
    elif text =="camera-off":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="OFFにします"))
        publish_cam_control("off")
            
    elif text =="still":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="撮影します"))
        publish_cam_control("still")
        
    elif text =="camera-state":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="ON_or_OFF"))
        publish_cam_control("state")
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text+":は設定されていません"))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
