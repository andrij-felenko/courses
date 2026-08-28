#include "splay_tree.hpp"
#include <iostream>

int main() {
    SplayTree<int, std::string> dns_cache;

    dns_cache.insert(101, "gateway.local");
    dns_cache.insert(202, "auth.internal");
    dns_cache.insert(303, "db.primary");

    // Гарячий доступ
    if (auto host = dns_cache.find(202)) {
        std::cout << "Хост знайдено: " << *host << "\n";
    }

    dns_cache.erase(101);
    return 0;
}
