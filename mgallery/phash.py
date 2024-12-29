import logging

import cv2
import numpy

from mgallery.utils import binary_array_to_hex


logger = logging.getLogger(__name__)


def get_image_phash(image: numpy.ndarray, image_size: int = 24, hash_size: int = 6) -> str | None:
    """
    Perceptual Hash computation.

    Implementation follows https://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
    """
    try:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, (image_size, image_size))
        dct = cv2.dct(numpy.float32(numpy.asarray(image)))

        dct_low_frequency = dct[:hash_size, :hash_size]
        dct_median = numpy.median(dct_low_frequency)

        binary_array = dct_low_frequency > dct_median
        return binary_array_to_hex(binary_array.flatten(), hash_size)
    except Exception as e:
        logger.error(e)
