import typer

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


BOOKING_URL='https://tennis-reservation.resawebfft.com/index.php?option=com_content&view=article&id=35&Itemid=119'

def main(dry_run: bool):
    typer.echo("Starting luxembook...")
    if dry_run:
        typer.echo("Luxembook is running in dry run mode")
        run()
    else:
        typer.echo(f"Luxembook is running in normal mode")
        run()


def run():
    chrome_options = Options()
    chrome_options.add_argument("headless")
    chrome_headless_browser = Chrome(options=chrome_options)
    chrome_headless_browser.get(BOOKING_URL)
    login(chrome_headless_browser)

    x_paths = ["/html/body/div[3]/div/div/div/main/article/div/div/div[2]/table/tbody/tr/td[2]/div[10]" for i in range(2,8) ]
    for x_path in x_paths:
        booking_slot = chrome_headless_browser.find_element(By.XPATH, x_path)
        print(booking_slot.text)


def login(browser):
    browser.find_element(By.ID, "modlgn-username").send_keys("fake")
    browser.find_element(By.ID, "modlgn-passwd").send_keys("fake")
    browser.find_element(By.ID, "form-login").submit()

def fetch_planning_for_date(date:str):
    print("not implemented yet")

if __name__ == "__main__":
    typer.run(main)