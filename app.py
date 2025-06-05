from flask import Flask, jsonify, request

from handler.image_http import get_image_metadata_api, get_image_api, get_images_api

app = Flask(__name__)


@app.route("/")
def root():
    """
    Root endpoint to check server health
    """
    return jsonify({"msg": "Server Running"}, 200)


@app.route("/metadata/<int:image_index>", methods=["GET"])
def get_image_metadata(image_index):
    """
    Returns title, URL for the provided image index
    """
    return get_image_metadata_api(image_index)


@app.route("/image/<int:image_index>", methods=["GET"])
def get_image(image_index):
    """
    Returns image in base64 for the provided image index
    """
    return get_image_api(image_index)


@app.route("/images", methods=["GET"])
def get_images():
    """
    Returns images in base64 for the provided filter from the metadata
    """
    filter_param = request.args.get("filter")
    if not filter_param:
        return get_images_api(None)
    return get_images_api(filter_param)


if __name__ == "__main__":
    app.run(debug=True)
