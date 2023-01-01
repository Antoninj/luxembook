import logging

import pendulum
import typer

from runner import BookRun, DryRun

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"logs/luxembook/luxembook_{pendulum.now().strftime('%Y-%m-%d %H:%M:%S')}.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def main(is_dry_run: bool):
    logger.info("Running luxembook")
    runner = DryRun() if is_dry_run else BookRun()
    runner.run()


if __name__ == "__main__":
    typer.run(main)
