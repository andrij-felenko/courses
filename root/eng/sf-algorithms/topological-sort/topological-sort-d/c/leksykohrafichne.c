/* Концепція лексикографічного сортування мовою C:
   Замість FIFO-черги використовується мінімальна купа (Min-Heap).
   Часова складність стає O((V + E) * log V). */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

void swap(int* a, int* b) { int t = *a; *a = *b; *b = t; }

typedef struct {
    int* data;
    int size;
} MinHeap;

void push_heap(MinHeap* hp, int val) {
    hp->data[hp->size] = val;
    int i = hp->size++;
    while (i > 0 && hp->data[(i - 1) / 2] > hp->data[i]) {
        swap(&hp->data[(i - 1) / 2], &hp->data[i]);
        i = (i - 1) / 2;
    }
}

int pop_heap(MinHeap* hp) {
    int res = hp->data[0];
    hp->data[0] = hp->data[--hp->size];
    int i = 0;
    while (2 * i + 1 < hp->size) {
        int left = 2 * i + 1, right = 2 * i + 2, min_idx = left;
        if (right < hp->size && hp->data[right] < hp->data[left]) min_idx = right;
        if (hp->data[i] <= hp->data[min_idx]) break;
        swap(&hp->data[i], &hp->data[min_idx]);
        i = min_idx;
    }
    return res;
}
