// A. Пара перевантажень
struct Label {
    void set(const std::string& s) { text_ = s; }             // копіювальне присвоєння
    void set(std::string&& s)      { text_ = std::move(s); }  // переміщувальне
    std::string text_;
};

// B. Приймач за значенням + переміщення
struct Label2 {
    void set(std::string s) { text_ = std::move(s); }
    std::string text_;
};
