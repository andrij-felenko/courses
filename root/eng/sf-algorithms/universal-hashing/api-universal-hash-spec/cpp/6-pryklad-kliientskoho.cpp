#include <iostream>

void client_example_cpp() {
    universal_hashing::Config cfg{
        .family = universal_hashing::FamilyType::MultiplyShift,
        .num_buckets = 2048,
        .use_custom_seed = false
    };

    auto hasher_res = universal_hashing::create_hasher(cfg);
    if (!hasher_res) {
        std::cerr << "Помилка створення хешера: " << hasher_res.error().message() << "\n";
        return;
    }

    const auto& hasher = *hasher_res;
    uint64_t key = 0xDEADBEEFCAFEBABEULL;
    uint64_t hash_val = hasher->hash(key);

    std::cout << "Ключ 0x" << std::hex << key << " -> Хеш-індекс: " << std::dec << hash_val << "\n";
}
