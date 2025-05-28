#!/usr/bin/env python3
"""
CoinEX WebSocket Latency Monitor
监控CoinEX WebSocket推送的延迟，计算本地接收时间与updateAt的差值
"""

import asyncio
import json
import gzip
import time
import logging
from typing import Optional, Dict, Any
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CoinEXLatencyMonitor:
    def __init__(self, coin: str = "BTC", currency: str = "USDT"):
        self.coin = coin.upper()
        self.currency = currency.upper()
        self.ws_url = "wss://socket.coinex.com/v2/spot"
        
        # 订阅消息模板
        self.depth_sub = {
            "method": "depth.subscribe",
            "params": {
                "market_list": [[f"{self.coin}{self.currency}", 50, "0", True]]
            },
            "id": 1957
        }
        
        self.bbo_sub = {
            "method": "bbo.subscribe", 
            "params": {
                "market_list": [f"{self.coin}{self.currency}"]
            },
            "id": 1958
        }
        
        self.ping_msg = {"method": "server.ping", "params": [], "id": 1959}
        
        # 统计数据
        self.latency_stats = []
        self.message_count = 0
        
    def decompress_message(self, data: bytes) -> str:
        """解压gzip消息"""
        try:
            return gzip.decompress(data).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to decompress message: {e}")
            return ""
    
    def calculate_latency(self, update_at: int) -> float:
        """计算延迟：本地时间 - updateAt时间（毫秒）"""
        local_time_ms = int(time.time() * 1000)
        latency_ms = local_time_ms - update_at
        
        # 记录详细的时间差计算过程
        logger.info(f"[TIME CALC] Local time: {local_time_ms}ms, UpdateAt: {update_at}ms, Latency: {latency_ms}ms")
        
        return latency_ms
    
    def log_latency_stats(self, latency_ms: float, message_type: str):
        """记录延迟统计"""
        self.latency_stats.append(latency_ms)
        self.message_count += 1
        
        logger.info(f"[{message_type}] Latency: {latency_ms:.2f}ms | "
                   f"Messages: {self.message_count}")
        
        # 每100条消息输出统计信息
        if self.message_count % 100 == 0:
            self.print_statistics()
    
    def print_statistics(self):
        """打印延迟统计信息"""
        if not self.latency_stats:
            return
            
        avg_latency = sum(self.latency_stats) / len(self.latency_stats)
        min_latency = min(self.latency_stats)
        max_latency = max(self.latency_stats)
        
        logger.info(f"=== Latency Statistics (last {len(self.latency_stats)} messages) ===")
        logger.info(f"Average: {avg_latency:.2f}ms")
        logger.info(f"Min: {min_latency:.2f}ms")
        logger.info(f"Max: {max_latency:.2f}ms")
        logger.info("=" * 50)
        
        # 清空统计数据，避免内存占用过多
        self.latency_stats = []
    
    async def handle_message(self, message: str):
        """处理WebSocket消息"""
        try:
            data = json.loads(message)
            
            # 处理pong消息
            if data.get("method") == "server.pong":
                logger.info("Received pong message")
                return
            
            # 先计算延迟，再决定是否记录原始消息
            should_log_raw = False
            
            # 处理depth更新
            if data.get("method") == "depth.update":
                if "data" in data and "depth" in data["data"]:
                    update_at = data["data"]["depth"].get("updated_at")
                    if update_at:
                        logger.info(f"[DEPTH UPDATE] Found updateAt: {update_at}")
                        latency = self.calculate_latency(update_at)
                        if latency > 1000:  # 延迟大于1秒
                            should_log_raw = True
                        self.log_latency_stats(latency, "DEPTH")
                    else:
                        logger.warning("[DEPTH UPDATE] No updated_at field found")
                else:
                    logger.warning("[DEPTH UPDATE] Invalid data structure")
            
            # 处理BBO更新
            elif data.get("method") == "bbo.update":
                if "data" in data:
                    update_at = data["data"].get("updated_at")
                    if update_at:
                        logger.info(f"[BBO UPDATE] Found updateAt: {update_at}")
                        latency = self.calculate_latency(update_at)
                        if latency > 1000:  # 延迟大于1秒
                            should_log_raw = True
                        self.log_latency_stats(latency, "BBO")
                    else:
                        logger.warning("[BBO UPDATE] No updated_at field found")
                else:
                    logger.warning("[BBO UPDATE] Invalid data structure")
            
            # 处理订阅确认
            elif "code" in data:
                if data["code"] == 0:
                    logger.info(f"Subscription successful: {message}")
                else:
                    logger.error(f"Subscription failed: {message}")
            
            # 只有延迟大于1秒时才记录原始消息
            if should_log_raw:
                logger.info(f"[HIGH LATENCY RAW MESSAGE] {message}")
                    
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON message: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def send_ping(self, websocket):
        """定期发送ping消息"""
        while True:
            try:
                await asyncio.sleep(30)  # 每30秒发送一次ping
                ping_json = json.dumps(self.ping_msg)
                logger.info(f"[SEND PING] {ping_json}")
                await websocket.send(ping_json)
                logger.info("Sent ping message")
            except Exception as e:
                logger.error(f"Failed to send ping: {e}")
                break
    
    async def connect_and_monitor(self):
        """连接WebSocket并开始监控"""
        logger.info(f"Starting latency monitor for {self.coin}/{self.currency}")
        
        while True:
            try:
                logger.info(f"Connecting to {self.ws_url}")
                
                async with websockets.connect(
                    self.ws_url,
                    compression=None,  # 手动处理gzip压缩
                    ping_interval=None,  # 禁用自动ping
                    ping_timeout=None,
                    close_timeout=10
                ) as websocket:
                    
                    logger.info("WebSocket connected successfully")
                    
                    # 发送订阅消息
                    depth_sub_json = json.dumps(self.depth_sub)
                    logger.info(f"[SEND DEPTH SUB] {depth_sub_json}")
                    await websocket.send(depth_sub_json)
                    logger.info("Sent depth subscription")
                    
                    bbo_sub_json = json.dumps(self.bbo_sub)
                    logger.info(f"[SEND BBO SUB] {bbo_sub_json}")
                    await websocket.send(bbo_sub_json)
                    logger.info("Sent BBO subscription")
                    
                    # 启动ping任务
                    ping_task = asyncio.create_task(self.send_ping(websocket))
                    
                    try:
                        # 主消息循环
                        async for message in websocket:
                            if isinstance(message, bytes):
                                # 解压gzip消息
                                decompressed = self.decompress_message(message)
                                if decompressed:
                                    await self.handle_message(decompressed)
                            else:
                                await self.handle_message(message)
                                
                    finally:
                        ping_task.cancel()
                        try:
                            await ping_task
                        except asyncio.CancelledError:
                            pass
                            
            except ConnectionClosed:
                logger.warning("WebSocket connection closed, reconnecting in 2 seconds...")
                await asyncio.sleep(2)
            except WebSocketException as e:
                logger.error(f"WebSocket error: {e}, reconnecting in 2 seconds...")
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Unexpected error: {e}, reconnecting in 5 seconds...")
                await asyncio.sleep(5)

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CoinEX WebSocket Latency Monitor")
    parser.add_argument("--coin", default="MAGA", help="Coin symbol (default: MAGA)")
    parser.add_argument("--currency", default="USDT", help="Currency symbol (default: USDT)")
    
    args = parser.parse_args()
    
    monitor = CoinEXLatencyMonitor(args.coin, args.currency)
    
    try:
        await monitor.connect_and_monitor()
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 