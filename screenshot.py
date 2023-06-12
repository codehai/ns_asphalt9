from subprocess import Popen, PIPE
from utils.log import logger


def get_format():
    cmd = "v4l2-ctl --list-formats"
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    output, error = p.communicate()
    if output:
        result = output.decode("utf-8")
        if "MJPG" in result:
            return "MJPG", "jpeg"
        elif "YUYV" in result:
            return "YUYV", "yuv"
        else:
            raise Exception("Not support formats type")
    if error:
        raise Exception(error.decode("utf-8"))


def screenshot():
    format, file_type = get_format()
    cmd = f"v4l2-ctl --device /dev/video0 --set-fmt-video=width=1920,height=1080,pixelformat={format} --stream-mmap --stream-to=./source.{file_type} --stream-count=1"
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, cwd="./images")
    p.wait()
    cmd = f"ffmpeg -loglevel quiet -y -s 1920*1080 -i ./source.{file_type} ./output.jpg"
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, cwd="./images")
    p.wait()


if __name__ == "__main__":
    screenshot()
