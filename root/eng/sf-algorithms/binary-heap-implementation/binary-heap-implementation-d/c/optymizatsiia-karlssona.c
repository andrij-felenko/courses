#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int *data;
    int size;
    int capacity;
} MinHeap;

MinHeap* min_heap_create(int capacity) {
    if (capacity <= 0) return NULL;
    MinHeap *h = (MinHeap*)malloc(sizeof(MinHeap));
    if (!h) return NULL;
    h->data = (int*)malloc(sizeof(int) * capacity);
    if (!h->data) {
        free(h);
        return NULL;
    }
    h->size = 0;
    h->capacity = capacity;
    return h;
}

void min_heap_free(MinHeap *h) {
    if (h) {
        free(h->data);
        free(h);
    }
}

static inline void swap_nodes(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

void sift_up(MinHeap *h, int i) {
    while (i > 0) {
        int parent = (i - 1) / 2;
        if (h->data[i] < h->data[parent]) {
            swap_nodes(&h->data[i], &h->data[parent]);
            i = parent;
        } else {
            break;
        }
    }
}

void sift_down(MinHeap *h, int i) {
    while (2 * i + 1 < h->size) {
        int left = 2 * i + 1;
        int right = 2 * i + 2;
        int smallest = left;

        if (right < h->size && h->data[right] < h->data[left]) {
            smallest = right;
        }
        if (h->data[smallest] < h->data[i]) {
            swap_nodes(&h->data[i], &h->data[smallest]);
            i = smallest;
        } else {
            break;
        }
    }
}

bool min_heap_push(MinHeap *h, int val) {
    if (!h || h->size >= h->capacity) return false;
    int idx = h->size++;
    h->data[idx] = val;
    sift_up(h, idx);
    return true;
}

bool min_heap_pop(MinHeap *h, int *out_min) {
    if (!h || h->size == 0) return false;
    if (out_min) *out_min = h->data[0];
    h->data[0] = h->data[--h->size];
    if (h->size > 0) {
        sift_down(h, 0);
    }
    return true;
}
