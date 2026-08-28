# Двоє дверей — двоє тонких адаптерів на ОДИН сервіс. Логіки в них нема.

def run_loop(hub: HubService) -> None:          # двері 1: автономний цикл
    while True:
        hub.tick()                              # єдиний виклик — сценарій tick
        sleep(30)

def run_cli(hub: HubService, argv: list[str]) -> None:   # двері 2: команда в терміналі
    match argv:
        case ["state"]:            print(hub.state())
        case ["set-threshold", c]: hub.set_threshold(float(c))
        case ["add", kind, room]:  hub.add_device(Device(kind, room))
