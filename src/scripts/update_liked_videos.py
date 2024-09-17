import logging
from lib.video_manager import VideoManager


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    setup_logging()
    try:
        video_manager = VideoManager()
        video_manager.update_liked_videos()
    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")


if __name__ == "__main__":
    main()
