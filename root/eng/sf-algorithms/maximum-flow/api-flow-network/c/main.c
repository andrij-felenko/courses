#include <stdint.h>
#include <stdbool.h>

#define MAX_NODES 5000
#define MAX_ARCS  60000

typedef struct {
    int to;         // Цільова вершина дуги
    int next;       // Індекс наступного ребра у списку суміжності (-1 = кінець)
    int64_t cap;    // Пропускна спроможність
    int64_t flow;   // Поточний потік через ребро
} FlowArcC;

typedef struct {
    int n;                      // Кількість вершин у мережі
    int arc_count;              // Загальна кількість дуг у масиві
    int head[MAX_NODES];        // Голова списку суміжності для кожної вершини
    FlowArcC arcs[MAX_ARCS];    // Статичний масив усіх спрямованих дуг
} FlowNetworkC;
