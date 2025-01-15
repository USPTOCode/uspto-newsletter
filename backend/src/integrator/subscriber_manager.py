import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import logging
from email_validator import validate_email, EmailNotValidError

class SubscriberManager:
    """Manages newsletter subscribers using SQLite database."""
    
    def __init__(self, db_path: str = 'data/subscribers.db'):
        """Initialize subscriber manager with database path."""
        self.db_path = db_path
        self.logger = logging.getLogger('SubscriberManager')
        self._ensure_db_exists()
        
    def _ensure_db_exists(self):
        """Create database and tables if they don't exist."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Subscribers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscribers (
                    email TEXT PRIMARY KEY,
                    name TEXT,
                    verification_token TEXT UNIQUE,
                    verified BOOLEAN DEFAULT FALSE,
                    subscribed BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Subscription preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS preferences (
                    email TEXT PRIMARY KEY,
                    format TEXT DEFAULT 'html',
                    frequency TEXT DEFAULT 'monthly',
                    categories TEXT,
                    FOREIGN KEY (email) REFERENCES subscribers(email)
                )
            ''')
            
            # Email history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    newsletter_id TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    FOREIGN KEY (email) REFERENCES subscribers(email)
                )
            ''')
            
            conn.commit()

    def add_subscriber(self, email: str, name: Optional[str] = None) -> Dict:
        """Add a new subscriber."""
        try:
            # Validate email
            valid = validate_email(email)
            email = valid.email

            verification_token = str(uuid.uuid4())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Add subscriber
                cursor.execute('''
                    INSERT INTO subscribers (email, name, verification_token)
                    VALUES (?, ?, ?)
                    ON CONFLICT(email) DO UPDATE SET
                        name = COALESCE(?, name),
                        updated_at = CURRENT_TIMESTAMP
                ''', (email, name, verification_token, name))
                
                # Initialize preferences
                cursor.execute('''
                    INSERT OR IGNORE INTO preferences (email)
                    VALUES (?)
                ''', (email,))
                
                conn.commit()
                
            self.logger.info(f"Added subscriber: {email}")
            return {
                'email': email,
                'verification_token': verification_token,
                'status': 'pending_verification'
            }
            
        except EmailNotValidError as e:
            self.logger.error(f"Invalid email address: {email}")
            raise ValueError(f"Invalid email address: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error adding subscriber: {e}")
            raise

    def verify_subscriber(self, token: str) -> bool:
        """Verify a subscriber using their verification token."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE subscribers
                    SET verified = TRUE,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE verification_token = ?
                ''', (token,))
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Verified subscriber with token: {token}")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error verifying subscriber: {e}")
            raise

    def unsubscribe(self, email: str, token: str) -> bool:
        """Unsubscribe a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE subscribers
                    SET subscribed = FALSE,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE email = ? AND verification_token = ?
                ''', (email, token))
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Unsubscribed: {email}")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error unsubscribing: {e}")
            raise

    def update_preferences(self, email: str, preferences: Dict) -> bool:
        """Update subscriber preferences."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                valid_formats = ['html', 'text', 'markdown']
                valid_frequencies = ['weekly', 'monthly', 'quarterly']
                
                format = preferences.get('format', 'html')
                frequency = preferences.get('frequency', 'monthly')
                categories = json.dumps(preferences.get('categories', []))
                
                if format not in valid_formats:
                    raise ValueError(f"Invalid format. Must be one of: {valid_formats}")
                if frequency not in valid_frequencies:
                    raise ValueError(f"Invalid frequency. Must be one of: {valid_frequencies}")
                
                cursor.execute('''
                    UPDATE preferences
                    SET format = ?,
                        frequency = ?,
                        categories = ?
                    WHERE email = ?
                ''', (format, frequency, categories, email))
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Updated preferences for: {email}")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating preferences: {e}")
            raise

    def get_active_subscribers(self) -> List[Dict]:
        """Get all active subscribers."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT s.*, p.*
                    FROM subscribers s
                    LEFT JOIN preferences p ON s.email = p.email
                    WHERE s.verified = TRUE
                    AND s.subscribed = TRUE
                ''')
                
                subscribers = []
                for row in cursor.fetchall():
                    subscriber = dict(row)
                    if subscriber['categories']:
                        subscriber['categories'] = json.loads(subscriber['categories'])
                    subscribers.append(subscriber)
                
                return subscribers
                
        except Exception as e:
            self.logger.error(f"Error getting active subscribers: {e}")
            raise

    def record_email_sent(self, email: str, newsletter_id: str, status: str):
        """Record when an email is sent to a subscriber."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO email_history (email, newsletter_id, status)
                    VALUES (?, ?, ?)
                ''', (email, newsletter_id, status))
                conn.commit()
                
            self.logger.info(f"Recorded email sent to {email} for newsletter {newsletter_id}")
            
        except Exception as e:
            self.logger.error(f"Error recording email history: {e}")
            raise

    def get_subscriber_stats(self) -> Dict:
        """Get subscriber statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total subscribers
                cursor.execute('SELECT COUNT(*) FROM subscribers')
                stats['total_subscribers'] = cursor.fetchone()[0]
                
                # Active subscribers
                cursor.execute('''
                    SELECT COUNT(*)
                    FROM subscribers
                    WHERE verified = TRUE AND subscribed = TRUE
                ''')
                stats['active_subscribers'] = cursor.fetchone()[0]
                
                # Format preferences
                cursor.execute('''
                    SELECT format, COUNT(*) as count
                    FROM preferences
                    GROUP BY format
                ''')
                stats['format_preferences'] = dict(cursor.fetchall())
                
                # Recent activity
                cursor.execute('''
                    SELECT COUNT(*) as count
                    FROM email_history
                    WHERE sent_at > datetime('now', '-30 days')
                ''')
                stats['emails_sent_last_30_days'] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Error getting subscriber stats: {e}")
            raise