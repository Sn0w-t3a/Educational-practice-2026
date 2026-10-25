# Настройка логирования: консоль (INFO+) и файл (DEBUG+).
import logging
import sys
from pathlib import Path


def setup_logger(name: str = "matrix_app",
                 log_file: str = "logs/app.log",
                 console_level: int = logging.INFO,
                 file_level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(console_level)
    console.setFormatter(fmt)
    logger.addHandler(console)

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(file_level)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logger.debug("Логгер '%s' инициализирован, файл: %s", name, log_file)
    return logger