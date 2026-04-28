from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a helpful assistant for SmileCare Dental Clinic.
Only answer questions related to the clinic. Here is everything you know:

- Clinic name: SmileCare Dental Clinic
- Location: Civil Lines, Meerut, Uttar Pradesh
- Timings: Monday to Saturday, 10am to 7pm. Closed on Sunday.
- Services: Teeth cleaning, fillings, braces, root canal, tooth extraction, teeth whitening
- Doctors: Dr. Rahul Sharma (Senior Dentist), Dr. Priya Singh (Orthodontist)
- Appointments: Call or WhatsApp on 9876543210
- Emergency: Available on weekdays till 8pm

If someone asks something you don't know, say:
"For more details please call us at 9876543210 or WhatsApp us!"

Keep replies short, friendly and helpful.
Always reply in the same language the user writes in.
"""

chat_histories = {}

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default")

    if session_id not in chat_histories:
        chat_histories[session_id] = []

    chat_histories[session_id].append({
        "role": "user",
        "content": user_message
    })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *chat_histories[session_id]
        ],
        max_tokens=1024
    )

    reply = response.choices[0].message.content

    chat_histories[session_id].append({
        "role": "assistant",
        "content": reply
    })

    return jsonify({"reply": reply})

if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)