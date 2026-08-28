// logger.hpp
template<typename T>
void log_data(T value) { /* Шаблон: не викликає ODR колізій */ }

// ПОМИЛКА ЛІНКУВАННЯ при include у декілька .cpp:
// template<>
// void log_data<const char*>(const char* value) { std::puts(value); }

// ПРАВИЛЬНЕ РІШЕННЯ 1: inline специфікатор (C++11/C++17)
template<>
inline void log_data<const char*>(const char* value) { 
    std::puts(value); 
}

// ПРАВИЛЬНЕ РІШЕННЯ 2: розділення на оголошення в .hpp та визначення в .cpp
// logger.hpp:
template<>
void log_data<std::string>(std::string value);

// logger.cpp:
template<>
void log_data<std::string>(std::string value) {
    std::printf("%s\n", value.c_str());
}
