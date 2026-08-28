#include <new>
#include <cstddef>
#include <iostream>

struct VariableSizedNode {
    std::size_t payload_size;

    // Класова функція деалокації зі спеціальним маркером destroying_delete_t
    static void operator delete(VariableSizedNode* ptr, std::destroying_delete_t) noexcept {
        std::cout << "Перехоплено знищення: розмір корисного навантаження = " << ptr->payload_size << '\n';
        
        // Розробник САМ зобов'язаний явно викликати деструктор!
        std::size_t total_bytes = sizeof(VariableSizedNode) + ptr->payload_size;
        ptr->~VariableSizedNode();

        // Звільнення блоку пам'яті потрібного динамічного розміру
        ::operator delete(static_cast<void*>(ptr), total_bytes);
    }
};
