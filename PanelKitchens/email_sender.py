import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Dict, Optional


class EmailSender:
    def __init__(self, smtp_config: Optional[Dict] = None):
        """
        אתחול שולח המייל
        smtp_config: {
            'server': 'smtp.gmail.com',
            'port': 587,
            'email': 'your_email@gmail.com',
            'password': 'your_app_password'
        }
        """
        self.config = smtp_config or self.load_config()

    def load_config(self) -> Dict:
        """טעינת הגדרות מקובץ או משתני סביבה"""
        config_file = "email_config.json"
        if os.path.exists(config_file):
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Try environment variables
        return {
            'server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
            'port': int(os.environ.get('SMTP_PORT', '587')),
            'email': os.environ.get('SMTP_EMAIL', ''),
            'password': os.environ.get('SMTP_PASSWORD', ''),
        }

    def is_configured(self) -> bool:
        """בדיקה אם המייל מוגדר"""
        return bool(self.config.get('email') and self.config.get('password'))

    def send_quote_email(self,
                         recipient_email: str,
                         customer_name: str,
                         pdf_path: str,
                         quote_summary: Dict) -> tuple[bool, str]:
        """
        שליחת הצעת מחיר במייל
        Returns: (success: bool, message: str)
        """
        if not self.is_configured():
            return False, "הגדרות המייל לא מוגדרות. יש להגדיר בהגדרות המערכת."

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config['email']
            msg['To'] = recipient_email
            msg['Subject'] = f"הצעת מחיר - Panel Kitchens - {customer_name}"

            # Email body
            body = self.create_email_body(customer_name, quote_summary)
            msg.attach(MIMEText(body, 'html', 'utf-8'))

            # Attach PDF
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    attachment = MIMEBase('application', 'pdf')
                    attachment.set_payload(f.read())
                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{os.path.basename(pdf_path)}"'
                    )
                    msg.attach(attachment)

            # Send email
            server = smtplib.SMTP(self.config['server'], self.config['port'])
            server.starttls()
            server.login(self.config['email'], self.config['password'])
            server.send_message(msg)
            server.quit()

            return True, "המייל נשלח בהצלחה!"

        except Exception as e:
            return False, f"שגיאה בשליחת המייל: {str(e)}"

    def create_email_body(self, customer_name: str, quote_summary: Dict) -> str:
        """יצירת גוף המייל"""
        total_amount = quote_summary.get('total_amount', 0)
        items_count = quote_summary.get('items_count', 0)

        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    direction: rtl;
                    text-align: right;
                    color: #333;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #d32f2f;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .summary {{
                    background-color: #fff;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #d32f2f;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Panel Kitchens</h1>
                    <p>מטבחים באיכות גבוהה</p>
                </div>

                <div class="content">
                    <h2>שלום {customer_name},</h2>

                    <p>תודה על התעניינותך בשירותי Panel Kitchens.</p>
                    <p>מצורפת הצעת המחיר שביקשת.</p>

                    <div class="summary">
                        <h3>סיכום ההצעה:</h3>
                        <ul>
                            <li>מספר פריטים: {items_count}</li>
                            <li>סה"כ לתשלום: ₪{total_amount:,.2f}</li>
                        </ul>
                    </div>

                    <p>ההצעה תקפה ל-14 ימים ממועד הפקתה.</p>
                    <p>לשאלות נוספות, אנא צור קשר:</p>
                    <ul>
                        <li>טלפון: 072-393-3997</li>
                        <li>דוא"ל: info@panel-k.co.il</li>
                        <li>כתובת: הנגרים 1 (מתחם הורדוס), באר שבע</li>
                    </ul>

                    <p>בברכה,<br>צוות Panel Kitchens</p>
                </div>

                <div class="footer">
                    <p>© 2025 Panel Kitchens. כל הזכויות שמורות.</p>
                    <p>הודעה זו נשלחה באופן אוטומטי, אנא אל תשיב למייל זה.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def save_config(self, config: Dict):
        """שמירת הגדרות המייל"""
        import json
        with open("email_config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        self.config = config

    def test_connection(self) -> tuple[bool, str]:
        """בדיקת חיבור לשרת המייל"""
        if not self.is_configured():
            return False, "הגדרות המייל לא מוגדרות"

        try:
            server = smtplib.SMTP(self.config['server'], self.config['port'])
            server.starttls()
            server.login(self.config['email'], self.config['password'])
            server.quit()
            return True, "החיבור הצליח!"
        except Exception as e:
            return False, f"שגיאה בחיבור: {str(e)}"