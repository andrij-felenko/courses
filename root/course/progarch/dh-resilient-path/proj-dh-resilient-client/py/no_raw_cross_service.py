# arch/no_raw_cross_service.py — фітнес-тест: сирий міжсервісний HTTP дозволено ЛИШЕ в клієнті.
CLIENT = "infra/service_client.py"                          # єдине легальне місце
SERVICES = {"telemetry", "core", "video", "hub", "payments", "push"}


def violations(calls):     # calls: [{"file","line","host","text"}] від сканера
    bad = []
    for c in calls:
        if c["file"] != CLIENT and c["host"] in SERVICES:      # йде в сусідній сервіс повз клієнт
            bad.append(f'{c["file"]}:{c["line"]} — сирий HTTP у «{c["host"]}» повз ServiceClient: {c["text"].strip()}')
    return bad


def main(calls):
    bad = violations(calls)
    if not bad:
        print("усі міжсервісні виклики йдуть крізь клієнт")
        return 0
    print("ЗРАДА КЛІЄНТА DH:")
    for b in bad:
        print("  " + b)
    return 1                        # exit 1 → CI червоний → merge заблоковано
