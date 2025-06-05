import requests

def fetch_image(url):
    """
    call's http endpoint to fetch image
    :param url:
    :return image:
    """
    response = requests.get(url)
    if response.status_code == 200:
       return response.content
    return None