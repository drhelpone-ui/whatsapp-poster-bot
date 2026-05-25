import os
import requests
from flask import Flask, request
from twilio.rest import Client
from utils.generate import create_political_poster
from utils.cloudinary_upload import upload_to_cloudinary

app = Flask(__name__)

# Railway पर सेट किए गए secret keys
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    user_message = request.form.get("Body")
    media_url = request.form.get("MediaUrl0")
    sender_number = request.form.get("From")

    if not user_message or not media_url:
        return "OK", 200

    if "SUPPORT" in user_message.upper():
        prompt = (
            "Indian political campaign poster, young leader, "
            "humanoid cockroach mascot, tricolor smoke, "
            "text 'COCKROACH JANATA PARTY', viral Indian style, cinematic, 8K"
        )
    elif "AGAINST" in user_message.upper():
        prompt = (
            "Indian anti cockroach protest poster, dramatic protest, "
            "tricolor smoke, text 'STOP COCKROACH CHAOS', viral Indian poster, 8K"
        )
    else:
        send_whatsapp_message(sender_number, "Photo के साथ 'SUPPORT' या 'AGAINST' लिखो")
        return "OK", 200

    try:
        poster_bytes = create_political_poster(media_url, prompt)
    except Exception as e:
        send_whatsapp_message(sender_number, "AI poster बनाने में दिक्कत आई, थोड़ी देर बाद try करें")
        return "OK", 200

    try:
        temp_file = f"/tmp/{sender_number}_poster.jpg"
        with open(temp_file, "wb") as f:
            f.write(poster_bytes)
        poster_url = upload_to_cloudinary(temp_file, resource_type="image")
    except:
        send_whatsapp_message(sender_number, "Upload fail, फिर से try करें")
        return "OK", 200

    try:
        send_whatsapp_message(sender_number, "ये रहा आपका political poster 👇", media_url=poster_url)
    except:
        send_whatsapp_message(sender_number, "Poster तैयार है! लिंक: " + poster_url)

    return "OK", 200

def send_whatsapp_message(to, body, media_url=None):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message_data = {"from": TWILIO_WHATSAPP_NUMBER, "to": to, "body": body}
    if media_url:
        message_data["media_url"] = [media_url]
    client.messages.create(**message_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
