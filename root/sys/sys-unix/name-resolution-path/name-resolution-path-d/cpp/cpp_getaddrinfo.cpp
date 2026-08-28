// cpp_getaddrinfo.cpp — Ідіоматичний C++20 варіант з RAII-обгорткою для freeaddrinfo
#include <iostream>
#include <string_view>
#include <memory>
#include <cstring>
#include <netdb.h>
#include <arpa/inet.h>

struct AddrInfoDeleter {
    void operator()(struct addrinfo* res) const noexcept {
        if (res) {
            ::freeaddrinfo(res);
        }
    }
};

using ScopedAddrInfo = std::unique_ptr<struct addrinfo, AddrInfoDeleter>;

bool resolve_host_cpp(std::string_view hostname) {
    struct addrinfo hints{};
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    struct addrinfo* raw_res = nullptr;
    int status = ::getaddrinfo(hostname.data(), "80", &hints, &raw_res);
    if (status != 0) {
        std::cerr << "Помилка розв'язання: " << ::gai_strerror(status) << '\n';
        return false;
    }

    ScopedAddrInfo res(raw_res);

    for (const struct addrinfo* rp = res.get(); rp != nullptr; rp = rp->ai_next) {
        char ipstr[INET6_ADDRSTRLEN]{};
        const void* addr = nullptr;

        if (rp->ai_family == AF_INET) {
            auto* ipv4 = reinterpret_cast<const struct sockaddr_in*>(rp->ai_addr);
            addr = &(ipv4->sin_addr);
        } else {
            auto* ipv6 = reinterpret_cast<const struct sockaddr_in6*>(rp->ai_addr);
            addr = &(ipv6->sin6_addr);
        }

        ::inet_ntop(rp->ai_family, addr, ipstr, sizeof(ipstr));
        std::cout << "Знайдено адресу [C++]: " << ipstr << '\n';
    }

    return true;
}
