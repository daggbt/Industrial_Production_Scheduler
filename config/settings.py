from datetime import timedelta

# Scheduling parameters
DEFAULT_HORIZON_MINUTES = 1440  # 24 hours
DEFAULT_OPTIMIZATION_TIMEOUT = 60  # seconds

# Operation durations (minutes)
OPERATION_DURATIONS = {
    'cutting': 45,
    'welding': 60,
    'assembly': 90,
    'painting': 120,
    'testing': 30,
    'machining': 75,
    'heat_treatment': 180,
    'quality_check': 25,
    'surface_finish': 55
}

# Visualization settings
GANTT_COLORS = [
    '#2E91E5',  # Blue
    '#E15F99',  # Pink
    '#1CA71C',  # Green
    '#FB0D0D',  # Red
    '#DA16FF',  # Purple
    '#222A2A',  # Dark Gray
    '#B68100',  # Orange
    '#750D86'   # Deep Purple
]

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
}