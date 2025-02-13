import asyncio
import ssl
import paho.mqtt.client as mqtt
import websockets
from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn

# Configuração do Broker MQTT
BROKER = "7f054615a7ef47f78f9f2892dbc87eac.s1.eu.hivemq.cloud"
PORT = 8884  # Porta WebSocket MQTT
TOPIC = "dice"
USERNAME = "dicewebbroker"
PASSWORD = "Dicewebbroker1"

# Criar a aplicação FastAPI para o Render detectar a porta aberta
app = FastAPI()

# Servir o arquivo HTML principal
@app.get("/")
def serve_index():
    return FileResponse("index.html")

# Lista de clientes WebSocket conectados
connected_clients = set()

# Callback quando uma mensagem MQTT chega
def on_message(client, userdata, message):
    msg = message.payload.decode()
    print(f"📩 Recebido MQTT: {msg}")
    loop = asyncio.get_event_loop()
    loop.create_task(send_to_websocket_clients(msg))

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

async def start_websocket():
    print("✅ Iniciando WebSocket Server na porta 8765")
    server = await websockets.serve(websocket_handler, "0.0.0.0", 8765)
    await server.wait_closed()

# Ajuste para rodar FastAPI e WebSockets corretamente no Render
def start_services():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Iniciar WebSockets em uma thread separada
    loop.create_task(start_websocket())

    # Rodar FastAPI no Render
    uvicorn.run(app, host="0.0.0.0", port=10000)

if __name__ == "__main__":
    start_services()
