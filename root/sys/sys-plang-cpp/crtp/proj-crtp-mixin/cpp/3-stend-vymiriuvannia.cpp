int main() {
    constexpr size_t ITERATIONS = 10'000'000;
    std::vector<uint8_t> buffer(1024);

    // ----------------------------------------------------
    // 1. БЕНЧМАРК CRTP STATIC DISPATCH
    // ----------------------------------------------------
    {
        OrderSingle order{1001, 5005, 150.50, 100, 1};
        volatile uint32_t dummy_sum = 0;

        auto start = std::chrono::high_resolution_clock::now();
        for (size_t i = 0; i < ITERATIONS; ++i) {
            order.order_id = i + 1;
            if (order.validate()) {
                dummy_sum += order.compute_checksum();
                order.serialize_to(buffer.data());
            }
        }
        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> elapsed = end - start;
        std::cout << "CRTP Static Dispatch Time: " << elapsed.count() << " ms\n";
    }

    // ----------------------------------------------------
    // 2. БЕНЧМАРК VIRTUAL DISPATCH
    // ----------------------------------------------------
    {
        VirtualOrderSingle v_order_obj;
        IVirtualProcessor* v_order = &v_order_obj;
        v_order_obj.order_id = 1001;
        v_order_obj.account_id = 5005;
        v_order_obj.price = 150.50;
        v_order_obj.quantity = 100;
        v_order_obj.side = 1;
        volatile uint32_t dummy_sum = 0;

        auto start = std::chrono::high_resolution_clock::now();
        for (size_t i = 0; i < ITERATIONS; ++i) {
            v_order_obj.order_id = i + 1;
            if (v_order->validate()) {
                dummy_sum += v_order->compute_checksum();
                v_order->serialize_to(buffer.data());
            }
        }
        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> elapsed = end - start;
        std::cout << "Virtual Dynamic Dispatch Time: " << elapsed.count() << " ms\n";
    }

    return 0;
}
