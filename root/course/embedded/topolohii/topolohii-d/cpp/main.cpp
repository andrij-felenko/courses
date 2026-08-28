#include <cstdint>
#include <optional>

struct NetPacket {
    uint16_t src;
    uint16_t dst;
    uint8_t  ttl{8};
};

/* 1. Логіка Зірки */
class StarRouter {
public:
    constexpr StarRouter(uint16_t selfAddr, uint16_t hubAddr) noexcept
        : selfAddr_{selfAddr}, hubAddr_{hubAddr} {}

    [[nodiscard]] constexpr std::optional<uint16_t> nextHop(const NetPacket& pkt) const noexcept {
        if (pkt.dst == selfAddr_) return selfAddr_;
        if (selfAddr_ == hubAddr_) return pkt.dst;
        return hubAddr_;
    }

private:
    uint16_t selfAddr_;
    uint16_t hubAddr_;
};

/* 2. Логіка Дерева (Cskip Range Check) */
class TreeRouter {
public:
    constexpr TreeRouter(uint16_t selfAddr, uint16_t parentAddr, 
                         uint16_t childRouter, uint16_t subMin, uint16_t subMax) noexcept
        : selfAddr_{selfAddr}, parentAddr_{parentAddr}, 
          childRouter_{childRouter}, subMin_{subMin}, subMax_{subMax} {}

    [[nodiscard]] constexpr std::optional<uint16_t> nextHop(const NetPacket& pkt) const noexcept {
        if (pkt.dst == selfAddr_) return selfAddr_;
        
        if (pkt.dst >= subMin_ && pkt.dst <= subMax_) {
            return childRouter_; /* Форвардинг вниз до піддерева */
        }
        return parentAddr_; /* Форвардинг вгору до кореня */
    }

private:
    uint16_t selfAddr_;
    uint16_t parentAddr_;
    uint16_t childRouter_;
    uint16_t subMin_;
    uint16_t subMax_;
};

/* 3. Логіка Чарунки (Failover to Backup Next-Hop) */
struct MeshRoute {
    uint16_t destination;
    uint16_t primaryHop;
    uint16_t backupHop;
};

class MeshRouter {
public:
    constexpr MeshRouter(uint16_t selfAddr, MeshRoute route) noexcept
        : selfAddr_{selfAddr}, route_{route} {}

    [[nodiscard]] constexpr std::optional<uint16_t> nextHop(const NetPacket& pkt, 
                                                            bool isPrimaryAlive) const noexcept {
        if (pkt.dst == selfAddr_) return selfAddr_;

        if (pkt.dst == route_.destination) {
            if (isPrimaryAlive) {
                return route_.primaryHop;
            }
            return route_.backupHop; /* Local repair fallback */
        }
        return std::nullopt;
    }

private:
    uint16_t  selfAddr_;
    MeshRoute route_;
};
