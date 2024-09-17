from scripts.update_liked_videos import main as update_liked_videos_main
from lib.logging_config import logger


def main():
    logger.info("좋아요 표시한 동영상 업데이트를 시작합니다.")
    update_liked_videos_main()
    logger.info("좋아요 표시한 동영상 업데이트가 완료되었습니다.")


if __name__ == "__main__":
    main()
