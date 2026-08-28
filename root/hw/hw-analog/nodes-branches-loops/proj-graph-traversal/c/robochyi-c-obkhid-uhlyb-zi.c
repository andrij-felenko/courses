#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

#define MAX_N 32          /* стеля вузлів  */
#define MAX_B 64          /* стеля гілок   */
#define MAX_DEG 8         /* макс. сусідів одного вузла */

/* гілка з'єднує вузли a та b (номер гілки = індекс у масиві) */
typedef struct { uint8_t a, b; } Branch;

/* список суміжності: для вузла v — пари (сусід, номер гілки) */
static uint8_t adj_node[MAX_N][MAX_DEG];
static uint8_t adj_br  [MAX_N][MAX_DEG];
static uint8_t deg     [MAX_N];                  /* скільки сусідів у вузла */

static void add_edge(uint8_t br, uint8_t a, uint8_t b) {
    adj_node[a][deg[a]] = b;  adj_br[a][deg[a]++] = br;
    adj_node[b][deg[b]] = a;  adj_br[b][deg[b]++] = br;   /* граф неорієнтований */
}

/* результат обходу */
static bool    visited[MAX_N];                   /* вузол уже відкрито?         */
static bool    br_done [MAX_B];                  /* гілку вже класифіковано?    */
static int8_t  parent_node[MAX_N];               /* батьківський вузол у дереві */
static uint8_t parent_br  [MAX_N];               /* гілка до батька             */
static uint8_t chord[MAX_B];                     /* список хорд                 */
static uint8_t n_tree, n_chords;

/* обхід углиб від start; повертає, скільки вузлів охоплено */
static uint8_t dfs(uint8_t start) {
    uint8_t stack[MAX_N];
    uint8_t sp = 0, seen = 0;

    visited[start] = true;  seen++;              /* вузол відкриваємо при ВХОДІ */
    parent_node[start] = -1;
    stack[sp++] = start;

    while (sp > 0) {
        uint8_t v = stack[--sp];                 /* беремо з вершини стека */
        for (uint8_t k = 0; k < deg[v]; ++k) {
            uint8_t u  = adj_node[v][k];
            uint8_t br = adj_br[v][k];
            if (br_done[br]) continue;           /* кожну гілку класифікуємо РАЗ */
            br_done[br] = true;
            if (!visited[u]) {                   /* веде в новий вузол → гілка дерева */
                visited[u]     = true;  seen++;
                parent_node[u] = (int8_t)v;
                parent_br[u]   = br;
                n_tree++;
                stack[sp++]    = u;              /* у стек кладемо лише НОВІ вузли */
            } else {                             /* веде в уже відкритий вузол → хорда */
                chord[n_chords++] = br;
            }
        }
    }
    return seen;
}
