"""
Base Model Configuration
Contains base utilities and timezone helpers
"""
# Import Base from core database to ensure shared metadata
# Import Base from core database to ensure shared metadata
from app.core.database import Base
from datetime import datetime, timezone, timedelta
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now():
    """Returns current datetime in IST timezone"""
    return datetime.now(IST)
