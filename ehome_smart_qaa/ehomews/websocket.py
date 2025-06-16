from fastapi import FastAPI, WebSocket
from api import ws_chat

app = FastAPI(title="ehome big model api server")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

app.websocket("/ws_chat")(ws_chat)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8961)