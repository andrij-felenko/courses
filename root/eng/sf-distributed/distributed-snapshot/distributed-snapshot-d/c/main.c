#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_PEERS 8
#define MAX_MESSAGES_PER_CHANNEL 32

typedef enum {
    MSG_DATA = 1,
    MSG_MARKER = 2
} MessageType;

typedef struct {
    MessageType type;
    uint32_t from_id;
    uint32_t to_id;
    int32_t payload;
} NetworkMessage;

typedef struct {
    uint32_t message_count;
    int32_t messages[MAX_MESSAGES_PER_CHANNEL];
} ChannelState;

typedef struct {
    uint32_t node_id;
    int32_t account_balance;
    
    /* Стан алгоритму знімка */
    bool state_recorded;
    int32_t snapshot_balance;
    
    uint32_t num_peers;
    bool channel_recording[MAX_PEERS];
    bool marker_received[MAX_PEERS];
    ChannelState recorded_channels[MAX_PEERS];
} SnapshotNode;

void node_init(SnapshotNode* node, uint32_t id, int32_t initial_balance, uint32_t num_peers) {
    node->node_id = id;
    node->account_balance = initial_balance;
    node->state_recorded = false;
    node->snapshot_balance = 0;
    node->num_peers = num_peers;
    
    for (uint32_t i = 0; i < num_peers; ++i) {
        node->channel_recording[i] = false;
        node->marker_received[i] = false;
        node->recorded_channels[i].message_count = 0;
    }
}

/* Ініціація знімка самим вузлом */
void node_initiate_snapshot(SnapshotNode* node, void (*send_fn)(NetworkMessage)) {
    node->state_recorded = true;
    node->snapshot_balance = node->account_balance;
    
    /* Розсилаємо маркери в усі вихідні канали */
    for (uint32_t peer = 0; peer < node->num_peers; ++peer) {
        if (peer == node->node_id) continue;
        
        /* Вмикаємо запис для вхідного каналу від цього вузла */
        node->channel_recording[peer] = true;
        node->marker_received[peer] = false;
        
        NetworkMessage marker = {
            .type = MSG_MARKER,
            .from_id = node->node_id,
            .to_id = peer,
            .payload = 0
        };
        send_fn(marker);
    }
}

/* Обробка вхідного повідомлення */
void node_handle_message(SnapshotNode* node, NetworkMessage msg, void (*send_fn)(NetworkMessage)) {
    uint32_t src = msg.from_id;
    
    if (msg.type == MSG_MARKER) {
        if (!node->state_recorded) {
            /* Випадок А: Перший отриманий маркер */
            node->state_recorded = true;
            node->snapshot_balance = node->account_balance;
            
            node->marker_received[src] = true;
            node->channel_recording[src] = false; /* Канал джерела порожній */
            node->recorded_channels[src].message_count = 0;
            
            /* Розсилаємо маркер далі */
            for (uint32_t peer = 0; peer < node->num_peers; ++peer) {
                if (peer == node->node_id) continue;
                
                if (peer != src) {
                    node->channel_recording[peer] = true;
                    node->marker_received[peer] = false;
                }
                
                NetworkMessage marker = {
                    .type = MSG_MARKER,
                    .from_id = node->node_id,
                    .to_id = peer,
                    .payload = 0
                };
                send_fn(marker);
            }
        } else {
            /* Випадок Б: Повторний маркер із каналу, що записувався */
            node->marker_received[src] = true;
            node->channel_recording[src] = false; /* Зупиняємо запис */
        }
    } else {
        /* Прикладне повідомлення (переказ коштів) */
        node->account_balance += msg.payload;
        
        /* Якщо для цього каналу триває запис, зберігаємо повідомлення у знімок */
        if (node->channel_recording[src]) {
            ChannelState* ch = &node->recorded_channels[src];
            if (ch->message_count < MAX_MESSAGES_PER_CHANNEL) {
                ch->messages[ch->message_count++] = msg.payload;
            }
        }
    }
}

bool node_is_snapshot_complete(const SnapshotNode* node) {
    if (!node->state_recorded) return false;
    for (uint32_t i = 0; i < node->num_peers; ++i) {
        if (i != node->node_id && !node->marker_received[i]) {
            return false;
        }
    }
    return true;
}
