import random

if __name__ == "__main__":
    cluster = [
        PNCounter("node-0"),
        PNCounter("node-1"),
        PNCounter("node-2")
    ]

    cluster[0].increment(15)
    cluster[0].decrement(3)  # Net: +12

    cluster[1].increment(8)
    cluster[1].decrement(2)  # Net: +6

    cluster[2].increment(30)
    cluster[2].decrement(10)  # Net: +20

    network_queue = []
    for i in range(len(cluster)):
        for j in range(len(cluster)):
            if i != j:
                # Додаємо повідомлення та його дублікати
                network_queue.append((i, j, cluster[i]))
                if (i + j) % 2 == 0:
                    network_queue.append((i, j, cluster[i]))

    # Хаотичне перемішування черги
    random.seed(42)
    random.shuffle(network_queue)

    # Доставка пакетів
    for from_node, to_node, payload in network_queue:
        cluster[to_node].merge(payload)

    expected = 38
    converged = all(node.value == expected for node in cluster)
    for i, node in enumerate(cluster):
        print(f"Вузол {i} стан: {node.value}")

    if converged:
        print("Успіх: усі репліки детерміновано зійшлися завдяки напіврешітці.")
