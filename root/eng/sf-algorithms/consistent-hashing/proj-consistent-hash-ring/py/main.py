import hashlib
import bisect
from typing import Dict, List, Optional

class ConsistentHashRing:
    def __init__(self, num_vnodes: int = 100):
        """
        Ініціалізація кільця консистентного хешування.
        :param num_vnodes: Кількість віртуальних вузлів на кожен фізичний сервер.
        """
        self.num_vnodes = num_vnodes
        self.ring: Dict[int, str] = {}         # vnode_hash -> physical_node_id
        self.sorted_keys: List[int] = []        # Впорядкований список хешів vnodes
        self.physical_nodes: set = set()

    def _hash(self, key: str) -> int:
        """32-бітний хеш на основі MD5 для рівномірного розсіювання."""
        md5_hex = hashlib.md5(key.encode('utf-8')).hexdigest()
        # Беремо перші 8 шістнадцяткових символів (32 біти)
        return int(md5_hex[:8], 16)

    def add_node(self, node_id: str) -> None:
        """Додає фізичний вузол із створенням V віртуальних вузлів."""
        if node_id in self.physical_nodes:
            return
        self.physical_nodes.add(node_id)

        for i in range(self.num_vnodes):
            vnode_key = f"{node_id}#vnode{i}"
            vnode_hash = self._hash(vnode_key)
            self.ring[vnode_hash] = node_id
            bisect.insort(self.sorted_keys, vnode_hash)

    def remove_node(self, node_id: str) -> None:
        """Вилучає фізичний вузол та всі його vnodes з кільця."""
        if node_id not in self.physical_nodes:
            return
        self.physical_nodes.remove(node_id)

        for i in range(self.num_vnodes):
            vnode_key = f"{node_id}#vnode{i}"
            vnode_hash = self._hash(vnode_key)
            if vnode_hash in self.ring:
                del self.ring[vnode_hash]
                idx = bisect.bisect_left(self.sorted_keys, vnode_hash)
                if idx < len(self.sorted_keys) and self.sorted_keys[idx] == vnode_hash:
                    del self.sorted_keys[idx]

    def get_node(self, key: str) -> Optional[str]:
        """
        Знаходить відповідальний вузол для заданого ключа.
        Шукає найближчий vnode за годинниковою стрілкою за O(log M).
        """
        if not self.ring:
            return None

        key_hash = self._hash(key)
        # Двійковий пошук першого vnode_hash >= key_hash
        idx = bisect.bisect_left(self.sorted_keys, key_hash)

        # Замикання кільця (wrap-around)
        if idx == len(self.sorted_keys):
            idx = 0

        target_vnode_hash = self.sorted_keys[idx]
        return self.ring[target_vnode_hash]


# Демонстраційна програма
if __name__ == "__main__":
    # Створюємо кільце з 150 vnodes на сервер
    ch = ConsistentHashRing(num_vnodes=150)

    # 1. Додаємо 3 сервери
    servers = ["Node-Alpha", "Node-Beta", "Node-Gamma"]
    for s in servers:
        ch.add_node(s)

    print(f"Кільце створено: {len(servers)} серверів, {len(ch.sorted_keys)} vnodes.")

    # 2. Розподіляємо 10,000 ключів
    num_keys = 10000
    initial_mapping = {}
    stats: Dict[str, int] = {s: 0 for s in servers}

    for i in range(num_keys):
        key = f"cache_key_user_{i}"
        node = ch.get_node(key)
        initial_mapping[key] = node
        stats[node] += 1

    print("\n--- Початковий розподіл навантаження ---")
    for s, count in stats.items():
        print(f"{s}: {count} ключів ({count / num_keys * 100:.2f}%)")

    # 3. Додаємо 4-й сервер Node-Delta
    print("\n>>> Додаємо новий сервер Node-Delta...")
    ch.add_node("Node-Delta")

    remapped_keys = 0
    new_stats: Dict[str, int] = {s: 0 for s in servers + ["Node-Delta"]}

    for key, old_node in initial_mapping.items():
        new_node = ch.get_node(key)
        new_stats[new_node] += 1
        if new_node != old_node:
            remapped_keys += 1

    print("\n--- Розподіл після додавання Node-Delta ---")
    for s, count in new_stats.items():
        print(f"{s}: {count} ключів ({count / num_keys * 100:.2f}%)")

    print(f"\nРебалансовано ключів: {remapped_keys} з {num_keys} ({remapped_keys / num_keys * 100:.2f}%)")
    print(f"Теоретичний мінімум 1/(N+1) = 1/4 = 25.0%")
