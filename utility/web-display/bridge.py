import asyncio, json
from websockets.server import serve
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

# --- WebSocket hub ---
clients = set()
async def ws_handler(websocket):
    clients.add(websocket)
    try:
        async for _ in websocket:
            pass
    finally:
        clients.discard(websocket)

async def ws_broadcast(msg: dict):
    if not clients: return
    data = json.dumps(msg)
    await asyncio.gather(*(c.send(data) for c in list(clients)), return_exceptions=True)

# --- OSC → broadcast (/display/value/<1..8> <0..127>) ---
async def osc_handler(addr, *args):
    await ws_broadcast({"addr": addr, "args": list(args)})

async def main():
    # WebSocket server on :8765
    ws_srv = await serve(ws_handler, host="", port=8765)

    # OSC UDP listener on :9001
    disp = Dispatcher()
    disp.map("/display/value/*", lambda addr, *a: asyncio.create_task(osc_handler(addr, *a)))
    osc_srv = AsyncIOOSCUDPServer(("0.0.0.0", 9001), disp, asyncio.get_running_loop())
    transport, _ = await osc_srv.create_serve_endpoint()

    print("WS : ws://0.0.0.0:8765")
    print("OSC: udp://0.0.0.0:9001  (send /display/value/<1..8> <0..127>)")
    try:
        await asyncio.Future()
    finally:
        transport.close()
        ws_srv.close()
        await ws_srv.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
