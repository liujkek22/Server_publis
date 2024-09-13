# -*- coding: utf-8 -*-

import asyncio
import websockets
import datetime

# 维护一个连接的客户端列表
clients = set()

async def send_test_data(interval):
    while True:
        if clients:
            test_data = f"测试数据: {datetime.datetime.now().isoformat()}"
            print(f"发送数据：{test_data}")
            await asyncio.gather(*(send_with_error_handling(client, test_data) for client in clients))
        await asyncio.sleep(interval)

async def send_with_error_handling(client, data):
    try:
        await client.send(data)
    except Exception as e:
        print(f"发送数据时出错: {e}")

async def handler(websocket, path):
    clients.add(websocket)
    print(f"客户端已连接：{websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"收到数据：{message}")
            await websocket.send(f"服务器收到：{message}")
    except websockets.ConnectionClosed:
        print(f"客户端断开连接：{websocket.remote_address}")
    finally:
        clients.remove(websocket)

async def main():
    port = 8765
    send_interval = 5  # 发送测试数据的间隔时间，单位为秒
    
    # 启动 WebSocket 服务器
    server = await websockets.serve(handler, "0.0.0.0", port)
    print(f"WebSocket 服务器已启动，监听端口 {port}")
    
    # 启动定时发送测试数据的任务
    await asyncio.gather(
        server.wait_closed(),
        send_test_data(send_interval)
    )

if __name__ == "__main__":
    asyncio.run(main())
