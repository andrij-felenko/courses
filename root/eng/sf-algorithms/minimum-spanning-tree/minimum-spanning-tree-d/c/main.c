#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

#define INF_WEIGHT INT64_MAX

typedef struct EdgeNode {
    int to;
    int64_t weight;
    struct EdgeNode *next;
} EdgeNode;

typedef struct {
    int num_vertices;
    EdgeNode **adj;
} Graph;

typedef struct {
    int u;
    int v;
    int64_t weight;
} MstEdge;

typedef struct {
    MstEdge *edges;
    int edge_count;
    int64_t total_weight;
    bool is_connected;
} MstResult;

typedef struct {
    int vertex;
    int64_t key;
} HeapNode;

typedef struct {
    HeapNode *data;
    int *pos;
    int size;
    int capacity;
} MinHeap;

static void heap_swap(MinHeap *h, int i, int j) {
    HeapNode tmp = h->data[i];
    h->data[i] = h->data[j];
    h->data[j] = tmp;
    h->pos[h->data[i].vertex] = i;
    h->pos[h->data[j].vertex] = j;
}

static void sift_up(MinHeap *h, int idx) {
    while (idx > 0) {
        int parent = (idx - 1) / 2;
        if (h->data[idx].key < h->data[parent].key) {
            heap_swap(h, idx, parent);
            idx = parent;
        } else break;
    }
}

static void sift_down(MinHeap *h, int idx) {
    while (true) {
        int left = 2 * idx + 1, right = 2 * idx + 2, smallest = idx;
        if (left < h->size && h->data[left].key < h->data[smallest].key) smallest = left;
        if (right < h->size && h->data[right].key < h->data[smallest].key) smallest = right;
        if (smallest != idx) {
            heap_swap(h, idx, smallest);
            idx = smallest;
        } else break;
    }
}

MinHeap* min_heap_create(int capacity) {
    MinHeap *h = (MinHeap*)malloc(sizeof(MinHeap));
    h->data = (HeapNode*)malloc(sizeof(HeapNode) * capacity);
    h->pos = (int*)malloc(sizeof(int) * capacity);
    h->size = 0;
    h->capacity = capacity;
    for (int i = 0; i < capacity; ++i) h->pos[i] = -1;
    return h;
}

void min_heap_free(MinHeap *h) {
    if (!h) return;
    free(h->data);
    free(h->pos);
    free(h);
}

void min_heap_insert_or_decrease(MinHeap *h, int v, int64_t key) {
    if (h->pos[v] == -1) {
        int idx = h->size++;
        h->data[idx].vertex = v;
        h->data[idx].key = key;
        h->pos[v] = idx;
        sift_up(h, idx);
    } else {
        int idx = h->pos[v];
        if (key < h->data[idx].key) {
            h->data[idx].key = key;
            sift_up(h, idx);
        }
    }
}

bool min_heap_extract_min(MinHeap *h, HeapNode *out) {
    if (h->size == 0) return false;
    *out = h->data[0];
    h->pos[out->vertex] = -1;
    h->size--;
    if (h->size > 0) {
        h->data[0] = h->data[h->size];
        h->pos[h->data[0].vertex] = 0;
        sift_down(h, 0);
    }
    return true;
}

MstResult prim_mst(const Graph *g) {
    int n = g->num_vertices;
    MstResult res = {0};
    if (n <= 0) return res;

    res.edges = (MstEdge*)malloc(sizeof(MstEdge) * (n > 1 ? n - 1 : 1));
    int64_t *key = (int64_t*)malloc(sizeof(int64_t) * n);
    int *parent = (int*)malloc(sizeof(int) * n);
    bool *in_mst = (bool*)calloc(n, sizeof(bool));
    MinHeap *heap = min_heap_create(n);

    for (int i = 0; i < n; ++i) {
        key[i] = INF_WEIGHT;
        parent[i] = -1;
    }

    key[0] = 0;
    min_heap_insert_or_decrease(heap, 0, 0);
    int visited = 0;

    while (heap->size > 0) {
        HeapNode node;
        min_heap_extract_min(heap, &node);
        int u = node.vertex;
        in_mst[u] = true;
        visited++;

        if (parent[u] != -1) {
            res.edges[res.edge_count].u = parent[u];
            res.edges[res.edge_count].v = u;
            res.edges[res.edge_count].weight = node.key;
            res.total_weight += node.key;
            res.edge_count++;
        }

        for (EdgeNode *e = g->adj[u]; e != NULL; e = e->next) {
            int v = e->to;
            int64_t w = e->weight;
            if (!in_mst[v] && w < key[v]) {
                key[v] = w;
                parent[v] = u;
                min_heap_insert_or_decrease(heap, v, w);
            }
        }
    }

    res.is_connected = (visited == n);

    min_heap_free(heap);
    free(key);
    free(parent);
    free(in_mst);
    return res;
}
