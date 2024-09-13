import asyncio
import websockets
import datetime

# 维护一个连接的客户端列表
clients = set()

async def send_test_data():
    while True:
        # 定时发送测试数据
        if clients:
            test_data = f"测试数据: {datetime.datetime.now().isoformat()}"
            print(f"发送数据：{test_data}")
            await asyncio.wait([client.send(test_data) for client in clients])
        # 每隔 5 秒发送一次
        await asyncio.sleep(5)

async def handler(websocket, path):
    # 当客户端连接时
    clients.add(websocket)
    print(f"客户端已连接：{websocket.remote_address}")
    try:
        async for message in websocket:
            # 处理客户端发送的数据
            print(f"收到数据：{message}")
            # 发送回客户端
            await websocket.send(f"服务器收到：{message}")
    except websockets.ConnectionClosed:
        print(f"客户端断开连接：{websocket.remote_address}")
    finally:
        # 连接关闭时从客户端列表中移除
        clients.remove(websocket)

async def main():
    # 启动 WebSocket 服务器，监听端口 8765
    start_server = websockets.serve(handler, "0.0.0.0", 8765)

    # 启动定时发送测试数据的任务
    await asyncio.gather(start_server, send_test_data())

if __name__ == "__main__":
    asyncio.run(main())
