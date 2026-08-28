#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>

#define MAX_V 32

/* Структура для представлення графа у вигляді матриці суміжності */
typedef struct {
    int num_vertices;
    bool adj[MAX_V][MAX_V];
} Graph;

/* Створення порожнього графа */
Graph create_graph(int n) {
    Graph g;
    g.num_vertices = n;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            g.adj[i][j] = false;
        }
    }
    return g;
}

/* Додавання неорієнтованого ребра */
void add_edge(Graph* g, int u, int v) {
    g->adj[u][v] = true;
    g->adj[v][u] = true;
}

/* Застосування перестановки p до графа g: H(p[i], p[j]) = g(i, j) */
Graph permute_graph(const Graph* g, const int* perm) {
    Graph h = create_graph(g->num_vertices);
    int n = g->num_vertices;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (g->adj[i][j]) {
                h.adj[perm[i]][perm[j]] = true;
            }
        }
    }
    return h;
}

/* Генерація випадкової перестановки (алгоритм Фішера — Йейтса) */
void generate_random_permutation(int* perm, int n) {
    for (int i = 0; i < n; i++) {
        perm[i] = i;
    }
    for (int i = n - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int temp = perm[i];
        perm[i] = perm[j];
        perm[j] = temp;
    }
}

/* Перевірка ізоморфізму графів через рекурсивний перебір перестановок */
bool check_isomorphism_recursive(const Graph* g1, const Graph* g2, int* perm, bool* used, int depth) {
    int n = g1->num_vertices;
    if (depth == n) {
        /* Перевірка збереження ребр */
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (g1->adj[i][j] != g2->adj[perm[i]][perm[j]]) {
                    return false;
                }
            }
        }
        return true;
    }

    for (int i = 0; i < n; i++) {
        if (!used[i]) {
            used[i] = true;
            perm[depth] = i;
            if (check_isomorphism_recursive(g1, g2, perm, used, depth + 1)) {
                return true;
            }
            used[i] = false;
        }
    }
    return false;
}

/* Оракул Мерліна: визначає, чи граф H ізоморфний G0 чи G1 */
int merlin_oracle(const Graph* g0, const Graph* g1, const Graph* h) {
    int n = h->num_vertices;
    int perm[MAX_V];
    bool used[MAX_V] = {false};

    if (check_isomorphism_recursive(g0, h, perm, used, 0)) {
        return 0;
    }

    for (int i = 0; i < n; i++) used[i] = false;
    if (check_isomorphism_recursive(g1, h, perm, used, 0)) {
        return 1;
    }

    /* Якщо не ізоморфний жодному, повертаємо випадок за замовчуванням */
    return 0;
}

/* Один раунд AM-протоколу для Артура */
bool arthur_am_round(const Graph* g0, const Graph* g1) {
    int n = g0->num_vertices;

    /* 1. Публічні монети Артура: вибір біта b та перестановки */
    int b = rand() % 2;
    int perm[MAX_V];
    generate_random_permutation(perm, n);

    /* 2. Побудова викликового графа H = pi(G_b) */
    const Graph* target = (b == 0) ? g0 : g1;
    Graph h = permute_graph(target, perm);

    /* 3. Отримання відповіді Мерліна b' */
    int merlin_choice = merlin_oracle(g0, g1, &h);

    /* 4. Перевірка відповіді Артуром */
    return (merlin_choice == b);
}

/* Повний AM-протокол з ампліфікацією точності (k раундів) */
bool run_gni_am_protocol(const Graph* g0, const Graph* g1, int rounds) {
    printf("--- Запуск AM-протоколу для GNI (%d раундів) ---\n", rounds);
    for (int r = 1; r <= rounds; r++) {
        bool accepted = arthur_am_round(g0, g1);
        if (!accepted) {
            printf("Раунд %d: Відхилено! Мерлін надав хибну відповідь.\n", r);
            return false; /* Неізоморфізм спростовано */
        }
    }
    printf("Всі %d раундів пройшли успішно. Графи НЕІЗОМОРФНІ з імовірністю >= 1 - (1/2)^%d\n", rounds, rounds);
    return true;
}

int main(void) {
    srand((unsigned int)time(NULL));

    /* Створення двох неізоморфних графів з 4 вершинами: Цикл C4 та Шлях P4 + ребро */
    Graph g0 = create_graph(4);
    add_edge(&g0, 0, 1); add_edge(&g0, 1, 2);
    add_edge(&g0, 2, 3); add_edge(&g0, 3, 0); /* Цикл C4 */

    Graph g1 = create_graph(4);
    add_edge(&g1, 0, 1); add_edge(&g1, 0, 2);
    add_edge(&g1, 0, 3); /* Зірка K_1,3 */

    printf("Тест 1: Неізоморфні графи (C4 та K_1,3)\n");
    run_gni_am_protocol(&g0, &g1, 10);

    printf("\nТест 2: Ізоморфні графи (G0 та перестановка G0)\n");
    int p[4] = {2, 3, 0, 1};
    Graph g0_iso = permute_graph(&g0, p);
    run_gni_am_protocol(&g0, &g0_iso, 10);

    return 0;
}
