namespace lib {
    class Money {
        friend Money operator+(Money a, Money b) { /* ... */ }
        // ім'я operator+ ніде в lib не оголошене — тільки тут
    };
}

lib::Money x, y;
auto z = x + y;              // знайдено виключно через пошук за аргументами
lib::operator+(x, y);        // не складеться: такого імені в lib нема
