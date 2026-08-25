# ⚙️ Практичний міні-рушій LSM-tree: MemTable, WAL та SSTable з фільтром Блума

У цій практичній вставці ми реалізуємо працюючий мініатюрний рушій зберігання даних типу Key-Value на основі архітектури **LSM-tree**.

---

## 1. Архітектурна схема міні-рушія

Наш рушій підтримує базові операції `put(key, value)`, `get(key)` та `del(key)` і складається з чотирьох основних компонентів:

1. **MemTable:** Впорядкований словник в оперативній пам'яті (у C++ — `std::map`, у Python — `dict` з додатковим сортуванням), що накопичує нові записи.
2. **WAL (Write-Ahead Log):** Дисковий журнал, куди кожна операція дописується послідовно перед зміною MemTable для гарантії стійкості при збоях (Durability).
3. **SSTable (Sorted String Table):** Незмінний дисковий файл, у який dампиться заповнений MemTable. Файл містить блок даних зі сортованими парами та індексний блок офсетів для швидкого двійкового пошуку.
4. **Bloom Filter:** Ймовірнісний бітовий масив для кожної SSTable, який з імовірністю 100% каже, якщо ключ **точно відсутній** у файлі, позбавляючи дискових читань.
5. **Маркер видалення (Tombstone):** Операція видалення `del(key)` записує у MemTable спеціальне значення-надгробок `__TOMBSTONE__`.

---

## 2. Реалізація C++ та Python

Нижче наведено повну вихідну реалізацію міні-рушія двома мовами у вкладках `:::tabs`. Кожна реалізація є самодостатньою, містить реальний код та приклад запуску.

:::tabs
```cpp
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <memory>
#include <algorithm>
#include <filesystem>

namespace fs = std::filesystem;

// ── 1. Простий фільтр Блума ──────────────────────────────────────────────────
class BloomFilter {
private:
    size_t size_;
    std::vector<bool> bits_;

    size_t hash1(const std::string& key) const {
        size_t h = 14695981039346656037ULL;
        for (char c : key) h = (h ^ c) * 1099511628211ULL;
        return h % size_;
    }

    size_t hash2(const std::string& key) const {
        size_t h = 0;
        for (char c : key) h = (h * 31) + c;
        return h % size_;
    }

public:
    explicit BloomFilter(size_t size = 1024) : size_(size), bits_(size, false) {}

    void add(const std::string& key) {
        bits_[hash1(key)] = true;
        bits_[hash2(key)] = true;
    }

    bool contains(const std::string& key) const {
        return bits_[hash1(key)] && bits_[hash2(key)];
    }
};

// ── 2. Представлення окремої SSTable на диску ────────────────────────────────
class SSTable {
public:
    std::string filename;
    BloomFilter filter;
    std::map<std::string, std::streamoff> index; // Індекс: key -> offset у файлі

    SSTable(std::string fname) : filename(std::move(fname)) {}

    static std::shared_ptr<SSTable> create(const std::string& fname, 
                                           const std::map<std::string, std::string>& data) {
        auto sst = std::make_shared<SSTable>(fname);
        std::ofstream out(fname, std::ios::binary);

        for (const auto& [k, v] : data) {
            std::streamoff offset = out.tellp();
            sst->index[k] = offset;
            sst->filter.add(k);
            out << k << ":" << v << "\n";
        }
        return sst;
    }

    bool get(const std::string& key, std::string& value) const {
        if (!filter.contains(key)) return false; // Пропущено завдяки Bloom Filter!

        auto it = index.find(key);
        if (it == index.end()) return false;

        std::ifstream in(filename, std::ios::binary);
        in.seekg(it->second);
        std::string line;
        if (std::getline(in, line)) {
            auto pos = line.find(':');
            if (pos != std::string::npos) {
                value = line.substr(pos + 1);
                return true;
            }
        }
        return false;
    }
};

// ── 3. Головний рушій LSM-Tree ───────────────────────────────────────────────
class LSMEngine {
private:
    const std::string TOMBSTONE = "__TOMBSTONE__";
    size_t max_mem_size_;
    std::string db_dir_;
    std::string wal_filename_;
    std::ofstream wal_stream_;
    std::map<std::string, std::string> memtable_;
    std::vector<std::shared_ptr<SSTable>> sstables_;
    int sst_counter_ = 0;

    void flush() {
        if (memtable_.empty()) return;
        std::string sst_name = db_dir_ + "/sst_" + std::to_string(++sst_counter_) + ".db";
        auto sst = SSTable::create(sst_name, memtable_);
        sstables_.insert(sstables_.begin(), sst); // Нові файли на початок списку

        memtable_.clear();
        wal_stream_.close();
        wal_stream_.open(wal_filename_, std::ios::out | std::ios::trunc); // Очищення WAL
        std::cout << "[Flush] MemTable скинуто в " << sst_name << "\n";
    }

public:
    LSMEngine(std::string dir, size_t max_mem_size = 3)
        : max_mem_size_(max_mem_size), db_dir_(std::move(dir)) {
        fs::create_directories(db_dir_);
        wal_filename_ = db_dir_ + "/wal.log";
        wal_stream_.open(wal_filename_, std::ios::app);
    }

    void put(const std::string& key, const std::string& value) {
        wal_stream_ << "PUT:" << key << ":" << value << "\n";
        wal_stream_.flush();

        memtable_[key] = value;
        if (memtable_.size() >= max_mem_size_) {
            flush();
        }
    }

    void del(const std::string& key) {
        put(key, TOMBSTONE);
    }

    std::string get(const std::string& key) {
        // 1. Пошук у MemTable
        auto it = memtable_.find(key);
        if (it != memtable_.end()) {
            if (it->second == TOMBSTONE) return "[NOT FOUND (Deleted)]";
            return it->second + " (Found in MemTable)";
        }

        // 2. Пошук у SSTables від найновішої до найстарішої
        for (const auto& sst : sstables_) {
            std::string val;
            if (sst->get(key, val)) {
                if (val == TOMBSTONE) return "[NOT FOUND (Deleted)]";
                return val + " (Found in " + sst->filename + ")";
            }
        }
        return "[NOT FOUND]";
    }
};

int main() {
    LSMEngine db("./lsm_demo_cpp", 3);

    std::cout << "--- Запис даних у LSM Engine ---\n";
    db.put("user_101", "Alice");
    db.put("user_102", "Bob");
    db.put("user_103", "Charlie"); // Призведе до Flush #1

    db.put("user_104", "Diana");
    db.put("user_102", "Bob_Updated"); // Оновлення значення
    db.del("user_101");                // Видалення через Tombstone

    std::cout << "\n--- Запити на читання (GET) ---\n";
    std::cout << "user_103: " << db.get("user_103") << "\n";
    std::cout << "user_102: " << db.get("user_102") << "\n";
    std::cout << "user_101: " << db.get("user_101") << "\n";
    std::cout << "user_999: " << db.get("user_999") << "\n";

    return 0;
}
```
```py
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
```
:::

---

## 3. Аналіз роботи та ключові нюанси

1. **Ефективність запису:** Операція `put()` виконує лише дві низькозатратні дії: дописує один рядок у кінець `wal.log` та вставляє вузол у `MemTable`. Затримка запису залишається сталою `O(1)` незалежно від загального обсягу бази даних.
2. **Точкове читання та Bloom Filter:** При виконанні `get("sensor_999")` система не звертається до диска для читання файлів SSTable, оскільки `filter.contains("sensor_999")` відразу повертає `false`.
3. **Очищення надгробків (Tombstone Garbage Collection):** Маркери видалення `__TOMBSTONE__` залишаються у SSTables до тих пір, поки фоновий процес ущільнення (Compaction) не об'єднає всі рівні SSTable і не вилучить ключ остаточно.
