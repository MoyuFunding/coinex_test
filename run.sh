#!/bin/bash

# CoinEX Latency Monitor启动脚本

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo "安装依赖..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 运行监控程序
echo "启动CoinEX延迟监控..."
python coinex_latency_monitor.py "$@" 