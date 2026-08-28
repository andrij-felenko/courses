// Один запис у фронті: клітина та її f-оцінка на мить укладання.
typedef struct { float f; int32_t cell; } HeapItem;

// Місткість фронту. Через ЛІНИВЕ видалення (нижче) клітина лягає в купу не раз,
// а щоразу, як сусід, закрившись, приносить до неї дешевший шлях; сусідів вісім.
// Тож стеля пушів — не N_CELLS (вершини), а до 8·N_CELLS (ребра сітки): візьмеш
// N_CELLS — на щільній сітці heap[] переповниться й запис піде ЗА межі масиву.
#define HEAP_CAP  (8 * N_CELLS + 1)   // 8·N ребер + 1 стартовий push
static HeapItem heap[HEAP_CAP];
static int      heap_len = 0;

static inline void heap_swap(int a, int b) {
    HeapItem t = heap[a]; heap[a] = heap[b]; heap[b] = t;
}

// Спливання: новий елемент у кінці «підіймається», доки менший за батька.
static void heap_sift_up(int i) {
    while (i > 0) {
        int parent = (i - 1) / 2;
        if (heap[i].f >= heap[parent].f) break;   // на місці
        heap_swap(i, parent);
        i = parent;
    }
}

// Потонення: елемент із вершини «осідає», міняючись із меншою дитиною.
static void heap_sift_down(int i) {
    for (;;) {
        int l = 2 * i + 1, r = 2 * i + 2, smallest = i;
        if (l < heap_len && heap[l].f < heap[smallest].f) smallest = l;
        if (r < heap_len && heap[r].f < heap[smallest].f) smallest = r;
        if (smallest == i) break;                  // обидві дитини не менші
        heap_swap(i, smallest);
        i = smallest;
    }
}

static void heap_push(int32_t cell, float f) {
    if (heap_len >= HEAP_CAP) return;   // запобіжник від виходу за межі масиву (за нашої місткості не спрацює)
    heap[heap_len].f = f;
    heap[heap_len].cell = cell;
    heap_sift_up(heap_len);
    heap_len++;
}

// Забрати клітину з найменшим f (вона завжди у heap[0]).
static int32_t heap_pop_min(void) {
    int32_t best = heap[0].cell;
    heap_len--;
    heap[0] = heap[heap_len];       // останній — на вершину
    heap_sift_down(0);              // і хай осяде
    return best;
}

static inline bool heap_empty(void) { return heap_len == 0; }
