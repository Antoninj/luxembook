import typer
import os
import pendulum
import logging

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

LUX_BOOKING_URL = "https://tennis-reservation.resawebfft.com/index.php?option=com_content&view=article&id=35&Itemid=119"
BOOKING_HOUR_XPATH = "/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/tbody/tr/td[1]/div[10]"  # 15:00
PLANNING_DATE_XPATH = (
    "/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/caption/strong"
)

FREE = "libre"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            f"logs/luxembook/luxembook_{pendulum.now().strftime('%Y-%m-%d %H:%M:%S')}.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def main(is_dry_run: bool):
    logger.info("Starting luxembook...")
    if is_dry_run:
        logger.info("Luxembook is running in dry run mode")
        dry_run()
    else:
        logger.info(f"Luxembook is running in normal mode")
        run()


def run():
    chrome_headless_browser = setup_chrome_headless_browser()
    booking_date_epoch = get_booking_date_timestamp()
    date_aware_booking_url = f"{LUX_BOOKING_URL}&temps={booking_date_epoch}"
    chrome_headless_browser.get(date_aware_booking_url)
    login(chrome_headless_browser)
    available_slots = find_available_slots(chrome_headless_browser)
    book_first_available_slot(available_slots, chrome_headless_browser)


def book_first_available_slot(available_slots, chrome_headless_browser):
    available_slots_it = iter(available_slots)
    try:
        available_slot = next(available_slots_it)
        available_slot.click()
        for handle in chrome_headless_browser.window_handles:
            logger.info(f"Handle: {handle}")
    except StopIteration:
        logger.info("No free booking slots")
        # trigger failure notification flow


def dry_run():
    chrome_headless_browser = setup_chrome_headless_browser()
    booking_date_epoch = get_booking_date_timestamp()
    date_aware_booking_url = f"{LUX_BOOKING_URL}&temps={booking_date_epoch}"
    chrome_headless_browser.get(date_aware_booking_url)
    find_available_slots(chrome_headless_browser)


def setup_chrome_headless_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--incognito")
    chrome_headless_browser = Chrome(
        options=chrome_options,
        service_log_path=f"logs/chromedriver/chromedriver_{pendulum.now().strftime('%Y-%m-%d %H:%M:%S')}.log",
    )
    return chrome_headless_browser


def login(browser):
    username = os.environ.get("username", "not_set")
    password = os.environ.get("password", "not_set")
    logger.info(f"Logging in with user {username}")
    browser.find_element(By.ID, "modlgn-username").send_keys(username)
    browser.find_element(By.ID, "modlgn-passwd").send_keys(password)
    browser.find_element(By.ID, "form-login").submit()


def get_booking_date_timestamp():
    logger.info(f"Current date: {pendulum.now()}")
    booking_date = pendulum.now().next(pendulum.SATURDAY)
    logger.info(f"Booking date: {booking_date}")
    return booking_date.timestamp()


def find_available_slots(chrome_headless_browser):
    planning_date = chrome_headless_browser.find_element(
        By.XPATH,
        PLANNING_DATE_XPATH,
    )
    logger.info(f"Fetching available slots for [{planning_date.text}]")
    booking_slots = {
        chrome_headless_browser.find_element(
            By.XPATH,
            f"/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/thead/tr/th[{i}]",
        ): chrome_headless_browser.find_element(
            By.XPATH,
            f"/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/tbody/tr/td[{i}]/div[10]",
        )
        for i in range(2, 8)
    }
    booking_hour = chrome_headless_browser.find_element(
        By.XPATH,
        BOOKING_HOUR_XPATH,
    )
    logger.info(f"Looking up available booking slots at {booking_hour.text}")
    available_slots = []
    for tennis_court, booking_slot in booking_slots.items():
        logger.info(f"Court {tennis_court.text}: {booking_slot.text}")
        if booking_slot.text == FREE:
            available_slots.append(booking_slot)
    return available_slots


if __name__ == "__main__":
    typer.run(main)
