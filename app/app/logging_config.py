
import logging
import logging.config
from contextlib import contextmanager
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger("finance_tracker")


def setup_logging():
    """Load logging configuration from YAML."""

    config_path = BASE_DIR / "logging.yaml"
    log_path = BASE_DIR / "app.log"

    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    config["handlers"]["file"]["filename"] = str(log_path)

    logging.config.dictConfig(config)


@contextmanager
def log_operation(operation):
    """Log an operation if it fails."""

    try:
        yield
    except Exception:
        logger.exception("Operation failed: %s", operation)
        raise
