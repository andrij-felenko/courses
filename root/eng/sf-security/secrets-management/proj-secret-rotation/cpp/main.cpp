#include <iostream>
#include <string>
#include <memory>
#include <atomic>
#include <thread>
#include <chrono>
#include <cstring>
#include <unistd.h>
#include <sys/mman.h>

namespace security {

/* RAII-обгортка для захищеного рядка з блокуванням у пам'яті */
class SecureString {
public:
    explicit SecureString(std::string_view data) : size_(data.size()) {
        long page_size = sysconf(_SC_PAGESIZE);
        size_t alloc_size = (size_ + 1 + page_size - 1) & ~(page_size - 1);

        if (posix_memalign(reinterpret_cast<void**>(&buffer_), page_size, alloc_size) != 0) {
            throw std::bad_alloc();
        }

        if (mlock(buffer_, alloc_size) != 0) {
            free(buffer_);
            throw std::runtime_error("mlock failed to lock secure memory");
        }

#ifdef MADV_DONTDUMP
        madvise(buffer_, alloc_size, MADV_DONTDUMP);
#endif

        std::memcpy(buffer_, data.data(), size_);
        buffer_[size_] = '\0';
    }

    ~SecureString() {
        if (buffer_) {
            long page_size = sysconf(_SC_PAGESIZE);
            size_t alloc_size = (size_ + 1 + page_size - 1) & ~(page_size - 1);

            /* Гарантоване занулення без усунення оптимізатором */
            explicit_bzero(buffer_, size_ + 1);

            munlock(buffer_, alloc_size);
            free(buffer_);
        }
    }

    // Заборона копіювання для запобігання дублюванню секретів у пам'яті
    SecureString(const SecureString&) = delete;
    SecureString& operator=(const SecureString&) = delete;

    // Дозвіл переміщення
    SecureString(SecureString&& other) noexcept : buffer_(other.buffer_), size_(other.size_) {
        other.buffer_ = nullptr;
        other.size_ = 0;
    }

    SecureString& operator=(SecureString&& other) noexcept {
        if (this != &other) {
            this->~SecureString();
            buffer_ = other.buffer_;
            size_ = other.size_;
            other.buffer_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::string_view view() const noexcept {
        return buffer_ ? std::string_view(buffer_, size_) : std::string_view{};
    }

private:
    char* buffer_{nullptr};
    size_t size_{0};
};

/* Структура облікових даних сервісу */
struct SecretCredentials {
    SecureString username;
    SecureString password;
    std::string lease_id;
    std::chrono::system_clock::time_point expires_at;

    SecretCredentials(std::string_view u, std::string_view p, std::string_view lease, std::chrono::seconds ttl)
        : username(u), password(p), lease_id(lease),
          expires_at(std::chrono::system_clock::now() + ttl) {}
};

/* Менеджер ротації секретів */
class SecretRotationManager {
public:
    explicit SecretRotationManager(std::chrono::seconds rotation_interval)
        : rotation_interval_(rotation_interval), running_(true) {
        
        // Отримання початкового секрету
        auto initial = fetch_from_vault(1);
        active_secret_.store(initial);

        // Запуск фонового потоку ротації
        worker_thread_ = std::thread(&SecretRotationManager::rotation_loop, this);
    }

    ~SecretRotationManager() {
        running_.store(false);
        if (worker_thread_.joinable()) {
            worker_thread_.join();
        }
    }

    /* Lock-free читання активного секрету */
    [[nodiscard]] std::shared_ptr<const SecretCredentials> get_secret() const noexcept {
        return std::atomic_load(&active_secret_);
    }

private:
    std::shared_ptr<SecretCredentials> fetch_from_vault(int version) {
        std::string user = "app_user_v" + std::to_string(version);
        std::string pass = "vault_sec_cpp_" + std::to_string(version) + "_xyz";
        std::string lease = "database/creds/app-cpp/" + std::to_string(version);
        
        return std::make_shared<SecretCredentials>(user, pass, lease, std::chrono::seconds(10));
    }

    void rotation_loop() {
        int version = 1;
        while (running_.load()) {
            std::this_thread::sleep_for(rotation_interval_);
            if (!running_.load()) break;

            version++;
            auto new_secret = fetch_from_vault(version);
            if (new_secret) {
                // Атомарна заміна спільного покажчика
                std::atomic_store(&active_secret_, new_secret);
                std::cout << "[CPP-Worker] Успішна ротація: користувач "
                          << new_secret->username.view() << " (Lease: "
                          << new_secret->lease_id << ")\n";
            }
        }
    }

    std::chrono::seconds rotation_interval_;
    std::atomic<bool> running_{false};
    std::shared_ptr<SecretCredentials> active_secret_{nullptr};
    std::thread worker_thread_;
};

} // namespace security

int main() {
    using namespace std::chrono_literals;

    security::SecretRotationManager manager(3s);

    for (int i = 0; i < 4; ++i) {
        auto secret = manager.get_secret();
        if (secret) {
            std::cout << "[CPP-Main] Запит " << (i + 1) << ": логін = "
                      << secret->username.view() << ", пароль = "
                      << secret->password.view() << "\n";
        }
        std::this_thread::sleep_for(2s);
    }

    std::cout << "[CPP-Main] Завершення роботи програми.\n";
    return 0;
}
