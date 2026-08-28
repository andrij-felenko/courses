// Концептуальне відображення об'єктної моделі GObject на класи C++20
#pragma once
#include <cstdint>
#include <memory>
#include <string_view>
#include <unordered_map>
#include <any>

using GType = std::uintptr_t;

// Еквівалент метакласу GTypeClass (визначає метадані та поведінку типу)
class ObjectClass {
public:
    virtual ~ObjectClass() = default;
    [[nodiscard]] virtual GType type_id() const noexcept = 0;
    [[nodiscard]] virtual std::string_view type_name() const noexcept = 0;
};

// Еквівалент екземпляра GObject з інкапсульованим керуванням життям
class Object : public std::enable_shared_from_this<Object> {
public:
    virtual ~Object() = default;

    virtual void dispose() noexcept {
        // Розрив можливих циклічних зв'язків
        m_qdata.clear();
    }

    void set_qdata(std::string_view key, std::any value) {
        m_qdata.insert_or_assign(std::string(key), std::move(value));
    }

    [[nodiscard]] std::any get_qdata(std::string_view key) const {
        if (auto it = m_qdata.find(std::string(key)); it != m_qdata.end()) {
            return it->second;
        }
        return {};
    }

private:
    std::unordered_map<std::string, std::any> m_qdata;
};
