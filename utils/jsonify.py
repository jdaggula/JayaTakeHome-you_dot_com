from flask import jsonify, Flask

from utils.custom_error import CustomError

app = Flask(__name__)


def you_json(args, success=True, message="", error=None, status_code=200):
    """
    Accepts a map and returns in json format
    """
    if not args:
        return jsonify({"error": "invalid request"}, 500)
    if not success:
        response = {
            "success": success,
            "message": message,
            "error": error,
        }
        return jsonify(response), status_code
    return jsonify(args), status_code


@app.errorhandler(CustomError)
def handle_custom_error(error):
    """handles custom errors"""
    return you_json(
        args=None,
        success=False,
        message=error.message,
        error={"code": error.error_code},
        status_code=error.status_code,
    )
