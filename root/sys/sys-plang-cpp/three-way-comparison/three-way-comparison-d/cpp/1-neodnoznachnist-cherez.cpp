struct Path {
    std::string str;
    Path(const char* s) : str(s) {} // Неявний конструктор!

    bool operator==(const char* s) const { return str == s; }
};

void run(Path p) {
    // У C++17 працювало:
    bool ok1 = (p == "test");

    // У C++20 вираз нижче призведе до помилки компіляції:
    // bool ok2 = ("test" == p);
}
