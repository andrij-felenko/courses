#include <iostream>
#include <fstream>
#include <string>
#include <unordered_map>
#include <chrono>
#include <vector>
#include <optional>

namespace mini_nosql {

struct KeyDirEntry {
    std::streampos value_offset;
    uint32_t value_size;
    uint64_t timestamp;
};

class MiniKVStore {
public:
    explicit MiniKVStore(const std::string& filename) : filename_(filename) {
        file_.open(filename_, std::ios::in | std::ios::out | std::ios::binary | std::ios::app);
        if (!file_.is_open()) {
            // Створення файлу, якщо не існує
            file_.open(filename_, std::ios::out | std::ios::binary);
            file_.close();
            file_.open(filename_, std::ios::in | std::ios::out | std::ios::binary | std::ios::app);
        }
    }

    ~MiniKVStore() {
        if (file_.is_open()) {
            file_.close();
        }
    }

    void set(const std::string& key, const std::string& value) {
        file_.seekp(0, std::ios::end);
        std::streampos record_pos = file_.tellp();

        uint64_t ts = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        uint16_t klen = static_cast<uint16_t>(key.size());
        uint32_t vlen = static_cast<uint32_t>(value.size());

        // Запис заголовка та даних строго послідовно
        file_.write(reinterpret_cast<const char*>(&ts), sizeof(ts));
        file_.write(reinterpret_cast<const char*>(&klen), sizeof(klen));
        file_.write(reinterpret_cast<const char*>(&vlen), sizeof(vlen));
        file_.write(key.data(), klen);
        file_.write(value.data(), vlen);
        file_.flush();

        std::streampos val_pos = record_pos + static_cast<std::streamoff>(sizeof(ts) + sizeof(klen) + sizeof(vlen) + klen);

        // Оновлення індексу в пам'яті
        keydir_[key] = {val_pos, vlen, ts};
    }

    std::optional<std::string> get(const std::string& key) {
        auto it = keydir_.find(key);
        if (it == keydir_.end()) {
            return std::nullopt;
        }

        file_.seekg(it->second.value_offset);
        std::string result(it->second.value_size, '\0');
        file_.read(&result[0], it->second.value_size);

        return result;
    }

    bool remove(const std::string& key) {
        auto it = keydir_.find(key);
        if (it == keydir_.end()) return false;

        file_.seekp(0, std::ios::end);
        uint64_t ts = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        uint16_t klen = static_cast<uint16_t>(key.size());
        uint32_t vlen = 0; // Tombstone

        file_.write(reinterpret_cast<const char*>(&ts), sizeof(ts));
        file_.write(reinterpret_cast<const char*>(&klen), sizeof(klen));
        file_.write(reinterpret_cast<const char*>(&vlen), sizeof(vlen));
        file_.write(key.data(), klen);
        file_.flush();

        keydir_.erase(it);
        return true;
    }

private:
    std::string filename_;
    std::fstream file_;
    std::unordered_map<std::string, KeyDirEntry> keydir_;
};

} // namespace mini_nosql
