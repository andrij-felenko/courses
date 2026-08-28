// Концептуальне відображення інтрузивного вузла ядра в C++
#pragma once
#include <atomic>
#include <string>
#include <functional>
#include <string_view>

struct KObjectType;

// Інтрузивний блок ядра, що вбудовується всередину об'єкта
class KObject {
public:
    KObject(std::string name, const KObjectType* type)
        : m_name(std::move(name)), m_ktype(type), m_refcount(1) {}

    void get() noexcept {
        m_refcount.fetch_add(1, std::memory_order_relaxed);
    }

    void put() noexcept;

    [[nodiscard]] const std::string& name() const noexcept { return m_name; }

private:
    std::string m_name;
    const KObjectType* m_ktype;
    std::atomic<int> m_refcount;
};

struct KObjectType {
    std::function<void(KObject*)> release;
};

inline void KObject::put() noexcept {
    if (m_refcount.fetch_sub(1, std::memory_order_acq_rel) == 1) {
        if (m_ktype && m_ktype->release) {
            m_ktype->release(this);
        }
    }
}
