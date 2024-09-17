import logging
from scripts.update_liked_videos import main as update_liked_videos_main

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("좋아요 표시한 동영상 업데이트를 시작합니다.")
    update_liked_videos_main()
    logger.info("좋아요 표시한 동영상 업데이트가 완료되었습니다.")


if __name__ == "__main__":
    main()
