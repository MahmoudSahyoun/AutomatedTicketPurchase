import subprocess
from playwright.sync_api import sync_playwright, TimeoutError
import time
import random

def install_playwright_browsers():
    # Install Playwright browsers if not already installed
    subprocess.run(["playwright", "install"], check=True)

def human_like_delay(min_seconds=1, max_seconds=3):
    time.sleep(random.uniform(min_seconds, max_seconds))

def visit_page(page, url):
    print(f"Visiting URL: {url}")
    page.goto(url)
    human_like_delay()

def accept_cookies(page):
    try:
        print("Trying to accept cookies...")
        page.click("button.sc-6f7nfk-0.igqnyx.sc-6xj3kx-3.kGtrtH", timeout=5000)
        print("Cookies accepted.")
    except TimeoutError:
        print("Cookies acceptance button not found or not needed.")
    except Exception as e:
        print(f"Failed to accept cookies: {e}")

def select_ticket_location(page):
    try:
        print("Trying to select the ticket location...")
        page.click(".sc-1mafo1b-10 li.sc-1mafo1b-8", timeout=60000)
        print("Ticket location selected.")
    except TimeoutError:
        print("Ticket location selection button not found.")
    except Exception as e:
        print(f"Failed to select ticket location: {e}")

def click_continue_button(page):
    try:
        print("Trying to click the continue button...")
        page.click("text=Continue", timeout=30000)
        print("Continue button clicked.")
    except TimeoutError:
        print("Continue button not found.")
    except Exception as e:
        print(f"Failed to click continue button: {e}")

def choose_ticket(page):
    try:
        print("Trying to choose a ticket...")
        ticket_items = page.query_selector_all("#stubhub-event-detail-listings-scroll-container div[tabindex='0'].sc-1bp3ico-0")
        prices = []
        for i, ticket in enumerate(ticket_items):
            price_element = ticket.query_selector(".sc-hlalgf-0")
            if price_element:
                price_text = price_element.inner_text().replace('€', '').replace(',', '').strip()
                prices.append((i, float(price_text)))
        
        if prices:
            cheapest_index = min(prices, key=lambda x: x[1])[0]
            ticket_items[cheapest_index].click()
            print(f"Ticket at position {cheapest_index} selected.")
    except TimeoutError:
        print("Ticket items not found.")
    except Exception as e:
        print(f"Failed to choose a ticket: {e}")

def click_select_button(page):
    try:
        print("Trying to click the select button...")
        page.click("a[title='Select'] button", timeout=60000)
        print("Select button clicked.")
    except TimeoutError:
        print("Select button not found.")
    except Exception as e:
        print(f"Failed to click the select button: {e}")

def click_google_sign_in_button(page):
    try:
        print("Trying to click the Google sign-in button...")
        page.click(".sc-1gpzx7h-2", timeout=30000)
        print("Google sign-in button clicked.")
    except TimeoutError:
        print("Google sign-in button not found.")
    except Exception as e:
        print(f"Failed to click Google sign-in button: {e}")

def enter_email_address(page, email):
    try:
        print("Trying to enter the email address...")
        page.fill(".Xb9hP input", email, timeout=30000)
        print("Email address entered.")
    except TimeoutError:
        print("Email input box not found.")
    except Exception as e:
        print(f"Failed to enter the email address: {e}")

def click_next_button(page):
    try:
        print("Trying to click the next button...")
        page.click("button.VfPpkd-LgbsSe.AjY5Oe", timeout=30000)
        print("Next button clicked.")
    except TimeoutError:
        print("Next button not found.")
    except Exception as e:
        print(f"Failed to click the next button: {e}")

def main():
    # Ensure Playwright browsers are installed
    install_playwright_browsers()

    artist_urls = ["https://www.viagogo.de/Konzert-Tickets/Rap-und-Hip-Hop/Travis-Scott-Karten"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        for url in artist_urls:
            page = context.new_page()
            visit_page(page, url)
            accept_cookies(page)
            select_ticket_location(page)
            click_continue_button(page)
            choose_ticket(page)
            click_select_button(page)
            click_google_sign_in_button(page)
            enter_email_address(page, "mahmoudsohyon123216@gmail.com")
            click_next_button(page)
            print("Keeping the browser open for 10 minutes...")
            time.sleep(600)
        
        browser.close()
        print("Browser closed successfully.")

if __name__ == "__main__":
    main()
