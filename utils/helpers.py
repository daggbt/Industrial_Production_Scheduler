from datetime import datetime, timedelta
from typing import Dict
from config.settings import OPERATION_DURATIONS

def get_operation_duration(operation: str) -> int:
    """Get the standard duration for an operation in minutes"""
    return OPERATION_DURATIONS.get(operation, 60)

def minutes_to_datetime(minutes: int, base_date: datetime = None) -> datetime:
    """Convert minutes to datetime"""
    if base_date is None:
        base_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    return base_date + timedelta(minutes=minutes)

def datetime_to_minutes(dt: datetime, base_date: datetime = None) -> int:
    """Convert datetime to minutes since base_date"""
    if base_date is None:
        base_date = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return int((dt - base_date).total_seconds() / 60)