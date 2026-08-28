struct Element {
    const int val;
};

void array_example() {
    alignas(Element) std::byte storage[sizeof(Element) * 2];

    auto* e0 = new (storage + 0 * sizeof(Element)) Element{10};
    auto* e1 = new (storage + 1 * sizeof(Element)) Element{20};

    // Отримання вказівника на перший елемент
    Element* p0 = std::launder(reinterpret_cast<Element*>(storage));
    
    // Чи можна робити p0 + 1 для доступу до другого елемента?
    // За стандартом C++: так, якщо p0 вказує на елемент масиву Element[2].
    // Але якщо об'єкти створювалися окремо у сирому буфері std::byte[],
    // вони формально не утворюють єдиний масив Element[2] до C++20!
    // Безпечний підхід:
    Element* p1 = std::launder(reinterpret_cast<Element*>(storage + sizeof(Element)));
}
