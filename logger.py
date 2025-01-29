import colorlog
import logging
from colorama import init, Fore
import random

FORMAT = "|%(asctime)s| - %(name)s - %(levelname)s - %(message)s"


def setup_gay_logger(logger_name=None, rainbow=True):
    init()

    def rainbow_colorize(text):
        colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
        start_index = random.randint(0, len(colors) - 1)
        colored_message = ''
        for index, char in enumerate(text):
            color = colors[(start_index + index) % len(colors)]
            colored_message += color + char
        return colored_message

    class RainbowColoredFormatter(colorlog.ColoredFormatter):
        def format(self, record):
            message = super().format(record)
            if rainbow:
                return rainbow_colorize(message)
            return message

    logger = colorlog.getLogger(logger_name if logger_name else 'root')
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        RainbowColoredFormatter(
            FORMAT,
            datefmt="%Y-%m-%d %H:%M:%S",  # Setting date format
            reset=False,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger
