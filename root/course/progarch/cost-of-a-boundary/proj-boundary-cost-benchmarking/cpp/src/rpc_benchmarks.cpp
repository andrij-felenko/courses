#include "boundary_benchmarks.hpp"
#include <benchmark/benchmark.h>
#include <nlohmann/json.hpp>
#include <sstream>
#include <cstring>
#include <thread>

#if defined(_WIN32)
    #include <winsock2.h>
    #include <ws2tcpip.h>
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
#endif

namespace boundary_benchmarks {

using json = nlohmann::json;

class WorkerThread {
public:
    std::jthread thread;
};

LocalRestServer::LocalRestServer() : m_worker(std::make_unique<WorkerThread>()) {}

LocalRestServer::~LocalRestServer() {
    stop();
}

void LocalRestServer::start(uint16_t port) {
#if defined(_WIN32)
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif

    int listenFd = static_cast<int>(::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP));
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(port);

    int opt = 1;
#if defined(_WIN32)
    ::setsockopt(listenFd, SOL_SOCKET, SO_REUSEADDR, reinterpret_cast<const char*>(&opt), sizeof(opt));
#else
    ::setsockopt(listenFd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif

    ::bind(listenFd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
    ::listen(listenFd, 16);

    socklen_t len = sizeof(addr);
    ::getsockname(listenFd, reinterpret_cast<sockaddr*>(&addr), &len);
    m_port = ntohs(addr.sin_port);
    m_listenFd = listenFd;
    m_running.store(true, std::memory_order_release);

    m_worker->thread = std::jthread([this](std::stop_token st) {
        while (!st.stop_requested() && m_running.load(std::memory_order_acquire)) {
            sockaddr_in clientAddr{};
            socklen_t clientLen = sizeof(clientAddr);
            int clientFd = static_cast<int>(::accept(m_listenFd, reinterpret_cast<sockaddr*>(&clientAddr), &clientLen));
            if (clientFd < 0) {
                break;
            }

            // Читання HTTP запиту
            char buffer[2048]{};
#if defined(_WIN32)
            int bytesRead = ::recv(clientFd, buffer, sizeof(buffer) - 1, 0);
#else
            ssize_t bytesRead = ::read(clientFd, buffer, sizeof(buffer) - 1);
#endif
            if (bytesRead > 0) {
                std::string raw(buffer, bytesRead);
                size_t bodyPos = raw.find("\r\n\r\n");
                if (bodyPos != std::string::npos) {
                    std::string body = raw.substr(bodyPos + 4);
                    try {
                        auto jReq = json::parse(body);
                        RequestPayload req{
                            .id = jReq["id"].get<int64_t>(),
                            .value = jReq["value"].get<double>(),
                            .tag = ""
                        };
                        ResponsePayload resp = executeBusinessLogic(req);

                        json jResp = {
                            {"id", resp.id},
                            {"result", resp.result},
                            {"success", resp.success}
                        };
                        std::string respBody = jResp.dump();
                        std::string httpResp =
                            "HTTP/1.1 200 OK\r\n"
                            "Content-Type: application/json\r\n"
                            "Content-Length: " + std::to_string(respBody.size()) + "\r\n"
                            "Connection: close\r\n\r\n" + respBody;

#if defined(_WIN32)
                        ::send(clientFd, httpResp.data(), static_cast<int>(httpResp.size()), 0);
#else
                        ::write(clientFd, httpResp.data(), httpResp.size());
#endif
                    } catch (...) {}
                }
            }
#if defined(_WIN32)
            ::closesocket(clientFd);
#else
            ::close(clientFd);
#endif
        }
    });
}

void LocalRestServer::stop() {
    if (m_running.exchange(false, std::memory_order_acq_rel)) {
#if defined(_WIN32)
        if (m_listenFd != -1) ::closesocket(m_listenFd);
#else
        if (m_listenFd != -1) ::close(m_listenFd);
#endif
        m_listenFd = -1;
    }
}

ResponsePayload LocalRestServer::sendHttpRequest(const RequestPayload& req) {
    int clientFd = static_cast<int>(::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP));
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(m_port);

    if (::connect(clientFd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0) {
#if defined(_WIN32)
        ::closesocket(clientFd);
#else
        ::close(clientFd);
#endif
        return ResponsePayload{.success = false};
    }

    // Серіалізація DTO у JSON
    json jReq = {
        {"id", req.id},
        {"value", req.value},
        {"tag", std::string(req.tag)}
    };
    std::string body = jReq.dump();
    std::string httpReq =
        "POST /compute HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: " + std::to_string(body.size()) + "\r\n"
        "Connection: close\r\n\r\n" + body;

#if defined(_WIN32)
    ::send(clientFd, httpReq.data(), static_cast<int>(httpReq.size()), 0);
#else
    ::write(clientFd, httpReq.data(), httpReq.size());
#endif

    char buffer[2048]{};
#if defined(_WIN32)
    int bytesRead = ::recv(clientFd, buffer, sizeof(buffer) - 1, 0);
    ::closesocket(clientFd);
#else
    ssize_t bytesRead = ::read(clientFd, buffer, sizeof(buffer) - 1);
    ::close(clientFd);
#endif

    if (bytesRead <= 0) {
        return ResponsePayload{.success = false};
    }

    std::string raw(buffer, bytesRead);
    size_t bodyPos = raw.find("\r\n\r\n");
    if (bodyPos == std::string::npos) {
        return ResponsePayload{.success = false};
    }

    auto jResp = json::parse(raw.substr(bodyPos + 4));
    return ResponsePayload{
        .id = jResp["id"].get<int64_t>(),
        .result = jResp["result"].get<double>(),
        .success = jResp["success"].get<bool>()
    };
}

// 5. gRPC сервіс із симуляцією двійкового пакування Protocol Buffers
LocalGrpcService::LocalGrpcService() : m_running(false) {}
LocalGrpcService::~LocalGrpcService() { stop(); }
void LocalGrpcService::start() { m_running = true; }
void LocalGrpcService::stop() { m_running = false; }

std::vector<uint8_t> LocalGrpcService::serializeProtobuf(const RequestPayload& req) {
    // Кодування у двійковий формат wire-format (tag, type, value)
    std::vector<uint8_t> bytes;
    bytes.reserve(32);

    // Поле 1: id (varint)
    bytes.push_back(0x08);
    uint64_t v = static_cast<uint64_t>(req.id);
    while (v >= 0x80) {
        bytes.push_back(static_cast<uint8_t>((v & 0x7F) | 0x80));
        v >>= 7;
    }
    bytes.push_back(static_cast<uint8_t>(v));

    // Поле 2: value (fixed64)
    bytes.push_back(0x11);
    const uint8_t* valBytes = reinterpret_cast<const uint8_t*>(&req.value);
    bytes.insert(bytes.end(), valBytes, valBytes + sizeof(double));

    // Поле 3: tag (length-delimited string)
    bytes.push_back(0x1A);
    std::string_view tag(req.tag);
    bytes.push_back(static_cast<uint8_t>(tag.size()));
    bytes.insert(bytes.end(), tag.begin(), tag.end());

    return bytes;
}

ResponsePayload LocalGrpcService::deserializeProtobuf(std::span<const uint8_t> bytes) {
    ResponsePayload resp{.id = 0, .result = 0.0, .success = true};
    size_t offset = 0;
    while (offset < bytes.size()) {
        uint8_t tag = bytes[offset++];
        if (tag == 0x08) {
            uint64_t v = 0;
            int shift = 0;
            while (offset < bytes.size()) {
                uint8_t b = bytes[offset++];
                v |= static_cast<uint64_t>(b & 0x7F) << shift;
                if (!(b & 0x80)) break;
                shift += 7;
            }
            resp.id = static_cast<int64_t>(v);
        } else if (tag == 0x11) {
            if (offset + 8 <= bytes.size()) {
                std::memcpy(&resp.result, &bytes[offset], sizeof(double));
                offset += 8;
            }
        }
    }
    return resp;
}

ResponsePayload LocalGrpcService::sendRpc(const RequestPayload& req) {
    // 1. Двійкова серіалізація запиту Protobuf
    auto reqBytes = serializeProtobuf(req);

    // 2. Імітація обробки сервером через HTTP/2 кадри
    ResponsePayload logicResp = executeBusinessLogic(req);

    // 3. Серіалізація відповіді Protobuf
    std::vector<uint8_t> respBytes;
    respBytes.push_back(0x08);
    respBytes.push_back(static_cast<uint8_t>(logicResp.id));
    respBytes.push_back(0x11);
    const uint8_t* valBytes = reinterpret_cast<const uint8_t*>(&logicResp.result);
    respBytes.insert(respBytes.end(), valBytes, valBytes + sizeof(double));

    // 4. Десеріалізація клієнтом
    return deserializeProtobuf(respBytes);
}

// Бенчмарк: локальний виклик REST через loopback TCP сокет та JSON
static void BM_LocalRestJsonCall(benchmark::State& state) {
    LocalRestServer server;
    server.start(0);

    RequestPayload req{.id = 1, .value = 100.5, .tag = "rest_test"};

    for (auto _ : state) {
        ResponsePayload resp = server.sendHttpRequest(req);
        benchmark::DoNotOptimize(resp);
        req.id++;
    }

    server.stop();
    state.SetItemsProcessed(state.iterations());
}
BENCHMARK(BM_LocalRestJsonCall)->Iterations(200);

// Бенчмарк: локальний виклик gRPC через Protocol Buffers
static void BM_LocalGrpcCall(benchmark::State& state) {
    LocalGrpcService service;
    service.start();

    RequestPayload req{.id = 1, .value = 100.5, .tag = "grpc_test"};

    for (auto _ : state) {
        ResponsePayload resp = service.sendRpc(req);
        benchmark::DoNotOptimize(resp);
        req.id++;
    }

    service.stop();
    state.SetItemsProcessed(state.iterations());
}
BENCHMARK(BM_LocalGrpcCall);

} // namespace boundary_benchmarks
