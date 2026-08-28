namespace std {
    class exception {
    public:
        // Конструктори та деструктор
        exception() noexcept;
        exception(const exception& other) noexcept;
        exception& operator=(const exception& other) noexcept;
        virtual ~exception() noexcept;

        // Поліморфний доступ до текстового повідомлення про помилку
        virtual const char* what() const noexcept;
    };
}
