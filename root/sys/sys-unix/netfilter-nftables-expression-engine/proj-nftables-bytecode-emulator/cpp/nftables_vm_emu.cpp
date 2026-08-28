// nftables_vm_emu.cpp - Ідіоматична реалізація віртуальної машини nftables мовою C++20
#include <iostream>
#include <vector>
#include <array>
#include <variant>
#include <unordered_set>
#include <span>
#include <cstdint>

namespace nftables {

enum class Verdict : int32_t {
    Continue = -1,
    Break    = -2,
    Accept   = 0,
    Drop     = 1
};

enum class PayloadBase {
    NetworkHeader,
    TransportHeader
};

enum class CmpOp {
    Equal,
    NotEqual
};

struct RegisterState {
    std::array<uint32_t, 16> regs{};

    void set_verdict(Verdict v) noexcept {
        regs[0] = static_cast<uint32_t>(v);
    }

    [[nodiscard]] Verdict get_verdict() const noexcept {
        return static_cast<Verdict>(static_cast<int32_t>(regs[0]));
    }
};

// Вирази ВМ у вигляді C++20 варіантів (std::variant)
struct PayloadExpr {
    PayloadBase base;
    uint32_t offset;
    uint32_t len;
    uint8_t dreg;
};

struct CmpExpr {
    uint8_t sreg;
    CmpOp op;
    uint32_t data;
};

struct BitwiseExpr {
    uint8_t sreg;
    uint8_t dreg;
    uint32_t mask;
    uint32_t xor_val;
};

struct LookupExpr {
    uint8_t sreg;
    std::unordered_set<uint32_t> set_elements;
};

struct ImmediateExpr {
    uint8_t dreg;
    uint32_t value;
};

using Expression = std::variant<PayloadExpr, CmpExpr, BitwiseExpr, LookupExpr, ImmediateExpr>;

class BytecodeEvaluator {
public:
    static constexpr uint32_t L3Offset = 0;
    static constexpr uint32_t L4Offset = 20;

    static Verdict evaluate_rule(std::span<const Expression> rule, std::span<const uint8_t> packet) {
        RegisterState regs{};
        regs.set_verdict(Verdict::Continue);

        for (const auto& expr : rule) {
            std::visit([&](const auto& e) {
                using T = std::decay_t<decltype(e)>;
                if constexpr (std::is_same_v<T, PayloadExpr>) {
                    eval_payload(e, regs, packet);
                } else if constexpr (std::is_same_v<T, CmpExpr>) {
                    eval_cmp(e, regs);
                } else if constexpr (std::is_same_v<T, BitwiseExpr>) {
                    eval_bitwise(e, regs);
                } else if constexpr (std::is_same_v<T, LookupExpr>) {
                    eval_lookup(e, regs);
                } else if constexpr (std::is_same_v<T, ImmediateExpr>) {
                    eval_immediate(e, regs);
                }
            }, expr);

            if (regs.get_verdict() == Verdict::Break) {
                return Verdict::Break;
            }
            if (static_cast<int32_t>(regs.get_verdict()) >= 0) {
                return regs.get_verdict();
            }
        }
        return regs.get_verdict();
    }

private:
    static void eval_payload(const PayloadExpr& e, RegisterState& regs, std::span<const uint8_t> pkt) {
        const uint32_t base_offset = (e.base == PayloadBase::TransportHeader) ? L4Offset : L3Offset;
        const uint32_t full_offset = base_offset + e.offset;

        if (full_offset + e.len > pkt.size()) {
            regs.set_verdict(Verdict::Break);
            return;
        }

        uint32_t val = 0;
        std::copy_n(pkt.data() + full_offset, e.len, reinterpret_cast<uint8_t*>(&val));
        regs.regs[e.dreg] = val;
    }

    static void eval_cmp(const CmpExpr& e, RegisterState& regs) {
        const uint32_t reg_val = regs.regs[e.sreg];
        const bool matched = (e.op == CmpOp::Equal) ? (reg_val == e.data) : (reg_val != e.data);
        if (!matched) {
            regs.set_verdict(Verdict::Break);
        }
    }

    static void eval_bitwise(const BitwiseExpr& e, RegisterState& regs) {
        const uint32_t sval = regs.regs[e.sreg];
        regs.regs[e.dreg] = (sval & e.mask) ^ e.xor_val;
    }

    static void eval_lookup(const LookupExpr& e, RegisterState& regs) {
        const uint32_t key = regs.regs[e.sreg];
        if (!e.set_elements.contains(key)) {
            regs.set_verdict(Verdict::Break);
        }
    }

    static void eval_immediate(const ImmediateExpr& e, RegisterState& regs) {
        regs.regs[e.dreg] = e.value;
    }
};

} // namespace nftables

int main() {
    // Симульований мережевий пакет
    std::vector<uint8_t> packet(40, 0);
    packet[9] = 6; // IPPROTO_TCP
    packet[22] = 0; packet[23] = 22; // Port 22

    // Правило nftables у вигляді вектора виразів
    const std::vector<nftables::Expression> rule = {
        nftables::PayloadExpr{.base = nftables::PayloadBase::NetworkHeader, .offset = 9, .len = 1, .dreg = 1},
        nftables::CmpExpr{.sreg = 1, .op = nftables::CmpOp::Equal, .data = 6},
        nftables::PayloadExpr{.base = nftables::PayloadBase::TransportHeader, .offset = 2, .len = 2, .dreg = 2},
        nftables::LookupExpr{.sreg = 2, .set_elements = {22, 80, 443}},
        nftables::ImmediateExpr{.dreg = 0, .value = static_cast<uint32_t>(nftables::Verdict::Drop)}
    };

    const auto result = nftables::BytecodeEvaluator::evaluate_rule(rule, packet);

    if (result == nftables::Verdict::Drop) {
        std::cout << "[nftables VM C++] Пакет відкинуто (NF_DROP)\n";
    } else if (result == nftables::Verdict::Accept) {
        std::cout << "[nftables VM C++] Пакет прийнято (NF_ACCEPT)\n";
    } else {
        std::cout << "[nftables VM C++] Умова не виконалася (NFT_BREAK)\n";
    }

    return 0;
}
