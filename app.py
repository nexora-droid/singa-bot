import os
import pytz
from datetime import datetime
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient
from apscheduler.schedulers.background import BackgroundScheduler
import dotenv 
import os
from dotenv import load_dotenv


SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SIGNING_SECRET = os.environ['SIGNING_SECRET']
CHANNEL_ID = "#singapore-hangout" 


app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SIGNING_SECRET
)

client = WebClient(token=SLACK_BOT_TOKEN)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


def send_anthem_message():
    client.chat_postMessage(
        channel=CHANNEL_ID,
        text="Please rise for the National Anthem.",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Please rise for the National Anthem.*"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Take the Pledge"
                        },
                        "style": "primary",
                        "action_id": "take_pledge"
                    }
                ]
            }
        ]
    )

@app.action("take_pledge")
def handle_pledge(ack, body):
    ack()

    user_id = body["user"]["id"]
    channel_id = body["channel"]["id"]
    ts = body["message"]["ts"]

    client.chat_update(
        channel=channel_id,
        ts=ts,
        text="Please rise for the National Anthem.",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Please rise for the National Anthem.*\n<@{user_id}> clicked take the pledge"
                }
            }
        ]
    )
    client.chat_postMessage(
        channel=channel_id,
        text=(
            "*🇸🇬 The National Pledge*\n\n"
            "We, the citizens of Singapore, pledge ourselves as one united people, regardless of race, language or religion, to build a democratic society based on justice and equality so as to achieve happiness, prosperity and progress for our nation."
        )
    )

@flask_app.route("/test/anthem")
def test_anthem():
    send_anthem_message()

def schedule_job():
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Singapore"))
    scheduler.add_job(send_anthem_message, "cron", hour=7, minute=30)
    scheduler.start()

schedule_job()

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@flask_app.route("/")
def home():
    return "Slack bot is running"

@flask_app.route("/slack/commands", methods=["POST"])
def slack_commands():
    data = request.form
    user_id = data.get("user_id")
    command = data.get("command")
    text = data.get("text")
    channel_id = data.get("channel_id")

    if command == "/singapore":
        client.chat_postMessage(
            channel=CHANNEL_ID,
            text="Singapore, officially the Republic of Singapore, is an island country and city-state in Southeast Asia. Its territory comprises one main island, 63 satellite islands and islets, and one outlying islet. The country is about one degree of latitude north of the equator, off the southern tip of the Malay Peninsula, bordering the Strait of Malacca to the west, the Singapore Strait to the south along with the Riau Islands in Indonesia, the South China Sea to the east and the Straits of Johor along with the State of Johor in Malaysia to the north."
        )
        return "", 200

    return "", 200
@flask_app.route("/health")
def health_check():
    return "OK", 200
startup_ping_sent = True
if __name__ == "__main__":
    if not startup_ping_sent:
        try:
            client.chat_postMessage(
                channel=CHANNEL_ID,
                text="Ping? Pong! Singa is back.... now will someone please send over the PFP for Singa..."
            )
        except Exception as e:
            print("Failed to send startup ping:", e)

    port = int(os.environ.get("PORT", 3000))
    flask_app.run(host="0.0.0.0", port=port)
