from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

EMAIL = os.getenv("SMTP_EMAIL")
APP_PASS = os.getenv("SMTP_APP_PASS")

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

@app.route("/debug")
def debug():
    return {
        "email": EMAIL,
        "pass": APP_PASS
    }

@app.route("/send-email", methods=["POST"])
def send_email():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "body kosong"}), 400

        to = data.get("to")

        if not to:
            return jsonify({"error": "email kosong"}), 400

        if not EMAIL or not APP_PASS:
            return jsonify({"error": "SMTP belum diset"}), 500

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Download Verification Code"
        msg["From"] = f"CORTEX OFFICIAL <{EMAIL}>"
        msg["To"] = to

        html = build_html(to)
        msg.attach(MIMEText(html, "html"))

        # ================= SMTP =================
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            print("CONNECT...")
            server.starttls()

            print("LOGIN...")
            server.login(EMAIL, APP_PASS)

            print("SEND...")
            server.send_message(msg)

        return jsonify({"status": "sent"})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ================= RUN (RAILWAY) =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
