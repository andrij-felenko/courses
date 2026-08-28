#include <numa.h>
#include <iostream>
#include <memory>
#include <stdexcept>

// Безпечна RAII-обгортка для struct bitmask
struct BitmaskDeleter {
    void operator()(bitmask* bm) const noexcept {
        if (bm) numa_bitmask_free(bm);
    }
};
using ScopedBitmask = std::unique_ptr<bitmask, BitmaskDeleter>;

ScopedBitmask make_scoped_nodemask() {
    bitmask* bm = numa_allocate_nodemask();
    if (!bm) throw std::bad_alloc();
    return ScopedBitmask(bm);
}

void configure_nodes_cpp() {
    auto nodes = make_scoped_nodemask();
    numa_bitmask_clearall(nodes.get());
    numa_bitmask_setbit(nodes.get(), 0);
    numa_bitmask_setbit(nodes.get(), 2);

    if (numa_bitmask_isbitset(nodes.get(), 0)) {
        std::cout << "Node 0 обрано для виділення пам'яті\n";
    }
}
