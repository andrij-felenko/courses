// Концептуальний псевдокод того, що генерує компілятор для: Widget* w = new Widget(42);
Widget* w = nullptr;
void* raw_memory = ::operator new(sizeof(Widget)); // Крок 1: виділення пам'яті

try {
    // Крок 2: виклик конструктора на отриманій сирій пам'яті
    w = static_cast<Widget*>(raw_memory);
    w->Widget::Widget(42); // виклик конструктора
} catch (...) {
    // Автоматичний відкат: звільнення сирої пам'яті, якщо конструктор дав збій
    ::operator delete(raw_memory);
    throw; // ретрансляція спійманого винятку
}
