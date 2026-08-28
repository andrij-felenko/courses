#include <new>
#include <string>
#include <iostream>

alignas(std::string) char storage[sizeof(std::string)]; // Сирий буфер

// Фаза 1 відсутня: пам'ять уже є. Виконується лише Фаза 2 (конструктор)
std::string* s = new (storage) std::string("Конфігурація");

std::cout << *s << '\n';

// КАТАСТРОФА: виклик delete s спробує звільнити стековий буфер у купі!
// delete s; // Невизначена поведінка (крах процесу)

// ПРАВИЛЬНО: явний виклик деструктора без деалокації пам'яті
s->~basic_string();
