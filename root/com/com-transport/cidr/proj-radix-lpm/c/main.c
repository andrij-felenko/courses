#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Вузол префіксного дерева Radix Trie */
typedef struct TrieNode {
    struct TrieNode *children[2]; /* 0: лівий нащадок, 1: правий нащадок */
    bool has_route;               /* прапорець закінчення префікса */
    uint32_t next_hop;            /* IP-адреса наступного маршрутизатора */
    uint32_t prefix_len;          /* довжина префікса /n */
} TrieNode;

/* Створення та ініціалізація нового вузла */
static TrieNode *trie_node_create(void) {
    TrieNode *node = (TrieNode *)calloc(1, sizeof(TrieNode));
    return node;
}

/* Отримання n-го біта 32-бітної адреси (0 = найстарший MSB, 31 = наймолодший LSB) */
static inline uint32_t get_bit(uint32_t ip, uint32_t bit_index) {
    return (ip >> (31 - bit_index)) & 1U;
}

/* Вставка префікса довільної довжини в дерево пересилання */
void trie_insert(TrieNode *root, uint32_t network_ip, uint32_t prefix_len, uint32_t next_hop) {
    if (!root || prefix_len > 32) return;

    TrieNode *curr = root;
    for (uint32_t i = 0; i < prefix_len; ++i) {
        uint32_t bit = get_bit(network_ip, i);
        if (!curr->children[bit]) {
            curr->children[bit] = trie_node_create();
        }
        curr = curr->children[bit];
    }

    curr->has_route = true;
    curr->next_hop = next_hop;
    curr->prefix_len = prefix_len;
}

/* Пошук найдовшого збігу префікса (Longest Prefix Match) */
bool trie_lookup(const TrieNode *root, uint32_t target_ip, uint32_t *out_next_hop, uint32_t *out_prefix_len) {
    if (!root) return false;

    const TrieNode *curr = root;
    const TrieNode *best_match = NULL;

    /* Перевіряємо наявність маршруту в корені (0.0.0.0/0 default route) */
    if (curr->has_route) {
        best_match = curr;
    }

    /* Послідовний спуск за бітами адреси цілі */
    for (uint32_t i = 0; i < 32; ++i) {
        uint32_t bit = get_bit(target_ip, i);
        if (!curr->children[bit]) {
            break; /* гілка закінчилася — точнішого збігу в дереві немає */
        }
        curr = curr->children[bit];
        if (curr->has_route) {
            best_match = curr; /* зафіксували точніший (довший) маршрут */
        }
    }

    if (best_match) {
        if (out_next_hop) *out_next_hop = best_match->next_hop;
        if (out_prefix_len) *out_prefix_len = best_match->prefix_len;
        return true;
    }
    return false;
}

/* Рекурсивне видалення префікса з підрізанням невикористаних вузлів */
static bool trie_remove_helper(TrieNode *node, uint32_t ip, uint32_t prefix_len, uint32_t depth) {
    if (!node) return false;

    if (depth == prefix_len) {
        if (!node->has_route) return false;
        node->has_route = false;
        /* Якщо вузол не має нащадків, його можна видалити */
        return (!node->children[0] && !node->children[1]);
    }

    uint32_t bit = get_bit(ip, depth);
    if (trie_remove_helper(node->children[bit], ip, prefix_len, depth + 1)) {
        free(node->children[bit]);
        node->children[bit] = NULL;
        /* Перевіряємо, чи став цей вузол порожнім */
        return (!node->has_route && !node->children[0] && !node->children[1]);
    }
    return false;
}

void trie_delete(TrieNode *root, uint32_t ip, uint32_t prefix_len) {
    if (root && prefix_len <= 32) {
        trie_remove_helper(root, ip, prefix_len, 0);
    }
}

/* Рекурсивне звільнення пам'яті всіх вузлів дерева */
void trie_free(TrieNode *root) {
    if (!root) return;
    trie_free(root->children[0]);
    trie_free(root->children[1]);
    free(root);
}

/* Допоміжна функція складання 32-бітного числа з 4 октетів */
uint32_t parse_ipv4(uint8_t a, uint8_t b, uint8_t c, uint8_t d) {
    return ((uint32_t)a << 24) | ((uint32_t)b << 16) | ((uint32_t)c << 8) | (uint32_t)d;
}

int main(void) {
    TrieNode *fib = trie_node_create();

    /* Заповнюємо таблицю FIB різними префіксами */
    trie_insert(fib, parse_ipv4(0, 0, 0, 0), 0, parse_ipv4(192, 0, 2, 1));          /* Default /0 */
    trie_insert(fib, parse_ipv4(198, 51, 0, 0), 16, parse_ipv4(10, 0, 0, 1));       /* Регіон /16 */
    trie_insert(fib, parse_ipv4(198, 51, 100, 0), 22, parse_ipv4(10, 0, 1, 1));     /* Дата-центр /22 */
    trie_insert(fib, parse_ipv4(198, 51, 100, 32), 27, parse_ipv4(10, 0, 2, 1));    /* Серверний пул /27 */

    /* Тестовий пакет для адреси 198.51.100.45 */
    uint32_t dst_ip = parse_ipv4(198, 51, 100, 45);
    uint32_t next_hop = 0, matched_len = 0;

    if (trie_lookup(fib, dst_ip, &next_hop, &matched_len)) {
        printf("Знайдено маршрут LPM: префікс /%u, Next-Hop: %u.%u.%u.%u\n",
               matched_len,
               (next_hop >> 24) & 0xFF,
               (next_hop >> 16) & 0xFF,
               (next_hop >> 8) & 0xFF,
               next_hop & 0xFF);
    } else {
        printf("Маршрут не знайдено: пакет скинуто\n");
    }

    trie_delete(fib, parse_ipv4(198, 51, 100, 32), 27);
    trie_free(fib);
    return 0;
}
