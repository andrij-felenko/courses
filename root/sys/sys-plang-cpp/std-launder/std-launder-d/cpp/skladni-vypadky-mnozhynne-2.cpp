void test_multiple_inheritance() {
    alignas(Derived) std::byte storage[sizeof(Derived)];
    
    auto* d1 = new (storage) Derived();
    Base2* b2 = d1; // b2 вказує на середину буфера storage (storage + offset)

    d1->~Derived();
    auto* d2 = new (storage) Derived();

    // Чи дійсний b2?
    // Ні! Тип Derived має нетривіальну структуру, а d2 замінив увесь об'єкт.
    // Звернення b2->g() без оновлення адреси або без std::launder є UB.
    
    Base2* valid_b2 = std::launder(reinterpret_cast<Base2*>(
        reinterpret_cast<std::byte*>(storage) + sizeof(Base1)
    ));
    valid_b2->g();
}
