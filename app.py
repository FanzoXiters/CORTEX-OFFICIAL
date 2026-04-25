from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("RESEND_API_KEY")

# ================= HTML TEMPLATE =================
def build_html(receiver_email):
    return f"""
<html>
  <body style="margin:0;padding:0;background:#000000;font-family:Arial,sans-serif;">

    <table width="100%" cellpadding="0" cellspacing="0" style="background:#000000;">
      <tr>
        <td align="center" style="padding:30px 10px;">

          <!-- CARD -->
          <table width="500" cellpadding="0" cellspacing="0"
            style="background:#000000;border-radius:14px;padding:25px;">

            <!-- TITLE -->
            <tr>
              <td align="center">
                <h2 style="margin:0;color:#ffffff;font-weight:600;">
                  Download Verification Code
                </h2>
                <p style="margin:8px 0 15px;color:#9aa0a6;font-size:13px;">
                  {receiver_email}
                </p>
                <hr style="border:none;border-top:1px solid #222;">
              </td>
            </tr>

            <!-- CONTENT -->
            <tr>
              <td style="text-align:center;padding:15px 10px;color:#d0d0d0;font-size:14px;line-height:1.6;">

                <p>
                  Terima kasih atas permintaan Anda untuk mengakses file kami.
                  Kami menghargai kepercayaan Anda.
                </p>

                <p>
                  Silahkan download link berikut untuk Android dan Safari untuk IOS.
                </p>

                <!-- KEY LICENSE -->
                <div style="margin:15px 0;padding:10px;
                            background:#111;
                            border-radius:8px;
                            font-size:13px;
                            color:#aaa;">
                  Key License:<br>
                  <b style="color:#fff;">
                    CX_{receiver_email[:5].upper()}_X9Z81A
                  </b>
                </div>

                <!-- TUTORIAL -->
                <p style="font-size:13px;color:#aaa;">
                  Silahkan klik link berikut untuk
                  <span style="color:#3b82f6;">tutorial pemasangan</span>,
                  dan untuk aplikasi tambahan.
                </p>

                <!-- BUTTON -->
                <div style="margin:20px 0;">
                  <a href="https://example.com"
                     style="background:#3b82f6;
                            color:#ffffff;
                            padding:14px 32px;
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

              </td>
            </tr>

          </table>

        </td>
      </tr>
    </table>

  </body>
</html>
"""

# ================= ROUTES =================
@app.route("/")
def home():
    return "API Running 🚀"

# 🔍 DEBUG API KEY
@app.route("/debug-key")
def debug_key():
    return {
        "key": API_KEY
    }

# ================= SEND EMAIL =================
@app.route("/send-email", methods=["POST"])
def send_email():
    try:
        print("===== DEBUG START =====")
        print("API KEY:", API_KEY)

        data = request.get_json()
        print("BODY:", data)

        if not data:
            return jsonify({"error": "body kosong"}), 400

        to = data.get("to")
        print("TO:", to)

        if not to:
            return jsonify({"error": "email kosong"}), 400

        html = build_html(to)

        print("REQUEST KE RESEND...")

        res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": "CORTEX OFFICIAL <developer@panjox.my.id>",
                "to": [to],
                "subject": "Download Verification Code",
                "html": html
            },
            timeout=10
        )

        print("STATUS CODE:", res.status_code)
        print("RESPONSE:", res.text)

        # 🔥 HANDLE ERROR BIAR JELAS
        if res.status_code != 200:
            return jsonify({
                "status": "failed",
                "code": res.status_code,
                "response": res.text
            }), 500

        return jsonify({
            "status": "sent",
            "response": res.json()
        })

    except Exception as e:
        print("ERROR DETAIL:", e)
        return jsonify({"error": str(e)}), 500


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
