// libnss_custom.cpp — Ідіоматична C++20 реалізація з безпечним розподільником буфера
#include <nss.h>
#include <netdb.h>
#include <cerrno>
#include <cstring>
#include <string_view>
#include <span>
#include <arpa/inet.h>
#include <cstdint>

namespace {
    constexpr std::string_view kLabSuffix = ".lab";
    constexpr std::string_view kSyntheticIp = "127.0.42.1";

    // Клас-допоміжник для безпечного розмежування типів у буфері без викликів malloc()
    class PlacementBuffer {
    public:
        explicit PlacementBuffer(std::span<char> buf) : buffer_(buf), offset_(0) {}

        template <typename T>
        T* allocate(size_t count = 1) noexcept {
            size_t align = alignof(T);
            size_t current_addr = reinterpret_cast<size_t>(buffer_.data() + offset_);
            size_t padding = (align - (current_addr % align)) % align;

            size_t total_bytes = padding + count * sizeof(T);
            if (offset_ + total_bytes > buffer_.size()) {
                return nullptr;
            }

            offset_ += padding;
            T* ptr = reinterpret_cast<T*>(buffer_.data() + offset_);
            offset_ += count * sizeof(T);
            return ptr;
        }

        char* copy_string(std::string_view str) noexcept {
            char* dest = allocate<char>(str.size() + 1);
            if (!dest) return nullptr;
            std::memcpy(dest, str.data(), str.size());
            dest[str.size()] = '\0';
            return dest;
        }

    private:
        std::span<char> buffer_;
        size_t offset_;
    };
}

extern "C" {

enum nss_status _nss_custom_gethostbyname2_r(
    const char *name,
    int af,
    struct hostent *result,
    char *buffer,
    size_t buflen,
    int *errnop,
    int *h_errnop) noexcept
{
    if (af != AF_INET || name == nullptr) {
        *h_errnop = HOST_NOT_FOUND;
        return NSS_STATUS_NOTFOUND;
    }

    std::string_view host_name(name);
    if (!host_name.ends_with(kLabSuffix)) {
        *h_errnop = HOST_NOT_FOUND;
        return NSS_STATUS_NOTFOUND;
    }

    PlacementBuffer allocator(std::span<char>(buffer, buflen));

    // 1. Копіюємо текстове ім'я
    char* h_name = allocator.copy_string(host_name);
    if (!h_name) {
        *errnop = ERANGE;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_TRYAGAIN;
    }

    // 2. Розміщуємо IPv4 адресу
    auto* addr_ptr = allocator.allocate<struct in_addr>();
    if (!addr_ptr) {
        *errnop = ERANGE;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_TRYAGAIN;
    }

    if (::inet_pton(AF_INET, kSyntheticIp.data(), addr_ptr) <= 0) {
        *errnop = EINVAL;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_UNAVAIL;
    }

    // 3. Формуємо масив вказівників на адреси
    auto** addr_list = allocator.allocate<char*>(2);
    if (!addr_list) {
        *errnop = ERANGE;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_TRYAGAIN;
    }
    addr_list[0] = reinterpret_cast<char*>(addr_ptr);
    addr_list[1] = nullptr;

    // 4. Формуємо порожній масив псевдонімів
    auto** alias_list = allocator.allocate<char*>(1);
    if (!alias_list) {
        *errnop = ERANGE;
        *h_errnop = NETDB_INTERNAL;
        return NSS_STATUS_TRYAGAIN;
    }
    alias_list[0] = nullptr;

    // Заповнюємо вихідну структуру hostent
    result->h_name = h_name;
    result->h_aliases = alias_list;
    result->h_addrtype = AF_INET;
    result->h_length = sizeof(struct in_addr);
    result->h_addr_list = addr_list;

    *h_errnop = NETDB_SUCCESS;
    return NSS_STATUS_SUCCESS;
}

enum nss_status _nss_custom_gethostbyname_r(
    const char *name,
    struct hostent *result,
    char *buffer,
    size_t buflen,
    int *errnop,
    int *h_errnop) noexcept
{
    return _nss_custom_gethostbyname2_r(name, AF_INET, result, buffer, buflen, errnop, h_errnop);
}

} // extern "C"
