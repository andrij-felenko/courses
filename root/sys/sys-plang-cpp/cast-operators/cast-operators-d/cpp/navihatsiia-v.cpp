struct BaseA { int a; };
struct BaseB { int b; };
struct Derived : BaseA, BaseB { int c; };

Derived obj;
BaseB* pBaseB = &obj; // Адреса зміщена на +8 байтів: 0x1008

// static_cast знає структуру класів і ВІДНІМАЄ 8 байтів!
// Результат: 0x1000 (початок об'єкта Derived)
Derived* pDerived = static_cast<Derived*>(pBaseB);
