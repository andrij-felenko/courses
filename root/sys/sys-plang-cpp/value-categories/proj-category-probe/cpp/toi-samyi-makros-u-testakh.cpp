class Config {
    std::string text_;
public:
    const std::string& text() const& { return text_; }   // з живого об'єкта — дивимося
    std::string        text() &&     { return std::move(text_); }  // з тимчасового — забираємо
};

extern Config cfg;

STATIC_CATEGORY(lvalue_t,  cfg.text());        // вид на чуже, без копії
STATIC_CATEGORY(prvalue_t, Config{}.text());   // нутрощі забрано

static_assert(!std::is_const_v<std::remove_reference_t<decltype((Config{}.text()))>>,
              "повернення const-значення вимикає переміщення");
