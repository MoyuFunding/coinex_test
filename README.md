# CoinEX WebSocket Latency Monitor

这个Python脚本用于监控CoinEX WebSocket推送的延迟，计算本地接收时间与推送的`updateAt`时间的差值。

## 功能特性

- 连接CoinEX WebSocket API v2
- 订阅深度数据(depth)和最佳买卖价(BBO)更新
- 实时计算延迟：本地接收时间 - updateAt时间
- 自动重连机制
- 延迟统计信息（平均值、最小值、最大值）
- 支持gzip压缩消息解压

## 快速开始

### 方法1：使用启动脚本（推荐）

```bash
# 给脚本执行权限（首次使用）
chmod +x run.sh

# 监控BTC/USDT的延迟
./run.sh

# 监控ETH/USDT的延迟
./run.sh --coin ETH --currency USDT

# 监控其他交易对
./run.sh --coin DOGE --currency BTC
```

启动脚本会自动：
- 创建Python虚拟环境（如果不存在）
- 安装所需依赖
- 激活虚拟环境
- 运行监控程序

### 方法2：手动安装和运行

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行监控程序
python coinex_latency_monitor.py
```

## 使用方法

### 命令行参数

- `--coin`: 币种符号（默认：BTC）
- `--currency`: 计价货币符号（默认：USDT）

### 使用示例

```bash
# 监控BTC/USDT的延迟
./run.sh

# 监控ETH/USDT的延迟
./run.sh --coin ETH --currency USDT

# 监控其他交易对
./run.sh --coin DOGE --currency BTC
```

## 输出示例

```
2024-01-15 10:30:15,123 - INFO - Starting latency monitor for BTC/USDT
2024-01-15 10:30:15,456 - INFO - Connecting to wss://socket.coinex.com/v2/spot
2024-01-15 10:30:15,789 - INFO - WebSocket connected successfully
2024-01-15 10:30:15,890 - INFO - Welcome message: {"code":0,"data":{},"message":"OK"}
2024-01-15 10:30:15,891 - INFO - Sent depth subscription
2024-01-15 10:30:15,892 - INFO - Sent BBO subscription
2024-01-15 10:30:16,123 - INFO - [DEPTH] Latency: 45.67ms | Messages: 1
2024-01-15 10:30:16,234 - INFO - [BBO] Latency: 23.45ms | Messages: 2
...
2024-01-15 10:35:16,789 - INFO - === Latency Statistics (last 100 messages) ===
2024-01-15 10:35:16,789 - INFO - Average: 34.56ms
2024-01-15 10:35:16,789 - INFO - Min: 12.34ms
2024-01-15 10:35:16,789 - INFO - Max: 78.90ms
2024-01-15 10:35:16,789 - INFO - ==================================================
```

## 延迟计算说明

延迟计算公式：
```
延迟(ms) = 本地接收时间(ms) - updateAt时间(ms)
```

- `本地接收时间`：Python脚本接收到WebSocket消息的时间戳
- `updateAt时间`：CoinEX服务器推送消息中包含的时间戳
- 正值表示延迟，负值可能表示时钟不同步

## 注意事项

1. 确保本地时钟与标准时间同步，以获得准确的延迟测量
2. 网络延迟会影响测量结果
3. 脚本会自动处理连接断开和重连
4. 每100条消息会输出一次统计信息
5. 使用Ctrl+C可以优雅地停止监控

## 技术实现

- 使用`asyncio`和`websockets`库实现异步WebSocket连接
- 自动处理gzip压缩的消息
- 实现心跳机制保持连接活跃
- 包含完整的错误处理和重连逻辑

## 文件说明

- `coinex_latency_monitor.py`: 主程序文件
- `requirements.txt`: Python依赖包列表
- `run.sh`: 启动脚本（推荐使用）
- `README.md`: 使用说明文档 