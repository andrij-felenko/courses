// Наївна і помилкова реалізація ScopeFail у C++98
class NaiveScopeFail {
    std::function<void()> fn_;
public:
    ~NaiveScopeFail() {
        if (std::uncaught_exception()) { // Працює некоректно при вкладеності!
            fn_();
        }
    }
};
