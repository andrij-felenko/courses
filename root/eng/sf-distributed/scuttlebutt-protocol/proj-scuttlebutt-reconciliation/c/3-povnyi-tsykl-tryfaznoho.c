/* Застосування дельт до локального стану C-рушія */
void apply_deltas_c(ScuttlebuttEngine *engine, const GossipDelta *deltas, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        const GossipDelta *d = &deltas[i];
        
        /* Пошук або створення вузла в локальній таблиці */
        EndpointState *target = NULL;
        for (size_t j = 0; j < engine->node_count; ++j) {
            if (strcmp(engine->nodes[j].node_id, d->node_id) == 0) {
                target = &engine->nodes[j];
                break;
            }
        }
        if (target == NULL && engine->node_count < MAX_NODES) {
            target = &engine->nodes[engine->node_count++];
            strncpy(target->node_id, d->node_id, MAX_STR_LEN - 1);
            target->generation = d->generation;
            target->max_version = 0;
            target->value_count = 0;
        }
        if (target == NULL) continue;

        if (d->generation > target->generation) {
            /* Оновлення епохи */
            target->generation = d->generation;
            target->max_version = d->version;
            target->value_count = 0;
            strncpy(target->values[0].key, d->key, MAX_STR_LEN - 1);
            strncpy(target->values[0].value, d->value, MAX_STR_LEN - 1);
            target->values[0].version = d->version;
            target->value_count = 1;
        } else if (d->generation == target->generation) {
            bool found = false;
            for (size_t k = 0; k < target->value_count; ++k) {
                if (strcmp(target->values[k].key, d->key) == 0) {
                    if (d->version > target->values[k].version) {
                        strncpy(target->values[k].value, d->value, MAX_STR_LEN - 1);
                        target->values[k].version = d->version;
                    }
                    found = true;
                    break;
                }
            }
            if (!found && target->value_count < MAX_KEYS_PER_NODE) {
                VersionedValue *nv = &target->values[target->value_count++];
                strncpy(nv->key, d->key, MAX_STR_LEN - 1);
                strncpy(nv->value, d->value, MAX_STR_LEN - 1);
                nv->version = d->version;
            }
            if (d->version > target->max_version) {
                target->max_version = d->version;
            }
        }
    }
}

int main(void) {
    ScuttlebuttEngine node_a, node_b;
    memset(&node_a, 0, sizeof(node_a));
    memset(&node_b, 0, sizeof(node_b));

    strncpy(node_a.local_node_id, "Node-A", MAX_STR_LEN - 1);
    strncpy(node_b.local_node_id, "Node-B", MAX_STR_LEN - 1);

    /* Ініціалізація локального стану Node-A */
    EndpointState *ea = &node_a.nodes[node_a.node_count++];
    strncpy(ea->node_id, "Node-A", MAX_STR_LEN - 1);
    ea->generation = 100;
    ea->max_version = 2;
    strncpy(ea->values[0].key, "STATUS", MAX_STR_LEN - 1);
    strncpy(ea->values[0].value, "NORMAL", MAX_STR_LEN - 1);
    ea->values[0].version = 1;
    strncpy(ea->values[1].key, "LOAD", MAX_STR_LEN - 1);
    strncpy(ea->values[1].value, "0.85", MAX_STR_LEN - 1);
    ea->values[1].version = 2;
    ea->value_count = 2;

    /* 1. Фаза SYN: Node-A надсилає дайджест до Node-B */
    GossipDigest syn_digest[MAX_NODES];
    size_t syn_len = 1;
    strncpy(syn_digest[0].node_id, "Node-A", MAX_STR_LEN - 1);
    syn_digest[0].generation = 100;
    syn_digest[0].max_version = 2;

    /* 2. Фаза ACK: Node-B обчислює дельти для Node-A та формує свій дайджест */
    GossipDelta ack_deltas[32];
    size_t ack_delta_count = collect_deltas_for_peer(&node_b, syn_digest, syn_len, ack_deltas, 32);

    /* 3. Фаза ACK2: Node-A застосовує ACK дельти і надсилає залишок до Node-B */
    apply_deltas_c(&node_a, ack_deltas, ack_delta_count);

    GossipDigest ack_digest[MAX_NODES];
    size_t ack_digest_len = 0; /* Node-B ще не має своїх ключів */
    GossipDelta ack2_deltas[32];
    size_t ack2_delta_count = collect_deltas_for_peer(&node_a, ack_digest, ack_digest_len, ack2_deltas, 32);

    /* Node-B застосовує ACK2 дельти */
    apply_deltas_c(&node_b, ack2_deltas, ack2_delta_count);

    printf("Реконсиляція C завершена успішно. Node-B знає про Node-A версію: %lu\n",
           node_b.nodes[0].max_version);
    return 0;
}
