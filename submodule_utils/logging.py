import sys
import logging

def logger_factory(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        logfile=None):
    """Set up a logger. Optionally pass a log file to write to.

    Parameters
    ----------
    level : int
        logging.DEBUG, logging.INFO, logging.WARNING, ...etc.
    
    format : str
        Format string for logging.

    logfile : str or None
        Log file to print logs to (i.e. *.log).
    """
    handlers = [logging.StreamHandler(sys.stdout)]
    if logfile:
        handlers.append(logging.FileHandler(logfile))
    logging.basicConfig(level=level, format=format, handlers=handlers)