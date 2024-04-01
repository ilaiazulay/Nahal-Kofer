import paho.mqtt.client as mqtt

# Global variable to store the latest sensor reading
sensor_reading = "0"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to MQTT broker")
        client.subscribe("sensors/ultrasonic/distance")
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    global sensor_reading
    sensor_reading = msg.payload.decode("utf-8")
    print(f"Received message: {sensor_reading} from topic: {msg.topic}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect("test.mosquitto.org", 1883, 360)
client.loop_start()


def get_sensor_reading():
    global sensor_reading
    return sensor_reading


def stop_mqtt():
    client.loop_stop()
    client.disconnect()
