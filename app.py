from flask import Flask, request, jsonify
import requests
import os
import random
import string

import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

API_KEY = os.getenv("RESEND_API_KEY")

# ================= FIREBASE INIT =================
cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://cortex-project-e8bfd-default-rtdb.firebaseio.com/"
})

# ================= LICENSE GENERATOR =================
def generate_key():
    chars = string.ascii_uppercase + string.digits
    return "CX_" + "".join(random.choices(chars, k=10))

# ================= HTML TEMPLATE (TIDAK DIUBAH UI) =================
def build_html(receiver_email, license_key):

    return f"""
<html>
<head>
  <meta name="color-scheme" content="light dark">
  <meta name="supported-color-schemes" content="light dark">

  <style>
    @media (prefers-color-scheme: dark) {{
      body {{ background:#000000 !important; }}
      .card {{ background:#000000 !important; }}
      .text {{ color:#e5e5e5 !important; }}
      .box {{ background:#2a2a2a !important; }}
    }}
  </style>
</head>

<body style="margin:0;padding:0;background:#ffffff;font-family:Arial,sans-serif;">

  <table width="100%">
    <tr>
      <td align="center" style="padding:30px 10px;">

        <table width="500" style="background:#ffffff;border-radius:14px;padding:25px;">
          <tr>
            <td align="center">

              <h2 style="margin:0;color:#111;">
                Download Verification Code
              </h2>

              <p style="margin:8px 0 15px;color:#666;font-size:13px;">
                {receiver_email}
              </p>

              <hr style="border:none;border-top:1px solid #ddd;">
            </td>
          </tr>

          <tr>
            <td style="text-align:center;padding:15px;color:#333;font-size:14px;line-height:1.6;">

              <p class="text">
                Terima kasih atas permintaan Anda untuk mengakses file kami.
              </p>

              <p class="text">
                Silahkan download aplikasi melalui link berikut.
              </p>

              <!-- LICENSE -->
              <div class="box" style="margin:15px 0;padding:10px;background:#f0f0f0;border-radius:8px;">
                Key License:<br>
                <b style="color:#2563eb;">
                  {license_key}
                </b>
              </div>

              <!-- BUTTON -->
              <a href="https://example.com"
                 style="background:#2563eb;color:#fff;padding:14px 32px;text-decoration:none;border-radius:8px;display:inline-block;">
                Download Now
              </a>

            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

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
    try:

        data = request.get_json()

        if not data:
            return jsonify({"error": "body kosong"}), 400

        to = data.get("to")
        device_id = data.get("device_id")

        if not to:
            return jsonify({"error": "email kosong"}), 400

        # 🔥 GENERATE LICENSE
        license_key = generate_key()

        # 🔥 SAVE KE FIREBASE
        db.reference("licenses").child(license_key).set({
            "email": to,
            "device_id": device_id if device_id else "",
            "status": "active"
        })

        # 🔥 BUILD EMAIL
        html = build_html(to, license_key)

        # 🔥 SEND EMAIL
        res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": "CORTEX OFFICIAL <developer@panjox.my.id>",
                "to": [to],
                "subject": "License Aktivasi",
                "html": html
            }
        )

        if res.status_code != 200:
            return jsonify({
                "status": "failed",
                "response": res.text
            }), 500

        return jsonify({
            "status": "success",
            "license": license_key
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= LOGIN CHECK (DEVICE LOCK) =================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    license_key = data.get("license")
    device_id = data.get("device_id")

    if not license_key or not device_id:
        return jsonify({"status": "error"}), 400

    ref = db.reference("licenses").child(license_key)
    snap = ref.get()

    if not snap:
        return jsonify({"status": "invalid"}), 404

    saved_device = snap.get("device_id")

    # 🔥 FIRST BIND
    if not saved_device:
        ref.update({"device_id": device_id})
        return jsonify({"status": "success", "msg": "first bind"})

    # 🔥 DEVICE CHECK
    if saved_device != device_id:
        return jsonify({"status": "blocked", "msg": "device not allowed"}), 403

    return jsonify({"status": "success", "msg": "login ok"})


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
