import os
import json

class BloomFilter:
    """Простий ймовірнісний фільтр Блума на основі бітового масиву."""
    def __init__(self, size=1024):
        self.size = size
        self.bits = [0] * size

    def _hash1(self, key: str) -> int:
        return hash(key) % self.size

    def _hash2(self, key: str) -> int:
        return (hash(key[::-1]) * 31) % self.size

    def add(self, key: str):
        self.bits[self._hash1(key)] = 1
        self.bits[self._hash2(key)] = 1

    def contains(self, key: str) -> bool:
        return self.bits[self._hash1(key)] == 1 and self.bits[self._hash2(key)] == 1


class SSTable:
    """Представлення незмінного відсортованого файлу SSTable на диску."""
    def __init__(self, filename: str):
        self.filename = filename
        self.index = {}          # key -> offset у файлі
        self.filter = BloomFilter()

    @classmethod
    def create(cls, filename: str, data: dict):
        sst = cls(filename)
        with open(filename, 'w', encoding='utf-8') as f:
            for key in sorted(data.keys()):
                val = data[key]
                offset = f.tell()
                sst.index[key] = offset
                sst.filter.add(key)
                f.write(f"{key}:{val}\n")
        return sst

    def get(self, key: str):
        # 1. Перевірка за допомогою фільтра Блума
        if not self.filter.contains(key):
            return None  # Ключ ТОЧНО відсутній у цьому файлі

        # 2. Пошук індексу
        if key not in self.index:
            return None

        offset = self.index[key]
        with open(self.filename, 'r', encoding='utf-8') as f:
            f.seek(offset)
            line = f.readline().strip()
            if ':' in line:
                k, v = line.split(':', 1)
                return v
        return None


class LSMEngine:
    """Міні-рушій зберігання даних на основі LSM-дерева."""
    TOMBSTONE = "__TOMBSTONE__"

    def __init__(self, db_dir: str = "./lsm_demo_py", max_mem_size: int = 3):
        self.db_dir = db_dir
        self.max_mem_size = max_mem_size
        self.memtable = {}
        self.sstables = []
        self.sst_counter = 0

        os.makedirs(self.db_dir, exist_ok=True)
        self.wal_path = os.path.join(self.db_dir, "wal.log")
        self.wal_file = open(self.wal_path, "a", encoding="utf-8")

    def _flush(self):
        if not self.memtable:
            return
        self.sst_counter += 1
        sst_path = os.path.join(self.db_dir, f"sst_{self.sst_counter}.db")
        sst = SSTable.create(sst_path, self.memtable)
        self.sstables.insert(0, sst)  # Найновіші файли попереду

        self.memtable.clear()
        self.wal_file.close()
        self.wal_file = open(self.wal_path, "w", encoding="utf-8")  # Очищення WAL
        print(f"[Flush] MemTable скинуто на диск -> {sst_path}")

    def put(self, key: str, value: str):
        # Запис у WAL
        self.wal_file.write(f"PUT:{key}:{value}\n")
        self.wal_file.flush()

        # Запис у MemTable
        self.memtable[key] = value
        if len(self.memtable) >= self.max_mem_size:
            self._flush()

    def delete(self, key: str):
        self.put(key, self.TOMBSTONE)

    def get(self, key: str) -> str:
        # 1. Шукаємо в MemTable
        if key in self.memtable:
            val = self.memtable[key]
            if val == self.TOMBSTONE:
                return "[NOT FOUND (Deleted)]"
            return f"{val} (Found in MemTable)"

        # 2. Шукаємо у SSTables (від найновішої до найстарішої)
        for sst in self.sstables:
            val = sst.get(key)
            if val is not None:
                if val == self.TOMBSTONE:
                    return "[NOT FOUND (Deleted)]"
                return f"{val} (Found in {sst.filename})"

        return "[NOT FOUND]"


if __name__ == "__main__":
    db = LSMEngine(db_dir="./lsm_demo_py", max_mem_size=3)

    print("--- Запис даних ---")
    db.put("sensor_1", "22.5C")
    db.put("sensor_2", "1013hPa")
    db.put("sensor_3", "55%")  # Flush #1 -> sst_1.db

    db.put("sensor_4", "0.05m/s")
    db.put("sensor_2", "1015hPa") # Оновлення
    db.delete("sensor_1")        # Tombstone

    print("\n--- Запити (GET) ---")
    print("sensor_3:", db.get("sensor_3"))
    print("sensor_2:", db.get("sensor_2"))
    print("sensor_1:", db.get("sensor_1"))
    print("sensor_999:", db.get("sensor_999"))
