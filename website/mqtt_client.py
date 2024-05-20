import paho.mqtt.client as mqtt

# Global variables to store the latest sensor readings
distance_reading = "0"
flow_rate_reading = "0"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to MQTT broker")
        client.subscribe("sensors/ultrasonic/distance")
        client.subscribe("sensors/water/flow")
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    global distance_reading, flow_rate_reading
    if msg.topic == "sensors/ultrasonic/distance":
        distance_reading = msg.payload.decode("utf-8")
        # print(f"Received distance: {distance_reading} from topic: {msg.topic}")
    elif msg.topic == "sensors/water/flow":
        flow_rate_reading = msg.payload.decode("utf-8")
        # print(f"Received flow rate: {flow_rate_reading} from topic: {msg.topic}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect("test.mosquitto.org", 1883, 360)
client.loop_start()


def get_distance_reading():
    global distance_reading
    return distance_reading


def get_flow_rate_reading():
    global flow_rate_reading
    return flow_rate_reading


def stop_mqtt():
    client.loop_stop()
    client.disconnect()
