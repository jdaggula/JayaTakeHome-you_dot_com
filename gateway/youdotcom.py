from constants import YOUDOTCOM_API
import requests

from utils.custom_error import InternalError


def refresh_image_metadata():
    """
    Refreshes the Image Metadata data local cache from YOUDOTCOM_API
    """
    response = requests.get(YOUDOTCOM_API)
    if response.status_code == 200:
        data = response.json()
        metadata_cache = {
            image["index"]: {
                "title": image["title"],
                "url": image["url"],
                "id": image["id"],
            }
            for image in data
        }
        return metadata_cache
    raise InternalError(message="Failed to fetch metadata from YOUDOTCOM_API")