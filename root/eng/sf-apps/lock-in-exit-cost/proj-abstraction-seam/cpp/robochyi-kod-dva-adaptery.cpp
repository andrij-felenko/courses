// --- логіка домену: жодної згадки про вендора, лише порт ---
void save_receipt(ObjectStore& store, const Order& o) {
    store.put("orders/" + o.id + "/receipt.json", render_receipt(o));
}

std::optional<Order> load_last_order(ObjectStore& store,
                                     const std::string& customer) {
    auto keys = store.list("orders/" + customer + "/");
    if (keys.empty()) return std::nullopt;
    std::sort(keys.begin(), keys.end());          // ключі впорядкуємо самі
    auto bytes = store.get(keys.back());
    return bytes ? std::optional<Order>(parse_order(*bytes)) : std::nullopt;
}
