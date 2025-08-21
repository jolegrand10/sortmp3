import logging
from logging.handlers import RotatingFileHandler
import sys


class Full_Log:
    """
        setup  full logging in a single call using a kind-of Façade pattern
    """

    def __init__(self, name, level):
        #
        lvl = getattr(logging, level.upper(), logging.INFO)
        logging.basicConfig(
            level=lvl,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.StreamHandler(sys.stdout),
                RotatingFileHandler(name + ".log", maxBytes=100_000,
                                    backupCount=3, encoding="utf-8"),
            ],
            force=True,  # écrase toute config/handlers existants (Python ≥3.8)
        )
