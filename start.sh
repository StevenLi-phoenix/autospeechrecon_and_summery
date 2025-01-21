#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到项目目录
cd "$SCRIPT_DIR"

# 激活虚拟环境
source .venv/bin/activate

# 运行程序
python3 run.py

# 如果程序异常退出，等待用户按键再关闭
if [ $? -ne 0 ]; then
    echo "程序异常退出，按任意键继续..."
    read -n 1
fi

# 退出虚拟环境
deactivate 