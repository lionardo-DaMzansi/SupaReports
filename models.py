"""
Database models for Supa Reports authentication and activity tracking
"""
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User account model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=True)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(255), unique=True, nullable=True)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    profile_picture = db.Column(db.String(255), default='/static/avatars/default-1.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    sessions = db.relationship('Session', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    stats = db.relationship('UserStats', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    def generate_verification_token(self):
        """Generate unique verification token"""
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token

    def generate_reset_token(self, expires_in_hours=24):
        """Generate password reset token with expiration"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=expires_in_hours)
        return self.reset_token

    def verify_reset_token(self, token):
        """Verify reset token is valid and not expired"""
        if not self.reset_token or self.reset_token != token:
            return False
        if not self.reset_token_expires or datetime.utcnow() > self.reset_token_expires:
            return False
        return True

    def clear_reset_token(self):
        """Clear reset token after use"""
        self.reset_token = None
        self.reset_token_expires = None

    def get_active_session(self):
        """Get user's active session if any"""
        return self.sessions.filter_by(is_active=True).first()

    def __repr__(self):
        return f'<User {self.email}>'


class Session(db.Model):
    """User session tracking"""
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_active = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 can be up to 45 chars
    user_agent = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    @staticmethod
    def generate_token():
        """Generate secure session token"""
        return secrets.token_urlsafe(32)

    def update_activity(self):
        """Update last active timestamp"""
        self.last_active = datetime.utcnow()
        db.session.commit()

    def deactivate(self):
        """Mark session as inactive"""
        self.is_active = False
        db.session.commit()

    def __repr__(self):
        return f'<Session {self.session_token[:8]}... User:{self.user_id}>'


class ActivityLog(db.Model):
    """User activity tracking"""
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)
    # Action types: 'audio_generated', 'video_generated', 'email_sent',
    #               'analysis_processed', 'report_generated'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    details = db.Column(db.Text, nullable=True)  # JSON string for additional metadata
    resource_id = db.Column(db.String(255), nullable=True)  # ID of created resource

    def __repr__(self):
        return f'<ActivityLog {self.action_type} User:{self.user_id} at {self.timestamp}>'


class UserStats(db.Model):
    """Aggregated user statistics"""
    __tablename__ = 'user_stats'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    reports_count = db.Column(db.Integer, default=0, nullable=False)
    audio_count = db.Column(db.Integer, default=0, nullable=False)
    video_count = db.Column(db.Integer, default=0, nullable=False)
    emails_sent_count = db.Column(db.Integer, default=0, nullable=False)
    analyses_count = db.Column(db.Integer, default=0, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def increment_stat(self, stat_type):
        """Increment a specific stat counter"""
        stat_mapping = {
            'audio_generated': 'audio_count',
            'video_generated': 'video_count',
            'email_sent': 'emails_sent_count',
            'analysis_processed': 'analyses_count',
            'report_generated': 'reports_count'
        }

        if stat_type in stat_mapping:
            attr = stat_mapping[stat_type]
            current = getattr(self, attr)
            setattr(self, attr, current + 1)
            self.last_updated = datetime.utcnow()
            db.session.commit()

    def __repr__(self):
        return f'<UserStats User:{self.user_id} Reports:{self.reports_count}>'


def init_db(app):
    """Initialize database with app context"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("✓ Database tables created")


def log_activity(user_id, action_type, details=None, resource_id=None):
    """
    Helper function to log user activity and update stats

    Args:
        user_id: ID of the user performing the action
        action_type: Type of action (audio_generated, video_generated, etc.)
        details: Optional dict with additional metadata (will be converted to JSON)
        resource_id: Optional ID of created resource
    """
    import json

    # Create activity log entry
    log = ActivityLog(
        user_id=user_id,
        action_type=action_type,
        timestamp=datetime.utcnow(),
        details=json.dumps(details) if details else None,
        resource_id=resource_id
    )
    db.session.add(log)

    # Update user stats
    user_stats = UserStats.query.get(user_id)
    if not user_stats:
        # Create stats record if doesn't exist
        user_stats = UserStats(user_id=user_id)
        db.session.add(user_stats)
        db.session.flush()  # Ensure record exists before increment

    user_stats.increment_stat(action_type)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging activity: {e}")
        raise
