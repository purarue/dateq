import os
import logging


logger = logging.getLogger("dateq")
logger.addHandler(logging.NullHandler())

if "DATEQ_DEBUG_LOGS" in os.environ:
    logging.basicConfig(level=logging.DEBUG)
