from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options


def fetch_page(url):
    options = Options()
    options.binary_location = "/usr/bin/firefox-esr"

    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(executable_path="/usr/local/bin/geckodriver")

    try:
        driver = webdriver.Firefox(service=service, options=options)

        driver.get(url)
        page_source = driver.page_source
        return page_source

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

    finally:
        if "driver" in locals():
            driver.quit()
