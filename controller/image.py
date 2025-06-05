import base64
import os.path

from constants import IMAGE_FOLDER, USE_DATABASE
from controller.cache import image_metadata_cache, image_cache
from gateway.images import fetch_image
from gateway.youdotcom import refresh_image_metadata
from repository.images import get_image_metadata_by_index, get_all_images_metadata, upsert_image_metadata
from utils.custom_error import NotFoundError, ValidationError, InternalError
from utils.jsonify import you_json


def get_metadata(image_index):
    """
    Controller method to refresh image metadata and return image url and title
    Depending on the USE_DATABASE it either uses hashmap vs database
    :param image_index:
    :return url and title:
    """
    if USE_DATABASE:
        metadata = get_image_metadata_by_index(image_index)
    else:
        metadata = image_metadata_cache.get(image_index)

    if metadata:
        return you_json(args={"title": metadata["title"], "url": metadata["url"]})

    if not USE_DATABASE:
        metadata = image_metadata_cache.get(image_index)

    if metadata:
        return you_json(args={"title": metadata["title"], "url": metadata["url"]})

    refresh_cache()
    if USE_DATABASE:
        metadata = get_image_metadata_by_index(image_index)
    else:
        metadata = image_metadata_cache.get(image_index)

    if metadata:
        return you_json(args={"title": metadata["title"], "url": metadata["url"]})

    if not USE_DATABASE:
        metadata = image_metadata_cache.get(image_index)

    if metadata:
        return you_json(args={"title": metadata["title"], "url": metadata["url"]})

    raise NotFoundError(message=f"Image with Index {image_index} not found")

def get_images():
    """
    fetch all images in base64
    Depending on the USE_DATABASE it either uses hashmap vs database
    :return images in base64 and image index:
    """
    images = {}

    if USE_DATABASE:
        images_metadata = get_all_images_metadata()
        for metadata in images_metadata:
            index = metadata["image_index"]
            file_path = metadata["file_path"]
            images[index] = encode_image_to_base64(file_path)
    else:
        for image_index in image_cache:
            images[image_index] = _get_image(image_index)

    return you_json(args=images)


def get_images_by_filter(filtered_parameters):
    """
    fetch images based on filter parameters in the image metadata
    :param filtered_parameters:
    :return images in base64 and index:
    """
    if not filtered_parameters:
        # No filters specified, fetch all images.
        return get_images()

    if USE_DATABASE:
        # Fetch metadata from the database.
        images_metadata = get_all_images_metadata()

        if not images_metadata:
            # No metadata found in the database.
            raise NotFoundError(message="No images found in the database.")

        # Validate the filter parameter.
        if filtered_parameters not in images_metadata[0]:
            raise ValidationError(
                message=f"Request with filter parameter '{filtered_parameters}' is invalid."
            )

        # Apply filtering and remove duplicates based on the parameter.
        exists = set()
        filtered_images = {}
        for metadata in images_metadata:
            property_value = metadata.get(filtered_parameters)
            if property_value not in exists:
                exists.add(property_value)
                filtered_images[metadata["image_index"]] = encode_image_to_base64(metadata["file_path"])

        return you_json(args=filtered_images)

    # In-memory cache path.
    refresh_cache()  # Ensure cache is up-to-date.

    if filtered_parameters not in next(iter(image_metadata_cache.values()), {}):
        raise ValidationError(
            message=f"Request with filter parameter '{filtered_parameters}' is invalid."
        )

    # Apply filtering and remove duplicates from in-memory metadata cache.
    exists = set()
    filtered_images = {}
    for index, metadata in image_metadata_cache.items():
        property_value = metadata.get(filtered_parameters)
        if property_value not in exists:
            exists.add(property_value)
            filtered_images[index] = _get_image(index)

    return you_json(args=filtered_images)

def fetch_and_save_image(url, filepath):
    """
    Internal method to fetch and save the image locally in file system.
    Can be extended to store image in a location(s3) and metadata in local rdbms
    :param url:
    :param filepath:
    :return:
    """
    image = fetch_image(url)
    if image:
        with open(filepath, "wb") as file:
            file.write(image)
            return filepath
    raise InternalError(message="unable to save file in local store")


def get_image(image_index):
    """
    fetched image by refreshing the cache if image doesnot exists in cache.
    if no image found for the index then return none
    :param image_index:
    :return index and image in base64:
    """
    return you_json(
        args={"index": image_index, "image": _get_image(image_index)},
    )


def _get_image(image_index):
    local_image_path = ""
    # If using the database, fetch data directly
    if USE_DATABASE:
        # Try fetching metadata from the database
        metadata = get_image_metadata_by_index(image_index)
        if metadata:
            local_image_path = metadata["file_path"]
            # Ensure the file exists on disk
            if os.path.exists(local_image_path):
                return encode_image_to_base64(local_image_path)

        # If not found or file is missing, refresh cache and retry
        refresh_cache()
        metadata = get_image_metadata_by_index(image_index)
        if metadata:
            local_image_path = metadata["file_path"]
            if os.path.exists(local_image_path):
                return encode_image_to_base64(local_image_path)

    # If not using the database, fall back to in-memory cache
    else:
        if not check_image_in_metadata(image_index) or not check_image_cache(image_index):
            refresh_cache()
        if not check_image_in_metadata(image_index):
            raise NotFoundError(message=f"Image with index {image_index} not found")
        local_image_path = image_cache[image_index]

    # Encode the image to base64
    return encode_image_to_base64(local_image_path)


def refresh_cache():
    """
    internal method to refresh the metadata cache and image cache
    :return:
    """
    # Fetch metadata from the external API
    metadata_cache = refresh_image_metadata()

    # Iterate through the fetched metadata
    for image_index, metadata in metadata_cache.items():
        title = metadata["title"]
        url = metadata["url"]
        id_ = metadata["id"]

        # Determine the image's local file path
        image_path = os.path.join(IMAGE_FOLDER, f"{image_index}.jpg")

        try:
            # Fetch and save the image locally
            local_image_path = fetch_and_save_image(url, image_path)

            if USE_DATABASE:
                # Upsert the metadata and image path into the database
                upsert_image_metadata(
                    image_index=image_index,
                    title=title,
                    url=url,
                    file_path=local_image_path,
                )
            else:
                # Update in-memory caches
                image_cache[image_index] = local_image_path
                image_metadata_cache[image_index] = {
                    "title": title,
                    "url": url,
                    "id": id_,
                }

        except InternalError as e:
            # Log or handle errors when saving images
            print(f"Failed to save image for index {image_index}: {e}")

    # When `USE_DATABASE` is enabled, skip modifying `image_metadata_cache`.
    # TODO this can be always available
    if not USE_DATABASE:
        image_metadata_cache.update(metadata_cache)


def check_image_in_metadata(image_index):
    """
    internal method to check image metadata in local hash map.
    can be extended to check local Database
    :param image_index:
    :return boolean:
    """
    return image_index in image_metadata_cache


def check_image_cache(image_index):
    """
    internal method to check if image in local image store.
    :param image_index:
    :return boolean:
    """
    return image_index in image_cache


def encode_image_to_base64(image_path):
    """
    internal method fro encoding the image to base64
    :param image_path:
    :return base64:
    """
    with open(image_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")
