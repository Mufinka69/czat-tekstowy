import logging

def setup_logger():

    if logger.hasHandlers():
        return

    logger = logging.getLogger()

    file_handler.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler("log.log", mode = "w")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    console_handler.setLevel(logging.INFO) 
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)