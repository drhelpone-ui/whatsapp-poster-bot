import io
import base64
import requests
from PIL import Image
import os

HF_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

def create_political_poster(media_url, prompt):
    # फोटो डाउनलोड करो
    img_response = requests.get(media_url)
    img = Image.open(io.BytesIO(img_response.content)).convert("RGB")
    img = img.resize((512, 512))

    # base64 बनाओ (API के लिए)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    payload = {
        "inputs": prompt,
        "parameters": {
            "image": img_base64,
            "strength": 0.7,
            "negative_prompt": "ugly, blurry, low quality, deformed face",
            "num_inference_steps": 30,
            "guidance_scale": 7.5
        }
    }
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    response = requests.post(HF_API_URL, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Hugging Face error: {response.text}")
    return response.content
