from subprocess import PIPE, Popen


def screenshot():
    cmd = "ffmpeg -loglevel quiet -y -f v4l2 -i /dev/video0 -frames:v 1 output.jpg"
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, cwd="./")
    p.wait()


if __name__ == "__main__":
    screenshot()
