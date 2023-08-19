


import requests
import urllib.error
import urllib.request


from bs4 import BeautifulSoup


def get_files_at_url(url: str, parse_for: str = "a"):
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    all_records = [f"{url}/{node.get('href')}" for node in soup.find_all(parse_for)]

    return all_records


def retrieve_url_file(url: str, destination: str):
    try:
        urllib.request.urlretrieve(url, destination)
    except urllib.error.HTTPError:
        print(f"Could not retrieve {url}.")
        pass