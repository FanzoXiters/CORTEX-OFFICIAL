from flask import Flask, request, jsonify
import requests
import os
import random
import string
import time
from supabase import create_client, Client

app = Flask(__name__)

# ================= ENV =================
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("SUPABASE ENV belum lengkap")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= LICENSE GENERATOR =================
def generate_key():
    chars = string.ascii_uppercase + string.digits
    return "CX_" + "".join(random.choices(chars, k=10))

# ================= EMAIL TEMPLATE (JANGAN DIUBAH) =================
def build_html(email, license_key):
    return f"""
<html>
<head>
  <meta name="color-scheme" content="light dark">
  <style>
    @media (prefers-color-scheme: dark) {{
      body {{ background:#000 !important; }}
      .box {{ background:#222 !important; }}
      .text {{ color:#ddd !important; }}
    }}
  </style>
</head>

<body style="margin:0;padding:0;background:#fff;font-family:Arial;">

  <div style="padding:20px;text-align:center;">

    <h2>Download Verification</h2>
    <p>{email}</p>

    <p class="text">
      Terima kasih atas pembelian Anda.
    </p>

    <div class="box" style="margin:15px;padding:10px;background:#f0f0f0;border-radius:8px;">
      <b>{license_key}</b>
    </div>

    <a href="https://example.com"
       style="background:#2563eb;color:#fff;padding:12px 20px;text-decoration:none;border-radius:6px;">
       Download Now
    </a>

  </div>

</body>
</html>
"""

# ================= HOME =================
@app.route("/")
def home():
    return "API Running 🚀"

# ================= SEND EMAIL =================
@app.route("/send-email", methods=["POST"])
def send_email():

    data = request.get_json()

    if not data:
        return jsonify({"error": "body kosong"}), 400

    to = data.get("to")
    device_id = data.get("device_id")

    if not to:
        return jsonify({"error": "email kosong"}), 400

    license_key = generate_key()
    now = int(time.time())

    # SAVE SUPABASE
    supabase.table("licenses").insert({
        "license": license_key,
        "email": to,
        "device_id": device_id or "",
        "status": "active",
        "created": now
    }).execute()

    # EMAIL SEND
    html = build_html(to, license_key)

    res = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": "CORTEX OFFICIAL <developer@panjox.my.id>",
            "to": [to],
            "subject": "License Aktivasi",
            "html": html
        }
    )

    if not res.ok:
        return jsonify({"status": "failed", "error": res.text}), 500

    return jsonify({
        "status": "success",
        "license": license_key
    })

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({"status": "error"}), 400

    license_key = data.get("license")
    device_id = data.get("device_id")

    if not license_key or not device_id:
        return jsonify({"status": "error"}), 400

    result = supabase.table("licenses").select("*").eq("license", license_key).execute()

    if not result.data:
        return jsonify({"status": "invalid"}), 404

    record = result.data[0]

    saved_device = record.get("device_id")

    # FIRST BIND
    if not saved_device:
        supabase.table("licenses").update({
            "device_id": device_id
        }).eq("license", license_key).execute()

        return jsonify({"status": "success", "msg": "first bind"})

    # DEVICE LOCK
    if saved_device != device_id:
        return jsonify({"status": "blocked"}), 403

    return jsonify({"status": "success", "msg": "login ok"})


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
