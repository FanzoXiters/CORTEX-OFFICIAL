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

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= LICENSE =================
def generate_key():
    chars = string.ascii_letters + string.digits
    return "Cx_" + "".join(random.choice(chars) for _ in range(16))

# ================= HTML (TIDAK DIUBAH UI SAMA SEKALI) =================
def build_html(receiver_email, license_key, download_url):
    return f"""
<html>
<head>
  <meta name="color-scheme" content="light dark">
  <meta name="supported-color-schemes" content="light dark">

  <style>
    @media (prefers-color-scheme: dark) {{
      body {{
        background:#000000 !important;
      }}
      .card {{
        background:#000000 !important;
      }}
      .text {{
        color:#e5e5e5 !important;
      }}
      .muted {{
        color:#b0b0b0 !important;
      }}
      .box {{
        background:#2a2a2a !important;
      }}
    }}
  </style>
</head>

<body style="margin:0;padding:0;background:#ffffff;font-family:Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:30px 10px;">

        <table width="500" cellpadding="0" cellspacing="0"
          style="background:#ffffff;border-radius:14px;padding:25px;"
          class="card">

          <tr>
            <td align="center">
              <h2 style="margin:0;color:#111;font-weight:600;">
                Download Verification Code
              </h2>

              <p style="margin:8px 0 15px;color:#666;font-size:15px;">
                {receiver_email}
              </p>

              <hr style="border:none;border-top:1px solid #ddd;">
            </td>
          </tr>

          <tr>
            <td style="text-align:center;padding:15px 10px;color:#333;font-size:14px;line-height:1.6;">

              <p class="text" style="margin:10px 0;">
                Terima kasih atas permintaan Anda untuk mengakses Aplikasi kami.
                Kami menghargai kepercayaan Anda.
              </p>

              <p class="text">
                Silahkan download link berikut untuk Android.
              </p>
              

              <div style="margin:15px 0;padding:10px;
                          background:#f0f0f0;
                          border-radius:8px;
                          font-size:13px;
                          color:#333;"
                   class="box">

                License:<br>

                <b style="color:#2563eb;">
                  {license_key}
                </b>
              </div>

              <p style="font-size:13px;color:#555;margin-top:10px;">
                Silahkan klik link berikut untuk
                <span style="color:#2563eb;">tutorial pemasangan</span>,
                dan untuk aplikasi tambahan.
              </p>

              <div style="margin:15px 0;">
                <a href="{download_url}"
                   style="background:#2563eb;
                          color:#ffffff;
                          padding:10px 40px;
                          text-decoration:none;
                          border-radius:8px;
                          font-weight:bold;
                          display:inline-block;">
                  Download Now
                </a>
              </div>

              <p style="font-size:12px;color:#777;">
                Jika Anda membutuhkan bantuan, silahkan hubungi penjual.
              </p>
              
              <p style="font-size:10px;color:#777;">
                ©CortexTools NewPatch
              </p>

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
        data = request.get_json() or {}

        to = data.get("to")
        download_url = data.get("download_url")  # 🔥 TAMBAH INI

        if not to:
            return jsonify({"error": "email kosong"}), 400

        if not download_url:
            download_url = "https://example.com"  # default fallback

        license_key = generate_key().strip()

        supabase.table("licenses").insert({
            "license": license_key,
            "email": to,
            "device_id": "",
            "download_url": download_url,   # 🔥 SIMPAN APK YANG DIPILIH ADMIN
            "status": "active",
            "created": int(time.time())
        }).execute()

        html = build_html(to, license_key, download_url)

        res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": "CORTEX OFFICIAL <developer@panjox.my.id>",
                "to": [to],
                "subject": "Download Verification Code",
                "html": html
            }
        )

        if not res.ok:
            return jsonify({"status": "failed", "error": res.text}), 500

        return jsonify({
            "status": "sent",
            "license": license_key,
            "download_url": download_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.form   # 🔥 INI WAJIB

        license_key = data.get("license")
        device_id = data.get("device_id")

        if not license_key or not device_id:
            return jsonify({"status": "error"}), 400

        license_key = license_key.strip().upper()

        result = supabase.table("licenses").select("*").eq("license", license_key).execute()

        if not result.data:
            return jsonify({"status": "invalid"}), 404

        record = result.data[0]
        saved_device = record.get("device_id")

        if not saved_device:
            supabase.table("licenses").update({
                "device_id": device_id
            }).eq("license", license_key).execute()
            return jsonify({"status": "success"})

        if saved_device != device_id:
            return jsonify({"status": "blocked"}), 403

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
