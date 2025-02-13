import asyncio
import ssl
import paho.mqtt.client as mqtt
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
import uvicorn


import socket

try:
    print("🔍 Testando resolução de DNS...")
    ip = socket.gethostbyname("7f054615a7ef47f78f9f2892dbc87eac.s1.eu.hivemq.cloud")
    print(f"✅ Resolução de DNS bem-sucedida: {ip}")
except socket.gaierror:
    print("❌ Erro: Não foi possível resolver o nome do host MQTT!")


# Configuração do Broker MQTT via WebSockets
BROKER_WS = "wss://7f054615a7ef47f78f9f2892dbc87eac.s1.eu.hivemq.cloud:8884/mqtt"
TOPIC = "dice"
USERNAME = "dicewebbroker"
PASSWORD = "Dicewebbroker1"

# Criar a aplicação FastAPI
app = FastAPI()

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

    # Enviar mensagem para os clientes WebSocket
    loop = asyncio.get_event_loop()
    loop.create_task(send_to_websocket_clients(msg))

async def send_to_websocket_clients(msg):
    if connected_clients:
        print(f"📡 Enviando para {len(connected_clients)} clientes WebSocket")
        await asyncio.gather(*(client.send_text(msg) for client in connected_clients))

# Configuração do Cliente MQTT via WebSockets
client = mqtt.Client(client_id="web_client", transport="websockets")
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado ao MQTT Broker via WebSockets!")
        client.subscribe(TOPIC)
    else:
        print(f"❌ Erro ao conectar: {rc}")

client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER_WS, 8884, 60)
    client.loop_start()
except Exception as e:
    print(f"❌ Erro ao conectar via WebSockets: {e}")

# Iniciar FastAPI
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
