import asyncio
import ssl
import paho.mqtt.client as mqtt
import websockets
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
import uvicorn

# Configuração do Broker MQTT
BROKER = "7f054615a7ef47f78f9f2892dbc87eac.s1.eu.hivemq.cloud"
PORT = 8884  # Porta WebSocket MQTT
TOPIC = "dice"
USERNAME = "dicewebbroker"
PASSWORD = "Dicewebbroker1"

# Criar a aplicação FastAPI
app = FastAPI()

# Servir o arquivo HTML principal
@app.get("/")
def serve_index():
    return FileResponse("index.html")

# Lista de clientes WebSocket conectados
connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    print("✅ Novo cliente conectado ao WebSocket")

    try:
        while True:
            await asyncio.sleep(1)  # Mantém a conexão aberta
    except Exception as e:
        print(f"🔌 Cliente desconectado: {e}")
    finally:
        connected_clients.remove(websocket)

# Callback quando uma mensagem MQTT chega
def on_message(client, userdata, message):
    msg = message.payload.decode()
    print(f"📩 Recebido MQTT: {msg}")
    asyncio.run_coroutine_threadsafe(send_to_websocket_clients(msg), asyncio.get_event_loop())

async def send_to_websocket_clients(msg):
    if connected_clients:
        print(f"📡 Enviando para {len(connected_clients)} clientes WebSocket")
        await asyncio.gather(*(client.send_text(msg) for client in connected_clients))

# Configuração do Cliente MQTT via WebSocket
client = mqtt.Client(transport="websockets")
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)
client.loop_start()

# Iniciar FastAPI
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
