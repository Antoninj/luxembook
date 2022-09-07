import logging
import os
from abc import ABC, abstractmethod
import pendulum

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

# X_PATHS
BOOKING_HOUR_XPATH = "/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/tbody/tr/td[1]/div[10]"  # 15:00
PLANNING_DATE_XPATH = "/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/caption/strong"
TENNIS_COURT_INFO_X_PATH = "/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/thead/tr/th[{}]"
BOOKING_SLOT_X_PATH = "/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/tbody/tr/td[{}]/div[10]"

FREE = "libre"


class Runner(ABC):
    LUX_BOOKING_URL = (
        "https://tennis-reservation.resawebfft.com/index.php?option=com_content&view=article&id=35&Itemid=119"
    )

    def __init__(self):
        self.browser = self.setup_chrome_headless_browser()

    @staticmethod
    def setup_chrome_headless_browser():
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--incognito")
        chrome_headless_browser = Chrome(
            options=chrome_options,
            service_log_path=f"logs/chromedriver/chromedriver_{pendulum.now().strftime('%Y-%m-%d %H:%M:%S')}.log",
        )
        return chrome_headless_browser

    @abstractmethod
    def run(self):
        pass

    @staticmethod
    def get_booking_date_timestamp(day_of_week: int):
        logger.info(f"Current date: {pendulum.now()}")
        booking_date = pendulum.now().next(day_of_week)
        logger.info(f"Booking date: {booking_date}")
        return booking_date.timestamp()

    def _find_available_slots(self):
        planning_date = self.browser.find_element(
            By.XPATH,
            PLANNING_DATE_XPATH,
        )
        logger.info(f"Fetching available slots for [{planning_date.text}]")
        booking_slot_by_tennis_court = {
            self.browser.find_element(By.XPATH, TENNIS_COURT_INFO_X_PATH.format(i)): self.browser.find_element(
                By.XPATH, BOOKING_SLOT_X_PATH.format(i)
            )
            for i in range(2, 8)
        }
        booking_hour = self.browser.find_element(
            By.XPATH,
            BOOKING_HOUR_XPATH,
        )
        logger.info(f"Looking up available booking slots at {booking_hour.text}")
        available_slots = []
        for tennis_court, booking_slot in booking_slot_by_tennis_court.items():
            logger.info(f"Court {tennis_court.text}: {booking_slot.text}")
            if booking_slot.text == FREE:
                available_slots.append(booking_slot)
        return available_slots


class DryRun(Runner):
    def __init__(self):
        super().__init__()

    def run(self):
        booking_date_epoch = self.get_booking_date_timestamp(pendulum.SATURDAY)
        date_aware_booking_url = f"{self.LUX_BOOKING_URL}&temps={booking_date_epoch}"
        self.browser.get(date_aware_booking_url)
        self._find_available_slots()


class LuxRun(Runner):
    def __init__(self):
        super().__init__()

    def run(self):
        booking_date_epoch = self.get_booking_date_timestamp(pendulum.SATURDAY)
        date_aware_booking_url = f"{self.LUX_BOOKING_URL}&temps={booking_date_epoch}"
        self.browser.get(date_aware_booking_url)
        self._login()
        available_slots = self._find_available_slots()
        self._book_first_available_slot(available_slots)

    def _login(self):
        username = os.environ.get("username", "not_set")
        password = os.environ.get("password", "not_set")
        logger.info(f"Logging in with user {username}")
        self.browser.find_element(By.ID, "modlgn-username").send_keys(username)
        self.browser.find_element(By.ID, "modlgn-passwd").send_keys(password)
        self.browser.find_element(By.ID, "form-login").submit()

    def _book_first_available_slot(self, available_slots):
        available_slots_it = iter(available_slots)
        try:
            available_slot = next(available_slots_it)
            available_slot.click()
            for handle in self.browser.window_handles:
                logger.info(f"Handle: {handle}")
        except StopIteration:
            logger.info("No free booking slots")
            # trigger failure notification flow
