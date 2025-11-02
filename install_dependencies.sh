#!/bin/bash
# 安装系统依赖脚本

echo "安装Chrome浏览器和中文字体..."

# 检测操作系统
if [ -f /etc/debian_version ]; then
    # Debian/Ubuntu
    sudo apt-get update
    
    # 安装Chrome
    if ! command -v google-chrome &> /dev/null; then
        echo "安装Google Chrome..."
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
    else
        echo "Chrome已安装"
    fi
    
    # 安装中文字体
    echo "安装中文字体..."
    sudo apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei fonts-arphic-ukai fonts-arphic-uming
    
    # 安装其他依赖
    sudo apt-get install -y python3-pip xvfb
    
elif [ -f /etc/redhat-release ]; then
    # Red Hat/CentOS
    sudo yum update -y
    sudo yum install -y google-chrome-stable
    sudo yum install -y wqy-microhei-fonts wqy-zenhei-fonts
    sudo yum install -y python3-pip xvfb
else
    echo "未知的操作系统"
    exit 1
fi

# 安装Python依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

echo "安装完成！"
echo "现在可以运行: python3 scrape_scys.py"
