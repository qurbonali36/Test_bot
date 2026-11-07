from flask import Flask, render_template_string, send_file, abort
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Basic HTML template for the verification page
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificate Verification</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1a1a24; color: #fff; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background-color: #2a2a36; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); max-width: 600px; width: 100%; text-align: center; border: 2px solid #C8A55E; }
        .header { color: #C8A55E; font-size: 28px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; }
        .status { font-size: 20px; color: #4CAF50; font-weight: bold; margin-bottom: 30px; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .details { text-align: left; margin-bottom: 30px; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 8px; }
        .details p { margin: 10px 0; font-size: 16px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }
        .details span { color: #C8A55E; font-weight: bold; display: inline-block; width: 130px; }
        .btn { display: inline-block; padding: 12px 24px; margin: 10px; background-color: #C8A55E; color: #000; text-decoration: none; font-weight: bold; border-radius: 6px; transition: background 0.3s; }
        .btn:hover { background-color: #e0b868; }
        .invalid { color: #F44336; }
        .invalid-icon { font-size: 48px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        {% if valid %}
            <div class="header">Verified Certificate</div>
            <div class="status">✅ VALID</div>
            <div class="details">
                <p><span>Certificate ID:</span> {{ cert.certificate_id }}</p>
                <p><span>Recipient:</span> {{ cert.recipient_name }}</p>
                <p><span>Test Name:</span> {{ cert.test_name }}</p>
                <p><span>Score:</span> {{ cert.score }}%</p>
                <p><span>Issue Date:</span> {{ cert.issue_date }}</p>
            </div>
            <a href="/download/{{ cert.certificate_id }}/png" class="btn" target="_blank">View Certificate (PNG)</a>
            <a href="/download/{{ cert.certificate_id }}/pdf" class="btn">Download PDF</a>
        {% else %}
            <div class="invalid-icon">❌</div>
            <div class="header invalid">Invalid Certificate</div>
            <p>This certificate could not be verified in our database.</p>
            <p>Please ensure you scanned a valid and official QR code.</p>
        {% endif %}
    </div>
</body>
</html>
"""

def get_db_connection():
    conn = sqlite3.connect('tg_bot.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/certificate/<cert_id>')
def verify_certificate(cert_id):
    conn = get_db_connection()
    cert = conn.execute('SELECT * FROM certificates WHERE certificate_id = ?', (cert_id,)).fetchone()
    conn.close()
    
    if cert:
        return render_template_string(TEMPLATE, valid=True, cert=cert)
    else:
        return render_template_string(TEMPLATE, valid=False), 404

@app.route('/download/<cert_id>/<format>')
def download_certificate(cert_id, format):
    conn = get_db_connection()
    cert = conn.execute('SELECT * FROM certificates WHERE certificate_id = ?', (cert_id,)).fetchone()
    conn.close()
    
    if not cert:
        abort(404)
        
    if format == 'png':
        path = cert['png_path']
        mimetype = 'image/png'
    elif format == 'pdf':
        path = cert['pdf_path']
        mimetype = 'application/pdf'
    else:
        abort(400)
        
    if os.path.exists(path):
        return send_file(path, mimetype=mimetype, as_attachment=(format=='pdf'))
    else:
        abort(404, "File not found on server.")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
