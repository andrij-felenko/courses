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
