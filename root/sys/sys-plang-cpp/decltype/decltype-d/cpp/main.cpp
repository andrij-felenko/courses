int i = 0;
const int& r = i;
int&&      x = 0;

decltype(i)              // int         — ім'я
decltype(r)              // const int&  — ім'я, оголошене посиланням
decltype(x)              // int&&       — ім'я; тип оголошення, а не категорія
decltype(i + 1)          // int         — вираз, prvalue
decltype(std::move(i))   // int&&       — вираз, xvalue
decltype(*&i)            // int&        — вираз, lvalue
