import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path


URL = "https://www.ireland.ie/en/india/newdelhi/services/visas/processing-times-and-decisions/#visa-decisions"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/140.0.0.0 Safari/537.36"
}


def find_ods_url():

    print(f"Checking website: {URL}")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    links = soup.find_all("a")

    for link in links:

        href = link.get("href")

        if href and ".ods" in href.lower():

            ods_url = urljoin(
                URL,
                href
            )

            print(
                f"ODS found: {ods_url}"
            )

            return ods_url

    raise FileNotFoundError(
        "No ODS file found on the website."
    )


def download_ods(ods_url):

    # Get filename from URL
    filename = Path(
        urlparse(ods_url).path
    ).name

    output_dir = Path("data/raw")

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        output_dir / filename
    )

    print(
        f"Downloading: {filename}"
    )

    response = requests.get(
        ods_url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    with open(
        output_path,
        "wb"
    ) as file:

        file.write(
            response.content
        )

    print(
        f"Saved to: {output_path}"
    )

    return output_path


def main():

    ods_url = find_ods_url()

    download_ods(
        ods_url
    )


if __name__ == "__main__":
    main()