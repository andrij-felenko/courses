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
