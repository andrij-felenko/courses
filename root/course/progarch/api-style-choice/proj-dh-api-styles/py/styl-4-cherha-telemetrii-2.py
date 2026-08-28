def on_message(_client, _userdata, msg) -> None:
    r = json.loads(msg.payload)
    dev = msg.topic.split("/")[3]
    store_reading(dev, r["v"], r["at"])   # МУСИТЬ бути ідемпотентним — див. нижче

ingest = mqtt.Client(client_id="ingest-1")
ingest.on_message = on_message
ingest.connect("broker.digitalhomes.io", 1883)
ingest.subscribe("dh/home/+/+/reading", qos=1)   # + — універсал на один рівень теми
ingest.loop_forever()
