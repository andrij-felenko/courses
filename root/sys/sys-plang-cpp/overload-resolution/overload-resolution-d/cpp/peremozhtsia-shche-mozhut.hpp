class Window {
public:
    void attach(const Config& cfg);   // запам'ятовує адресу надовго
    void attach(Config&&) = delete;   // на тимчасовому об'єкті — заборона
};

Config make_config();

Window w;
Config c = make_config();
w.attach(c);               // добре: lvalue, живе стільки, скільки треба
w.attach(make_config());   // помилка компіляції
