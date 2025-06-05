from controller.image import get_metadata, get_image, get_images_by_filter
from utils.custom_error import ValidationError


def get_image_metadata_api(image_index):
    """
    Handler api for get image metadata Title and URL
    :param image_index:
    :return image Title and URL:
    """
    if not image_index:
        raise ValidationError(message="Image index is Required")
    return get_metadata(image_index)

def get_image_api(image_index):
    """
    Handler api for get image by index
    :param image_index:
    :return image in base64:
    """
    if not image_index:
        raise ValidationError(message="Image index is Required")
    return get_image(image_index)

def get_images_api(filtered_parameters):
    """
    Handler api for get_images_api
    :param filtered_parameters:
    :return images in base64:
    """
    return get_images_by_filter(filtered_parameters)