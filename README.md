# luxembook

Luxembourg gardens tennis court automated booking bot.

## Overview

Luxembook is a CLI application that automates the process of booking a tennis court on
the [FFT online booking platform](https://tennis-reservation.resawebfft.com/)
using [Selenium](https://www.selenium.dev/) web browser automation technology.

## Running locally without Docker (MacOS)

1. Install dev and runtime dependencies: `poetry install`
2. Download the [chromedriver executable archive](https://chromedriver.chromium.org/downloads) matching your locally
   installed version of chrome
3. Unzip the chromedriver executable archive and move it to `~/.local/bin`
4. Set the `username` and ` password`environment variables with your login credentials
5. Run `python src/luxembook.py true` for dry run mode
6. If MacOS complains, bypass untrusted software quarantine: `xattr -d com.apple.quarantine chromedriver`

## Running locally using Docker

1. Make sure you have [Docker](https://docs.docker.com/get-docker/) locally installed and running
2. From the root of the repository, run :`docker build . -t luxembook:latest` to build the docker image
3. Then run `docker run --env username={your_username} --env password={your_password} luxembook`

## Disclaimer

Use at your own risk.

## License

[MIT](https://mit-license.org/)
