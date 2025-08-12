import logging
from logging.handlers import RotatingFileHandler


class Full_Log:
    """
        setup  full logging in a single call using a kind-of Façade pattern
    """

    def __init__(self, name, verbose=True, debug=True):
        #
        # inhibit other 3rd party loggers
        #
        logger = logging.getLogger(name)
        logger.setLevel(logging.WARNING)
        #
        # redefine the root logger
        #
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        if debug:
            formatter = logging.Formatter('%(asctime)s *%(levelname)s* %(module)s %(message)s', "%Y-%m-%d %H:%M:%S")
        else:
            formatter = logging.Formatter('%(asctime)s *%(levelname)s* %(message)s', "%Y-%m-%d %H:%M:%S")
        file_handler = RotatingFileHandler(name + '.log', 'a', 100000, 3)

        if debug:
            file_handler.setLevel(logging.DEBUG)
        else:
            file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        if verbose:
            stream_handler.setLevel(logging.INFO)
        else:
            stream_handler.setLevel(logging.WARNING)
        if debug:
            stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
