/* Допоміжне сортування дельт за версією для гарантії інваріанта префікса */
static int compare_deltas_by_version(const void *a, const void *b) {
    const GossipDelta *da = (const GossipDelta *)a;
    const GossipDelta *db = (const GossipDelta *)b;
    if (da->version < db->version) return -1;
    if (da->version > db->version) return 1;
    return 0;
}

/* Генерація дельт для партнера на основі його дайджесту */
size_t collect_deltas_for_peer(const ScuttlebuttEngine *engine,
                               const GossipDigest *peer_digest,
                               size_t peer_digest_len,
                               GossipDelta *out_deltas,
                               size_t max_out_deltas) {
    size_t total_deltas = 0;
    size_t approx_bytes = 0;

    for (size_t i = 0; i < engine->node_count; ++i) {
        const EndpointState *local_node = &engine->nodes[i];
        
        /* Шукаємо запис про цей вузол у дайджесті партнера */
        const GossipDigest *peer_entry = NULL;
        for (size_t j = 0; j < peer_digest_len; ++j) {
            if (strcmp(peer_digest[j].node_id, local_node->node_id) == 0) {
                peer_entry = &peer_digest[j];
                break;
            }
        }

        /* Тимчасовий масив для дельт цього конкретного вузла */
        GossipDelta node_deltas[MAX_KEYS_PER_NODE];
        size_t node_delta_count = 0;

        if (peer_entry == NULL || local_node->generation > peer_entry->generation) {
            /* Партнер нічого не знає або його покоління застаріло: віддаємо всі ключі */
            for (size_t k = 0; k < local_node->value_count; ++k) {
                GossipDelta *d = &node_deltas[node_delta_count++];
                strncpy(d->node_id, local_node->node_id, MAX_STR_LEN - 1);
                d->generation = local_node->generation;
                strncpy(d->key, local_node->values[k].key, MAX_STR_LEN - 1);
                strncpy(d->value, local_node->values[k].value, MAX_STR_LEN - 1);
                d->version = local_node->values[k].version;
            }
        } else if (local_node->generation == peer_entry->generation &&
                   local_node->max_version > peer_entry->max_version) {
            /* Покоління збігається, але ми маємо свіжіші версії */
            for (size_t k = 0; k < local_node->value_count; ++k) {
                if (local_node->values[k].version > peer_entry->max_version) {
                    GossipDelta *d = &node_deltas[node_delta_count++];
                    strncpy(d->node_id, local_node->node_id, MAX_STR_LEN - 1);
                    d->generation = local_node->generation;
                    strncpy(d->key, local_node->values[k].key, MAX_STR_LEN - 1);
                    strncpy(d->value, local_node->values[k].value, MAX_STR_LEN - 1);
                    d->version = local_node->values[k].version;
                }
            }
        }

        /* Сортуємо дельти цього вузла за зростанням версій */
        qsort(node_deltas, node_delta_count, sizeof(GossipDelta), compare_deltas_by_version);

        /* Додаємо в вихідний пакет з контролем MTU */
        for (size_t k = 0; k < node_delta_count; ++k) {
            size_t item_size = sizeof(GossipDelta);
            if (approx_bytes + item_size > MTU_PAYLOAD_LIMIT || total_deltas >= max_out_deltas) {
                return total_deltas; /* Пакет заповнено без створення дірок у версіях */
            }
            out_deltas[total_deltas++] = node_deltas[k];
            approx_bytes += item_size;
        }
    }

    return total_deltas;
}
