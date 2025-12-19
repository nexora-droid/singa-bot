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
    client.chat.postMessage(
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

    client.chat.update(
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


    client.chat.postMessage(
        channel=channel_id,
        text=(
            "We, the citizens of Singapore, pledge ourselves as one united people, "
            "regardless of race, language or religion, to build a democratic society "
            "based on justice and equality so as to achieve happiness, prosperity "
            "and progress for our nation."
        )
    )

def schedule_job():
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Singapore"))
    scheduler.add_job(send_anthem_message, "cron", hour=6, minute=0)
    scheduler.start()

schedule_job()

def send_startup_ping():
    client.chat.postMessage(
        channel=CHANNEL_ID,
        text="Ping? Pong! Singa is back.... now will someone please send over the PFP for Singa..."
    )

send_startup_ping()

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@flask_app.route("/")
def home():
    return "Slack bot is running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    flask_app.run(host="0.0.0.0", port=port)
