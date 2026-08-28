#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <optional>
#include <span>
#include <cstring>

#if defined(_WIN32)
#include <windows.h>
inline void secure_zero(void* ptr, std::size_t sz) noexcept {
    SecureZeroMemory(ptr, sz);
}
#else
inline void secure_zero(void* ptr, std::size_t sz) noexcept {
    explicit_bzero(ptr, sz);
}
#endif

/* Безпечний контейнер пам'яті: автоматичне занулення в деструкторі */
class SecureByteVector {
public:
    SecureByteVector() = default;
    explicit SecureByteVector(std::size_t size) : data_(size) {}
    SecureByteVector(const uint8_t* ptr, std::size_t len) : data_(ptr, ptr + len) {}
    
    ~SecureByteVector() {
        if (!data_.empty()) {
            secure_zero(data_.data(), data_.size());
        }
    }
    
    SecureByteVector(const SecureByteVector& other) = default;
    SecureByteVector& operator=(const SecureByteVector& other) = default;
    SecureByteVector(SecureByteVector&& other) noexcept = default;
    SecureByteVector& operator=(SecureByteVector&& other) noexcept = default;

    [[nodiscard]] std::span<const uint8_t> span() const noexcept { return data_; }
    [[nodiscard]] std::span<uint8_t> span() noexcept { return data_; }
    [[nodiscard]] const uint8_t* data() const noexcept { return data_.data(); }
    [[nodiscard]] uint8_t* data() noexcept { return data_.data(); }
    [[nodiscard]] std::size_t size() const noexcept { return data_.size(); }
    [[nodiscard]] bool empty() const noexcept { return data_.empty(); }

    void resize(std::size_t sz) { data_.resize(sz); }
    void push_back(uint8_t b) { data_.push_back(b); }
    void append(std::span<const uint8_t> s) { data_.insert(data_.end(), s.begin(), s.end()); }

private:
    std::vector<uint8_t> data_;
};

enum class SaslStatus {
    Ok,
    Continue,
    ErrorAuth,
    ErrorSyntax,
    ErrorMemory
};

enum class SaslState {
    Init,
    Step,
    Done,
    Fail
};

struct SaslCredentials {
    std::optional<std::string> authzid;
    std::string authcid;
    std::string password;
};

/* Поліморфний інтерфейс під'єднуваного механізму SASL */
class ISaslMechanism {
public:
    virtual ~ISaslMechanism() = default;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;

    virtual SaslStatus client_start(const SaslCredentials& cred, SecureByteVector& out) = 0;
    virtual SaslStatus client_step(std::span<const uint8_t> in, SecureByteVector& out) = 0;

    virtual SaslStatus server_start(SecureByteVector& out) = 0;
    virtual SaslStatus server_step(std::span<const uint8_t> in, SecureByteVector& out,
                                  std::string& authenticated_user) = 0;
};
