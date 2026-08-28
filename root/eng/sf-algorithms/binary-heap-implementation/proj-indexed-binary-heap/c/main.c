#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <limits.h>

typedef struct {
    int id;
    int key;
} HeapNode;

typedef struct {
    HeapNode *data;
    int *pos;
    int size;
    int capacity;
} IndexedMinHeap;

IndexedMinHeap* indexed_heap_create(int capacity) {
    if (capacity <= 0) return NULL;
    IndexedMinHeap *h = (IndexedMinHeap*)malloc(sizeof(IndexedMinHeap));
    if (!h) return NULL;
    h->data = (HeapNode*)malloc(sizeof(HeapNode) * capacity);
    h->pos = (int*)malloc(sizeof(int) * capacity);
    if (!h->data || !h->pos) {
        free(h->data);
        free(h->pos);
        free(h);
        return NULL;
    }
    h->size = 0;
    h->capacity = capacity;
    for (int i = 0; i < capacity; ++i) {
        h->pos[i] = -1;
    }
    return h;
}

void indexed_heap_free(IndexedMinHeap *h) {
    if (!h) return;
    free(h->data);
    free(h->pos);
    free(h);
}

static inline void heap_swap(IndexedMinHeap *h, int i, int j) {
    HeapNode temp = h->data[i];
    h->data[i] = h->data[j];
    h->data[j] = temp;
    h->pos[h->data[i].id] = i;
    h->pos[h->data[j].id] = j;
}

static void sift_up(IndexedMinHeap *h, int i) {
    while (i > 0) {
        int p = (i - 1) / 2;
        if (h->data[i].key < h->data[p].key) {
            heap_swap(h, i, p);
            i = p;
        } else {
            break;
        }
    }
}

static void sift_down(IndexedMinHeap *h, int i) {
    while (2 * i + 1 < h->size) {
        int left = 2 * i + 1;
        int right = 2 * i + 2;
        int smallest = left;

        if (right < h->size && h->data[right].key < h->data[left].key) {
            smallest = right;
        }
        if (h->data[smallest].key < h->data[i].key) {
            heap_swap(h, i, smallest);
            i = smallest;
        } else {
            break;
        }
    }
}

bool indexed_heap_contains(const IndexedMinHeap *h, int id) {
    if (!h || id < 0 || id >= h->capacity) return false;
    return h->pos[id] != -1;
}

bool indexed_heap_push(IndexedMinHeap *h, int id, int key) {
    if (!h || h->size >= h->capacity || indexed_heap_contains(h, id)) {
        return false;
    }
    int idx = h->size++;
    h->data[idx].id = id;
    h->data[idx].key = key;
    h->pos[id] = idx;
    sift_up(h, idx);
    return true;
}

bool indexed_heap_pop(IndexedMinHeap *h, int *out_id, int *out_key) {
    if (!h || h->size == 0) return false;
    if (out_id) *out_id = h->data[0].id;
    if (out_key) *out_key = h->data[0].key;

    h->pos[h->data[0].id] = -1;
    h->size--;
    if (h->size > 0) {
        h->data[0] = h->data[h->size];
        h->pos[h->data[0].id] = 0;
        sift_down(h, 0);
    }
    return true;
}

bool indexed_heap_decrease_key(IndexedMinHeap *h, int id, int new_key) {
    if (!h || !indexed_heap_contains(h, id)) return false;
    int idx = h->pos[id];
    if (new_key > h->data[idx].key) return false;
    h->data[idx].key = new_key;
    sift_up(h, idx);
    return true;
}

bool indexed_heap_increase_key(IndexedMinHeap *h, int id, int new_key) {
    if (!h || !indexed_heap_contains(h, id)) return false;
    int idx = h->pos[id];
    if (new_key < h->data[idx].key) return false;
    h->data[idx].key = new_key;
    sift_down(h, idx);
    return true;
}

bool indexed_heap_delete(IndexedMinHeap *h, int id) {
    if (!h || !indexed_heap_contains(h, id)) return false;
    int idx = h->pos[id];
    int old_key = h->data[idx].key;
    h->pos[id] = -1;
    h->size--;

    if (idx == h->size) {
        return true;
    }

    h->data[idx] = h->data[h->size];
    h->pos[h->data[idx].id] = idx;

    if (h->data[idx].key < old_key) {
        sift_up(h, idx);
    } else {
        sift_down(h, idx);
    }
    return true;
}
