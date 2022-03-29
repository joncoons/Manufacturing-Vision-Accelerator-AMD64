import os
import sys
import time
from time import sleep
from pathlib import Path

# frame_root = "/frame_volume"
# annotated_root = "/annotated_frame_volume"
# retrain_root = "/retrain_frame_volume"
img_root = "/images_volume"

def file_cleanup(seconds):
    # img_root_arr = [frame_root, annotated_root, retrain_root]
    while True:
        # print(f"Searching files to delete older than {seconds} seconds...")
        current_time = time.time()
        # print(time.localtime())
        # for img_root in img_root_arr:
        img_list = os.listdir(img_root)
        # print(f"Image List: {img_list}")
        if not img_list:
            continue
        for filename in img_list:
            img_path = os.path.join(img_root, filename) 
            if (current_time - os.stat(img_path).st_mtime) > seconds:
                os.remove(img_path)
                # print(f"Deleted image: {filename}")
        time.sleep(120)

if __name__ == "__main__":
    try:
        RETENTION_POLICY_SECONDS = int(os.environ["RETENTION_POLICY_SECONDS"])
    except ValueError as error:
        print(error)
        sys.exit(1)
    file_cleanup(RETENTION_POLICY_SECONDS)
