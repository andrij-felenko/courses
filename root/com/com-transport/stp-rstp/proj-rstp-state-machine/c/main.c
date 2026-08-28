#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Перелік ролей портів RSTP (IEEE 802.1w)
typedef enum {
    ROLE_DISABLED = 0,
    ROLE_ROOT,
    ROLE_DESIGNATED,
    ROLE_ALTERNATE,
    ROLE_BACKUP
} rstp_port_role_t;

// Перелік станів портів RSTP
typedef enum {
    STATE_DISCARDING = 0,
    STATE_LEARNING,
    STATE_FORWARDING
} rstp_port_state_t;

// Структура 8-байтового Bridge ID (пріоритет + MAC-адреса)
typedef struct {
    uint16_t priority;
    uint8_t  mac[6];
} bridge_id_t;

// Вектор пріоритету BPDU
typedef struct {
    bridge_id_t root_id;
    uint32_t    root_path_cost;
    bridge_id_t designated_bridge_id;
    uint16_t    designated_port_id;
} rstp_priority_vector_t;

// Вхідний кадр BPDU
typedef struct {
    uint16_t               protocol_id;
    uint8_t                version;
    uint8_t                bpdu_type;
    uint8_t                flags;
    rstp_priority_vector_t vector;
    uint16_t               message_age;
    uint16_t               max_age;
    uint16_t               hello_time;
    uint16_t               forward_delay;
} rstp_bpdu_t;

// Порівняння двох Bridge ID (повертає <0 якщо a < b, >0 якщо a > b, 0 якщо однакові)
static int compare_bridge_id(const bridge_id_t *a, const bridge_id_t *b) {
    if (a->priority != b->priority) {
        return (a->priority < b->priority) ? -1 : 1;
    }
    return memcmp(a->mac, b->mac, 6);
}

// Порівняння векторів пріоритету BPDU
// Повертає true, якщо vector_a кращий (має вищий пріоритет), ніж vector_b
bool is_vector_superior(const rstp_priority_vector_t *a, const rstp_priority_vector_t *b) {
    // 1. Порівняння Root ID
    int cmp_root = compare_bridge_id(&a->root_id, &b->root_id);
    if (cmp_root != 0) {
        return cmp_root < 0;
    }

    // 2. Порівняння Root Path Cost
    if (a->root_path_cost != b->root_path_cost) {
        return a->root_path_cost < b->root_path_cost;
    }

    // 3. Порівняння Designated Bridge ID
    int cmp_desig_bridge = compare_bridge_id(&a->designated_bridge_id, &b->designated_bridge_id);
    if (cmp_desig_bridge != 0) {
        return cmp_desig_bridge < 0;
    }

    // 4. Порівняння Designated Port ID
    return a->designated_port_id < b->designated_port_id;
}

// Обробка вхідного BPDU та визначення нової ролі порту
rstp_port_role_t process_incoming_bpdu(const rstp_bpdu_t *incoming_bpdu,
                                       const rstp_priority_vector_t *current_port_vector,
                                       const bridge_id_t *our_bridge_id) {
    // Якщо прийшов кращий BPDU, ніж наш поточний активний вектор
    if (is_vector_superior(&incoming_bpdu->vector, current_port_vector)) {
        // Якщо Root ID в BPDU менший за наш власний BID, ми стаємо транзитним вузлом (Root Port)
        if (compare_bridge_id(&incoming_bpdu->vector.root_id, our_bridge_id) < 0) {
            return ROLE_ROOT;
        } else {
            // Інакше ми програли вибори на цьому сегменті і блокуємо порт (Alternate Port)
            return ROLE_ALTERNATE;
        }
    }

    // Якщо наш власний BPDU кращий, наш порт залишається Designated Port
    return ROLE_DESIGNATED;
}

int main(void) {
    bridge_id_t root_bridge = { .priority = 4096, .mac = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55} };
    bridge_id_t our_bridge  = { .priority = 32768, .mac = {0x00, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE} };

    rstp_priority_vector_t current_vector = {
        .root_id = our_bridge,
        .root_path_cost = 0,
        .designated_bridge_id = our_bridge,
        .designated_port_id = 0x8001
    };

    rstp_bpdu_t rx_bpdu = {
        .protocol_id = 0,
        .version = 2,
        .bpdu_type = 2,
        .flags = 0x3E, // Proposal + Designated Role + Forwarding
        .vector = {
            .root_id = root_bridge,
            .root_path_cost = 4,
            .designated_bridge_id = root_bridge,
            .designated_port_id = 0x8002
        }
    };

    rstp_port_role_t new_role = process_incoming_bpdu(&rx_bpdu, &current_vector, &our_bridge);

    printf("Результат виборів RSTP (C):\n");
    if (new_role == ROLE_ROOT) {
        printf("Статус: Порт обрано як Root Port (найкоротший шлях до Root Bridge)\n");
    } else if (new_role == ROLE_ALTERNATE) {
        printf("Статус: Порт обрано як Alternate Port (блокування для усунення петлі)\n");
    } else {
        printf("Статус: Порт залишається Designated Port\n");
    }

    return 0;
}
