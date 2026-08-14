# 💻 Практичні застосування та алгоритмічні задачі на базі BFS

Пошук у ширину (BFS) виступає базовим інструментальним мотором для розв'язання широкого спектра практичних інженерних задач — від трасування доріжок на друкованих платах та навігації в двовимірних лабіринтах до виявлення циклів у мережевих графах, розфарбовування областей растрових зображень (Flood Fill), перевірки графів на дводольність, трансформації слів (Word Ladder), аналізу топології мереж та маршрутизації в графах із вагами ребер `0` та `1`.

Нижче наведено практичні реалізації із розширеним прозовим аналізом, покроковим простеженням станів, крайовими випадками, порівняльними таблицями та кодовими прикладами чотирма мовами програмування (C, C++, Python, TypeScript).

### 1. Пошук найкоротшого шляху у двовимірній сітці (Grid BFS)

У задачах робототехніки, ігрових рушіях, автопілотах автономних транспортних засобів та геоінформаційних системах (GIS) карта місцевості подається у вигляді двовимірної квадратної сітки `N × M`. Окремі клітини є вільними для проходу (`.`), а інші — непрохідними перешкодами (`#`).

#### Аналіз топології двовимірної сітки:
Кожна клітина `(r, c)` розглядається як окрема вершина графа. Залежно від умов задачі, зв'язність сітки може утворювати два типи графічних топологій:
1. **4-зв'язана сітка (Orthogonal Movement):** Рух дозволено лише ортогонально — вгору, вниз, ліворуч та праворуч. Сусіди задаються векторами зміщення `dr[] = {-1, 1, 0, 0}` та `dc[] = {0, 0, -1, 1}`.
2. **8-зв'язана сітка (Diagonal Movement):** Рух дозволено також по діагоналях. Сусіди задаються 8 векторами зміщення, що додає кутові діагональні кроки.

#### Валідація крайових умов та лінеаризація координат:
При кожному розпуску ребер у сітці необхідно виконувати сувору перевірку виходу за межі масиву (Boundary Check):
`0 <= nr < rows` та `0 <= nc < cols`.

У високоефективних C-реалізаціях для зменшення кількості виділень пам'яті під подвійні вказівники застосовується **лінеаризація координат**: двовимірні координати `(r, c)` упаковуються в один одновимірний індекс `index = r * cols + c`. Зворотне розпакування виконується операціями `r = index / cols` та `c = index % cols`.

#### Детальний аналіз використання пам'яті та кеш-локальності:
При роботі із двовимірними сітками розміром `N × M` масив відстаней `dist` зберігає значення відстані до кожної клітини. У разі використання двовимірного динамічного масиву `int** dist` виникає високий ступінь фрагментації купи через виділення `N` окремих блоків пам'яті. Це спричиняє промахи кешу процесора (L1/L2 Cache Misses) під час сканування суміжних рядків.

Використання лінеаризованого одновимірного масиву `int dist[N * M]` гарантує розташування всіх елементів у неперервному блоці пам'яті. Апаратний предіктор зчитування (Hardware Prefetcher) процесора здатний завчасно завантажувати наступні елементи рядка у кеш-лінії по 64 байти, підвищуючи швидкість обходу сітки на 30–45%.

#### Крайові випадки та простеження:
- **Старт або Ціль у перешкоді:** Якщо `grid[start] == '#'` або `grid[target] == '#'`, функція негайно повертає `-1` без запуску обходу.
- **Старт збігається з Цільно:** Якщо `start == target`, відстань дорівнює `0`.
- **Повна ізольованість:** Якщо цільова клітина повністю оточена стінами `#`, BFS обробить усю досяжну компоненту зв'язності і поверне `-1`.

:::tabs
```c
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct { int r, c; } PointC;

int bfs_grid_c(const char* const* grid, int rows, int cols, PointC start, PointC target) {
    if (grid[start.r][start.c] == '#' || grid[target.r][target.c] == '#') return -1;

    bool** visited = (bool**)malloc(sizeof(bool*) * rows);
    int** dist = (int**)malloc(sizeof(int*) * rows);
    for (int i = 0; i < rows; ++i) {
        visited[i] = (bool*)calloc(cols, sizeof(bool));
        dist[i] = (int*)malloc(sizeof(int) * cols);
        for (int j = 0; j < cols; ++j) dist[i][j] = -1;
    }

    PointC* queue = (PointC*)malloc(sizeof(PointC) * rows * cols);
    int head = 0, tail = 0;

    visited[start.r][start.c] = true;
    dist[start.r][start.c] = 0;
    queue[tail++] = start;

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};
    int result = -1;

    while (head < tail) {
        PointC curr = queue[head++];
        if (curr.r == target.r && curr.c == target.c) {
            result = dist[curr.r][curr.c];
            break;
        }

        for (int i = 0; i < 4; ++i) {
            int nr = curr.r + dr[i];
            int nc = curr.c + dc[i];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                grid[nr][nc] != '#' && !visited[nr][nc]) {
                visited[nr][nc] = true;
                dist[nr][nc] = dist[curr.r][curr.c] + 1;
                queue[tail++] = (PointC){nr, nc};
            }
        }
    }

    for (int i = 0; i < rows; ++i) {
        free(visited[i]);
        free(dist[i]);
    }
    free(visited); free(dist); free(queue);
    return result;
}
```
```cpp
#include <vector>
#include <queue>
#include <string>

struct Point { int r, c; };

int bfs_grid_cpp(const std::vector<std::string>& grid, Point start, Point target) {
    int rows = grid.size();
    int cols = grid[0].size();
    if (grid[start.r][start.c] == '#' || grid[target.r][target.c] == '#') return -1;

    std::vector<std::vector<int>> dist(rows, std::vector<int>(cols, -1));
    std::queue<Point> q;

    dist[start.r][start.c] = 0;
    q.push(start);

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    while (!q.empty()) {
        Point curr = q.front();
        q.pop();

        if (curr.r == target.r && curr.c == target.c) {
            return dist[curr.r][curr.c];
        }

        for (int i = 0; i < 4; ++i) {
            int nr = curr.r + dr[i];
            int nc = curr.c + dc[i];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                grid[nr][nc] != '#' && dist[nr][nc] == -1) {
                dist[nr][nc] = dist[curr.r][curr.c] + 1;
                q.push({nr, nc});
            }
        }
    }
    return -1;
}
```
```python
from collections import deque

def bfs_grid_python(grid: list[str], start: tuple[int, int], target: tuple[int, int]) -> int:
    rows, cols = len(grid), len(grid[0])
    if grid[start[0]][start[1]] == '#' or grid[target[0]][target[1]] == '#':
        return -1

    dist = [[-1] * cols for _ in range(rows)]
    q = deque([start])
    dist[start[0]][start[1]] = 0

    dr = [-1, 1, 0, 0]
    dc = [0, 0, -1, 1]

    while q:
        r, c = q.popleft()
        if (r, c) == target:
            return dist[r][c]

        for i in range(4):
            nr, nc = r + dr[i], c + dc[i]
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '#' and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))

    return -1
```
```typescript
function bfsGridTS(grid: string[], start: [number, number], target: [number, number]): number {
    const rows = grid.length;
    const cols = grid[0].length;
    if (grid[start[0]][start[1]] === '#' || grid[target[0]][target[1]] === '#') return -1;

    const dist: number[][] = Array.from({ length: rows }, () => Array(cols).fill(-1));
    const queue: [number, number][] = [start];
    dist[start[0]][start[1]] = 0;

    const dr = [-1, 1, 0, 0];
    const dc = [0, 0, -1, 1];
    let head = 0;

    while (head < queue.length) {
        const [r, c] = queue[head++];
        if (r === target[0] && c === target[1]) return dist[r][c];

        for (let i = 0; i < 4; i++) {
            const nr = r + dr[i];
            const nc = c + dc[i];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                grid[nr][nc] !== '#' && dist[nr][nc] === -1) {
                dist[nr][nc] = dist[r][c] + 1;
                queue.push([nr, nc]);
            }
        }
    }
    return -1;
}
```
:::

### 2. Заповнення областей растрових зображень (Flood Fill)

Алгоритм Flood Fill є основою інструмента «Заливка» у графічних редакторах (MS Paint, Adobe Photoshop, GIMP) та застосовується у медичній візуалізації для сегментації пухлин на томограмах (МРТ/КТ). Задача полягає у зміні кольору суцільної області суміжних пікселів одного вихідного тону `target_color` на новий колір `new_color`.

#### Перевага ітеративного BFS над рекурсивним DFS у Flood Fill:
У растрових зображеннях високої роздільної здатності (наприклад, `3840 × 2160` пікселів 4K) рекурсивна реалізація DFS робить мільйони глибинних викликів. Оскільки кожен виклик функції створює новий стек-фрейм (зберігаючи локальні змінні та адресу повернення), рекурсія вичерпує системний стек (обмежений зазвичай 1–8 МБ) за лічені мілісекунди, що викликає аварійне завершення програми **Stack Overflow**.

Ітеративний BFS використовує пам'ять оперативної купи (Heap) під чергу `queue`. Купа обмежена лише загальним обсягом RAM пристрою, що забезпечує абсолютну інженерну стійкість заливки на зображеннях будь-яких розмірів.

#### Модифікація прямо за місцем (In-place Processing):
Особливістю Flood Fill є те, що масив зображення слугує власною структурою відвіданості: як тільки пікселю присвоюється `new_color`, він більше не збігається з `target_color`, що виключає повторну обробку без виділення додаткового масиву `visited`.

#### Оптимізація сканування рядками (Scanline Flood Fill):
Просунутий інженерний варіант BFS для заливки зображень — **Scanline Flood Fill**. Замість додавання кожного пікселя до черги окремо, алгоритм знаходить неперервний горизонтальний відрізок пікселів одинакового кольору, зафарбовує весь відрізок за один цикл і додає до черги лише крайні пікселі верхнього та нижнього сусідніх рядків. Це зменшує розмір черги у 10–50 разів і мінімізує кількість оновлень пам'яті.

:::tabs
```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct { int r, c; } PixelC;

void flood_fill_c(int** image, int rows, int cols, int start_r, int start_c, int new_color) {
    int target_color = image[start_r][start_c];
    if (target_color == new_color) return;

    PixelC* queue = (PixelC*)malloc(sizeof(PixelC) * rows * cols);
    int head = 0, tail = 0;

    image[start_r][start_c] = new_color;
    queue[tail++] = (PixelC){start_r, start_c};

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    while (head < tail) {
        PixelC curr = queue[head++];
        for (int i = 0; i < 4; ++i) {
            int nr = curr.r + dr[i];
            int nc = curr.c + dc[i];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && image[nr][nc] == target_color) {
                image[nr][nc] = new_color;
                queue[tail++] = (PixelC){nr, nc};
            }
        }
    }
    free(queue);
}
```
```cpp
#include <vector>
#include <queue>

void flood_fill_cpp(std::vector<std::vector<int>>& image, int start_r, int start_c, int new_color) {
    int rows = image.size();
    int cols = image[0].size();
    int target_color = image[start_r][start_c];
    if (target_color == new_color) return;

    std::queue<std::pair<int, int>> q;
    image[start_r][start_c] = new_color;
    q.push({start_r, start_c});

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    while (!q.empty()) {
        auto [r, c] = q.front();
        q.pop();

        for (int i = 0; i < 4; ++i) {
            int nr = r + dr[i];
            int nc = c + dc[i];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && image[nr][nc] == target_color) {
                image[nr][nc] = new_color;
                q.push({nr, nc});
            }
        }
    }
}
```
```python
from collections import deque

def flood_fill_python(image: list[list[int]], start_r: int, start_c: int, new_color: int) -> None:
    rows, cols = len(image), len(image[0])
    target_color = image[start_r][start_c]
    if target_color == new_color:
        return

    q = deque([(start_r, start_c)])
    image[start_r][start_c] = new_color

    dr = [-1, 1, 0, 0]
    dc = [0, 0, -1, 1]

    while q:
        r, c = q.popleft()
        for i in range(4):
            nr, nc = r + dr[i], c + dc[i]
            if 0 <= nr < rows and 0 <= nc < cols and image[nr][nc] == target_color:
                image[nr][nc] = new_color
                q.append((nr, nc))
```
```typescript
function floodFillTS(image: number[][], start_r: number, start_c: number, new_color: number): void {
    const rows = image.length;
    const cols = image[0].length;
    const target_color = image[start_r][start_c];
    if (target_color === new_color) return;

    const queue: [number, number][] = [[start_r, start_c]];
    image[start_r][start_c] = new_color;

    const dr = [-1, 1, 0, 0];
    const dc = [0, 0, -1, 1];
    let head = 0;

    while (head < queue.length) {
        const [r, c] = queue[head++];
        for (let i = 0; i < 4; i++) {
            const nr = r + dr[i];
            const nc = c + dc[i];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && image[nr][nc] === target_color) {
                image[nr][nc] = new_color;
                queue.push([nr, nc]);
            }
        }
    }
}
```
:::

### 3. Перевірка графа на дводольність (Bipartite Graph Checking)

Граф називається дводольним (Bipartite), якщо його вершини можна розділити на дві недотичні множини `V_1` та `V_2` так, що кожне ребро графа з'єднує вершину з `V_1` із вершиною з `V_2`.

#### Практичні застосування дводольних графів:
1. **Задачі про призначення (Job Assignment):** Множина `V_1` — працівники, `V_2` — задачі. Ребра показують кваліфікаційну придатність.
2. **Системи рекомендацій (Bipartite Matching):** Множина `V_1` — користувачі, `V_2` — товари або відеоролики.
3. **Компілятори:** Розподіл регістрів процесора та виявлення конфліктів у графах інтерференції змінних.

#### Алгоритмічний критерій:
Граф є дводольним тоді й лише тоді, коли він **не містить циклів непарної довжини**. BFS дозволяє перевірити дводольність за допомогою 2-розфарбування:
- Стартовій вершині присвоюється колір `1`.
- Усім сусідам відкриваного вузла присвоюється протилежний колір `3 - color[u]`.
- Якщо при обробці ребра з'ясовується, що сусід уже відвіданий і має **такий самий колір** (`color[v] == color[u]`), то граф містить непарний цикл і не є дводольним.

#### Аналіз для несвоєрозвідних графів (Disconnected Graphs):
Якщо граф складається з кількох ізольованих компонент зв'язності, зовнішній цикл зобов'язаний ітерируватися по всіх вершинах від `0` до `V-1`. Для кожної непофарбованої вершини `color[i] == 0` запускається окрема хвиля BFS. Лише якщо всі компоненти успішно розфарбовані у 2 кольори без конфліктів, граф визнається дводольним.

:::tabs
```c
#include <stdbool.h>
#include <stdlib.h>

bool is_bipartite_c(int num_vertices, const int* const* adj, const int* adj_sizes) {
    int* color = (int*)calloc(num_vertices, sizeof(int));
    int* queue = (int*)malloc(sizeof(int) * num_vertices);

    for (int start = 0; start < num_vertices; ++start) {
        if (color[start] != 0) continue;

        int head = 0, tail = 0;
        color[start] = 1;
        queue[tail++] = start;

        while (head < tail) {
            int u = queue[head++];
            for (int i = 0; i < adj_sizes[u]; ++i) {
                int v = adj[u][i];
                if (color[v] == 0) {
                    color[v] = 3 - color[u];
                    queue[tail++] = v;
                } else if (color[v] == color[u]) {
                    free(color); free(queue);
                    return false;
                }
            }
        }
    }
    free(color); free(queue);
    return true;
}
```
```cpp
#include <vector>
#include <queue>

bool is_bipartite_cpp(const std::vector<std::vector<int>>& adj) {
    int n = adj.size();
    std::vector<int> color(n, 0);

    for (int start = 0; start < n; ++start) {
        if (color[start] != 0) continue;

        std::queue<int> q;
        color[start] = 1;
        q.push(start);

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            for (int v : adj[u]) {
                if (color[v] == 0) {
                    color[v] = 3 - color[u];
                    q.push(v);
                } else if (color[v] == color[u]) {
                    return false;
                }
            }
        }
    }
    return true;
}
```
```python
from collections import deque

def is_bipartite_python(adj: list[list[int]]) -> bool:
    n = len(adj)
    color = [0] * n

    for start in range(n):
        if color[start] != 0:
            continue

        q = deque([start])
        color[start] = 1

        while q:
            u = q.popleft()
            for v in adj[u]:
                if color[v] == 0:
                    color[v] = 3 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True
```
```typescript
function isBipartiteTS(adj: number[][]): boolean {
    const n = adj.length;
    const color = Array(n).fill(0);

    for (let start = 0; start < n; start++) {
        if (color[start] !== 0) continue;

        const queue: number[] = [start];
        color[start] = 1;
        let head = 0;

        while (head < queue.length) {
            const u = queue[head++];
            for (const v of adj[u]) {
                if (color[v] === 0) {
                    color[v] = 3 - color[u];
                    queue.push(v);
                } else if (color[v] === color[u]) {
                    return false;
                }
            }
        }
    }
    return true;
}
```
:::

### 4. Алгоритм 0-1 BFS з двостороньою чергою (0-1 BFS with Deque)

У графах, де ваги ребер приймають лише два можливих значення `w ∈ {0, 1}`, стандартний алгоритм Дейкстри з пріоритетною купою `O((V + E) log V)` є надлишковим. Застосування двосторонньої черги (`std::deque` / `collections.deque`) дозволяє знайти найкоротший шлях за строго лінійний час `O(V + E)`.

#### Інженерна доцільність та сфери застосування:
1. **Маршрутизація в сітках із різними типами покриття:** Наприклад, рух по асфальтованій дор�Геометрична аналогія: площа круга радіуса `d` становить `π d²`. Якщо замість одного круга радіуса `d` побудувати два круги радіуса `d/2`, їхня сумарна площа дорівнюватиме `2 · π (d/2)² = (π d²) / 2`, тобто обсяг сканування скорочується вдвічі при `d = 2` і експоненціально при зростанні `d`. Для графа з `b = 10` та `d = 6` односторонній BFS перевіряє **1 000 000** вершин, тоді як двосторонній — лише **2 000** вершин, забезпечуючи прискорення в 500 разів!

#### Динамічний вибір активного фронту (Frontier Selection Heuristic):
В оптимізованих системних реалізаціях на кожному кроці алгоритму для розширення вибирається хвиля з **меншим розміром черги** (`min(queue_forward.size(), queue_backward.size())`). Це запобігає розростанню хвилі з боку вузлів із високим ступенем розгалуження (High-Degree Hubs) і додатково прискорює пошук.

:::tabs
```c
#include <stdbool.h>
#include <stdlib.h>

int bidirectional_bfs_c(int num_vertices, const int* const* adj, const int* adj_sizes, int start, int target) {
    if (start == target) return 0;

    int* dist_f = (int*)malloc(sizeof(int) * num_vertices);
    int* dist_b = (int*)malloc(sizeof(int) * num_vertices);
    for (int i = 0; i < num_vertices; ++i) dist_f[i] = dist_b[i] = -1;

    int* q_f = (int*)malloc(sizeof(int) * num_vertices);
    int* q_b = (int*)malloc(sizeof(int) * num_vertices);
    int head_f = 0, tail_f = 0, head_b = 0, tail_b = 0;

    dist_f[start] = 0; q_f[tail_f++] = start;
    dist_b[target] = 0; q_b[tail_b++] = target;

    int result = -1;

    while (head_f < tail_f && head_b < tail_b) {
        // Крок прямої хвилі
        int u_f = q_f[head_f++];
        for (int i = 0; i < adj_sizes[u_f]; ++i) {
            int v = adj[u_f][i];
            if (dist_b[v] != -1) {
                result = dist_f[u_f] + 1 + dist_b[v];
                goto cleanup;
            }
            if (dist_f[v] == -1) {
                dist_f[v] = dist_f[u_f] + 1;
                q_f[tail_f++] = v;
            }
        }

        // Крок зворотної хвилі
        int u_b = q_b[head_b++];
        for (int i = 0; i < adj_sizes[u_b]; ++i) {
            int v = adj[u_b][i];
            if (dist_f[v] != -1) {
                result = dist_b[u_b] + 1 + dist_f[v];
                goto cleanup;
            }
            if (dist_b[v] == -1) {
                dist_b[v] = dist_b[u_b] + 1;
                q_b[tail_b++] = v;
            }
        }
    }

cleanup:
    free(dist_f); free(dist_b); free(q_f); free(q_b);
    return result;
}
```
```cpp
#include <vector>
#include <queue>

int bidirectional_bfs_cpp(const std::vector<std::vector<int>>& adj, int start, int target) {
    if (start == target) return 0;
    int n = adj.size();

    std::vector<int> dist_f(n, -1), dist_b(n, -1);
    std::queue<int> q_f, q_b;

    dist_f[start] = 0; q_f.push(start);
    dist_b[target] = 0; q_b.push(target);

    while (!q_f.empty() && !q_b.empty()) {
        int u_f = q_f.front(); q_f.pop();
        for (int v : adj[u_f]) {
            if (dist_b[v] != -1) return dist_f[u_f] + 1 + dist_b[v];
            if (dist_f[v] == -1) {
                dist_f[v] = dist_f[u_f] + 1;
                q_f.push(v);
            }
        }

        int u_b = q_b.front(); q_b.pop();
        for (int v : adj[u_b]) {
            if (dist_f[v] != -1) return dist_b[u_b] + 1 + dist_f[v];
            if (dist_b[v] == -1) {
                dist_b[v] = dist_b[u_b] + 1;
                q_b.push(v);
            }
        }
    }
    return -1;
}
```
```python
from collections import deque

def bidirectional_bfs_python(adj: list[list[int]], start: int, target: int) -> int:
    if start == target:
        return 0
    n = len(adj)

    dist_f, dist_b = [-1] * n, [-1] * n
    q_f, q_b = deque([start]), deque([target])
    dist_f[start], dist_b[target] = 0, 0

    while q_f and q_b:
        u_f = q_f.popleft()
        for v in adj[u_f]:
            if dist_b[v] != -1:
                return dist_f[u_f] + 1 + dist_b[v]
            if dist_f[v] == -1:
                dist_f[v] = dist_f[u_f] + 1
                q_f.append(v)

        u_b = q_b.popleft()
        for v in adj[u_b]:
            if dist_f[v] != -1:
                return dist_b[u_b] + 1 + dist_f[v]
            if dist_b[v] == -1:
                dist_b[v] = dist_b[u_b] + 1
                q_b.append(v)

    return -1
```
```typescript
function bidirectionalBfsTS(adj: number[][], start: number, target: number): number {
    if (start === target) return 0;
    const n = adj.length;

    const dist_f = Array(n).fill(-1);
    const dist_b = Array(n).fill(-1);
    const q_f = [start], q_b = [target];
    dist_f[start] = 0; dist_b[target] = 0;

    let head_f = 0, head_b = 0;

    while (head_f < q_f.length && head_b < q_b.length) {
        const u_f = q_f[head_f++];
        for (const v of adj[u_f]) {
            if (dist_b[v] !== -1) return dist_f[u_f] + 1 + dist_b[v];
            if (dist_f[v] === -1) {
                dist_f[v] = dist_f[u_f] + 1;
                q_f.push(v);
            }
        }

        const u_b = q_b[head_b++];
        for (const v of adj[u_b]) {
            if (dist_f[v] !== -1) return dist_b[u_b] + 1 + dist_f[v];
            if (dist_f[v] === -1) {
                dist_f[v] = dist_b[u_b] + 1;
                q_b.push(v);
            }
        }
    }
    return -1;
}
```
:::

### 6. Задача про трансформацію слів (Word Ladder)

У цій алгоритмічній задачі задано початкове слово `begin_word`, кінцеве слово `end_word` та словник допустимих слів `word_list`. За один крок дозволяється змінювати лише одну літеру слова так, щоб утворене нове слово належить словнику. Необхідно знайти найкоротший ланцюжок трансформацій.

#### Неявний граф (Implicit Graph):
Вершинами графа виступають рядки одинакової довжини. Ребро існує між двома словами тоді й лише тоді, коли відстань Геммінга між ними дорівнює 1 (різниця в 1 символ).
Оскільки будувати повний граф суміжності для словника з десятків тисяч слів заздалегідь занадто довго `O(N² · L)`, сусіди генеруються динамічно під час BFS: для кожного з `L` символів поточного слова перебираються 26 літер алфавіту, і перевіряється наявність у хеш-сеті словника.

:::tabs
```c
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int ladder_length_c(const char* begin_word, const char* end_word, const char** word_list, int word_count) {
    int len = strlen(begin_word);
    int target_idx = -1;
    for (int i = 0; i < word_count; ++i) {
        if (strcmp(word_list[i], end_word) == 0) {
            target_idx = i;
            break;
        }
    }
    if (target_idx == -1) return 0;

    int* dist = (int*)malloc(sizeof(int) * word_count);
    for (int i = 0; i < word_count; ++i) dist[i] = -1;

    int* queue = (int*)malloc(sizeof(int) * word_count);
    int head = 0, tail = 0;

    for (int i = 0; i < word_count; ++i) {
        int diff = 0;
        for (int k = 0; k < len; ++k) {
            if (begin_word[k] != word_list[i][k]) diff++;
        }
        if (diff == 1) {
            dist[i] = 2; // Кількість слів у ланцюжку (begin + word_list[i])
            queue[tail++] = i;
        }
    }

    int result = 0;
    while (head < tail) {
        int u = queue[head++];
        if (u == target_idx) {
            result = dist[u];
            break;
        }

        for (int v = 0; v < word_count; ++v) {
            if (dist[v] == -1) {
                int diff = 0;
                for (int k = 0; k < len; ++k) {
                    if (word_list[u][k] != word_list[v][k]) diff++;
                }
                if (diff == 1) {
                    dist[v] = dist[u] + 1;
                    queue[tail++] = v;
                }
            }
        }
    }

    free(dist); free(queue);
    return result;
}
```
```cpp
#include <string>
#include <vector>
#include <unordered_set>
#include <queue>

int ladder_length_cpp(std::string begin_word, std::string end_word, const std::vector<std::string>& word_list) {
    std::unordered_set<std::string> dict(word_list.begin(), word_list.end());
    if (!dict.contains(end_word)) return 0;

    std::queue<std::pair<std::string, int>> q;
    q.push({begin_word, 1});

    while (!q.empty()) {
        auto [word, len] = q.front();
        q.pop();

        if (word == end_word) return len;

        for (std::size_t i = 0; i < word.length(); ++i) {
            char original = word[i];
            for (char c = 'a'; c <= 'z'; ++c) {
                word[i] = c;
                if (dict.contains(word)) {
                    dict.erase(word); // Вилучення замість visited!
                    q.push({word, len + 1});
                }
            }
            word[i] = original;
        }
    }
    return 0;
}
```
```python
from collections import deque

def ladder_length_python(begin_word: str, end_word: str, word_list: list[str]) -> int:
    dict_set = set(word_list)
    if end_word not in dict_set:
        return 0

    q = deque([(begin_word, 1)])

    while q:
        word, length = q.popleft()
        if word == end_word:
            return length

        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = word[:i] + c + word[i+1:]
                if next_word in dict_set:
                    dict_set.remove(next_word)
                    q.append((next_word, length + 1))
    return 0
```
```typescript
function ladderLengthTS(beginWord: string, endWord: string, wordList: string[]): number {
    const dictSet = new Set(wordList);
    if (!dictSet.has(endWord)) return 0;

    const queue: [string, number][] = [[beginWord, 1]];
    let head = 0;

    while (head < queue.length) {
        const [word, length] = queue[head++];
        if (word === endWord) return length;

        for (let i = 0; i < word.length; i++) {
            for (let c = 97; c <= 122; c++) {
                const char = String.fromCharCode(c);
                const nextWord = word.slice(0, i) + char + word.slice(i + 1);
                if (dictSet.has(nextWord)) {
                    dictSet.delete(nextWord);
                    queue.push([nextWord, length + 1]);
                }
            }
        }
    }
    return 0;
}
```
:::

### 7. Обчислення системних топологічних метрик (Eccentricity, Radius, Diameter, Center)

У мережевому інжинірингу, теорії телекомунікацій та супутниковому зв'язку BFS використовується для обчислення фундаментальних топологічних характеристик графа:

#### Поняття та формули:
1. **Ексцентриситет вершини `ε(v)`:** Максимальна з найкоротших відстаней від вершини `v` до всіх інших досяжних вершин графа:
```text
ε(v) = max_{u ∈ V} dist(v, u)
```
   Для обчислення `ε(v)` достатньо виконати один повний прогін BFS із початком у вершині `v` і взяти максимальне значення у масиві `dist[]`.
2. **Діаметр графа `D`:** Найбільший ексцентриситет серед усіх вершин графа:
```text
D = max_{v ∈ V} ε(v)
```
   Показує максимальну можливу затримку передачі даних між будь-якими двома вузлами мережі у найгіршому випадку.
3. **Радіус графа `R`:** Найменший ексцентриситет серед усіх вершин графа:
```text
R = min_{v ∈ V} ε(v)
```
4. **Центр графа (Graph Center):** Множина вершин, чий ексцентриситет дорівнює радіусу графа:
```text
Center(G) = { v ∈ V | ε(v) = R }
```
   Вузли з цієї множини слугують оптимальними місцями для розміщення центральних серверів, баз даних або маршрутизаторів ядра (Core Routers), оскільки вони мінімізують максимальний час відгуку до найвіддаленіших клієнтів.     const u_f = q_f[head_f++];
        for (const v of adj[u_f]) {
            if (dist_b[v] !== -1) return dist_f[u_f] + 1 + dist_b[v];
            if (dist_f[v] === -1) {
                dist_f[v] = dist_f[u_f] + 1;
                q_f.push(v);
            }
        }

        const u_b = q_b[head_b++];
        for (const v of adj[u_b]) {
            if (dist_f[v] !== -1) return dist_b[u_b] + 1 + dist_f[v];
            if (dist_b[v] === -1) {
                dist_b[v] = dist_b[u_b] + 1;
                q_b.push(v);
            }
        }
    }
    return -1;
}
```
:::

### 6. Задача про трансформацію слів (Word Ladder)

У цій алгоритмічній задачі задано початкове слово `begin_word`, кінцеве слово `end_word` та словник допустимих слів `word_list`. За один крок дозволяється змінювати лише одну літеру слова так, щоб утворене нове слово належить словнику. Необхідно знайти найкоротший ланцюжок трансформацій.

#### Неявний граф (Implicit Graph):
Вершинами графа виступають рядки одинакової довжини. Ребро існує між двома словами тоді й лише тоді, коли відстань Геммінга між ними дорівнює 1 (різниця в 1 символ).
Оскільки будувати повний граф суміжності для словника з десятків тисяч слів заздалегідь занадто довго `O(N² · L)`, сусіди генеруються динамічно під час BFS: для кожного з `L` символів поточного слова перебираються 26 літер алфавіту, і перевіряється наявність у хеш-сеті словника.

:::tabs
```c
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int ladder_length_c(const char* begin_word, const char* end_word, const char** word_list, int word_count) {
    int len = strlen(begin_word);
    int target_idx = -1;
    for (int i = 0; i < word_count; ++i) {
        if (strcmp(word_list[i], end_word) == 0) {
            target_idx = i;
            break;
        }
    }
    if (target_idx == -1) return 0;

    int* dist = (int*)malloc(sizeof(int) * word_count);
    for (int i = 0; i < word_count; ++i) dist[i] = -1;

    int* queue = (int*)malloc(sizeof(int) * word_count);
    int head = 0, tail = 0;

    for (int i = 0; i < word_count; ++i) {
        int diff = 0;
        for (int k = 0; k < len; ++k) {
            if (begin_word[k] != word_list[i][k]) diff++;
        }
        if (diff == 1) {
            dist[i] = 2; // Кількість слів у ланцюжку (begin + word_list[i])
            queue[tail++] = i;
        }
    }

    int result = 0;
    while (head < tail) {
        int u = queue[head++];
        if (u == target_idx) {
            result = dist[u];
            break;
        }

        for (int v = 0; v < word_count; ++v) {
            if (dist[v] == -1) {
                int diff = 0;
                for (int k = 0; k < len; ++k) {
                    if (word_list[u][k] != word_list[v][k]) diff++;
                }
                if (diff == 1) {
                    dist[v] = dist[u] + 1;
                    queue[tail++] = v;
                }
            }
        }
    }

    free(dist); free(queue);
    return result;
}
```
```cpp
#include <string>
#include <vector>
#include <unordered_set>
#include <queue>

int ladder_length_cpp(std::string begin_word, std::string end_word, const std::vector<std::string>& word_list) {
    std::unordered_set<std::string> dict(word_list.begin(), word_list.end());
    if (!dict.contains(end_word)) return 0;

    std::queue<std::pair<std::string, int>> q;
    q.push({begin_word, 1});

    while (!q.empty()) {
        auto [word, len] = q.front();
        q.pop();

        if (word == end_word) return len;

        for (std::size_t i = 0; i < word.length(); ++i) {
            char original = word[i];
            for (char c = 'a'; c <= 'z'; ++c) {
                word[i] = c;
                if (dict.contains(word)) {
                    dict.erase(word); // Вилучення замість visited!
                    q.push({word, len + 1});
                }
            }
            word[i] = original;
        }
    }
    return 0;
}
```
```python
from collections import deque

def ladder_length_python(begin_word: str, end_word: str, word_list: list[str]) -> int:
    dict_set = set(word_list)
    if end_word not in dict_set:
        return 0

    q = deque([(begin_word, 1)])

    while q:
        word, length = q.popleft()
        if word == end_word:
            return length

        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = word[:i] + c + word[i+1:]
                if next_word in dict_set:
                    dict_set.remove(next_word)
                    q.append((next_word, length + 1))
    return 0
```
```typescript
function ladderLengthTS(beginWord: string, endWord: string, wordList: string[]): number {
    const dictSet = new Set(wordList);
    if (!dictSet.has(endWord)) return 0;

    const queue: [string, number][] = [[beginWord, 1]];
    let head = 0;

    while (head < queue.length) {
        const [word, length] = queue[head++];
        if (word === endWord) return length;

        for (let i = 0; i < word.length; i++) {
            for (let c = 97; c <= 122; c++) {
                const char = String.fromCharCode(c);
                const nextWord = word.slice(0, i) + char + word.slice(i + 1);
                if (dictSet.has(nextWord)) {
                    dictSet.delete(nextWord);
                    queue.push([nextWord, length + 1]);
                }
            }
        }
    }
    return 0;
}
```
:::

### 7. Обчислення системних топологічних метрик (Eccentricity, Radius, Diameter, Center)

У мережевому інжинірингу, теорії телекомунікацій та супутниковому зв'язку BFS використовується для обчислення фундаментальних топологічних характеристик графа:

#### Поняття та формули:
1. **Ексцентриситет вершини $\epsilon(v)$:** Максимальна з найкоротших відстаней від вершини $v$ до всіх інших досяжних вершин графа:
   $$\epsilon(v) = \max_{u \in V} d(v, u)$$
   Для обчислення $\epsilon(v)$ достатньо виконати один повний прогін BFS із початком у вершині $v$ і взяти максимальне значення у масиві $dist[]$.
2. **Діаметр графа $D$:** Найбільший ексцентриситет серед усіх вершин графа:
   $$D = \max_{v \in V} \epsilon(v)$$
   Показує максимальну можливу затримку передачі даних між будь-якими двома вузлами мережі у найгіршому випадку.
3. **Радіус графа $R$:** Найменший ексцентриситет серед усіх вершин графа:
   $$R = \min_{v \in V} \epsilon(v)$$
4. **Центр графа (Graph Center):** Множина вершин, чий ексцентриситет дорівнює радіусу графа:
   $$\text{Center}(G) = \{ v \in V \mid \epsilon(v) = R \}$$
   Вузли з цієї множини слугують оптимальними місцями для розміщення центральних серверів, баз даних або маршрутизаторів ядра (Core Routers), оскільки вони мінімізують максимальний час відгуку до найвіддаленіших клієнтів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

void compute_graph_metrics_c(int num_vertices, const int* const* adj, const int* adj_sizes) {
    int* ecc = (int*)malloc(sizeof(int) * num_vertices);
    int* dist = (int*)malloc(sizeof(int) * num_vertices);
    int* queue = (int*)malloc(sizeof(int) * num_vertices);

    for (int start = 0; start < num_vertices; ++start) {
        for (int i = 0; i < num_vertices; ++i) dist[i] = -1;
        int head = 0, tail = 0;

        dist[start] = 0;
        queue[tail++] = start;
        int max_d = 0;

        while (head < tail) {
            int u = queue[head++];
            if (dist[u] > max_d) max_d = dist[u];

            for (int i = 0; i < adj_sizes[u]; ++i) {
                int v = adj[u][i];
                if (dist[v] == -1) {
                    dist[v] = dist[u] + 1;
                    queue[tail++] = v;
                }
            }
        }
        ecc[start] = max_d;
    }

    int diameter = 0;
    int radius = 1e9;
    for (int i = 0; i < num_vertices; ++i) {
        if (ecc[i] > diameter) diameter = ecc[i];
        if (ecc[i] < radius) radius = ecc[i];
    }

    printf("Діаметр графа: %d, Радіус графа: %d\n", diameter, radius);
    free(ecc); free(dist); free(queue);
}
```
```cpp
#include <vector>
#include <queue>
#include <algorithm>
#include <iostream>

void compute_graph_metrics_cpp(const std::vector<std::vector<int>>& adj) {
    int n = adj.size();
    std::vector<int> ecc(n, 0);

    for (int start = 0; start < n; ++start) {
        std::vector<int> dist(n, -1);
        std::queue<int> q;

        dist[start] = 0;
        q.push(start);
        int max_d = 0;

        while (!q.empty()) {
            int u = q.front();
            q.pop();
            max_d = std::max(max_d, dist[u]);

            for (int v : adj[u]) {
                if (dist[v] == -1) {
                    dist[v] = dist[u] + 1;
                    q.push(v);
                }
            }
        }
        ecc[start] = max_d;
    }

    int diameter = *std::max_element(ecc.begin(), ecc.end());
    int radius = *std::min_element(ecc.begin(), ecc.end());

    std::cout << "Діаметр: " << diameter << ", Радіус: " << radius << "\n";
}
```
```python
from collections import deque

def compute_graph_metrics_python(adj: list[list[int]]) -> tuple[int, int, list[int]]:
    n = len(adj)
    ecc = [0] * n

    for start in range(n):
        dist = [-1] * n
        q = deque([start])
        dist[start] = 0
        max_d = 0

        while q:
            u = q.popleft()
            max_d = max(max_d, dist[u])

            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    q.append(v)

        ecc[start] = max_d

    diameter = max(ecc)
    radius = min(ecc)
    center = [i for i in range(n) if ecc[i] == radius]

    return diameter, radius, center
```
```typescript
function computeGraphMetricsTS(adj: number[][]): { diameter: number; radius: number; center: number[] } {
    const n = adj.length;
    const ecc: number[] = Array(n).fill(0);

    for (let start = 0; start < n; start++) {
        const dist = Array(n).fill(-1);
        const queue: number[] = [start];
        dist[start] = 0;
        let head = 0;
        let max_d = 0;

        while (head < queue.length) {
            const u = queue[head++];
            max_d = Math.max(max_d, dist[u]);

            for (const v of adj[u]) {
                if (dist[v] === -1) {
                    dist[v] = dist[u] + 1;
                    queue.push(v);
                }
            }
        }
        ecc[start] = max_d;
    }

    const diameter = Math.max(...ecc);
    const radius = Math.min(...ecc);
    const center = ecc.map((e, idx) => (e === radius ? idx : -1)).filter(idx => idx !== -1);

    return { diameter, radius, center };
}
```
:::

### 8. Маршрутизація пакетиків у мережевих топологіях (Spanning Tree Protocol)

У комп'ютерних мережах стандарту Ethernet (IEEE 802.1D) для усунення зациклення кадрів та запобігання широкомовним штормам (Broadcast Storms) вимикачі (Switches) будують мінімальне покривне дерево (Spanning Tree) за допомогою модифікованого обходу в ширину BFS.

#### Системна логіка STP:
- Всі вимикачі обмінюються повідомленнями BPDU (Bridge Protocol Data Units).
- Вибирається єдиний кореневий вимикач (Root Bridge) з найменшим системним ідентифікатором (Bridge ID).
- Від кореневого вимикача запускається хвиля BFS для знаходження найкоротшого шляху до кожного порту у мережі.
- Усі ребра графа, які утворюють цикли (недеревні ребра BFS), переводяться у заблокований стан (Blocking Mode). При відмові активного каналу BFS негайно перебудовує топологію, активуючи резервне ребро.

### 9. Пошук у просторі станів головоломок (State Space Search: 8-Puzzle)

У штучному інтелекті та системному аналізі графом може виступати простір станів фізичної системи або комбінаторної головоломки (наприклад, "П'ятнашки" 8-Puzzle, Рубік `3×3×3` або розгадування кросвордів).

#### Особливості простору станів:
1. **Динамічна генерація вузлів:** Граф не існує у пам'яті заздалегідь — кожен стан подається унікальним текстом чи числом, а ребра є допустимими ходами (переміщення порожньої клітини вгору, вниз, ліворуч, праворуч).
2. **Гарантія мінімальної кількості ходів:** BFS гарантує знаходження рішення за мінімально можливу кількість ходів, оскільки спочатку досліджуються всі стани, досяжні за 1 хід, потім за 2 ходи і так далі.
3. **Хешування відвіданих станів:** Для виключення зациклення використовується хеш-таблиця `std::unordered_set<std::string>` або бітовий упакований індекс `uint64_t`.

#### Числовий аналіз складності простору станів:
Для класичної головоломки 8-Puzzle кількість можливих перестановок становить $9! = 362\ 880$. Рівно половина з них є нерозв'язними через парність інверсій. Таким чином, досяжна компонента містить $181\ 440$ станів. Повний BFS обходить увесь простір за частку секунди, тоді як для головоломки 15-Puzzle ($16! \approx 2.09 \times 10^{13}$) односторонній BFS вимагає занадто багато пам'яті, що спонукає використовувати A* або двосторонній BFS.

### 10. Пошук компонент зв'язності у великих соціальних та біологічних мережах

У веб-краулерах (Web Crawlers), аналізі соціальних мереж (Facebook, LinkedIn) та біоінформатиці (мережі взаємодії білків PPI — Protein-Protein Interaction) BFS є основним інструментом виділення зв'язних скупчень та кластерів:

#### Практичні задачі мережевого кластерного аналізу:
- **Пошук найкоротших ланцюжків знайомств (Degrees of Separation):** Розрахунок відстані між довільними двома користувачами у соціальній мережі.
- **Індексація веб-сторінок:** Веб-краулер починає з переліку стартових URL-адрес і розгортає хвилю BFS, скануючи гіперпосилання `<a href="...">` для повної індексації досяжного сегмента інтернету.

#### Обмеження глибини та виявлення пасток у краулерах (Depth-Limited Crawling):
Для уникнення блокування у безкінечних динамічних генераторах URL-адрес (наприклад, календарях із перемиканням місяців) краулер BFS обмежує глибину пошуку полем `depth <= max_depth`. Усі посилання, виявлені на граничному рівні `max_depth`, обробляються, але їхні вихідні посилання більше не додаються до черги.

### Порівняльна аналітична таблиця застосувань BFS

| Алгоритм / Варіант | Структура даних | Часова складність | Просторова складність | Типове застосування |
| :--- | :--- | :--- | :--- | :--- |
| **Grid BFS** | Черга FIFO | `O(N × M)` | `O(N × M)` | Навігація роботів, лабіринти |
| **Flood Fill** | Черга FIFO / Deque | `O(N × M)` | `O(N × M)` | Заливка в графічних редакторах |
| **Bipartite Check** | Черга + 2 кольори | `O(V + E)` | `O(V)` | Розподіл ресурсів, виявлення непарних циклів |
| **0-1 BFS** | Двостороння черга `deque` | `O(V + E)` | `O(V)` | Графи з вагами ребер `0` та `1` |
| **Bidirectional BFS** | Дві черги FIFO | `O(b^{d/2})` | `O(b^{d/2})` | Пошук найкоротших шляхів між двома вузлами |
| **Word Ladder** | Черга FIFO + Хеш-сет | `O(N · L · 26)` | `O(N · L)` | Мовні трансформації, біоінформатика |
| **Graph Metrics** | Послідовні BFS | `O(V · (V + E))` | `O(V)` | Аналіз топології мереж, розміщення серверів |
| **STP Routing** | BFS хвиля BPDU | `O(V + E)` | `O(V)` | Комутація Ethernet, занепад зациклень |
| **State Space BFS** | Черга + Хеш-сет | `O(b^d)` | `O(b^d)` | Штучний інтелект, розв'язання головоломок |
| **Web Crawler BFS** | Черга + Хеш-таблиця | `O(V + E)` | `O(V)` | Пошукові системи, індексація мережі |
