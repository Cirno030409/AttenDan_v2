from flask import Flask, abort, request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

configuration = Configuration(
    access_token="jJB5tomYR2uZSFeWE6RwTjauThL6p9w+P2EMC4AcfSoSM4+AB/GFRjaxOy3JdQdvZRR0E1cMWhZx7th0aAXSGZIcY3zO7PkLigbT3fHFaaXS987uX8onqE49Et9jUzxOt4rBFdnyFj3dtRpQIti0DgdB04t89/1O/w1cDnyilFU="
)
handler = WebhookHandler("efd4eede94989d952dddee0f0dddff32")


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)],
            )
        )


if __name__ == "__main__":
    app.run()
