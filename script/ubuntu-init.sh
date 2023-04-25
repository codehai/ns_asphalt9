#!/bin/bash

mv /etc/apt/sources.list /etc/apt/sources.list.bak
echo "# \u9ed8\u8ba4\u6ce8\u91ca\u4e86\u6e90\u7801\u955c\u50cf\u4ee5\u63d0\u9ad8 apt update \u901f\u5ea6\uff0c\u5982\u6709\u9700\u8981\u53ef\u81ea\u884c\u53d6\u6d88\u6ce8\u91ca
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy main restricted universe multiverse
# deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy main restricted universe multiverse
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy-updates main restricted universe multiverse
# deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy-updates main restricted universe multiverse
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy-backports main restricted universe multiverse
# deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy-backports main restricted universe multiverse

deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy-security main restricted universe multiverse
# deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy-security main restricted universe multiverse

# deb http://ports.ubuntu.com/ubuntu-ports/ jammy-security main restricted universe multiverse
# # deb-src http://ports.ubuntu.com/ubuntu-ports/ jammy-security main restricted universe multiverse

# \u9884\u53d1\u5e03\u8f6f\u4ef6\u6e90\uff0c\u4e0d\u5efa\u8bae\u542f\u7528
# deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy-proposed main restricted universe multiverse
# # deb-src http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy-proposed main restricted universe multiverse
" > /etc/apt/sources.list

rm /etc/apt/sources.list.d/proposed.list
rm /etc/apt/sources.list.d/proposed.list.save 

apt-get update
apt-get install -y curl libssl-dev libpq-dev libcurl4-openssl-dev libsm6 libxext6 software-properties-common python3-pip python3-dev python3-tk
apt-get install gcc-11-base=11.3.0-1ubuntu1~22.04 cpp-11=11.3.0-1ubuntu1~22.04
apt-get install -y libssl-dev zlib1g-dev gcc g++ make
apt-get install libglib2.0-0=2.72.4-0ubuntu1
apt-get install libdbus-glib-1-dev

ln -s /usr/bin/python3 /usr/bin/python
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 8529B1E0F8BF7F65C12FABB0A4BCBD87CEF9E52D
add-apt-repository -y ppa:alex-p/tesseract-ocr5
apt update
apt install python3-pip tesseract-ocr v4l-utils ffmpeg

pip install nxbt pytesseract pytest -i https://pypi.tuna.tsinghua.edu.cn/simple
