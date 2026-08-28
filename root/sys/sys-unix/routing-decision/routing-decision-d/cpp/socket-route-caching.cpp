#include <atomic>

// Опис кешу маршруту в сокеті C++ з використанням атомарного вказівника std::atomic
namespace net::kernel_sim {
    struct DstEntry;

    struct Sock {
        // У C++ кешований маршрут зберігається як атомарний або безпечний вказівник
        std::atomic<const DstEntry*> sk_dst_cache{nullptr};
    };
}
