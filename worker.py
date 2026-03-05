"""
worker.py
Standalone background worker for Render.
Starts the scanner scheduler and keeps the process alive.
"""
import time
import logging
from app import create_app
from database.db import init_db
from scanner.scheduler import start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s"
)

log = logging.getLogger(__name__)

if __name__ == "__main__":
    log.info("🚀 Starting crypto scanner worker...")
    app = create_app()
    init_db(app)
    start_scheduler(app)
    log.info("⏰ Worker running — press Ctrl+C to stop")
    while True:
        time.sleep(60)
