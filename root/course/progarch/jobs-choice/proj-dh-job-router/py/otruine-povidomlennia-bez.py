sys = make_system()
for i in range(4):
    sys.broker.put(Job("notify", {"i": i}, f"n-{i}"))

processed: set[str] = set()
attempts = 0


def handle(job):
    global attempts
    attempts += 1
    if job.payload["i"] == 2:
        raise RuntimeError("otruta: несправний payload")
    if job.key in processed:                          # ідемпотентність: дубль — нічого
        return
    processed.add(job.key)


sys.broker.deliver("notify", handle)
print("оброблено:", len(processed), " спроб:", attempts, " DLQ:", len(sys.broker.dlq))
