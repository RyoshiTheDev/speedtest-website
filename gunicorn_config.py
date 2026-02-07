import os

# Bind to the PORT environment variable
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# Worker configuration
workers = 2
worker_class = 'sync'
timeout = 120

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
