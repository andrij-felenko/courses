alignas(Widget) std::byte buffer[sizeof(Widget)];

// Створюємо перший екземпляр
Widget* w1 = ::new (buffer) Widget("Перший об'єкт");
w1->process();
w1->~Widget(); // завершуємо час життя першого об'єкта

// У тому самому буфері конструюємо другий екземпляр
Widget* w2 = ::new (buffer) Widget("Другий об'єкт");
w2->process();
w2->~Widget(); // завершуємо час життя другого об'єкта
