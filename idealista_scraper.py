import json
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import time
from random import randint
import os
import sys
import csv
import argparse
from page_fetcher import fetch_page

EXPRESSIONS_FILE = Path(__file__).parent / "filtering_descriptions_expressions.json"
with open(EXPRESSIONS_FILE, encoding="utf-8") as f:
    config = json.load(f)

GASTOS_KEYWORDS = config.get("expressions", [])


def create_csv(data, csv_filename):
    """
    Creates a CSV file from the input data.

    Args:
        data (list): A list of dictionaries containing the data to be written to the CSV file.
        csv_filename (str): The name of the CSV file to create.
    """
    if not data:
        print("The input data is empty.")
        return
    fields = data[0].keys()
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, csv_filename)
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in data:
                row["Localidad"] = row["Localidad"].strip()
                writer.writerow(row)
        print(f"CSV file '{csv_path}' has been created successfully!")
    except Exception as e:
        print(f"An error occurred while writing the CSV file: {e}")


def parse_html(html, div_class):
    """
    Parses the HTML content and returns a list of divs with the specified class.

    Args:
        html (str): The HTML content to parse.
        div_class (str): The class of the divs to extract.
    Returns:
        list: A list of divs with the specified class.
    """
    soup = BeautifulSoup(html, "html.parser")
    divs = soup.find_all("div", class_=div_class)
    return divs


def extract_html_content(divs):
    """
    Extracts the content of a div from a page.

    Args:
        divs (list): A list of divs to extract the content from.

    Returns:
        list: A list of dictionaries containing the extracted content.
    """
    content = []
    for div in divs:
        try:
            chars = div.find("div", class_="item-detail-char").find_all(
                "span", class_="item-detail"
            )
            rooms = chars[0].get_text()
            price = div.find("span", class_="item-price h2-simulated").get_text()
            address = "".join(
                div.find("a", class_="item-link")
                .get_text()
                .replace("\n", "")
                .split(",")[:2]
            ).strip()
            href = div.find("a", class_="item-link")["href"]
            link = f"https://www.idealista.com{href}"
            expenses = "✅" if extract_offer_description_data(link) else "❌"

            content.append(
                {
                    "Precio": price,
                    "Gastos incluidos": expenses,
                    "Localidad": address,
                    "Habitaciones": rooms,
                    "Link": link,
                }
            )
        except Exception as e:
            print(f"Error extracting div: {e}")
            continue
    return content


def extract_offer_description_data(link):
    """
    Extracts the offer description data from a link.

    Args:
        link (str): The link to extract the offer description data from.

    Returns:
        bool: True if the offer description data is found, False otherwise.
    """
    html = fetch_page(link)
    if not html:
        return False
    soup = BeautifulSoup(html, "html.parser")
    for comment in soup.find_all("div", class_="comment"):
        for p in comment.find_all("p"):
            text_norm = (
                p.get_text().lower().translate(str.maketrans("áéíóúüñç", "aeiouunç"))
            )
            if any(k in text_norm for k in GASTOS_KEYWORDS):
                return True
    return False


def get_div_content(url, div_class):
    """
    Retrieves the content of a div from a page.

    Args:
        url (str): The URL of the page to fetch.
        div_class (str): The class of the div to extract.

    Returns:
        list: A list of dictionaries containing the extracted content.
    """
    html = fetch_page(url)
    if not html:
        print("Fetching failed. Trying local cache…")
        html = load_page_from_file(url)
        if not html:
            print("No cache found.")
            return []
    save_page_locally(url, html)
    divs = parse_html(html, div_class)
    return extract_html_content(divs)


def sleep_randomly(min_delay, max_delay):
    """
    Sleeps for a random amount of time between min_delay and max_delay seconds.

    Args:
        min_delay (int): The minimum delay in seconds.
        max_delay (int): The maximum delay in seconds.
    """
    time.sleep(randint(min_delay, max_delay))


def save_page_locally(url, html):
    """
    Saves a page to the local cache.

    Args:
        url (str): The URL of the page to save.
        html (str): The HTML content of the page.
    """
    os.makedirs("./cached_pages", exist_ok=True)
    filename = (
        "./cached_pages/"
        + url.replace("https://", "").replace("http://", "").replace("/", "_")
        + ".html"
    )
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Page saved locally as {filename}")


def load_page_from_file(url):
    """
    Loads a page from the local cache.

    Args:
        url (str): The URL of the page to load.

    Returns:
        str: The HTML content of the page, or None if the file does not exist.
    """
    filename = (
        url.replace("https://", "").replace("http://", "").replace("/", "_") + ".html"
    )
    path = os.path.join("./cached_pages", filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def adapt_url(base_url, page_number):
    """
    Inserts or replaces 'pagina-{n}.htm' in the path of base_url.

    Args:
        base_url (str): The base URL to adapt.
        page_number (int): The page number to insert or replace.

    Returns:
        str: The adapted URL.
    """
    parsed = urlparse(base_url)
    path = parsed.path.rstrip("/")
    parts = path.split("/") if path else []
    parts = [p for p in parts if not p.startswith("pagina-")]
    parts.append(f"pagina-{page_number}.htm")
    new_path = "/".join(parts)
    new_url = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            new_path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )
    return new_url


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="idealista_scraper.py",
        description="Idealista room scraper: specify URL, page range, and delay",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-u", "--url", help="Base Idealista URL with filters (without 'pagina-X')"
    )
    parser.add_argument(
        "-p",
        "--pages",
        nargs=2,
        type=int,
        required=True,
        metavar=("START", "END"),
        help="Page range to scrape, specify start and end as two integers, e.g. '1 5'",
    )
    parser.add_argument(
        "-d",
        "--delay",
        nargs=2,
        type=int,
        default=[2, 20],
        metavar=("MIN", "MAX"),
        help="Random sleep range in seconds, specify min and max as two integers, e.g. '2 20'",
    )
    parser.add_argument(
        "-o", "--output", default="results.csv", help="Output CSV filename"
    )
    args = parser.parse_args()

    try:
        start_page, end_page = args.pages
        if start_page > end_page:
            raise ValueError
    except Exception:
        parser.error("--pages must be two integers with start <= end")
    try:
        min_delay, max_delay = args.delay
        if min_delay > max_delay:
            raise ValueError
    except Exception:
        parser.error("--delay must be two integers with min <= max")

    results = []
    try:
        for i in range(start_page, end_page + 1):
            page_url = adapt_url(args.url, i)
            print("Scraping", page_url)
            data = get_div_content(page_url, "item-info-container")
            results.extend(data)
            sleep_randomly(min_delay, max_delay)
    except KeyboardInterrupt:
        print("Keyboard interrupt. Saving results to CSV…")
        create_csv(results, args.output)
        sys.exit(0)

    create_csv(results, args.output)
