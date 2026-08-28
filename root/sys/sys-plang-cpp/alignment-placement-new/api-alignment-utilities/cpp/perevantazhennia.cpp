struct alignas(64) CacheAlignedBlock {
    int counter;
    char payload[60];
};

// Компілятор C++17 транслює цей рядок у:
// operator new(sizeof(CacheAlignedBlock), std::align_val_t(64))
CacheAlignedBlock* p = new CacheAlignedBlock();

// Транслюється у:
// operator delete(p, sizeof(CacheAlignedBlock), std::align_val_t(64))
delete p;
