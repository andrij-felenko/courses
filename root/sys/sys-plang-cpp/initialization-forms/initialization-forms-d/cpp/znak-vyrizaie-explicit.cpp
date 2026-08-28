struct Meters {
    explicit Meters(double v) : value(v) {}
    double value;
};

void fly(Meters altitude);

Meters a(100.0);      // ok:     пряма — розглядають усі конструктори
Meters b = 100.0;     // ПОМИЛКА: копіювальна — explicit не потрапив у кандидати
fly(100.0);           // ПОМИЛКА: з тієї ж причини
fly(Meters(100.0));   // ok:     конструктор названо явно
