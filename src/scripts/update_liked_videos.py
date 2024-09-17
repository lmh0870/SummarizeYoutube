import logging
from lib.video_manager import update_liked_videos

logging.basicConfig(level=logging.INFO)


def main():
    update_liked_videos()


if __name__ == "__main__":
    main()
