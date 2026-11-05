#include <atomic>
#include <array>
#include <vector>
#include <cassert>

constexpr size_t MAX_THREADS = 128;

struct HazardPointer {
    std::atomic<std::thread::id> owner;
    std::atomic<void*> pointer;
};

extern std::array<HazardPointer, MAX_THREADS> g_hazard_pointers;

template <typename T>
class HazardPointerProtector {
private:
    HazardPointer* hp_slot = nullptr;

public:
    HazardPointerProtector() {
        // Пошук вільного слота для поточного потоку
        auto tid = std::this_thread::get_id();
        for (auto& hp : g_hazard_pointers) {
            std::thread::id expected;
            if (hp.owner.compare_exchange_strong(expected, tid, std::memory_order_relaxed)) {
                hp_slot = &hp;
                break;
            }
        }
        assert(hp_slot != nullptr && "Переповнення масиву Hazard Pointers");
    }

    ~HazardPointerProtector() {
        if (hp_slot) {
            hp_slot->pointer.store(nullptr, std::memory_order_release);
            hp_slot->owner.store(std::thread::id(), std::memory_order_release);
        }
    }

    T* protect(std::atomic<T*>& atomic_src) {
        T* ptr = nullptr;
        do {
            ptr = atomic_src.load(std::memory_order_relaxed);
            hp_slot->pointer.store(ptr, std::memory_order_seq_cst);
        } while (atomic_src.load(std::memory_order_acquire) != ptr);
        return ptr;
    }
};

template <typename T>
void retire_node(T* node) {
    static thread_local std::vector<T*> retired_list;
    retired_list.push_back(node);

    if (retired_list.size() >= 32) { // Поріг сканування
        std::vector<void*> active_hps;
        for (auto& hp : g_hazard_pointers) {
            void* p = hp.pointer.load(std::memory_order_acquire);
            if (p) active_hps.push_back(p);
        }

        auto it = retired_list.begin();
        while (it != retired_list.end()) {
            bool is_hazard = false;
            for (void* active_p : active_hps) {
                if (*it == active_p) {
                    is_hazard = true;
                    break;
                }
            }
            if (!is_hazard) {
                delete *it;
                it = retired_list.erase(it);
            } else {
                ++it;
            }
        }
    }
}
