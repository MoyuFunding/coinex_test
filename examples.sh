#!/bin/bash

# CoinEX延迟监控示例脚本
# 展示如何监控不同的交易对

echo "CoinEX延迟监控示例"
echo "==================="
echo ""

echo "1. 监控BTC/USDT（默认）:"
echo "   ./run.sh"
echo ""

echo "2. 监控ETH/USDT:"
echo "   ./run.sh --coin ETH --currency USDT"
echo ""

echo "3. 监控DOGE/BTC:"
echo "   ./run.sh --coin DOGE --currency BTC"
echo ""

echo "4. 监控其他热门交易对:"
echo "   ./run.sh --coin SOL --currency USDT"
echo "   ./run.sh --coin ADA --currency USDT"
echo "   ./run.sh --coin DOT --currency USDT"
echo "   ./run.sh --coin LINK --currency USDT"
echo ""

echo "选择要监控的交易对（输入数字1-4，或按Enter使用默认BTC/USDT）:"
read -r choice

case $choice in
    1|"")
        echo "启动BTC/USDT监控..."
        ./run.sh
        ;;
    2)
        echo "启动ETH/USDT监控..."
        ./run.sh --coin ETH --currency USDT
        ;;
    3)
        echo "启动DOGE/BTC监控..."
        ./run.sh --coin DOGE --currency BTC
        ;;
    4)
        echo "请输入币种符号（如SOL）:"
        read -r coin
        echo "请输入计价货币（如USDT）:"
        read -r currency
        echo "启动${coin}/${currency}监控..."
        ./run.sh --coin "$coin" --currency "$currency"
        ;;
    *)
        echo "无效选择，使用默认BTC/USDT..."
        ./run.sh
        ;;
esac 