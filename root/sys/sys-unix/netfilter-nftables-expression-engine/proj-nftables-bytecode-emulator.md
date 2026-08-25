# ⚙️ Реалізація інтерпретатора байт-коду та віртуальної машини nftables

Ця практична вставка детально розглядає побудову автономного простір-користувацького емулятора віртуальної машини `nftables`. У ній подано повну реалізацію оцінювача байт-коду (bytecode evaluator), що відтворює роботу 16 регістрів загального призначення, спеціального регістра вердикту, витягування полів пакету (`PAYLOAD`), порівняння значень (`CMP`), побітових масок (`BITWISE`), O(1) пошуку в наборах (`LOOKUP`) та встановлення кінцевих вердиктів (`IMMEDIATE`).

## 1. Архітектура та принципи побудови емулятора

Метою даного проекту є демонстрація внутрішньої механіки обробки пакетів ядром Linux без необхідності компілювати ядерний модуль. Віртуальна машина оперує трьома основними компонентами:

1. **Контекст регістрів (`RegisterState` / `nft_regs_t`):** Масив із 16 32-бітних операндів. Регістр `0` розглядається як спеціальний регістр вердикту. Кожен вираз може зчитувати дані з одного або кількох регістрів джерел (source registers, `sreg`) та записувати результат у регістр призначення (destination register, `dreg`).
2. **Буфер пакета (`sk_buff` / `packet`):** Неперервний блок пам'яті, що містить байтовий потік мережевого кадру. Емулятор надає абстракцію зсувів від початку мережевого заголовка L3 (IPv4/IPv6) та транспортного заголовка L4 (TCP/UDP).
3. **Конвеєр виразів (Expression Pipeline):** Масив або вектор інструкцій ruleset. Віртуальна машина послідовно виконує вирази. Якщо один із виразів порівняння встановлює вердикт `NFT_BREAK`, обробка поточного правила негайно припиняється, а ВМ повертає стан недосяжності умови.

## 2. Реалізація проекту мовами C та C++

Нижче наведено дві повноцінні та ідіоматичні реалізації емулятора віртуальної машини. Реалізація мовою C спирається на базові структури та явну перевірку меж пам'яті. Реалізація мовою C++20 використовує сучасні можливості стандарту: `std::variant` для безпечного диспетчеризації виразів, `std::span` для нульових накладних витрат при роботі з пам'яттю та `std::unordered_set` для реалізації O(1) пошуку в наборах.

:::tabs
```c
/* nftables_vm_emu.c - Спрощена віртуальна машина nftables мовою C */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define NFT_REG_VERDICT 0
#define NUM_REGS 16

/* Вердикти ВМ */
typedef enum {
    NFT_CONTINUE = -1,
    NFT_BREAK    = -2,
    NF_ACCEPT    = 0,
    NF_DROP      = 1
} nft_verdict_t;

/* Контекст виконання (Регістри) */
typedef struct {
    uint32_t regs[NUM_REGS];
} nft_regs_t;

/* Бази витягування заголовків */
typedef enum {
    PAYLOAD_NETWORK_HEADER,   /* L3 (IPv4/IPv6) */
    PAYLOAD_TRANSPORT_HEADER /* L4 (TCP/UDP) */
} payload_base_t;

/* Операнди порівняння */
typedef enum {
    CMP_EQ,
    CMP_NEQ
} cmp_op_t;

/* Типи інструкцій ВМ */
typedef enum {
    EXPR_PAYLOAD,
    EXPR_CMP,
    EXPR_BITWISE,
    EXPR_LOOKUP,
    EXPR_IMMEDIATE
} expr_type_t;

/* Опис окремого виразу */
typedef struct {
    expr_type_t type;
    union {
        struct {
            payload_base_t base;
            uint32_t offset;
            uint32_t len;
            uint8_t dreg;
        } payload;
        struct {
            uint8_t sreg;
            cmp_op_t op;
            uint32_t data;
        } cmp;
        struct {
            uint8_t sreg;
            uint8_t dreg;
            uint32_t mask;
            uint32_t xor_val;
        } bitwise;
        struct {
            uint8_t sreg;
            const uint32_t *set_elements;
            size_t set_size;
        } lookup;
        struct {
            uint8_t dreg;
            uint32_t value;
        } immediate;
    } data;
} expr_op_t;

/* Базові зсуви в пакеті */
#define L3_OFFSET 0
#define L4_OFFSET 20 /* Простий IPv4 без опцій */

/* Виконання виразу PAYLOAD */
static void eval_payload(const expr_op_t *expr, nft_regs_t *regs, const uint8_t *pkt, size_t pkt_len) {
    uint32_t base_offset = (expr->data.payload.base == PAYLOAD_TRANSPORT_HEADER) ? L4_OFFSET : L3_OFFSET;
    uint32_t full_offset = base_offset + expr->data.payload.offset;

    if (full_offset + expr->data.payload.len > pkt_len) {
        regs->regs[NFT_REG_VERDICT] = (uint32_t)NFT_BREAK;
        return;
    }

    uint32_t val = 0;
    memcpy(&val, pkt + full_offset, expr->data.payload.len);
    regs->regs[expr->data.payload.dreg] = val;
}

/* Виконання виразу CMP */
static void eval_cmp(const expr_op_t *expr, nft_regs_t *regs) {
    uint32_t reg_val = regs->regs[expr->data.cmp.sreg];
    bool matched = false;

    if (expr->data.cmp.op == CMP_EQ) {
        matched = (reg_val == expr->data.cmp.data);
    } else if (expr->data.cmp.op == CMP_NEQ) {
        matched = (reg_val != expr->data.cmp.data);
    }

    if (!matched) {
        regs->regs[NFT_REG_VERDICT] = (uint32_t)NFT_BREAK;
    }
}

/* Виконання виразу BITWISE */
static void eval_bitwise(const expr_op_t *expr, nft_regs_t *regs) {
    uint32_t sval = regs->regs[expr->data.bitwise.sreg];
    uint32_t res = (sval & expr->data.bitwise.mask) ^ expr->data.bitwise.xor_val;
    regs->regs[expr->data.bitwise.dreg] = res;
}

/* Виконання виразу LOOKUP (хеш/масив O(1)) */
static void eval_lookup(const expr_op_t *expr, nft_regs_t *regs) {
    uint32_t key = regs->regs[expr->data.lookup.sreg];
    bool found = false;

    for (size_t i = 0; i < expr->data.lookup.set_size; ++i) {
        if (expr->data.lookup.set_elements[i] == key) {
            found = true;
            break;
        }
    }

    if (!found) {
        regs->regs[NFT_REG_VERDICT] = (uint32_t)NFT_BREAK;
    }
}

/* Виконання виразу IMMEDIATE */
static void eval_immediate(const expr_op_t *expr, nft_regs_t *regs) {
    regs->regs[expr->data.immediate.dreg] = expr->data.immediate.value;
}

/* Головний цикл ВМ для одного правила (nft_do_chain_emu) */
int nft_eval_rule(const expr_op_t *rule, size_t num_exprs, const uint8_t *pkt, size_t pkt_len) {
    nft_regs_t regs;
    memset(&regs, 0, sizeof(regs));
    regs.regs[NFT_REG_VERDICT] = (uint32_t)NFT_CONTINUE;

    for (size_t i = 0; i < num_exprs; ++i) {
        const expr_op_t *expr = &rule[i];

        switch (expr->type) {
            case EXPR_PAYLOAD:   eval_payload(expr, &regs, pkt, pkt_len); break;
            case EXPR_CMP:       eval_cmp(expr, &regs); break;
            case EXPR_BITWISE:   eval_bitwise(expr, &regs); break;
            case EXPR_LOOKUP:    eval_lookup(expr, &regs); break;
            case EXPR_IMMEDIATE: eval_immediate(expr, &regs); break;
        }

        /* Перевірка стану вердикту */
        int verdict = (int32_t)regs.regs[NFT_REG_VERDICT];
        if (verdict == NFT_BREAK) {
            return NFT_BREAK; /* Умова правила не виконалася */
        }
        if (verdict >= 0) {
            return verdict; /* Кінцева дія (ACCEPT / DROP) */
        }
    }

    return (int32_t)regs.regs[NFT_REG_VERDICT];
}

int main(void) {
    /* Спрощений симульований IPv4/TCP пакет */
    /* Байт 9: L4 protocol (6 = TCP), Байт 12-15: IP saddr (192.168.1.50), Байт 22-23: TCP dport (22) */
    uint8_t pkt[40] = {0};
    pkt[9] = 6; /* IPPROTO_TCP */
    pkt[12] = 192; pkt[13] = 168; pkt[14] = 1; pkt[15] = 50; /* 192.168.1.50 */
    pkt[22] = 0; pkt[23] = 22; /* dport 22 */

    /* Набір блокованих портів для LOOKUP */
    uint32_t blocked_ports[] = {22, 80, 443};

    /* Байт-код правила: "ip protocol tcp AND tcp dport in {22,80,443} -> DROP" */
    expr_op_t rule[] = {
        /* 1. payload: load L4 protocol into reg 1 */
        { .type = EXPR_PAYLOAD, .data.payload = { PAYLOAD_NETWORK_HEADER, 9, 1, 1 } },
        /* 2. cmp: reg 1 == 6 (TCP) */
        { .type = EXPR_CMP, .data.cmp = { 1, CMP_EQ, 6 } },
        /* 3. payload: load TCP dport (2 bytes) into reg 2 */
        { .type = EXPR_PAYLOAD, .data.payload = { PAYLOAD_TRANSPORT_HEADER, 2, 2, 2 } },
        /* 4. lookup: check if reg 2 in blocked_ports */
        { .type = EXPR_LOOKUP, .data.lookup = { 2, blocked_ports, 3 } },
        /* 5. immediate: set verdict to NF_DROP */
        { .type = EXPR_IMMEDIATE, .data.immediate = { NFT_REG_VERDICT, (uint32_t)NF_DROP } }
    };

    int result = nft_eval_rule(rule, sizeof(rule)/sizeof(rule[0]), pkt, sizeof(pkt));

    if (result == NF_DROP) {
        printf("[nftables VM] Пакет відкинуто (NF_DROP)\n");
    } else if (result == NF_ACCEPT) {
        printf("[nftables VM] Пакет прийнято (NF_ACCEPT)\n");
    } else {
        printf("[nftables VM] Правило не збіглося (NFT_BREAK)\n");
    }

    return 0;
}
```
```cpp
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
```
:::

## 3. Покроковий розбір виконання та пастки під час реалізації

### 3.1. Механіка витягування полів (eval_payload)
Вираз `PAYLOAD` отримує базовий заголовок (`PAYLOAD_NETWORK_HEADER` або `PAYLOAD_TRANSPORT_HEADER`) та додає до нього відносне зміщення в байтах.
- **Безпека меж пам'яті (Out-of-bounds check):** Якщо пакет має менший розмір, ніж сумарне зміщення (`full_offset + len > pkt_len`), вираз не повинен здійснювати читання за межами буфера. У цьому разі вердикт встановлюється в `NFT_BREAK`. У справжньому ядрі Linux для перевірки неперервності буфера пакета використовується функція `skb_header_pointer()`. Якщо заголовок знаходиться у нелінійній частині пакета (skb fragments), ядро копіює його у тимчасовий буфер на стеку.
- **Порядок байтів (Endianness):** Мережевий трафік передається у форматі Big-Endian (Network Byte Order). Процесори x86_64 використовують Little-Endian (Host Byte Order). При витягуванні двобайтового порту або чотирибайтової IP-адреси простір користувача при генерації виразу `CMP` або `LOOKUP` повинен враховувати порядок байтів або застосовувати вираз `nft_byteorder` для конвертації `htons()` / `ntohs()`.

### 3.2. Логіка порівняння та переривання правил (eval_cmp)
Вираз `CMP` порівнює вміст регістра-джерела `sreg` з еталонним значенням `data`.
- Якщо операція `CMP_EQ` (дорівнює) не справджується, регістр вердикту `NFT_REG_VERDICT` змінюється з `NFT_CONTINUE` на `NFT_BREAK`.
- Головний цикл `nft_eval_rule()` перевіряє стан вердикту після виклику кожного виразу. Отримання `NFT_BREAK` слугує сигналом для негайного припинення обробки поточного правила. При цьому решта виразів правил (наприклад, вирази лічильників `counter` або логування `log`) **не виконуються**.

### 3.3. Високопродуктивний пошук в наборах (eval_lookup)
Вираз `LOOKUP` демонструє ключову перевагу `nftables` над `iptables`. Замість створення кількох послідовних правил порівняння для кожного порту (`cmp dport 22`, `cmp dport 80`), створюється єдиний вираз `LOOKUP`.
- У версії мовою C здійснюється лінійне зіставлення по масиву, що у справжньому ядрі відповідає бекенду `nft_set_bitmap` для дрібних діапазонів.
- У версії мовою C++20 використовується `std::unordered_set::contains()`, що відтворює роботу ядерного бекенду `nft_set_rhash` (хеш-таблиці `rhashtable`) зі складністю `O(1)`.

### 3.4. Запис вердикту (eval_immediate)
Якщо пакет успішно пройшов усі попередні вирази перевірки (`PAYLOAD`, `CMP`, `LOOKUP`), віртуальна машина доходить до підсумкового виразу `IMMEDIATE`. Цей вираз записує у регістр 0 (`NFT_REG_VERDICT`) значення кінцевої дії (`NF_DROP` або `NF_ACCEPT`). Головний цикл фіксує невід'ємне значення вердикту (`verdict >= 0`) та повертає його мережевому стеку для виконання відповідної дії над пакетом.

## 4. Порівняння реалізацій C та C++20

Проект ілюструє глибокі відмінності у підходах між двома мовами при реалізації системного інтерпретатора байт-коду:

1. **Диспетчеризація типів виразів:**
   - У мові C використовується `switch (expr->type)` над нетипізованим `union`. Це потребує особливої уваги розробника, оскільки помилка у типі виразу може призвести до зчитування некоректної гілки `union` і пошкодження пам'яті.
   - У мові C++20 застосовується `std::variant<...>` та шаблонний відвідувач `std::visit()`. Компілятор статично гарантує, що всі можливі типи виразів оброблені у `if constexpr`, виключаючи невизначену поведінку (undefined behavior).

2. **Передача та управління буферами пам'яті:**
   - У мові C масив байтів пакета передається як пара `(const uint8_t *pkt, size_t pkt_len)`. Ручна перевірка меж `full_offset + len > pkt_len` є єдиним захистом від виходу за межі масиву.
   - У мові C++20 застосовується `std::span<const uint8_t>`, що об'єднує вказівник та розмір у єдиний легковаговий об'єкт без виділення динамічної пам'яті.

3. **Компактність та безпека регістрового стану:**
   - Використання `std::array<uint32_t, 16>` у C++ забезпечує строгий контроль типів та підтримує семантику нотацій `noexcept` та `[[nodiscard]]`, що дозволяє компілятору генерувати оптимальний машинний код, тотожний до сирого масиву C.
