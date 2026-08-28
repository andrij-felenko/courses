#include <iostream>
#include <cstdint>
#include <span>

void executeDistributedWorkerCpp(uint32_t myNodeId) {
    DsmEngineConfig config{
        .sharedHeapSize = 1024 * 1024 * 16,
        .nodeId = myNodeId,
        .totalNodes = 2,
        .enableSimdAcceleration = true
    };

    // Приклад виклику C++ обгортки середовища
    if (dsm_init(reinterpret_cast<const dsm_config_t*>(&config)) != DSM_SUCCESS) {
        std::cerr << "Не вдалося ініціалізувати середовище DSM\n";
        return;
    }

    auto* memoryBlock = static_cast<uint64_t*>(dsm_alloc_shared(8192));
    if (memoryBlock == nullptr) {
        dsm_destroy();
        return;
    }

    std::span<uint64_t> sharedArray{memoryBlock, 8192 / sizeof(uint64_t)};

    dsm_barrier(0);

    if (myNodeId == 0) {
        dsm_lock_acquire(100);
        sharedArray[0] = 0xDEADBEEFCAFEBABEULL;
        dsm_lock_release(100);
    } else if (myNodeId == 1) {
        dsm_lock_acquire(200);
        sharedArray[10] = 0x0123456789ABCDEFULL;
        dsm_lock_release(200);
    }

    dsm_barrier(1);

    dsm_free_shared(memoryBlock);
    dsm_destroy();
}
