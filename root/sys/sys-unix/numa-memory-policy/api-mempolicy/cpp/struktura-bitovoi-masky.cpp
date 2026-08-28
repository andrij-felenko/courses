#include <numa.h>
#include <memory>
#include <iostream>

struct BitmaskDeleter {
    void operator()(struct bitmask* bm) const noexcept {
        if (bm) {
            numa_free_nodemask(bm);
        }
    }
};

using UniqueBitmask = std::unique_ptr<struct bitmask, BitmaskDeleter>;

inline UniqueBitmask make_node_mask(std::initializer_list<unsigned int> node_ids) {
    UniqueBitmask mask(numa_allocate_nodemask());
    if (!mask) {
        throw std::bad_alloc();
    }
    for (unsigned int node : node_ids) {
        numa_bitmask_setbit(mask.get(), node);
    }
    return mask;
}
