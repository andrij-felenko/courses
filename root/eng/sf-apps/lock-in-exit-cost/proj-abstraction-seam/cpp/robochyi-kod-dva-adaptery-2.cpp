#include <memory>

enum class Vendor { A, B };

// Єдине місце, що знає обидва адаптери. Уся решта коду бачить лише
// ObjectStore. Переїзд на іншого вендора = змінити конфіг, а не логіку.
std::unique_ptr<ObjectStore> make_store(Vendor v, const std::string& target) {
    switch (v) {
        case Vendor::A: return std::make_unique<VendorAStore>(target);
        case Vendor::B: return std::make_unique<VendorBStore>(target);
    }
    throw StoreError("unknown vendor");
}

int main() {
    auto store = make_store(Vendor::A, "orders-bucket");  // ← лише тут
    // Переїзд на B: make_store(Vendor::B, "orders-container").
    // save_receipt / load_last_order не змінюються ВЗАГАЛІ.
    save_receipt(*store, some_order);
}
