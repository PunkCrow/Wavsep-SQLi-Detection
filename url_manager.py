import random
import requests
import validators


def get_random_url(filename):
    try:
        with open(filename, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]  # Ensure no empty lines
        return random.choice(urls) if urls else None
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
        return None
    except IOError as e:
        print(f"An error occurred while reading the file: {e}")
        return None


def check_url_reachability(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return True
    except requests.RequestException as e:
        print(f"Failed to reach {url}.")


def is_valid_url(url):
    # use simple_host = True to validate localhost
    return validators.url(url, simple_host=True)
