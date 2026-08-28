#include <cstdint>
#include <iostream>
#include <optional>
#include <span>
#include <string_view>
#include <vector>

enum class DescType : uint8_t {
    Configuration = 0x02,
    Interface     = 0x04,
    Endpoint      = 0x05,
};

struct Endpoint {
    uint8_t  address;      // bEndpointAddress: біт 7 — напрям, біти 3..0 — номер
    uint8_t  attributes;   // bmAttributes: біти 1..0 — тип передачі
    uint16_t max_packet;   // wMaxPacketSize
    uint8_t  interval;     // bInterval
};

struct Interface {
    uint8_t               number;
    uint8_t               class_code;
    uint8_t               declared_eps;
    std::vector<Endpoint> endpoints;
};

struct ConfigTree {
    uint16_t               total_length{0};
    uint8_t                num_interfaces{0};
    std::vector<Interface> interfaces;
};

static uint16_t le16(const uint8_t *p) {
    return static_cast<uint16_t>(p[0] | (static_cast<uint16_t>(p[1]) << 8));
}

std::optional<ConfigTree> parse_config(std::span<const uint8_t> buf) {
    ConfigTree tree;
    Interface *cur = nullptr;

    size_t off = 0;
    while (off + 2 <= buf.size()) {
        uint8_t b_len  = buf[off];
        uint8_t b_type = buf[off + 1];

        if (b_len == 0 || off + b_len > buf.size()) {
            return std::nullopt;
        }

        switch (static_cast<DescType>(b_type)) {
        case DescType::Configuration:
            if (b_len < 9) return std::nullopt;
            tree.total_length   = le16(&buf[off + 2]);
            tree.num_interfaces = buf[off + 4];
            break;

        case DescType::Interface:
            if (b_len < 9) return std::nullopt;
            tree.interfaces.push_back({
                .number       = buf[off + 2],
                .class_code   = buf[off + 5],
                .declared_eps = buf[off + 4],
                .endpoints    = {}
            });
            cur = &tree.interfaces.back();
            break;

        case DescType::Endpoint: {
            if (b_len < 7 || cur == nullptr) return std::nullopt;
            cur->endpoints.push_back({
                .address    = buf[off + 2],
                .attributes = buf[off + 3],
                .max_packet = le16(&buf[off + 4]),
                .interval   = buf[off + 6]
            });
            break;
        }

        default:
            break;
        }

        off += b_len;
    }
    return tree;
}

static std::string_view xfer(uint8_t attr) {
    switch (attr & 0x03u) {
    case 0:  return "контрольна";
    case 1:  return "ізохронна";
    case 2:  return "масова";
    default: return "переривна";
    }
}

void dump_tree(const ConfigTree &t) {
    std::cout << "Конфігурація: wTotalLength=" << t.total_length
              << ", інтерфейсів=" << static_cast<int>(t.num_interfaces) << "\n";
    for (const auto &f : t.interfaces) {
        std::cout << "  Інтерфейс " << static_cast<int>(f.number)
                  << "  клас 0x" << std::hex << static_cast<int>(f.class_code) << std::dec
                  << "  точок: " << f.endpoints.size()
                  << " (обіцяно " << static_cast<int>(f.declared_eps) << ")\n";
        for (const auto &e : f.endpoints) {
            std::cout << "    Точка 0x" << std::hex << static_cast<int>(e.address) << std::dec
                      << "  " << ((e.address & 0x80u) ? "IN " : "OUT")
                      << "  " << xfer(e.attributes)
                      << "  wMaxPacketSize=" << e.max_packet << "\n";
        }
    }
}

static constexpr uint8_t raw[] = {
    0x09,0x02, 0x43,0x00, 0x02, 0x01, 0x00, 0x80, 0x32,
    0x09,0x04, 0x00, 0x00, 0x01, 0x02, 0x02, 0x01, 0x00,
    0x05,0x24, 0x00, 0x10,0x01,
    0x05,0x24, 0x01, 0x00, 0x01,
    0x04,0x24, 0x02, 0x02,
    0x05,0x24, 0x06, 0x00, 0x01,
    0x07,0x05, 0x81, 0x03, 0x08,0x00, 0xFF,
    0x09,0x04, 0x01, 0x00, 0x02, 0x0A, 0x00, 0x00, 0x00,
    0x07,0x05, 0x02, 0x02, 0x40,0x00, 0x00,
    0x07,0x05, 0x82, 0x02, 0x40,0x00, 0x00,
};

int main() {
    auto tree = parse_config(raw);
    if (!tree) {
        std::cout << "пошкоджений дескриптор\n";
        return 1;
    }
    dump_tree(*tree);
    return 0;
}
