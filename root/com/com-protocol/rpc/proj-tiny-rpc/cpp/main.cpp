#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <unordered_map>
#include <functional>
#include <cstdint>
#include <cstring>

enum class RpcStatus : uint64_t {
    Ok = 0,
    NotFound = 1,
    InvalidArgument = 2,
    DecodeError = 3
};

struct RpcMessage {
    uint64_t call_id{0};
    uint64_t method_id{0};
    RpcStatus status{RpcStatus::Ok};
    std::vector<uint8_t> payload;
};

class VarintCodec {
public:
    static void encode(uint64_t value, std::vector<uint8_t>& out) {
        while (value >= 0x80) {
            out.push_back(static_cast<uint8_t>((value & 0x7F) | 0x80));
            value >>= 7;
        }
        out.push_back(static_cast<uint8_t>(value & 0x7F));
    }

    static std::expected<uint64_t, RpcStatus> decode(std::span<const uint8_t> buf, size_t& offset) {
        uint64_t result = 0;
        int shift = 0;
        while (offset < buf.size()) {
            uint8_t byte = buf[offset++];
            result |= static_cast<uint64_t>(byte & 0x7F) << shift;
            if ((byte & 0x80) == 0) {
                return result;
            }
            shift += 7;
            if (shift >= 64) return std::unexpected(RpcStatus::DecodeError);
        }
        return std::unexpected(RpcStatus::DecodeError);
    }
};

class RpcSerializer {
public:
    static std::vector<uint8_t> pack(const RpcMessage& msg) {
        std::vector<uint8_t> out;
        VarintCodec::encode(msg.call_id, out);
        VarintCodec::encode(msg.method_id, out);
        VarintCodec::encode(static_cast<uint64_t>(msg.status), out);
        VarintCodec::encode(msg.payload.size(), out);
        out.insert(out.end(), msg.payload.begin(), msg.payload.end());
        return out;
    }

    static std::expected<RpcMessage, RpcStatus> unpack(std::span<const uint8_t> buf) {
        size_t off = 0;
        auto cid = VarintCodec::decode(buf, off);
        auto mid = VarintCodec::decode(buf, off);
        auto st  = VarintCodec::decode(buf, off);
        auto len = VarintCodec::decode(buf, off);

        if (!cid || !mid || !st || !len) return std::unexpected(RpcStatus::DecodeError);
        if (off + *len > buf.size()) return std::unexpected(RpcStatus::DecodeError);

        RpcMessage msg;
        msg.call_id = *cid;
        msg.method_id = *mid;
        msg.status = static_cast<RpcStatus>(*st);
        msg.payload.assign(buf.begin() + off, buf.begin() + off + *len);
        return msg;
    }
};

/* ── 3. Диспетчер сервера та скелетон ── */
class RpcServer {
public:
    using Handler = std::function<std::expected<std::vector<uint8_t>, RpcStatus>(std::span<const uint8_t>)>;

    void register_handler(uint64_t method_id, Handler handler) {
        handlers_[method_id] = std::move(handler);
    }

    std::vector<uint8_t> dispatch(std::span<const uint8_t> request_bytes) {
        auto req = RpcSerializer::unpack(request_bytes);
        if (!req) return {};

        RpcMessage resp;
        resp.call_id = req->call_id;
        resp.method_id = req->method_id;

        auto it = handlers_.find(req->method_id);
        if (it == handlers_.end()) {
            resp.status = RpcStatus::NotFound;
        } else {
            auto res = it->second(req->payload);
            if (res) {
                resp.status = RpcStatus::Ok;
                resp.payload = std::move(*res);
            } else {
                resp.status = res.error();
            }
        }
        return RpcSerializer::pack(resp);
    }

private:
    std::unordered_map<uint64_t, Handler> handlers_;
};

/* ── 4. Клієнтський стаб для виклику арифметичних методів ── */
class CalculatorClient {
public:
    explicit CalculatorClient(RpcServer& server) : server_(server) {}

    std::expected<uint64_t, RpcStatus> add(uint64_t a, uint64_t b) {
        RpcMessage req;
        req.call_id = ++next_call_id_;
        req.method_id = 1; // Method Add
        VarintCodec::encode(a, req.payload);
        VarintCodec::encode(b, req.payload);

        auto wire_req = RpcSerializer::pack(req);
        auto wire_resp = server_.dispatch(wire_req);

        auto resp = RpcSerializer::unpack(wire_resp);
        if (!resp) return std::unexpected(RpcStatus::DecodeError);
        if (resp->status != RpcStatus::Ok) return std::unexpected(resp->status);

        size_t off = 0;
        return VarintCodec::decode(resp->payload, off);
    }

private:
    RpcServer& server_;
    uint64_t next_call_id_{0};
};

int main() {
    RpcServer server;
    server.register_handler(1, [](std::span<const uint8_t> req) -> std::expected<std::vector<uint8_t>, RpcStatus> {
        size_t off = 0;
        auto a = VarintCodec::decode(req, off);
        auto b = VarintCodec::decode(req, off);
        if (!a || !b) return std::unexpected(RpcStatus::InvalidArgument);

        std::vector<uint8_t> out;
        VarintCodec::encode(*a + *b, out);
        return out;
    });

    CalculatorClient client(server);
    auto sum = client.add(1024, 2048);
    if (sum) {
        std::cout << "C++ RPC Add(1024, 2048) = " << *sum << std::endl;
    }
    return 0;
}
