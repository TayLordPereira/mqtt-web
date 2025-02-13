import asyncio
import websockets
import paho.mqtt.client as mqtt

# Configuração do Broker MQTT
BROKER = "hivemq.cloud"
PORT = 1883
TOPIC = "dice"

# Lista de clientes WebSocket conectados
connected_clients = set()

# Callback quando uma mensagem MQTT chega
def on_message(client, userdata, message):
    msg = message.payload.decode()
    print(f"Recebido MQTT: {msg}")
    asyncio.run(send_to_websocket_clients(msg))

async def send_to_websocket_clients(msg):
    if connected_clients:
        await asyncio.gather(*(client.send(msg) for client in connected_clients))

# Configuração do Cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.subscribe(TOPIC)
mqtt_client.loop_start()

# Servidor WebSocket
async def websocket_handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            pass  # WebSocket escutando MQTT
    finally:
        connected_clients.remove(websocket)

start_server = websockets.serve(websocket_handler, "0.0.0.0", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
