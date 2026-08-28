#include <string_view>
#include <functional>
#include <vector>
#include <algorithm>
#include <span>

class I18nContextManager {
public:
    using ObserverCallback = std::function<void(std::string_view new_locale)>;

    static I18nContextManager& instance() noexcept {
        static I18nContextManager manager;
        return manager;
    }

    void register_observer(ObserverCallback observer) {
        observers_.push_back(std::move(observer));
    }

    void set_locale(std::string_view locale_tag, 
                    const void *catalog_ptr = nullptr, 
                    const void *font_ptr = nullptr) {
        current_locale_ = locale_tag;
        active_catalog_ = catalog_ptr;
        active_font_    = font_ptr;

        for (const auto &cb : observers_) {
            if (cb) {
                cb(current_locale_);
            }
        }
    }

    [[nodiscard]] std::string_view current_locale() const noexcept {
        return current_locale_;
    }

    [[nodiscard]] const void* active_catalog() const noexcept {
        return active_catalog_;
    }

    [[nodiscard]] const void* active_font() const noexcept {
        return active_font_;
    }

private:
    I18nContextManager() = default;
    std::string_view current_locale_{"en-US"};
    const void *active_catalog_{nullptr};
    const void *active_font_{nullptr};
    std::vector<ObserverCallback> observers_;
};
