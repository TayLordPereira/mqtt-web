import asyncio
import ssl
import paho.mqtt.client as mqtt
import websockets
from fastapi import FastAPI
import uvicorn

# Configuração do Broker MQTT
BROKER = "7f054615a7ef47f78f9f2892dbc87eac.s1.eu.hivemq.cloud"
PORT = 8884  # Porta WebSocket MQTT
TOPIC = "dice"
USERNAME = "dicewebbroker"
PASSWORD = "Dicewebbroker1"

# Criar a aplicação FastAPI para o Render detectar a porta aberta
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Servidor MQTT WebSocket rodando!"}

# Lista de clientes WebSocket conectados
connected_clients = set()

# Callback quando uma mensagem MQTT chega
def on_message(client, userdata, message):
    msg = message.payload.decode()
    print(f"📩 Recebido MQTT: {msg}")
    asyncio.run(send_to_websocket_clients(msg))

async def send_to_websocket_clients(msg):
    if connected_clients:
        await asyncio.gather(*(client.send(msg) for client in connected_clients))

# Configuração do Cliente MQTT via WebSocket
client = mqtt.Client(transport="websockets")
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)
client.loop_start()

# Servidor WebSocket
async def websocket_handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            pass
    finally:
        connected_clients.remove(websocket)

# Iniciar o Servidor WebSocket
async def start_websocket():
    server = await websockets.serve(websocket_handler, "0.0.0.0", 8765)
    await server.wait_closed()

# Iniciar Servidor Web e WebSocket em paralelo
async def main():
    websocket_task = asyncio.create_task(start_websocket())
    api_task = asyncio.create_task(uvicorn.run(app, host="0.0.0.0", port=10000))
    await asyncio.gather(websocket_task, api_task)

if __name__ == "__main__":
    asyncio.run(main())
