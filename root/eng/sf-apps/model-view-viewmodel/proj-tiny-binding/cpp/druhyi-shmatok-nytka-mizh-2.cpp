// ── 2б. Зв'язок: дві підписки, прапорець і деструктор ──

// Найтонший «віджет»: текст плюс сповіщення про правку користувачем.
struct TextField {
    std::string text;
    std::function<void(const std::string&)> onEdit;

    void typeIn(std::string s) {                 // так «друкує користувач»
        text = std::move(s);
        if (onEdit) onEdit(text);
    }
    void show(std::string s) { text = std::move(s); }   // запис із коду — БЕЗ сповіщення
};

template <class T>
class Binding {
public:
    using ToView  = std::function<std::string(const T&)>;
    using ToModel = std::function<T(const std::string&)>;

    Binding(TextField& w, Property<T>& p, ToView toView, ToModel toModel)
        : w_(w), p_(p), toView_(std::move(toView)) {

        id_ = p_.on([this](const T& v) { w_.show(toView_(v)); });   // властивість → віджет

        w_.onEdit = [this, toModel](const std::string& s) {         // віджет → властивість
            if (writing_) return;                                   // друге коло не робимо
            writing_ = true;
            p_.set(toModel(s));                                     // ← точка зупину тут
            writing_ = false;
        };

        w_.show(toView_(p_.get()));                                 // початкове наповнення
    }

    ~Binding() { p_.off(id_); w_.onEdit = nullptr; }   // відписку не можна забути

    Binding(const Binding&) = delete;                  // зв'язок не копіюють
    Binding& operator=(const Binding&) = delete;

private:
    TextField& w_;
    Property<T>& p_;
    ToView toView_;
    std::size_t id_ = 0;
    bool writing_ = false;
};
