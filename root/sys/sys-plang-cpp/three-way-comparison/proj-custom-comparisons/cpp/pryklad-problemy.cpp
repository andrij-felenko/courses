struct LegacyBuffer {
    const char* data;
    LegacyBuffer(const char* s) : data(s) {}

    // У C++17 цей метод працював лише для викликів buf == "test"
    bool operator==(const char* s) const {
        return std::strcmp(data, s) == 0;
    }
};

void check_buffer(LegacyBuffer buf) {
    // У C++20 цей вираз породжує фатальну неоднозначність (ambiguity):
    // Кандидат 1: неявне приведення "test" до LegacyBuffer і виклик порівняння двох об'єктів.
    // Кандидат 2: переписаний перевернутий виклик buf.operator==("test").
    // if ("test" == buf) { ... } // Помилка компіляції: ambiguous overload!
}
