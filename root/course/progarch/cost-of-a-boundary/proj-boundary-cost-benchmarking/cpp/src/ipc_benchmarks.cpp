#include "boundary_benchmarks.hpp"
#include <benchmark/benchmark.h>
#include <thread>
#include <cstring>

#if defined(_WIN32)
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #include <afunix.h>
#else
    #include <sys/socket.h>
    #include <sys/un.h>
    #include <unistd.h>
#endif

namespace boundary_benchmarks {

UnixSocketChannel::UnixSocketChannel() {
#if defined(_WIN32)
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);

    // Створення підключеної пари TCP loopback сокетів на Windows (або AF_UNIX)
    SOCKET listener = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = 0;

    ::bind(listener, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
    ::listen(listener, 1);

    int len = sizeof(addr);
    ::getsockname(listener, reinterpret_cast<sockaddr*>(&addr), &len);

    SOCKET client = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    ::connect(client, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
    SOCKET server = ::accept(listener, nullptr, nullptr);

    m_clientFd = static_cast<int>(client);
    m_serverFd = static_cast<int>(server);
    ::closesocket(listener);
    m_initialized = true;
#else
    int fds[2];
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0) {
        m_clientFd = fds[0];
        m_serverFd = fds[1];
        m_initialized = true;
    }
#endif
}

UnixSocketChannel::~UnixSocketChannel() {
    close();
#if defined(_WIN32)
    WSACleanup();
#endif
}

void UnixSocketChannel::close() {
    if (m_initialized) {
#if defined(_WIN32)
        if (m_clientFd != -1) ::closesocket(m_clientFd);
        if (m_serverFd != -1) ::closesocket(m_serverFd);
#else
        if (m_clientFd != -1) ::close(m_clientFd);
        if (m_serverFd != -1) ::close(m_serverFd);
#endif
        m_clientFd = -1;
        m_serverFd = -1;
        m_initialized = false;
    }
}

bool UnixSocketChannel::sendRequest(const RequestPayload& req) {
    const char* buf = reinterpret_cast<const char*>(&req);
    size_t size = sizeof(RequestPayload);
#if defined(_WIN32)
    return ::send(m_clientFd, buf, static_cast<int>(size), 0) == static_cast<int>(size);
#else
    return ::write(m_clientFd, buf, size) == static_cast<ssize_t>(size);
#endif
}

bool UnixSocketChannel::receiveRequest(RequestPayload& req) {
    char* buf = reinterpret_char<char*>(&req);
    size_t size = sizeof(RequestPayload);
#if defined(_WIN32)
    return ::recv(m_serverFd, buf, static_cast<int>(size), MSG_WAITALL) == static_cast<int>(size);
#else
    return ::read(m_serverFd, buf, size) == static_cast<ssize_t>(size);
#endif
}

bool UnixSocketChannel::sendResponse(const ResponsePayload& resp) {
    const char* buf = reinterpret_cast<const char*>(&resp);
    size_t size = sizeof(ResponsePayload);
#if defined(_WIN32)
    return ::send(m_serverFd, buf, static_cast<int>(size), 0) == static_cast<int>(size);
#else
    return ::write(m_serverFd, buf, size) == static_cast<ssize_t>(size);
#endif
}

bool UnixSocketChannel::receiveResponse(ResponsePayload& resp) {
    char* buf = reinterpret_cast<char*>(&resp);
    size_t size = sizeof(ResponsePayload);
#if defined(_WIN32)
    return ::recv(m_clientFd, buf, static_cast<int>(size), MSG_WAITALL) == static_cast<int>(size);
#else
    return ::read(m_clientFd, buf, size) == static_cast<ssize_t>(size);
#endif
}

// Бенчмарк: міжпроцесний виклик через AF_UNIX сокет
// Перетин межі процесів та ядра: 4 системні виклики (send/recv), копіювання пам'яті в ядрі
static void BM_UnixDomainSocketIPC(benchmark::State& state) {
    UnixSocketChannel channel;

    std::atomic<bool> running{true};
    std::jthread serverWorker([&](std::stop_token st) {
        RequestPayload req;
        while (!st.stop_requested() && running.load(std::memory_order_relaxed)) {
            if (channel.receiveRequest(req)) {
                ResponsePayload resp = executeBusinessLogic(req);
                channel.sendResponse(resp);
            } else {
                break;
            }
        }
    });

    RequestPayload req{.id = 100, .value = 3.1415, .tag = "ipc_test"};

    for (auto _ : state) {
        if (!channel.sendRequest(req)) {
            state.SkipWithError("Помилка надсилання IPC запиту");
            break;
        }
        ResponsePayload resp;
        if (!channel.receiveResponse(resp)) {
            state.SkipWithError("Помилка отримання IPC відповіді");
            break;
        }
        benchmark::DoNotOptimize(resp);
        req.id++;
    }

    running.store(false, std::memory_order_release);
    channel.close();
    state.SetItemsProcessed(state.iterations());
}
BENCHMARK(BM_UnixDomainSocketIPC);

} // namespace boundary_benchmarks
