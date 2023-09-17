from time import sleep

from loguru import logger

from shortame.config import settings
from shortame.services.key_generation_services import ShortUrlGenerator

if __name__ == "__main__":
    logger.add(sink="key_generator.log")
    logger.info("Executing the Key Generator service")
    keygen = ShortUrlGenerator()
    minimum_size = settings.short_url_minimum_queue_size
    while True:
        logger.info("Comparing the current queue size with the minimum size")
        if keygen.queue.current_size() <= minimum_size:
            logger.info(f"Queue size is less than {minimum_size}")
            keygen.generate_and_enque()
        else:
            logger.info("Queue size is greather than minimum size")
            logger.info("Sleeping for 5 seconds")
            sleep(5)
