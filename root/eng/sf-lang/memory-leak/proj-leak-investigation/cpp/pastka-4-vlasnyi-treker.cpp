#include <iostream>
#include <vector>
#include <string_view>
#include <source_location>

struct AllocationInfo {
    void *address{nullptr};
    std::size_t bytes{0};
    std::string_view filename;
    std::uint32_t line_number{0};
};

class EmbeddedLeakTracker {
    static inline std::vector<AllocationInfo> records;
public:
    static void *track_alloc(std::size_t size, const std::source_location loc = std::source_location::current()) {
        void *p = std::malloc(size);
        if (p) {
            records.push_back({ p, size, loc.file_name(), loc.line() });
        }
        return p;
    }

    static void track_free(void *p) noexcept {
        if (!p) return;
        for (auto it = records.begin(); it != records.end(); ++it) {
            if (it->address == p) {
                records.erase(it);
                break;
            }
        }
        std::free(p);
    }

    static void report() {
        if (records.empty()) {
            std::cout << "[C++ Трекер] Усі ресурси чисто повернуто.\n";
            return;
        }
        std::cout << "[C++ Трекер] Виявлено " << records.size() << " витоків:\n";
        for (const auto &rec : records) {
            std::cout << "  - " << rec.bytes << " байтів у " 
                      << rec.filename << ":" << rec.line_number << "\n";
        }
    }
};

int main() {
    void *chunk1 = EmbeddedLeakTracker::track_alloc(64);
    void *chunk2 = EmbeddedLeakTracker::track_alloc(128);
    EmbeddedLeakTracker::track_free(chunk1);
    // chunk2 не звільняється
    EmbeddedLeakTracker::report();
    EmbeddedLeakTracker::track_free(chunk2);
    return 0;
}
