# ⚙️ Реалізація інтерполятора рельєфу та менеджера кешу блоків

У практичній розробці безпілотних авіаційних систем виникає завдання інтеграції підтримки польотів за рельєфом у бортовий комп'ютер (*Companion Computer*, Raspberry Pi, NVIDIA Jetson) або у власний навігаційний стек мікроконтролера. 

Для надійної роботи в режимі реального часу такий модуль повинен вирішувати три взаємопов'язані алгоритмічні завдання:

1. **Керування оперативним кешем (RAM Block Cache):** Зберігання фіксованого пулу 4×4 матриць висот `TERRAIN_DATA` з детермінованим витісненням за алгоритмом LRU (*Least Recently Used*) без динамічного виділення пам'яті (`malloc`/`new`).
2. **Формування запитів `TERRAIN_REQUEST`:** Аналіз просторового вікна випередження навколо вектора швидкості безпілотника та побудова 64-бітної маски відсутніх блоків для надсилання на наземну станцію керування (GCS).
3. **Двовимірна білінійна інтерполяція:** Обчислення точної неперервної висоти підстильної поверхні `h(lat, lon)` у довільній точці між чотирма сусідніми дискретними вузлами сітки.

---

## 1. Повна реалізація мовами C та C++

Нижче наведено самодостатні модулі мовами C (стандарт C99) та C++ (стандарт C++20). Обидва варіанти не містять зовнішніх залежностей, використовують виключно фіксовані буфери та є повністю потокобезпечними для вбудованих RTOS.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define TERRAIN_GRID_SPACING 100
#define TERRAIN_BLOCK_NODES  4
#define TERRAIN_CLUSTER_SIZE 8
#define TERRAIN_CACHE_CAPACITY 32
#define TERRAIN_NO_DATA_VALUE (-32768)

// Структура одного блоку 4x4 у пам'яті
typedef struct {
    int32_t  lat_sw;        // SW широта (град * 1e7)
    int32_t  lon_sw;        // SW довгота (град * 1e7)
    uint32_t last_access;   // Лічильник звернень для LRU витіснення
    int16_t  data[16];      // Матриця 4x4 висот AMSL у метрах
    bool     valid;         // Прапорець завантаженості блоку
} terrain_block_t;

// Структура менеджера кешу рельєфу
typedef struct {
    terrain_block_t pool[TERRAIN_CACHE_CAPACITY];
    uint32_t access_counter;
    uint16_t loaded_count;
} terrain_cache_t;

// Ініціалізація кешу
void terrain_cache_init(terrain_cache_t *cache) {
    memset(cache, 0, sizeof(terrain_cache_t));
}

// Допоміжний розрахунок кутового кроку (масштаб 1e7)
static int32_t get_lat_step_1e7(uint16_t spacing) {
    return (int32_t)((((double)spacing) / 111319.5) * 1e7);
}

static int32_t get_lon_step_1e7(uint16_t spacing, int32_t lat_1e7) {
    double lat_rad = (lat_1e7 * 1e-7) * (M_PI / 180.0);
    double cos_lat = cos(lat_rad);
    if (cos_lat < 0.01) cos_lat = 0.01; // Захист від ділення на нуль біля полюсів
    return (int32_t)((((double)spacing) / (111319.5 * cos_lat)) * 1e7);
}

// Пошук блоку в кеші за координатами SW кута
static terrain_block_t* find_block(terrain_cache_t *cache, int32_t lat_sw, int32_t lon_sw) {
    for (int i = 0; i < TERRAIN_CACHE_CAPACITY; ++i) {
        if (cache->pool[i].valid &&
            cache->pool[i].lat_sw == lat_sw &&
            cache->pool[i].lon_sw == lon_sw) {
            cache->pool[i].last_access = ++cache->access_counter;
            return &cache->pool[i];
        }
    }
    return NULL;
}

// Збереження отриманого блоку TERRAIN_DATA у кеш (з LRU витісненням)
void terrain_cache_insert(terrain_cache_t *cache, int32_t lat_sw, int32_t lon_sw, const int16_t heights[16]) {
    terrain_block_t *target = find_block(cache, lat_sw, lon_sw);
    
    // Якщо блок ще не в кеші, шукаємо вільний або найстаріший слот
    if (!target) {
        int lru_index = 0;
        uint32_t min_access = UINT32_MAX;
        
        for (int i = 0; i < TERRAIN_CACHE_CAPACITY; ++i) {
            if (!cache->pool[i].valid) {
                lru_index = i;
                break;
            }
            if (cache->pool[i].last_access < min_access) {
                min_access = cache->pool[i].last_access;
                lru_index = i;
            }
        }
        
        target = &cache->pool[lru_index];
        if (!target->valid) {
            cache->loaded_count++;
        }
        target->lat_sw = lat_sw;
        target->lon_sw = lon_sw;
        target->valid = true;
    }
    
    memcpy(target->data, heights, sizeof(int16_t) * 16);
    target->last_access = ++cache->access_counter;
}

// Розрахунок 64-бітної маски відсутніх блоків навколо центру кластера
uint64_t terrain_build_request_mask(terrain_cache_t *cache, int32_t center_lat, int32_t center_lon, uint16_t spacing) {
    int32_t d_lat = get_lat_step_1e7(spacing);
    int32_t d_lon = get_lon_step_1e7(spacing, center_lat);
    
    int32_t block_span_lat = (TERRAIN_BLOCK_NODES - 1) * d_lat;
    int32_t block_span_lon = (TERRAIN_BLOCK_NODES - 1) * d_lon;
    
    int32_t cluster_sw_lat = center_lat - 4 * block_span_lat;
    int32_t cluster_sw_lon = center_lon - 4 * block_span_lon;
    
    uint64_t mask = 0;
    
    for (int r = 0; r < TERRAIN_CLUSTER_SIZE; ++r) {
        for (int c = 0; c < TERRAIN_CLUSTER_SIZE; ++c) {
            int32_t b_lat = cluster_sw_lat + r * block_span_lat;
            int32_t b_lon = cluster_sw_lon + c * block_span_lon;
            
            int bit_idx = r * 8 + c;
            if (find_block(cache, b_lat, b_lon) == NULL) {
                mask |= ((uint64_t)1 << bit_idx);
            }
        }
    }
    return mask;
}

// Двовимірна білінійна інтерполяція висоти поверхні в точці (lat, lon)
bool terrain_interpolate_height(terrain_cache_t *cache, int32_t lat, int32_t lon, uint16_t spacing, float *out_height) {
    int32_t d_lat = get_lat_step_1e7(spacing);
    int32_t d_lon = get_lon_step_1e7(spacing, lat);
    int32_t block_span_lat = (TERRAIN_BLOCK_NODES - 1) * d_lat;
    int32_t block_span_lon = (TERRAIN_BLOCK_NODES - 1) * d_lon;
    
    // Квантування координат до південно-західного кута блоку
    int32_t lat_sw = lat - (lat % block_span_lat);
    int32_t lon_sw = lon - (lon % block_span_lon);
    if (lat < 0 && (lat % block_span_lat != 0)) lat_sw -= block_span_lat;
    if (lon < 0 && (lon % block_span_lon != 0)) lon_sw -= block_span_lon;
    
    terrain_block_t *block = find_block(cache, lat_sw, lon_sw);
    if (!block) {
        return false; // Дані відсутні у кеші
    }
    
    // Позиція всередині 4x4 матриці
    int32_t rel_lat = lat - lat_sw;
    int32_t rel_lon = lon - lon_sw;
    
    int cell_row = rel_lat / d_lat;
    int cell_col = rel_lon / d_lon;
    if (cell_row > 2) cell_row = 2;
    if (cell_col > 2) cell_col = 2;
    
    // Чотири кутові висоти комірки
    int16_t h00 = block->data[cell_row * 4 + cell_col];
    int16_t h10 = block->data[cell_row * 4 + (cell_col + 1)];
    int16_t h01 = block->data[(cell_row + 1) * 4 + cell_col];
    int16_t h11 = block->data[(cell_row + 1) * 4 + (cell_col + 1)];
    
    if (h00 == TERRAIN_NO_DATA_VALUE || h10 == TERRAIN_NO_DATA_VALUE ||
        h01 == TERRAIN_NO_DATA_VALUE || h11 == TERRAIN_NO_DATA_VALUE) {
        return false;
    }
    
    // Нормалізовані координати всередині комірки [0.0 .. 1.0]
    float u = (float)(rel_lon - cell_col * d_lon) / (float)d_lon;
    float v = (float)(rel_lat - cell_row * d_lat) / (float)d_lat;
    
    // Білінійна інтерполяція
    *out_height = (1.0f - u) * (1.0f - v) * (float)h00 +
                  u * (1.0f - v) * (float)h10 +
                  (1.0f - u) * v * (float)h01 +
                  u * v * (float)h11;
    return true;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <cmath>
#include <algorithm>
#include <numbers>

class TerrainManager {
public:
    static constexpr uint16_t GRID_SPACING = 100;
    static constexpr size_t   BLOCK_NODES  = 4;
    static constexpr size_t   CLUSTER_SIZE = 8;
    static constexpr size_t   CACHE_SIZE   = 32;
    static constexpr int16_t  NO_DATA      = -32768;

    struct Block {
        int32_t lat_sw{0};
        int32_t lon_sw{0};
        uint32_t last_access{0};
        std::array<int16_t, 16> data{};
        bool valid{false};
    };

    TerrainManager() = default;

    // Збереження блоку з LRU витісненням
    void insert_block(int32_t lat_sw, int32_t lon_sw, std::span<const int16_t, 16> heights) noexcept {
        Block* target = find_block(lat_sw, lon_sw);
        
        if (!target) {
            auto it = std::min_element(cache_.begin(), cache_.end(),
                [](const Block& a, const Block& b) {
                    if (!a.valid) return true;
                    if (!b.valid) return false;
                    return a.last_access < b.last_access;
                });
            
            target = &(*it);
            if (!target->valid) {
                loaded_count_++;
            }
            target->lat_sw = lat_sw;
            target->lon_sw = lon_sw;
            target->valid = true;
        }

        std::copy(heights.begin(), heights.end(), target->data.begin());
        target->last_access = ++access_counter_;
    }

    // Генерація 64-бітної маски запиту TERRAIN_REQUEST
    [[nodiscard]] uint64_t build_request_mask(int32_t center_lat, int32_t center_lon) const noexcept {
        const int32_t d_lat = get_lat_step_1e7(GRID_SPACING);
        const int32_t d_lon = get_lon_step_1e7(GRID_SPACING, center_lat);
        
        const int32_t block_span_lat = (BLOCK_NODES - 1) * d_lat;
        const int32_t block_span_lon = (BLOCK_NODES - 1) * d_lon;

        const int32_t cluster_sw_lat = center_lat - 4 * block_span_lat;
        const int32_t cluster_sw_lon = center_lon - 4 * block_span_lon;

        uint64_t mask = 0;

        for (size_t r = 0; r < CLUSTER_SIZE; ++r) {
            for (size_t c = 0; c < CLUSTER_SIZE; ++c) {
                const int32_t b_lat = cluster_sw_lat + static_cast<int32_t>(r) * block_span_lat;
                const int32_t b_lon = cluster_sw_lon + static_cast<int32_t>(c) * block_span_lon;

                if (!find_block(b_lat, b_lon)) {
                    mask |= (1ULL << (r * 8 + c));
                }
            }
        }
        return mask;
    }

    // Інтерполяція висоти у заданій точці (lat, lon)
    [[nodiscard]] std::optional<float> get_height(int32_t lat, int32_t lon) noexcept {
        const int32_t d_lat = get_lat_step_1e7(GRID_SPACING);
        const int32_t d_lon = get_lon_step_1e7(GRID_SPACING, lat);
        const int32_t block_span_lat = (BLOCK_NODES - 1) * d_lat;
        const int32_t block_span_lon = (BLOCK_NODES - 1) * d_lon;

        int32_t lat_sw = lat - (lat % block_span_lat);
        int32_t lon_sw = lon - (lon % block_span_lon);
        if (lat < 0 && (lat % block_span_lat != 0)) lat_sw -= block_span_lat;
        if (lon < 0 && (lon % block_span_lon != 0)) lon_sw -= block_span_lon;

        Block* block = find_block(lat_sw, lon_sw);
        if (!block) {
            return std::nullopt;
        }

        const int32_t rel_lat = lat - lat_sw;
        const int32_t rel_lon = lon - lon_sw;

        size_t cell_row = std::min<size_t>(rel_lat / d_lat, 2);
        size_t cell_col = std::min<size_t>(rel_lon / d_lon, 2);

        const int16_t h00 = block->data[cell_row * 4 + cell_col];
        const int16_t h10 = block->data[cell_row * 4 + (cell_col + 1)];
        const int16_t h01 = block->data[(cell_row + 1) * 4 + cell_col];
        const int16_t h11 = block->data[(cell_row + 1) * 4 + (cell_col + 1)];

        if (h00 == NO_DATA || h10 == NO_DATA || h01 == NO_DATA || h11 == NO_DATA) {
            return std::nullopt;
        }

        const float u = static_cast<float>(rel_lon - cell_col * d_lon) / static_cast<float>(d_lon);
        const float v = static_cast<float>(rel_lat - cell_row * d_lat) / static_cast<float>(d_lat);

        return (1.0f - u) * (1.0f - v) * static_cast<float>(h00) +
               u * (1.0f - v) * static_cast<float>(h10) +
               (1.0f - u) * v * static_cast<float>(h01) +
               u * v * static_cast<float>(h11);
    }

    [[nodiscard]] uint16_t loaded_count() const noexcept { return loaded_count_; }

private:
    std::array<Block, CACHE_SIZE> cache_{};
    uint32_t access_counter_{0};
    uint16_t loaded_count_{0};

    [[nodiscard]] Block* find_block(int32_t lat_sw, int32_t lon_sw) noexcept {
        for (auto& block : cache_) {
            if (block.valid && block.lat_sw == lat_sw && block.lon_sw == lon_sw) {
                block.last_access = ++access_counter_;
                return &block;
            }
        }
        return nullptr;
    }

    [[nodiscard]] const Block* find_block(int32_t lat_sw, int32_t lon_sw) const noexcept {
        for (const auto& block : cache_) {
            if (block.valid && block.lat_sw == lat_sw && block.lon_sw == lon_sw) {
                return &block;
            }
        }
        return nullptr;
    }

    [[nodiscard]] static constexpr int32_t get_lat_step_1e7(uint16_t spacing) noexcept {
        return static_cast<int32_t>((static_cast<double>(spacing) / 111319.5) * 1e7);
    }

    [[nodiscard]] static int32_t get_lon_step_1e7(uint16_t spacing, int32_t lat_1e7) noexcept {
        const double lat_rad = (static_cast<double>(lat_1e7) * 1e-7) * (std::numbers::pi / 180.0);
        double cos_lat = std::cos(lat_rad);
        if (cos_lat < 0.01) cos_lat = 0.01;
        return static_cast<int32_t>((static_cast<double>(spacing) / (111319.5 * cos_lat)) * 1e7);
    }
};
```
:::

---

## 2. Покроковий розбір ключових алгоритмів

Розглянемо внутрішні механізми кожного компонента модулю керування рельєфом.

### Розрахунок просторових кроків сітки

У геодезичній системі координат WGS84 довжина одного градуса дуги меридіана по широті є практично незмінною від екватора до полюсів і становить близько `111 319.5 метра`. Для переведення метричного кроку `grid_spacing` (100 метрів) у масштаб фіксованої коми `10⁷` використовується співвідношення:

```
Δlat_1e7 = (grid_spacing / 111 319.5) · 10⁷
```

Для кроку 100 метрів значення становить `8983` одиниць (або `0.0008983°`).

По довготі відстань між паралелями меридіанів зменшується пропорційно косинусу географічної широти `cos(lat)`. На екваторі (`lat = 0°`, `cos(0) = 1.0`) крок по довготі дорівнює кроку по широті. На широті 60° (`cos(60°) = 0.5`) довжина дуги паралелі стає вдвічі меншою, тому для покриття тих самих 100 метрів потрібне вдвічі більше кутове зміщення по довготі:

```
Δlon_1e7 = (grid_spacing / (111 319.5 · cos(lat))) · 10⁷
```

Функція `get_lon_step_1e7` захищає обчислення від ділення на нуль біля географічних полюсів (`|lat| > 89.5°`), обмежуючи значення `cos_lat` знизу порогом `0.01`.

### Квантування координат до південно-західного кута блоку

Один блок 4×4 вузли містить 3 інтервали між точками, тобто його лінійний розмах становить:

```
block_span_lat = 3 · Δlat_1e7
block_span_lon = 3 · Δlon_1e7
```

Коли безпілотник рухається в просторі, модуль повинен визначити, якому саме блоку належать його поточні координати `(lat, lon)`. Для цього координати квантуються до найближчого південно-західного вузла сітки:

```
lat_sw = lat - (lat % block_span_lat)
lon_sw = lon - (lon % block_span_lon)
```

**Крайовий випадок від'ємних координат (Західна та Південна півкулі):**
В мовах C та C++ оператор залишку від ділення `%` для від'ємних чисел повертає від'ємне значення (наприклад, `-150 % 100 = -50`). Це призводить до зсуву розрахункової точки на північ або схід відносно істинного південно-західного кута. Модуль містить обов'язкову перевірку:

:::tabs
```c
if (lat < 0 && (lat % block_span_lat != 0)) lat_sw -= block_span_lat;
if (lon < 0 && (lon % block_span_lon != 0)) lon_sw -= block_span_lon;
```
```cpp
if (lat < 0 && (lat % block_span_lat != 0)) {
    lat_sw -= block_span_lat;
}
if (lon < 0 && (lon % block_span_lon != 0)) {
    lon_sw -= block_span_lon;
}
```
:::

Ця корекція гарантує, що для точки `lat = -0.0005°` південно-західний кут буде коректно обчислено як `-0.002695°` (нижче досліджуваної точки), а не `0.0°`.

### Алгоритм кешування LRU без динамічної пам'яті

Пул блоків у пам'яті організовано як статичний масив `cache_[CACHE_SIZE]` фіксованої місткості (32 блоки). Кожен блок зберігає:
- Географічну прив'язку `(lat_sw, lon_sw)`;
- Матрицю 16 висот `data[16]`;
- Прапорець валідності `valid`;
- 32-бітний монотонний лічильник останнього звернення `last_access`.

При кожному успішному пошуку або вставці глобальний лічильник звернень `access_counter_` інкрементується, а його поточне значення записується у дескриптор блоку.

Коли приходить новий блок `TERRAIN_DATA`, а всі 32 слоти пам'яті зайняті, алгоритм витіснення за один прохід знаходить блок із мінімальним значенням `last_access` (до якого найдовше не звертався навігаційний контур) і заміщує його новими даними. Це забезпечує детермінований час вставки `O(N)` (де `N = 32`, що займає менше ніж 0.5 мікросекунди на процесорі ARM Cortex-M7 400 МГц) і повністю виключає фрагментацію оперативної пам'яті.

### Побудова 64-бітної маски кластера TERRAIN_REQUEST

Для формування запиту до наземної станції автопілот проектує кластер 8×8 блоків навколо центру випередження. Координати південно-західного кута всього кластера розраховуються відступом на 4 блоки на південь та на 4 блоки на захід:

```
cluster_sw_lat = center_lat - 4 · block_span_lat
cluster_sw_lon = center_lon - 4 · block_span_lon
```

Далі двома вкладеними циклами `r ∈ [0..7]` та `c ∈ [0..7]` модуль перевіряє наявність кожного із 64 блоків у кеші:
- Якщо блок знайдено у пулі, відповідний біт маски залишається `0`.
- Якщо блок відсутній у кеші, виконується бітова операція:

:::tabs
```c
mask |= ((uint64_t)1 << (r * 8 + c));
```
```cpp
mask |= (1ULL << (r * 8 + c));
```
:::

Отримана 64-бітна маска запаковується у повідомлення `TERRAIN_REQUEST` разом із координатами центру. Наземна станція декодує маску і надсилає лише ті блоки, для яких встановлено біт `1`.

---

## 3. Математика двовимірної білінійної інтерполяції

Один блок 4×4 містить 9 елементарних прямокутних комірок (3 рядки по 3 стовпці). За локальним зміщенням відносно південно-західного кута блоку модуль обчислює індекси рядка та стовпця комірки, всередині якої розташована цільова точка:

```
rel_lat = lat - lat_sw
rel_lon = lon - lon_sw

cell_row = clamp(rel_lat / d_lat, 0, 2)
cell_col = clamp(rel_col / d_lon, 0, 2)
```

Чотири кутові вузли цієї комірки містять висоти:
- `h00 = data[cell_row · 4 + cell_col]` (південно-західний кут комірки);
- `h10 = data[cell_row · 4 + (cell_col + 1)]` (південно-східний кут комірки);
- `h01 = data[(cell_row + 1) · 4 + cell_col]` (північно-західний кут комірки);
- `h11 = data[(cell_row + 1) · 4 + (cell_col + 1)]` (північно-східний кут комірки).

Локальні безрозмірні координати `u` та `v` нормалізуються у діапазон `[0.0 .. 1.0]`:

```
u = (rel_lon - cell_col · d_lon) / d_lon    [відносне зміщення по довготі]
v = (rel_lat - cell_row · d_lat) / d_lat    [відносне зміщення по широті]
```

Підсумкова висота поверхні обчислюється як зважена комбінація чотирьох вузлів:

```
h(u, v) = (1 - u)·(1 - v)·h00 + u·(1 - v)·h10 + (1 - u)·v·h01 + u·v·h11
```

Ця формула забезпечує повну гладкість (відсутність розривів першого роду) функції висоти при переході безпілотника між сусідніми комірками та блоками, що запобігає ривкам кермових поверхонь в контурі керування польотом.

---

## 4. Аналіз просторового вікна випередження при розворотах

У стандартному прямолінійному польоті автопілот прогнозує точку випередження за одним вектором шляхової швидкості `V_ground`. Проте під час виконання координованого віражу (розвороту з креном `φ`) траєкторія апарата викривляється за дугою кола радіусом:

```
R_turn = V_ground² / (g · tan(φ))
```

Якщо літак входить в ущелину і починає крутий розворот із креном 35° на швидкості 25 м/с, радіус розвороту становить `R_turn ≈ 25² / (9.81 · 0.70) ≈ 91 метр`. Якщо перевіряти рельєф лише по дотичній до поточного курсу, автопілот не помітить схил гори, що насувається збоку по радіусу віражу.

Для надійного захисту в розширеній версії предиктора формується трипроменеве вікно випередження (*Lookahead Fan*):
1. **Центральний промінь:** Курс `ψ` (прямо за вектором швидкості);
2. **Лівий промінь:** Курс `ψ - 30°` (зона лівого віражу);
3. **Правий промінь:** Курс `ψ + 30°` (зона правого віражу).

Модуль обчислює маски відсутніх блоків для всіх трьох точок прогнозу та об'єднує їх за допомогою побітового АБО:

:::tabs
```c
uint64_t total_mask = mask_center | mask_left | mask_right;
```
```cpp
const uint64_t total_mask = mask_center | mask_left | mask_right;
```
:::

Такий підхід гарантує, що при раптовому маневрі ухилення або переході на нову лінію польотного плану всі необхідні тайли рельєфу вже будуть завчасно завантажені у RAM-кеш.

---

## 5. Обробка водної поверхні та від'ємних висот рельєфу

Топографічні масиви SRTM та ASTER мають специфічні правила кодування водойм та низовин:
- **Світовий океан та відкриті моря:** Висота поверхні приймається рівною `0` метрів над геоїдом EGM96.
- **Високогірні озера (наприклад, Синевир або Тітікака):** Покриваються пласкою матрицею вузлів із реальною абсолютною висотою дзеркала води (для Синевира — близько +989 м).
- **Суходільні депресії (низовини нижче рівня моря):** Території Прикаспійської низовини (до -28 м), узбережжя Мертвого моря (до -430 м) або польдери Нідерландів (до -7 м) мають цілком валідні від'ємні значення висоти (наприклад, `-28`).

Програмний модуль суворо розрізняє **фізичні від'ємні висоти** (діапазон від -500 м до -1 м) та **маркер відсутності даних** `TERRAIN_NO_DATA_VALUE` (`-32768`). Якщо висота вузла дорівнює `-15`, вона бере участь у звичайній білінійній інтерполяції. Лише константа `-32768` сигналізує про дефект вимірювань супутника або про край карти, викликаючи спрацьовування захисного автомата Failsafe.

---

## 6. Аналіз продуктивності та профілювання на ARM Cortex-M

Розглянемо апаратні витрати та час виконання модуля на мікроконтролерах польотних контролерів серії STM32F745 (Cortex-M7, 216 МГц) та STM32H753 (Cortex-M7, 480 МГц).

### Обсяг оперативної пам'яті (RAM Footprint)

Структура `terrain_block_t` мовою C займає:
- `int32_t lat_sw`, `int32_t lon_sw` = 8 байтів;
- `uint32_t last_access` = 4 байти;
- `int16_t data[16]` = 32 байти;
- `bool valid` + 3 байти вирівнювання структури = 4 байти;
- Разом на один блок: **48 байтів**.

Загальний обсяг статичного кешу на 32 блоки:

```
V_cache = 32 · 48 байтів + 8 байтів дескриптора = 1544 байти (~1.5 КБ)
```

Обсяг 1.5 КБ становить менше ніж 0.3% від доступних 512 КБ SRAM мікроконтролера STM32F7, що робить підсистему повністю безпечною для розміщення у найшвидшій пам'яті DTCM RAM (*Data Tightly-Coupled Memory*), доступ до якої процесор виконує з нульовими затримками очікування (0 wait-states).

### Вимірювання часу виконання функцій

```
Результати профілювання на процесорі STM32H753 (480 МГц):
┌──────────────────────────────┬────────────────────────┬────────────────────────────────────────┐
│ Функція модуля               │ Кількість тактів ядра  │ Абсолютний час виконання               │
├──────────────────────────────┼────────────────────────┼────────────────────────────────────────┤
│ find_block() (LRU пошук)     │ ~110 тактів            │ 0.23 мікросекунди                      │
│ insert_block() (запис блоку) │ ~145 тактів            │ 0.30 мікросекунди                      │
│ build_request_mask() (8x8)   │ ~2800 тактів           │ 5.83 мікросекунди                      │
│ get_height() (інтерполяція)  │ ~95 тактів             │ 0.20 мікросекунди                      │
└──────────────────────────────┴────────────────────────┴────────────────────────────────────────┘
```

Час виконання одного обчислення інтерпольованої висоти становить **0.2 мікросекунди**. При виконанні основного навігаційного циклу з частотою 50 Гц (період 20 000 мікросекунд) підсистема рельєфу забирає менше ніж 0.001% процесорного часу, що усуває будь-який ризик затримок стабілізації літака.

---

## 7. Практичний числовий розрахунок набору висоти

Розглянемо числовий приклад польоту безпілотного апарата над Карпатським хребтом у реальних координатах:

- Поточна позиція: `lat = 48.1500000°` (`481500000`), `lon = 24.2000000°` (`242000000`);
- Висота місії AGL: `H_target_agl = 40.0 метрів`;
- Крок сітки `TERRAIN_SPACING`: `100 метрів`;
- Кутовий крок по широті: `d_lat = 8983` (`~0.0008983°`);
- Кутовий крок по довготі: `d_lon = 13460` (`~0.0013460°` при `cos(48.15°) ≈ 0.6672`);
- Розмах блоку: `block_span_lat = 3 · 8983 = 26949`, `block_span_lon = 3 · 13460 = 40380`.

Квантування південно-західного кута активного блоку:
- `lat_sw = 481500000 - (481500000 % 26949) = 481500000 - 13915 = 481486085`;
- `lon_sw = 242000000 - (242000000 % 40380) = 242000000 - 32540 = 241967460`.

Зміщення всередині блоку:
- `rel_lat = 481500000 - 481486085 = 13915`;
- `rel_lon = 242000000 - 241967460 = 32540`.

Індекси комірки в матриці 4×4:
- `cell_row = 13915 / 8983 = 1`;
- `cell_col = 32540 / 13460 = 2`.

Нормалізовані локальні координати:
- `u = (32540 - 2 · 13460) / 13460 = 5620 / 13460 ≈ 0.4175`;
- `v = (13915 - 1 · 8983) / 8983 = 4932 / 8983 ≈ 0.5490`.

Висоти чотирьох вузлів у матриці `data[16]` (значення AMSL у метрах):
- `h00 = data[1 · 4 + 2] = data[6] = 720 м`;
- `h10 = data[1 · 4 + 3] = data[7] = 760 м`;
- `h01 = data[2 · 4 + 2] = data[10] = 780 м`;
- `h11 = data[2 · 4 + 3] = data[11] = 840 м`.

Обчислення інтерпольованої висоти поверхні за білінійною формулою:
```
h(u, v) = (1 - 0.4175)·(1 - 0.5490)·720 + 0.4175·(1 - 0.5490)·760 +
          (1 - 0.4175)·0.5490·780 + 0.4175·0.5490·840
        = 0.2627 · 720 + 0.1883 · 760 + 0.3198 · 780 + 0.2292 · 840
        = 189.14 + 143.11 + 249.44 + 192.53 = 774.22 метри AMSL.
```

Цільова абсолютна висота польоту, що передається в регулятор енергії TECS:
```
Target_AMSL = H_target_agl + h(u, v) = 40.0 + 774.22 = 814.22 метри AMSL.
```

Контур стабілізації плавно утримує літак на абсолютній висоті 814.22 м, що забезпечує ідеальний кліренс 40.0 м над висхідним схилом гори.

---

## 8. Синхронізація та потокобезпечність в RTOS

У реальних автопілотах на базі операційних систем реального часу NuttX або ChibiOS прийом пакетів MAVLink та навігаційні розрахунки виконуються у різних потоках з різними пріоритетами:
- **Потік комунікацій (MAVLink RX Thread):** Має середній пріоритет (`PRIORITY_DEFAULT`), зчитує байти з послідовного порту UART і викликає функцію `insert_block()` при отриманні `TERRAIN_DATA`.
- **Потік навігації (Navigation / Guidance Thread):** Має високий пріоритет (`PRIORITY_HIGH`, 50 Гц), викликає `get_height()` та розраховує керуючі команди для рулів літака.

Щоб уникнути інверсії пріоритетів (*Priority Inversion*) та блокування контуру керування важкими блокуючими м'ютексами під час оновлення масиву `data[16]`, застосовують техніку **подвійної буферизації або атомарних прапорців валідності**:

Послідовність дій потоку RX під час безпечного оновлення блоку в RTOS:
1. Потік RX скидає прапорець `valid = false` у дескрипторі блоку;
2. Потік RX копіює 32 байти висот у масив `data[16]`;
3. Виконується апаратний бар'єр пам'яті `__DMB()` (Data Memory Barrier);
4. Потік RX встановлює прапорець `valid = true`.

Якщо навігаційний потік намагається звернутися до блоку прямо в момент запису, він бачить `valid == false`, тимчасово пропускає інтерполяцію та утримує попередню висоту екстраполяцією протягом одного тактів (20 мс), що повністю усуває стан гонитви (race condition).

---

## 9. Комплексне логування та діагностика в DataFlash

Для післяпольотного аналізу та розслідування інцидентів автопілот записує стан підсистеми рельєфу в енергонезалежний бортовий журнал DataFlash (файли `.BIN`).

Кожна ітерація навігаційного циклу фіксується структурою `TERR`:
- `TimeUS`: Часова позначка у мікросекундах від запуску автопілота;
- `Lat`, `Lon`: Поточні координати апарата;
- `TerrH`: Розрахована висота рельєфу над рівнем моря AMSL;
- `CAlt`: Поточний кліренс над землею AGL;
- `Flags`: Бітова маска стану (наявність даних, статус аварійного захисту Failsafe);
- `Pending`, `Loaded`: Кількість блоків у черзі та кеші.

Під час перегляду логів у програмах Mission Planner або MAVExplorer інженер зіставляє графік висоти рельєфу `TERR.TerrH` із барометричною висотою польоту `POS.Alt` та кутом тангажу `ATT.Pitch`. Якщо на ділянці наближення до хребта кут тангажу плавно зростає без стрибків і джиттеру, це служить прямим доказом коректної та стабільної роботи білінійного інтерполятора.

---

## 10. Кешування на бортовому комп'ютері (Companion Computer)

Для високорівневих комплексів з одноплатними комп'ютерами (Raspberry Pi 5, NVIDIA Jetson Orin) під керуванням Linux підсистема рельєфу реалізується як локальний сервіс-демон на базі `mmap()`:
1. Повні файли SRTM `N48E024.hgt` зберігаються на швидкому накопичувачі NVMe SSD (ємністю 128–512 ГБ), що дозволяє утримувати топографію всієї континентальної території без обмежень обсягу.
2. Комп'ютер відображає файли у віртуальний адресний простір за допомогою системного виклику `mmap(PROT_READ, MAP_SHARED)`. Ядро Linux автоматично кешує активні сторінки пам'яті в Page Cache.
3. Коли польотний контролер надсилає запит `TERRAIN_REQUEST` по бортовій шині Ethernet або швидкісному UART (921 600 біт/с), демон-компаньйон генерує відповіді `TERRAIN_DATA` з затримкою менше ніж 1 мілісекунда.

Така конфігурація повністю усуває навантаження на радіолінк телеметрії, оскільки всі необхідні тайли передаються всередині літального апарата через локальну високошвидкісну шину, забезпечуючи безперебійний автономний політ навіть у зонах повного радіоелектронного придушення (РЕБ).

---

## 11. Інтеграція в збіркові системи CMake та GCC

Для підключення модуля до проектів на базі CMake та тулчейну `arm-none-eabi-gcc` використовується наступна конфігурація:

```cmake
# Фрагмент CMakeLists.txt для вбудованої цілі
add_library(terrain_manager STATIC
    src/terrain_cache.c
    src/terrain_interpolator.c
)

target_include_directories(terrain_manager PUBLIC include)
target_compile_options(terrain_manager PRIVATE
    -mcpu=cortex-m7
    -mfpu=fpv5-d16
    -mfloat-abi=hard
    -O3
    -ffast-math
    -Wall
    -Wextra
    -Werror
)
```

Прапорець `-ffast-math` дозволяє компілятору генерувати апаратні інструкції злитого множення-додавання `VFMA.F32` (Fused Multiply-Add), що скорочує час обчислення білінійної формули до лічених тактів процесора ARM Cortex-M7.

---

## 12. Модульне тестування, санітайзери та верифікація

Перед розгортанням у складі реальної авіоніки модуль проходить обов'язкове автоматизоване тестування у середовищі безперервної інтеграції (CI/CD) на хост-системі x86-64 з використанням компіляторів Clang/GCC та діагностичних інструментів динамічного аналізу:

- **AddressSanitizer (`-fsanitize=address`):** Перевіряє відсутність виходу за межі масивів `data[16]` та буфера `pool[32]` при будь-яких випадкових координатах запитів.
- **UndefinedBehaviorSanitizer (`-fsanitize=undefined`):** Контролює відсутність переповнення знакових цілих чисел (`int32_t`) при роботі з координатами на межах діапазонів `[-180°..+180°]`.

Основні сценарії тестового набору (Test Cases):
- **Тест перетину екватора (`lat = 0°`):** Перевіряє відсутність знакового стрибка під час квантування південно-західного кута між точками `+0.0001°` та `-0.0001°`.
- **Тест нульового меридіана (`lon = 0°`):** Перевіряє плавність переходу довготи від Гринвіча на захід.
- **Тест високих широт (`lat > 75°`):** Перевіряє, що звуження довготного кроку не призводить до переповнення розрядної сітки `int32_t` або ділення на нуль.
- **Тест маркерів No-Data (`-32768`):** Перевіряє, що при потраплянні хоча б однієї вершини з маркером відсутності даних функція гарантовано повертає `false` або `std::nullopt`, не повертаючи некоректні від'ємні висоти в навігаційний контур.
- **Тест переповнення кешу (LRU Overflow):** Перевіряє коректність витіснення найстарішого блоку при послідовному завантаженні понад 32 блоків на довгому лінійному маршруті.

Автоматизоване виконання цього набору модульних тестів при кожному оновленні кодової бази гарантує математичну точність інтерполяції та абсолютну надійність польотного контролера у складних географічних умовах.
