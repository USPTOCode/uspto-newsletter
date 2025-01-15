import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import os
from pathlib import Path
import logging

class NewsletterEmailer:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not all([self.smtp_username, self.smtp_password]):
            raise ValueError("SMTP credentials not configured")
        
        self.logger = logging.getLogger('NewsletterEmailer')

    def send_newsletter(self, recipients: List[str], html_content: str, text_content: str, subject: str):
        """Send newsletter to list of recipients."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = ', '.join(recipients)

            # Add content
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            self.logger.info(f"Newsletter sent to {len(recipients)} recipients")
            return True

        except Exception as e:
            self.logger.error(f"Error sending newsletter: {e}")
            raise

    def send_test_email(self, recipient: str, html_content: str, text_content: str, subject: str):
        """Send a test newsletter to a single recipient."""
        return self.send_newsletter([recipient], html_content, text_content, subject)