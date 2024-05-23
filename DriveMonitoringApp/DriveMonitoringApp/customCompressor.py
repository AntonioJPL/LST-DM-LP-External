import logging
from django.middleware.gzip import GZipMiddleware

logger = logging.getLogger(__name__)

class CustomGZipMiddleware(GZipMiddleware):
    def process_response(self, request, response):
        logger.debug(f"Response Content-Type: {response['Content-Type']}")
        logger.debug(f"Response Size: {len(response.content)} bytes")
        response = super().process_response(request, response)
        if response.has_header('Content-Encoding'):
            logger.debug(f"Compressed response with {response['Content-Encoding']}")
        else:
            logger.debug("Response was not compressed")
        return response