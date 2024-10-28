from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service



def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())  # Use ChromeDriverManager in Service
    driver = webdriver.Chrome(service=service, options=options)  # Pass 'service' and 'options' correctly
    return driver


def wait_for_page_load(driver, timeout=60):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Page loaded successfully.")
    except TimeoutException:
        print("Page load timed out.")

def visit_page(driver, url):
    try:
        print(f"Visiting URL: {url}")
        driver.get(url)
        wait_for_page_load(driver)
    except Exception as e:
        print(f"Exception occurred while visiting URL: {url} - {e}")

def accept_cookies(driver):
    try:
        print("Trying to accept cookies...")
        accept_cookies_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[p[text()='Allow All']]"))
        )
        accept_cookies_button.click()
        print("Cookies accepted.")
    except (NoSuchElementException, TimeoutException):
        print("No cookies acceptance needed or failed.")

def select_ticket_location(driver, option_index=0, retries=3):
    while retries > 0:
        try:
            print("Trying to select the ticket location...")
            ticket_options_container = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sc-1mafo1b-10"))
            )
            print("Ticket options container found.")
            
            # Save the container's HTML for debugging
            with open('ticket_options_container.html', 'w', encoding='utf-8') as f:
                f.write(ticket_options_container.get_attribute('outerHTML'))
            print("Container HTML saved.")
            
            # Using a refined XPath to find ticket options
            ticket_options = ticket_options_container.find_elements(By.XPATH, ".//li[contains(@class, 'sc-1mafo1b-8')]")
            print(f"Found {len(ticket_options)} ticket options.")
            
            if ticket_options:
                if option_index < len(ticket_options):
                    selected_option = ticket_options[option_index]
                else:
                    selected_option = ticket_options[0]
                    print(f"Provided index {option_index} is out of range. Selecting the first option.")
                
                print("Selected option found, attempting to click.")
                driver.execute_script("arguments[0].scrollIntoView(true);", selected_option)
                time.sleep(1)  # Give time for scroll
                selected_option.click()
                print("Ticket location selected.")
                return
            else:
                print("No ticket options found.")
        except TimeoutException:
            print("Timed out waiting for the ticket options to become clickable.")
        except WebDriverException as e:
            print(f"WebDriverException: {e}")
        except Exception as e:
            print(f"Exception: {e}")
        retries -= 1
        print(f"Retrying... ({retries} retries left)")
        time.sleep(2)  # Wait before retrying
    
    driver.save_screenshot('ticket_location_error.png')
    with open('ticket_location_error.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print("Page source saved for debugging.")

def switch_to_new_tab(driver, expected_tabs=2):
    try:
        print(f"Switching to the new tab... (expecting {expected_tabs} tabs)")
        WebDriverWait(driver, 30).until(EC.number_of_windows_to_be(expected_tabs))
        driver.switch_to.window(driver.window_handles[-1])  # Switch to the latest tab
        wait_for_page_load(driver)
        time.sleep(5)  # Adding a delay to ensure the new tab is fully loaded
        print("Switched to the new tab.")
    except TimeoutException:
        print("Timed out waiting for the new tab to appear.")
        driver.save_screenshot('switch_to_new_tab_timeout.png')
        with open('switch_to_new_tab_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to switch to the new tab: {e}")
        driver.save_screenshot('switch_to_new_tab_error.png')
        with open('switch_to_new_tab_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)


def click_continue_button(driver):
    try:
        print("Trying to click the continue button...")
        wait_for_page_load(driver)

        continue_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sc-6f7nfk-0 igqnyx') and contains(text(), 'Continue')]"))
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", continue_button)
        driver.execute_script("arguments[0].click();", continue_button)
        print("Continue button clicked.")

    except TimeoutException:
        print("Timed out waiting for the continue button to become clickable.")
        driver.save_screenshot('continue_button_timeout.png')
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to click the continue button: {e}")
        driver.save_screenshot('screenshot.png')
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def choose_ticket(driver, ticket_position=0):
    try:
        print("Trying to choose a ticket...")
        retry_attempts = 3
        while retry_attempts > 0:
            try:
                tickets_container = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.ID, "stubhub-event-detail-listings-scroll-container"))
                )
                print("Tickets container found.")
                
                # Find ticket items using a more specific selector
                ticket_items = tickets_container.find_elements(By.XPATH, "//div[@tabindex='0' and contains(@class, 'sc-1bp3ico-0')]")
                if not ticket_items:
                    print("No ticket items found.")
                    return

                print(f"Found {len(ticket_items)} ticket items.")

                prices = []
                for i, ticket in enumerate(ticket_items):
                    try:
                        # More precise XPath to find the price
                        price_element = ticket.find_element(By.XPATH, ".//div[contains(@class, 'sc-hlalgf-0') and contains(text(), '€')]")
                        price_text = price_element.text.replace('€', '').replace(',', '').strip()
                        price = float(price_text)
                        prices.append(price)
                        print(f"Ticket {i}: Price found - {price}")
                    except NoSuchElementException:
                        print(f"Ticket {i}: Price element not found.")
                    except ValueError:
                        print(f"Ticket {i}: Could not convert price to float. Raw text: {price_text}")

                if not prices:
                    print("No prices found in ticket items.")
                    return

                cheapest_index = prices.index(min(prices))
                chosen_index = ticket_position if ticket_position < len(ticket_items) else cheapest_index

                # Refetch the ticket items to avoid stale element reference
                ticket_items = tickets_container.find_elements(By.XPATH, "//div[@tabindex='0' and contains(@class, 'sc-1bp3ico-0')]")
                selected_ticket = ticket_items[chosen_index]
                
                driver.execute_script("arguments[0].scrollIntoView(true);", selected_ticket)
                selected_ticket.click()
                print(f"Ticket at position {chosen_index} selected.")
                
                # Wait for 1 second and save the HTML of the page
                time.sleep(1)
                save_ticket_location_html(driver)
                break
            except StaleElementReferenceException:
                print("Stale element reference exception caught. Refetching the elements and retrying...")
                retry_attempts -= 1
                time.sleep(2)  # Adding a small delay before retrying
            except TimeoutException:
                print("Timed out waiting for ticket options.")
                break
            except Exception as e:
                print(f"Failed to choose a ticket: {e}")
                driver.save_screenshot('choose_ticket_error.png')
                print(driver.page_source)
                break

    except Exception as e:
        print(f"Exception in choose_ticket: {e}")

def save_ticket_location_html(driver):
    try:
        print("Saving ticket location HTML...")
        with open('ticketlocationoptions.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Ticket location options HTML saved to 'ticketlocationoptions.html'.")
    except Exception as e:
        print(f"Failed to save ticket location HTML: {e}")
        driver.save_screenshot('ticket_location_html_error.png')
        with open('ticket_location_html_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def select_ticket_location(driver, option_index=0, retries=3):
    while retries > 0:
        try:
            print("Trying to select the ticket location...")
            ticket_options_container = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sc-1mafo1b-10"))
            )
            print("Ticket options container found.")
            
            # Save the container's HTML for debugging
            with open('ticket_options_container.html', 'w', encoding='utf-8') as f:
                f.write(ticket_options_container.get_attribute('outerHTML'))
            print("Container HTML saved.")
            
            # Using a refined XPath to find ticket options
            ticket_options = ticket_options_container.find_elements(By.XPATH, ".//li[contains(@class, 'sc-1mafo1b-8')]")
            print(f"Found {len(ticket_options)} ticket options.")
            
            if ticket_options:
                if option_index < len(ticket_options):
                    selected_option = ticket_options[option_index]
                else:
                    selected_option = ticket_options[0]
                    print(f"Provided index {option_index} is out of range. Selecting the first option.")
                
                print("Selected option found, attempting to click.")
                driver.execute_script("arguments[0].scrollIntoView(true);", selected_option)
                time.sleep(1)  # Give time for scroll
                selected_option.click()
                print("Ticket location selected.")
                return
            else:
                print("No ticket options found. Attempting to find links directly.")

                # Attempting to find <a> tags directly as a fallback
                ticket_links = ticket_options_container.find_elements(By.XPATH, ".//a[contains(@class, 'feTKXE')]")
                print(f"Found {len(ticket_links)} ticket links directly.")
                
                if ticket_links:
                    if option_index < len(ticket_links):
                        selected_link = ticket_links[option_index]
                    else:
                        selected_link = ticket_links[0]
                        print(f"Provided index {option_index} is out of range. Selecting the first link.")
                    
                    print("Selected link found, attempting to click.")
                    driver.execute_script("arguments[0].scrollIntoView(true);", selected_link)
                    time.sleep(1)  # Give time for scroll
                    selected_link.click()
                    print("Ticket location selected via direct link.")
                    return
                else:
                    print("No ticket links found.")
                    
        except StaleElementReferenceException:
            print("Stale element reference exception caught. Refetching the elements and retrying...")
        except TimeoutException:
            print("Timed out waiting for the ticket options to become clickable.")
        except WebDriverException as e:
            print(f"WebDriverException: {e}")
        except Exception as e:
            print(f"Exception: {e}")
        
        retries -= 1
        print(f"Retrying... ({retries} retries left)")
        time.sleep(2)  # Wait before retrying
    
    driver.save_screenshot('ticket_location_error.png')
    with open('ticket_location_error.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print("Page source saved for debugging.")



def click_select_button(driver):
    try:
        print("Trying to click the 'Select' button...")
        
        # Wait until the 'Select' button is clickable
        select_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@title='Select']/button"))
        )
        
        print("Select button found.")
        driver.execute_script("arguments[0].scrollIntoView(true);", select_button)
        time.sleep(1)  # Give time for scroll
        
        # Click the 'Select' button
        select_button.click()
        print("'Select' button clicked.")
        
    except TimeoutException:
        print("Timed out waiting for the 'Select' button.")
        driver.save_screenshot('select_button_timeout.png')
        with open('select_button_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to click the 'Select' button: {e}")
        driver.save_screenshot('select_button_error.png')
        with open('select_button_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def wait_and_click_start_button(driver, wait_time=20):
    try:
        print(f"Waiting for {wait_time} seconds before clicking the 'Start' button...")
        time.sleep(wait_time)  # Wait for the specified time

        print("Looking for the 'Start' button...")

        # Use a more precise locator strategy to find the 'Start' button
        start_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sc-6f7nfk-0 boCQCS')]//div[contains(@class, 'sc-1nhsy7a-6 cHcTWl') and text()='Start']"))
        )

        print("'Start' button found. Attempting to click...")
        driver.execute_script("arguments[0].scrollIntoView(true);", start_button)
        time.sleep(1)  # Give time for scroll
        start_button.click()
        print("'Start' button clicked.")

    except TimeoutException:
        print("Timed out waiting for the 'Start' button.")
        driver.save_screenshot('start_button_timeout.png')
        with open('start_button_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to click the 'Start' button: {e}")
        driver.save_screenshot('start_button_error.png')
        with open('start_button_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def click_continue_2(driver):
    try:
        print("Trying to click the second 'Continue' button...")

        # Use the precise locator strategy to find the second 'Continue' button
        continue_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sc-6f7nfk-0 boCQCS') and text()='Continue']"))
        )

        print("Second 'Continue' button found. Attempting to click...")
        driver.execute_script("arguments[0].scrollIntoView(true);", continue_button)
        time.sleep(1)  # Give time for scroll
        continue_button.click()
        print("Second 'Continue' button clicked.")

    except TimeoutException:
        print("Timed out waiting for the second 'Continue' button.")
        driver.save_screenshot('continue_button_2_timeout.png')
        with open('continue_button_2_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to click the second 'Continue' button: {e}")
        driver.save_screenshot('continue_button_2_error.png')
        with open('continue_button_2_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
def enter_email_address(driver, email):
    try:
        print("Trying to enter the email address...")

        # Wait until the email input box is present and then enter the email
        email_input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
        )
        
        print("Email input box found.")
        email_input_box.clear()  # Clear any pre-filled text
        email_input_box.send_keys(email)
        print("Email address entered.")
        
    except TimeoutException:
        print("Timed out waiting for the email input box.")
        driver.save_screenshot('email_input_box_timeout.png')
        with open('email_input_box_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except NoSuchElementException:
        print("Email input box not found.")
        driver.save_screenshot('email_input_box_not_found.png')
        with open('email_input_box_not_found.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to enter the email address: {e}")
        driver.save_screenshot('email_input_box_error.png')
        with open('email_input_box_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def click_continue_as_guest_button(driver):
    try:
        print("Trying to click the 'Continue as a Guest' button...")

        # Wait until the 'Continue as a Guest' button is clickable
        continue_as_guest_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sc-6f7nfk-0 hzAJOO')]"))
        )

        print("'Continue as a Guest' button found.")
        driver.execute_script("arguments[0].scrollIntoView(true);", continue_as_guest_button)
        time.sleep(1)  # Give time for scroll
        continue_as_guest_button.click()
        print("'Continue as a Guest' button clicked.")



        #save html
        time.sleep(5)  # Wait for the new content to load
        with open('post_continue_as_guest.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("HTML saved after clicking 'Continue as a Guest'.")

    except TimeoutException:
        print("Timed out waiting for the 'Continue as a Guest' button.")
        driver.save_screenshot('continue_as_guest_button_timeout.png')
        with open('continue_as_guest_button_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to click the 'Continue as a Guest' button: {e}")
        driver.save_screenshot('continue_as_guest_button_error.png')
        with open('continue_as_guest_button_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def enter_first_name(driver, first_name):
    try:
        print("Trying to enter the first name...")

        # Wait until the first name input box is present and then enter the first name
        first_name_input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='firstName']"))
        )
        
        print("First name input box found.")
        first_name_input_box.clear()  # Clear any pre-filled text
        first_name_input_box.send_keys(first_name)
        print("First name entered.")
        
    except TimeoutException:
        print("Timed out waiting for the first name input box.")
        driver.save_screenshot('first_name_input_box_timeout.png')
        with open('first_name_input_box_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except NoSuchElementException:
        print("First name input box not found.")
        driver.save_screenshot('first_name_input_box_not_found.png')
        with open('first_name_input_box_not_found.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to enter the first name: {e}")
        driver.save_screenshot('first_name_input_box_error.png')
        with open('first_name_input_box_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def enter_last_name(driver, last_name):
    try:
        print("Trying to enter the last name...")

        # Wait until the last name input box is present and then enter the last name
        last_name_input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='lastName']"))
        )
        
        print("Last name input box found.")
        last_name_input_box.clear()  # Clear any pre-filled text
        last_name_input_box.send_keys(last_name)
        print("Last name entered.")
        
    except TimeoutException:
        print("Timed out waiting for the last name input box.")
        driver.save_screenshot('last_name_input_box_timeout.png')
        with open('last_name_input_box_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except NoSuchElementException:
        print("Last name input box not found.")
        driver.save_screenshot('last_name_input_box_not_found.png')
        with open('last_name_input_box_not_found.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to enter the last name: {e}")
        driver.save_screenshot('last_name_input_box_error.png')
        with open('last_name_input_box_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def enter_phone_number(driver, phone_number):
    try:
        print("Trying to enter the phone number...")

        # Wait until the phone number input box is present and then enter the phone number
        phone_number_input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='phoneNumber.phoneNumber']"))
        )
        
        print("Phone number input box found.")
        phone_number_input_box.clear()  # Clear any pre-filled text
        phone_number_input_box.send_keys(phone_number)
        print("Phone number entered.")
        
    except TimeoutException:
        print("Timed out waiting for the phone number input box.")
        driver.save_screenshot('phone_number_input_box_timeout.png')
        with open('phone_number_input_box_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except NoSuchElementException:
        print("Phone number input box not found.")
        driver.save_screenshot('phone_number_input_box_not_found.png')
        with open('phone_number_input_box_not_found.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to enter the phone number: {e}")
        driver.save_screenshot('phone_number_input_box_error.png')
        with open('phone_number_input_box_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def click_yes_button(driver):
    try:
        print("Trying to click the 'Yes' button...")

        # Wait until the 'Yes' button is clickable
        yes_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sc-6f7nfk-0 boCQCS') and contains(text(), 'Yes')]"))
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", yes_button)
        time.sleep(1)  # Give time for scroll

        # Click the 'Yes' button
        yes_button.click()
        print("'Yes' button clicked.")

    except TimeoutException:
        print("Timed out waiting for the 'Yes' button.")
        driver.save_screenshot('yes_button_timeout.png')
        with open('yes_button_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to click the 'Yes' button: {e}")
        driver.save_screenshot('yes_button_error.png')
        with open('yes_button_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)


def choose_payment_method(driver):
    try:
        print("Trying to click the 'Choose Payment Method' button...")
        payment_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "sc-a1zmw8-0 bKxUzC"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", payment_button)
        time.sleep(1)  # Give time for scroll
        payment_button.click()
        print("'Choose Payment Method' button clicked.")
    except TimeoutException:
        print("Timed out waiting for the 'Choose Payment Method' button.")
        driver.save_screenshot('choose_payment_method_timeout.png')
        with open('choose_payment_method_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to click the 'Choose Payment Method' button: {e}")
        driver.save_screenshot('choose_payment_method_error.png')
        with open('choose_payment_method_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def save_personal_details(driver):
    try:
        time.sleep(2)  # Wait 2 seconds before saving the HTML
        print("Saving personal details HTML...")
        with open('personal_details.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Personal details HTML saved to 'personal_details.html'.")
    except Exception as e:
        print(f"Failed to save personal details HTML: {e}")
        driver.save_screenshot('save_personal_details_error.png')
        with open('save_personal_details_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)



def enter_address_line1(driver, address="prager st 53 leipzig room 366"):
    try:
        print("Trying to enter the address line 1...")
        
        # Wait until the address line 1 input box is present
        address_input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='address.addressLine1']"))
        )
        
        print("Address line 1 input box found.")
        address_input_box.clear()  # Clear any pre-filled text
        address_input_box.send_keys(address)  # Enter the address line 1
        print("Address line 1 entered.")
        
    except TimeoutException:
        print("Timed out waiting for the address line 1 input box.")
        driver.save_screenshot('address_input_box_timeout.png')
        with open('address_input_box_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to enter the address line 1: {e}")
        driver.save_screenshot('address_input_box_error.png')
        with open('address_input_box_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)


def enter_address_line2(driver, address):
    try:
        print("Trying to enter the address line 2...")
        
        # Wait until the address line 2 input box is present and then enter the address
        address_input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='address-line2']"))
        )
        
        print("Address line 2 input box found.")
        address_input_box.clear()  # Clear any pre-filled text
        address_input_box.send_keys(address)
        print("Address line 2 entered.")
        
    except TimeoutException:
        print("Timed out waiting for the address line 2 input box.")
        driver.save_screenshot('address_line2_input_box_timeout.png')
        with open('address_line2_input_box_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except NoSuchElementException:
        print("Address line 2 input box not found.")
        driver.save_screenshot('address_line2_input_box_not_found.png')
        with open('address_line2_input_box_not_found.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to enter the address line 2: {e}")
        driver.save_screenshot('address_line2_input_box_error.png')
        with open('address_line2_input_box_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)


def enter_postcode(driver, postcode):
    try:
        print("Trying to enter the postcode...")
        
        # Wait until the postcode input box is present and then enter the postcode
        postcode_input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='postal-code']"))
        )
        
        print("Postcode input box found.")
        postcode_input_box.clear()  # Clear any pre-filled text
        postcode_input_box.send_keys(postcode)
        print("Postcode entered.")
        
    except TimeoutException:
        print("Timed out waiting for the postcode input box.")
        driver.save_screenshot('postcode_input_box_timeout.png')
        with open('postcode_input_box_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except NoSuchElementException:
        print("Postcode input box not found.")
        driver.save_screenshot('postcode_input_box_not_found.png')
        with open('postcode_input_box_not_found.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to enter the postcode: {e}")
        driver.save_screenshot('postcode_input_box_error.png')
        with open('postcode_input_box_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)




def enter_city(driver, city):
    try:
        print("Trying to enter the city...")
        
        # Wait until the city input box is present and then enter the city
        city_input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='address-level2']"))
        )
        
        print("City input box found.")
        city_input_box.clear()  # Clear any pre-filled text
        city_input_box.send_keys(city)
        print("City entered.")
        
    except TimeoutException:
        print("Timed out waiting for the city input box.")
        driver.save_screenshot('city_input_box_timeout.png')
        with open('city_input_box_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except NoSuchElementException:
        print("City input box not found.")
        driver.save_screenshot('city_input_box_not_found.png')
        with open('city_input_box_not_found.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to enter the city: {e}")
        driver.save_screenshot('city_input_box_error.png')
        with open('city_input_box_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def enter_phone_number2(driver, phone_number):
    try:
        print("Trying to enter the phone number...")
        
        # Wait until the phone number input box is present and then enter the phone number
        phone_number_input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='tel-national']"))
        )
        
        print("Phone number input box found.")
        phone_number_input_box.clear()  # Clear any pre-filled text
        phone_number_input_box.send_keys(phone_number)
        print("Phone number entered.")
        
    except TimeoutException:
        print("Timed out waiting for the phone number input box.")
        driver.save_screenshot('phone_number_input_box_timeout.png')
        with open('phone_number_input_box_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except NoSuchElementException:
        print("Phone number input box not found.")
        driver.save_screenshot('phone_number_input_box_not_found.png')
        with open('phone_number_input_box_not_found.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to enter the phone number: {e}")
        driver.save_screenshot('phone_number_input_box_error.png')
        with open('phone_number_input_box_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def enter_card_number(driver, card_number):
    try:
        print("Switching to the card number iframe...")
        iframe = WebDriverWait(driver, 30).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@name, 'card number input frame')]"))
        )
        print("Switched to the card number iframe.")
        
        # Add a small delay to ensure the iframe content is fully loaded
        time.sleep(2)

        print("Looking for the card number input field...")
        card_number_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='cardnumber']"))
        )
        print("Card number input field found.")

        print("Entering card number...")
        card_number_input.send_keys(card_number)
        print("Card number entered.")
        
        # Switch back to the default content
        driver.switch_to.default_content()

    except TimeoutException:
        print("Timed out waiting for the card number input field.")
        driver.save_screenshot('card_number_timeout.png')
        with open('card_number_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to enter the card number: {e}")
        driver.save_screenshot('card_number_error.png')
        with open('card_number_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
def input_full_name(driver, full_name="xxxxxxxxxxxxxx"):
    try:
        print("Trying to enter the full name...")

        # Wait until the full name input box is present
        full_name_input_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='address.fullName']"))
        )

        print("Full name input box found.")
        full_name_input_box.clear()  # Clear any pre-filled text
        full_name_input_box.send_keys(full_name)  # Enter the full name
        print("Full name entered.")
        
    except TimeoutException:
        print("Timed out waiting for the full name input box.")
        driver.save_screenshot('full_name_input_box_timeout.png')
        with open('full_name_input_box_timeout.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)
    except Exception as e:
        print(f"Failed to enter the full name: {e}")
        driver.save_screenshot('full_name_input_box_error.png')
        with open('full_name_input_box_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)

def save_html_before_card_entry(driver):
    try:
        print("Saving HTML before entering card number...")
        with open('before_card_entry.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("HTML saved to 'before_card_entry.html'.")
    except Exception as e:
        print(f"Failed to save HTML before card entry: {e}")
        driver.save_screenshot('save_html_before_card_entry_error.png')
        with open('save_html_before_card_entry_error.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(driver.page_source)



def main():
    artist_urls = [
    "https://www.viagogo.de/Konzert-Tickets/Rap-und-Hip-Hop/Travis-Scott-Karten"
]


    driver = setup_driver()
    try:
        for url in artist_urls:
            print(f"Processing artist URL: {url}")
            visit_page(driver, url)
            accept_cookies(driver)
            select_ticket_location(driver)  # Chooses the concert location
            switch_to_new_tab(driver, expected_tabs=2)
            click_continue_button(driver)  # Clicks the continue button before choosing ticket
            choose_ticket(driver)  # Chooses the ticket type (e.g., VIP, normal)
            click_select_button(driver)  # Clicks the 'Select' button

            # Switch to the new tab before waiting and clicking the 'Start' button
            switch_to_new_tab(driver, expected_tabs=3)
            wait_and_click_start_button(driver)  # Waits and clicks the 'Start' button
            click_continue_2(driver)  # Clicks the second 'Continue' button
            enter_email_address(driver, "xxxxxxxx")  # Enters the email address
            click_continue_as_guest_button(driver)  # Clicks the 'Continue as a Guest' button
            enter_first_name(driver, "xxxxxxx")  # Enters the first name
            enter_last_name(driver, "xxxxxx")  # Enters the last name
            enter_phone_number(driver, "xxxxxx")  # Enters the phone number
            click_continue_2(driver)
            click_yes_button(driver)  # Clicks the 'Yes' button
            time.sleep(2)  # Wait 2 seconds before trying to press the continue button
            save_personal_details(driver)
            input_full_name(driver, "xxxxxxxxx")  # Enters the full name
            enter_address_line1(driver, "xxxxxxxx")  # Enters the address line 1
            enter_address_line2(driver, "xxxxxx")  # Enters the address line 2
            enter_postcode(driver, "xxxxxx")  # Enters the postcode
            enter_city(driver, "xxxxxx")  # Enters the city
            enter_phone_number2(driver,"xxxxxxx")  # Enters the phone number
            click_continue_2(driver)
            click_continue_2(driver)
            click_continue_2(driver)
            
            save_html_before_card_entry(driver)  # Save HTML before entering card number
            
            enter_card_number(driver, "xxxxxxxxxxxx")  # Enters the card number
            click_continue_2(driver)
            
            print("Keeping the browser open for 10 minutes...")
            time.sleep(600)

    except Exception as e:
        print(f"Exception in main: {e}")
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()
