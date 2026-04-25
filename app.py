from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("RESEND_API_KEY")

# ================= HTML TEMPLATE =================
def build_html(receiver_email):
    return f"""
    <html>
      <body style="margin:0;padding:0;background:#000;font-family:Arial;">
        <table width="100%" style="background:#000;">
          <tr>
            <td align="center" style="padding:30px;">
              <table width="500" style="background:#000;border-radius:14px;padding:25px;">
                
                <tr>
                  <td align="center">
                    <h2 style="color:#fff;">Download Verification Code</h2>
                    <p style="color:#aaa;">{receiver_email}</p>
                    <hr style="border-top:1px solid #222;">
                  </td>
                </tr>

                <tr>
                  <td style="text-align:center;color:#ccc;">
                    
                    <p>Silahkan download untuk Android / iOS</p>

                    <div style="background:#111;padding:10px;border-radius:8px;">
                      Key License:<br>
                      <b style="color:#fff;">CX_{receiver_email[:5].upper()}_X9Z81A</b>
                    </div>

                    <div style="margin:20px;">
                      <a href="https://example.com"
                         style="background:#3b82f6;color:#fff;padding:12px 25px;
                                text-decoration:none;border-radius:8px;">
                        Download Now
                      </a>
                    </div>

                    <p style="font-size:12px;color:#777;">
                      Jika butuh bantuan, hubungi penjual.
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
