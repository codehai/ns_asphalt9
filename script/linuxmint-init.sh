#!/bin/bash

echo "start"

ln -s /usr/bin/python3 /usr/bin/python
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 8529B1E0F8BF7F65C12FABB0A4BCBD87CEF9E52D
add-apt-repository -y ppa:alex-p/tesseract-ocr5
apt update
apt install python3-pip tesseract-ocr v4l-utils ffmpeg
pip install nxbt pytesseract pytest -i https://pypi.tuna.tsinghua.edu.cn/simple