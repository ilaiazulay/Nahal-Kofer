import paho.mqtt.client as mqtt
import threading

# Global variables to store the latest sensor readings
distance_reading = "0"
flow_rate_reading = "0"
ph_reading = "7"

# Timer variables
distance_timer = None
flow_timer = None
ph_timer = None

# Timeout duration in seconds
TIMEOUT = 10


def reset_distance():
    global distance_reading
    distance_reading = "1000"


def reset_flow():
    global flow_rate_reading
    flow_rate_reading = "1000"


def reset_ph():
    global ph_reading
    ph_reading = "1000"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to MQTT broker")
        client.subscribe("sensors/ultrasonic/distance")
        client.subscribe("sensors/water/flow")
        client.subscribe("sensors/water/ph")
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    global distance_reading, flow_rate_reading, ph_reading, distance_timer, flow_timer, ph_timer

    if msg.topic == "sensors/ultrasonic/distance":
        distance_reading = msg.payload.decode("utf-8")
        # print(f"Received distance: {distance_reading} from topic: {msg.topic}")
        if distance_timer:
            distance_timer.cancel()
        distance_timer = threading.Timer(TIMEOUT, reset_distance)
        distance_timer.start()

    elif msg.topic == "sensors/water/flow":
        flow_rate_reading = msg.payload.decode("utf-8")
        # print(f"Received flow rate: {flow_rate_reading} from topic: {msg.topic}")
        if flow_timer:
            flow_timer.cancel()
        flow_timer = threading.Timer(TIMEOUT, reset_flow)
        flow_timer.start()

    elif msg.topic == "sensors/water/ph":
        ph_reading = msg.payload.decode("utf-8")
        # print(f"Received ph: {ph_reading} from topic: {msg.topic}")
        if ph_timer:
            ph_timer.cancel()
        ph_timer = threading.Timer(TIMEOUT, reset_ph)
        ph_timer.start()


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


def get_ph_reading():
    global ph_reading
    return ph_reading


def stop_mqtt():
    client.loop_stop()
    client.disconnect()
