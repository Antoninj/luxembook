import typer
import pendulum
import logging

from src.runner import LuxRun, DryRun

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
    logger.info("Starting luxembook...")
    if is_dry_run:
        logger.info("Luxembook is running in dry run mode")
        runner = DryRun()
    else:
        logger.info(f"Luxembook is running in normal mode")
        runner = LuxRun()
    runner.run()


if __name__ == "__main__":
    typer.run(main)
