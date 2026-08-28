typedef struct {
    char key[64];
    uint32_t frequency;
} cm_heavy_item_t;

typedef struct {
    uint32_t capacity;
    uint32_t size;
    cm_heavy_item_t *items;
} cm_min_heap_t;

static void heap_sift_down(cm_min_heap_t *heap, uint32_t idx) {
    while (2 * idx + 1 < heap->size) {
        uint32_t left = 2 * idx + 1;
        uint32_t right = 2 * idx + 2;
        uint32_t smallest = left;
        
        if (right < heap->size && heap->items[right].frequency < heap->items[left].frequency) {
            smallest = right;
        }
        if (heap->items[idx].frequency <= heap->items[smallest].frequency) {
            break;
        }
        cm_heavy_item_t tmp = heap->items[idx];
        heap->items[idx] = heap->items[smallest];
        heap->items[smallest] = tmp;
        idx = smallest;
    }
}

void cm_track_heavy(cm_min_heap_t *heap, cm_sketch_t *sketch, const char *key, uint32_t count) {
    cm_update_conservative(sketch, key, strlen(key), count);
    uint32_t est = cm_estimate(sketch, key, strlen(key));
    
    /* Перевірка, чи ключ уже є в купі */
    for (uint32_t i = 0; i < heap->size; ++i) {
        if (strcmp(heap->items[i].key, key) == 0) {
            heap->items[i].frequency = est;
            heap_sift_down(heap, i);
            return;
        }
    }
    
    if (heap->size < heap->capacity) {
        strncpy(heap->items[heap->size].key, key, 63);
        heap->items[heap->size].frequency = est;
        uint32_t curr = heap->size++;
        while (curr > 0) {
            uint32_t parent = (curr - 1) / 2;
            if (heap->items[parent].frequency <= heap->items[curr].frequency) break;
            cm_heavy_item_t tmp = heap->items[parent];
            heap->items[parent] = heap->items[curr];
            heap->items[curr] = tmp;
            curr = parent;
        }
    } else if (est > heap->items[0].frequency) {
        strncpy(heap->items[0].key, key, 63);
        heap->items[0].frequency = est;
        heap_sift_down(heap, 0);
    }
}
