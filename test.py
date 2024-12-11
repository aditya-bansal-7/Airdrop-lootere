from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_with_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = "https://debank.com/profile/0xea7d5a968d1e870ec89558e544553b112b76f88f"
        page.goto(url)
        page.wait_for_timeout(5000)  # Wait 5 seconds for dynamic content

        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        print(soup.prettify())

        browser.close()

scrape_with_playwright()
