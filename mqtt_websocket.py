import paho.mqtt.client as mqtt
import ssl

# Configuração do Broker MQTT
BROKER = "7f054615a7ef47f78f9f2892dbc87eac.s1.eu.hivemq.cloud"
PORT = 8883
TOPIC = "dice"
USERNAME = "dicewebbroker"
PASSWORD = "Dicewebbroker1"

# Configurar cliente MQTT com autenticação e TLS
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado ao MQTT Broker!")
        client.subscribe(TOPIC)
    else:
        print(f"❌ Erro ao conectar, código: {rc}")

client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)  # Usa TLS sem verificação de certificado
client.on_connect = on_connect

client.connect(BROKER, PORT, 60)

client.loop_forever()
