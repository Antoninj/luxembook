import typer
import os
import pendulum

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 15:00
BOOKING_HOUR_XPATH = "/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/tbody/tr/td[1]/div[10]"
PLANNING_DATE_XPATH = (
    "/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/caption/strong"
)
LUX_BOOKING_URL = "https://tennis-reservation.resawebfft.com/index.php?option=com_content&view=article&id=35&Itemid=119"


def main(is_dry_run: bool):
    typer.echo("Starting luxembook...")
    if is_dry_run:
        typer.echo("Luxembook is running in dry run mode")
        dry_run()
    else:
        typer.echo(f"Luxembook is running in normal mode")
        run()


def run():
    chrome_headless_browser = setup_chrome_headless_browser()
    booking_date_epoch = get_booking_date_timestamp()
    date_aware_booking_url = f"{LUX_BOOKING_URL}&temps={booking_date_epoch}"
    chrome_headless_browser.get(date_aware_booking_url)
    login(chrome_headless_browser)
    check_available_slots(chrome_headless_browser)


def dry_run():
    chrome_headless_browser = setup_chrome_headless_browser()
    booking_date_epoch = get_booking_date_timestamp()
    date_aware_booking_url = f"{LUX_BOOKING_URL}&temps={booking_date_epoch}"
    chrome_headless_browser.get(date_aware_booking_url)
    check_available_slots(chrome_headless_browser)


def setup_chrome_headless_browser():
    chrome_options = Options()
    chrome_options.add_argument("headless")
    chrome_headless_browser = Chrome(options=chrome_options)
    return chrome_headless_browser


def login(browser):
    username = os.environ.get("username", "not_set")
    password = os.environ.get("password", "not_set")
    typer.echo(f"Logging in with user {username}")
    browser.find_element(By.ID, "modlgn-username").send_keys(username)
    browser.find_element(By.ID, "modlgn-passwd").send_keys(password)
    browser.find_element(By.ID, "form-login").submit()


def get_booking_date_timestamp():
    typer.echo(f"Current date: {pendulum.now()}")
    booking_date = pendulum.now().next(pendulum.SATURDAY)
    typer.echo(f"Booking date: {booking_date}")
    return booking_date.timestamp()


def check_available_slots(chrome_headless_browser):
    planning_date = chrome_headless_browser.find_element(
        By.XPATH,
        PLANNING_DATE_XPATH,
    )
    typer.echo(f"Fetching available slots for [{planning_date.text}]")
    booking_slots_x_paths = {
        f"/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/thead/tr/th[{i}]": f"/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/tbody/tr/td[{i}]/div[10]"
        for i in range(2, 8)
    }
    booking_hour = chrome_headless_browser.find_element(
        By.XPATH,
        BOOKING_HOUR_XPATH,
    )
    typer.echo(f"Looking up available booking slots at {booking_hour.text}")
    for tennis_court_x_path, booking_slot_x_path in booking_slots_x_paths.items():
        booking_slot = chrome_headless_browser.find_element(
            By.XPATH, booking_slot_x_path
        )
        tennis_court = chrome_headless_browser.find_element(
            By.XPATH, tennis_court_x_path
        )
        typer.echo(f"Checking court [{tennis_court.text}] availability")
        typer.echo(booking_slot.text)


if __name__ == "__main__":
    typer.run(main)
