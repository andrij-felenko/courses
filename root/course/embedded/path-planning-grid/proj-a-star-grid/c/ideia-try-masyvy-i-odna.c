#include <stdint.h>
#include <stdbool.h>

#define GRID_W   64
#define GRID_H   64
#define N_CELLS  (GRID_W * GRID_H)

// Згортання (x,y) ⟷ лінійний індекс. Тримаємо в одному місці, щоб не наплутати.
static inline int   idx_of(int x, int y) { return y * GRID_W + x; }
static inline int   x_of(int idx)        { return idx % GRID_W;   }
static inline int   y_of(int idx)        { return idx / GRID_W;   }

// Мапа зайнятості: 0 = вільно, 1 = стіна. Один байт на клітину заради простоти
// (можна ужати до біта, якщо пам'ять геть на межі — див. пастку 1).
static uint8_t  grid[N_CELLS];

// Ціна найдешевшого відомого шляху від старту до клітини. INF = ще не досягнута.
static float    g_cost[N_CELLS];

// «Хлібні крихти»: звідки прийшли в цю клітину. -1 = нізвідки (старт або не досягнута).
static int32_t  came_from[N_CELLS];

#define INF   1e30f     // «нескінченність» для g: більша за будь-який реальний шлях
