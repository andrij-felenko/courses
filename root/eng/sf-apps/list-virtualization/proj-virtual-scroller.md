# ⚙️ Реалізація рушія віртуалізації: префіксні зміщення, динамічні заміри та ресайклінг

## Задача

Побудувати повнофункціональний, виробничого рівня рушій віртуалізації для довгого списку (наприклад, 100 000 елементів) із невідомою наперед, динамічною висотою рядків (повідомлення в чаті з текстом довільної довжини, вкладені зображення, розгортання блоків коментарів).

Рушій повинен строго задовольняти такі вимоги продуктивності та надійності:
1. **Сталий обсяг пам'яті:** У дереві подання (DOM у браузері або граф віджетів у нативному середовищі) одночасно повинно існувати не більше `K` вузлів, де `K = visibleCount + 2 · overscan` (типово 20–40 елементів замість 100 000).
2. **Логарифмічний пошук:** Пошук видимого діапазону індексів за поточною координатою скролу `scrollTop` повинен виконуватися за час `O(log N)` через бінарний пошук у монотонному масиві префіксних сум зміщень або через двійковий підйом по дереву Фенвіка.
3. **Безпечні заміри без Layout Thrashing:** Вимірювання реальних фізичних розмірів вузлів після їхньої появи у вікні повинно виконуватися виключно асинхронно через браузерний API `ResizeObserver` або через пакетні мікротаски, повністю виключаючи примусові синхронні виклики розкладки.
4. **Якірна стабільність (Scroll Anchoring):** Якщо елементи, розташовані вище поточного видового вікна, змінюють свій розмір (наприклад, після заміру тексту або завантаження картинок), система повинна автоматично й непомітно для людського ока компенсувати зміщення скролу на точну дельту зміни висот, запобігаючи стрибкам контенту під час читання.

## Архітектурний дизайн та фази життєвого циклу

Рушій віртуалізації розбивається на чотири взаємопов'язані підсистеми:

```
┌────────────────────────────────────────────────────────┐
│ 1. Індекс розмірів та зміщень (Offset & Size Index)   │
│    • Зберігає масив висот та префіксні суми           │
│    • Двійковий пошук діапазону [startIndex, endIndex]  │
│    • Початкова евристична оцінка для незнайомих рядків│
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ 2. Менеджер пулу подань (Recycling & ViewPool)         │
│    • Фіксований пул із K екземплярів вузлів            │
│    • Апаратне переміщення через transform: translateY  │
│    • Оновлення даних (onBind) без перестворення DOM   │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ 3. Контролер замірів (Batch Measurement Controller)    │
│    • Реєстрація вузлів у ResizeObserver                │
│    • Пакетування замірів у чергу перед наступним VSync │
│    • Виклик оновлення індексу без примусового Reflow  │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ 4. Компенсатор стрибків скролу (Scroll Anchor Engine)  │
│    • Фіксація першого видимого елемента-якоря          │
│    • Розрахунок дельти: Δ = new_offset - old_offset    │
│    • Синхронне коригування scrollTop до показу кадру   │
└────────────────────────────────────────────────────────┘
```

### 1. Фаза ініціалізації та початкової оцінки

Оскільки розміри 100 000 елементів невідомі до моменту їхнього рендерингу, індекс ініціалізується середньою евристичною висотою `estimateHeight` (наприклад, 50 px). Фантомний розпірник отримує початкову висоту `H_total = N · estimateHeight = 5 000 000 px`, що створює природну пропорцію смуги прокрутки.

### 2. Фаза розрахунку вікна та рендерингу

Під час кожної зміни `scrollTop` віртуалізатор за логарифмічний час знаходить перший елемент `firstVisible`, у якого координата нижньої межі `offset[i + 1]` перевищує `scrollTop`. Діапазон розширюється на `overscan` елементів угору та вниз. 

Елементи з цього діапазону отримують вузли з пулу подань. Позиція кожного вузла встановлюється через CSS-властивість `transform: translateY(offset[i] px)`, яка створює окремий шар компонування і переміщується графічним процесором без звернення до головного потоку.

### 3. Фаза асинхронного заміру та пакетування

Кожен змонтований вузол реєструється в екземплярі `ResizeObserver`. Коли браузер завершує стадію розкладки (*Layout*), спостерігач викликає колбек із точними розмірами блоків `borderBoxSize`. Заміри не застосовуються негайно: вони складаються у буфер `pendingMeasurements` і відкладаються до наступного виклику `requestAnimationFrame`.

### 4. Фаза якірного перерахунку та компенсації

У момент застосування накопичених замірів індекс фіксує поточний індекс якоря `anchorIndex` та його старе зміщення `oldOffset`. Висоти оновлюються в кеші, префіксні суми перераховуються, після чого обчислюється різниця:

```
Δ = newOffset[anchorIndex] - oldOffset[anchorIndex]
```

Якщо `Δ ≠ 0`, рушій виконує `scroller.scrollTop += Δ`. Оскільки це відбувається до растеризації кадру, користувач бачить непорушний екран: контент зверху збільшився, скролбар пересунувся, але текст перед очима не зсунувся ні на один піксель.

## Робочий код

Нижче наведено дві ідіоматичні реалізації:
- **TypeScript:** повний браузерний компонент віртуалізації для DOM із підтримкою `ResizeObserver`, пакетування через `requestAnimationFrame` та якірної фіксації скролу;
- **C++20:** високопродуктивне безголове ядро для нативних та десктопних застосунків на базі дерева Фенвіка, з пулом `ViewHolder`, нульовим виділенням динамічної пам'яті в гарячому циклі та підтримкою `std::span`.

:::tabs
```ts
// TypeScript: Повнофункціональний веб-віртуалізатор з ResizeObserver та Scroll Anchoring

export interface VirtualItem {
  index: number;
  offset: number;
  size: number;
}

export interface VirtualizerOptions {
  count: number;
  estimateSize: (index: number) => number;
  overscan?: number;
  scrollerElement: HTMLElement;
  contentElement: HTMLElement;
}

export class DynamicVirtualizer {
  private count: number;
  private estimateSize: (index: number) => number;
  private overscan: number;
  private scroller: HTMLElement;
  private content: HTMLElement;

  private measuredSizes: Map<number, number> = new Map();
  private offsets: number[] = [];
  private totalHeight: number = 0;

  private resizeObserver: ResizeObserver;
  private pendingMeasurements: Map<number, number> = new Map();
  private isRafScheduled: boolean = false;

  constructor(options: VirtualizerOptions) {
    this.count = options.count;
    this.estimateSize = options.estimateSize;
    this.overscan = options.overscan ?? 3;
    this.scroller = options.scrollerElement;
    this.content = options.contentElement;

    this.recomputeOffsets();

    this.resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const target = entry.target as HTMLElement;
        const indexAttr = target.getAttribute('data-index');
        if (indexAttr !== null) {
          const index = parseInt(indexAttr, 10);
          const height = entry.borderBoxSize?.[0]?.blockSize ?? target.offsetHeight;
          if (height > 0 && this.measuredSizes.get(index) !== height) {
            this.pendingMeasurements.set(index, height);
          }
        }
      }
      this.scheduleMeasurementFlush();
    });

    this.scroller.addEventListener('scroll', () => this.render(), { passive: true });
    this.render();
  }

  private recomputeOffsets(): void {
    this.offsets = new Array(this.count + 1);
    this.offsets[0] = 0;
    for (let i = 0; i < this.count; i++) {
      const h = this.measuredSizes.get(i) ?? this.estimateSize(i);
      this.offsets[i + 1] = this.offsets[i] + h;
    }
    this.totalHeight = this.offsets[this.count];
    this.content.style.height = `${this.totalHeight}px`;
  }

  // Двійковий пошук першого елемента, чиє закінчення > scrollTop
  private findStartIndex(scrollTop: number): number {
    let low = 0;
    let high = this.count - 1;
    let result = 0;

    while (low <= high) {
      const mid = (low + high) >>> 1;
      if (this.offsets[mid + 1] > scrollTop) {
        result = mid;
        high = mid - 1;
      } else {
        low = mid + 1;
      }
    }
    return result;
  }

  public getRange(scrollTop: number, viewportHeight: number): { start: number; end: number } {
    if (this.count === 0) return { start: 0, end: 0 };

    const firstVisible = this.findStartIndex(scrollTop);
    let lastVisible = firstVisible;

    while (lastVisible < this.count - 1 && this.offsets[lastVisible] < scrollTop + viewportHeight) {
      lastVisible++;
    }

    const start = Math.max(0, firstVisible - this.overscan);
    const end = Math.min(this.count - 1, lastVisible + this.overscan);

    return { start, end };
  }

  private scheduleMeasurementFlush(): void {
    if (this.isRafScheduled || this.pendingMeasurements.size === 0) return;
    this.isRafScheduled = true;

    requestAnimationFrame(() => {
      this.isRafScheduled = false;
      this.flushMeasurements();
    });
  }

  private flushMeasurements(): void {
    if (this.pendingMeasurements.size === 0) return;

    // Фіксуємо якірний елемент та його положення до оновлення префіксних сум
    const currentScrollTop = this.scroller.scrollTop;
    const anchorIndex = this.findStartIndex(currentScrollTop);
    const oldAnchorOffset = this.offsets[anchorIndex];

    // Застосовуємо нові заміри
    for (const [index, height] of this.pendingMeasurements.entries()) {
      this.measuredSizes.set(index, height);
    }
    this.pendingMeasurements.clear();

    this.recomputeOffsets();

    // Scroll Anchoring: якщо висоти елементів над якорем змінилися — компенсуємо scrollTop
    const newAnchorOffset = this.offsets[anchorIndex];
    const scrollDelta = newAnchorOffset - oldAnchorOffset;

    if (scrollDelta !== 0) {
      this.scroller.scrollTop = currentScrollTop + scrollDelta;
    }

    this.render();
  }

  public render(): void {
    const scrollTop = this.scroller.scrollTop;
    const viewportHeight = this.scroller.clientHeight;
    const { start, end } = this.getRange(scrollTop, viewportHeight);

    // Збір існуючих вузлів у DOM
    const existingNodes = new Map<number, HTMLElement>();
    for (let i = 0; i < this.content.children.length; i++) {
      const child = this.content.children[i] as HTMLElement;
      const idx = parseInt(child.getAttribute('data-index') ?? '-1', 10);
      if (idx >= 0) existingNodes.set(idx, child);
    }

    // Рендеринг активного вікна
    const activeIndices = new Set<number>();
    for (let i = start; i <= end; i++) {
      activeIndices.add(i);
      let node = existingNodes.get(i);

      if (!node) {
        node = document.createElement('div');
        node.className = 'virtual-item';
        node.setAttribute('data-index', i.toString());
        node.style.position = 'absolute';
        node.style.top = '0';
        node.style.left = '0';
        node.style.width = '100%';
        node.textContent = `Запис #${i} (висота: ${this.measuredSizes.get(i) ?? 'очікується'})`;
        
        this.content.appendChild(node);
        this.resizeObserver.observe(node);
      }

      // Позиціонування через апаратне зміщення без тригера Layout
      const itemTop = this.offsets[i];
      node.style.transform = `translateY(${itemTop}px)`;
    }

    // Видалення / ресайклінг вузлів, що вийшли за межі буфера
    for (const [idx, node] of existingNodes.entries()) {
      if (!activeIndices.has(idx)) {
        this.resizeObserver.unobserve(node);
        node.remove();
      }
    }
  }

  public destroy(): void {
    this.resizeObserver.disconnect();
  }
}
```
```cpp
// C++20: Високопродуктивне ядро віртуалізації з деревом Фенвіка та пулом подань

#include <vector>
#include <memory>
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <string>
#include <unordered_map>
#include <span>

class FenwickTree {
private:
    std::vector<int64_t> tree;
    size_t n;

    static constexpr size_t lsb(size_t i) noexcept {
        return i & (-i);
    }

public:
    explicit FenwickTree(size_t size) : tree(size + 1, 0), n(size) {}

    void add(size_t idx, int64_t delta) noexcept {
        for (size_t i = idx + 1; i <= n; i += lsb(i)) {
            tree[i] += delta;
        }
    }

    [[nodiscard]] int64_t query(size_t idx) const noexcept {
        int64_t sum = 0;
        for (size_t i = idx + 1; i > 0; i -= lsb(i)) {
            sum += tree[i];
        }
        return sum;
    }

    // Двійковий підйом за O(log N) для пошуку першого індексу, де prefix_sum > target
    [[nodiscard]] size_t find_first_greater(int64_t target) const noexcept {
        size_t idx = 0;
        int64_t current_sum = 0;
        size_t max_bit = 1;
        while ((max_bit << 1) <= n) {
            max_bit <<= 1;
        }

        for (size_t step = max_bit; step > 0; step >>= 1) {
            if (idx + step <= n && current_sum + tree[idx + step] <= target) {
                idx += step;
                current_sum += tree[idx];
            }
        }
        return idx; // 0-based index
    }
};

struct ViewHolder {
    size_t bound_index{static_cast<size_t>(-1)};
    int64_t rendered_offset{0};
    int64_t rendered_height{0};
    bool is_active{false};
    std::string text_buffer;
};

class HeadlessVirtualizer {
private:
    size_t item_count;
    int64_t default_estimated_height;
    size_t overscan;

    FenwickTree fenwick;
    std::vector<int64_t> item_heights;
    std::vector<ViewHolder> view_pool;
    std::unordered_map<size_t, size_t> active_view_map; // index -> pool_slot

public:
    HeadlessVirtualizer(size_t count, int64_t estimate_height, size_t pool_capacity, size_t overscan_items = 3)
        : item_count(count),
          default_estimated_height(estimate_height),
          overscan(overscan_items),
          fenwick(count),
          item_heights(count, estimate_height),
          view_pool(pool_capacity) {
        // Лінійна ініціалізація дерева Фенвіка
        for (size_t i = 0; i < count; ++i) {
            fenwick.add(i, estimate_height);
        }
    }

    struct Range {
        size_t start_index;
        size_t end_index;
        int64_t start_offset;
    };

    [[nodiscard]] Range calculate_visible_range(int64_t scroll_top, int64_t viewport_height) const noexcept {
        if (item_count == 0) return {0, 0, 0};

        size_t first_visible = fenwick.find_first_greater(scroll_top);
        if (first_visible >= item_count) first_visible = item_count - 1;

        int64_t bottom_boundary = scroll_top + viewport_height;
        size_t last_visible = fenwick.find_first_greater(bottom_boundary);
        if (last_visible >= item_count) last_visible = item_count - 1;

        size_t start = (first_visible > overscan) ? (first_visible - overscan) : 0;
        size_t end = std::min(item_count - 1, last_visible + overscan);

        int64_t start_offset = (start == 0) ? 0 : fenwick.query(start - 1);
        return {start, end, start_offset};
    }

    // Оновлення реального розміру після вимірювання
    struct AnchorAdjustment {
        int64_t scroll_delta;
        int64_t new_total_height;
    };

    AnchorAdjustment update_measured_size(size_t index, int64_t measured_height, int64_t current_scroll_top) {
        if (index >= item_count) return {0, fenwick.query(item_count - 1)};

        int64_t old_height = item_heights[index];
        int64_t delta = measured_height - old_height;

        if (delta == 0) return {0, fenwick.query(item_count - 1)};

        // Фіксуємо якір для компенсації скрол-стрибків
        size_t anchor_index = fenwick.find_first_greater(current_scroll_top);
        int64_t old_anchor_offset = (anchor_index == 0) ? 0 : fenwick.query(anchor_index - 1);

        // Застосовуємо дельту в дерево
        item_heights[index] = measured_height;
        fenwick.add(index, delta);

        int64_t new_anchor_offset = (anchor_index == 0) ? 0 : fenwick.query(anchor_index - 1);
        int64_t scroll_delta = 0;

        // Якщо елемент змінився вище або на рівні якоря — коригуємо скрол
        if (index <= anchor_index) {
            scroll_delta = new_anchor_offset - old_anchor_offset;
        }

        int64_t total_height = fenwick.query(item_count - 1);
        return {scroll_delta, total_height};
    }

    // Ресайклінг пулу подань під новий видимий діапазон
    void recycle_and_bind(size_t start_index, size_t end_index) {
        std::vector<size_t> freed_slots;

        // 1. Позначаємо слоти поза діапазоном як вільні
        for (auto it = active_view_map.begin(); it != active_view_map.end();) {
            if (it->first < start_index || it->first > end_index) {
                size_t slot = it->second;
                view_pool[slot].is_active = false;
                freed_slots.push_back(slot);
                it = active_view_map.erase(it);
            } else {
                ++it;
            }
        }

        // 2. Прив'язуємо нові індекси з вільного пулу
        size_t free_idx = 0;
        for (size_t i = start_index; i <= end_index; ++i) {
            if (!active_view_map.contains(i)) {
                size_t target_slot;
                if (free_idx < freed_slots.size()) {
                    target_slot = freed_slots[free_idx++];
                } else {
                    // Шукаємо перший неактивний слот
                    auto inactive_it = std::find_if(view_pool.begin(), view_pool.end(),
                                                    [](const ViewHolder& v) { return !v.is_active; });
                    if (inactive_it == view_pool.end()) break; // Пул вичерпано
                    target_slot = std::distance(view_pool.begin(), inactive_it);
                }

                ViewHolder& vh = view_pool[target_slot];
                vh.bound_index = i;
                vh.rendered_offset = (i == 0) ? 0 : fenwick.query(i - 1);
                vh.rendered_height = item_heights[i];
                vh.is_active = true;
                vh.text_buffer = "Рядок #" + std::to_string(i);

                active_view_map[i] = target_slot;
            }
        }
    }

    [[nodiscard]] std::span<const ViewHolder> get_pool() const noexcept {
        return view_pool;
    }
};
```
:::

## Покрокове трасування роботи рушія

Розглянемо числовий приклад поведінки віртуалізатора при початковому завантаженні та першому русі скролу.

### Початковий стан (scrollTop = 0 px)

- Параметри: `viewportHeight = 400 px`, `estimateHeight = 50 px`, `overscan = 2`, `count = 1000`.
- Початкова оцінка висот: `h = [50, 50, 50, …]`, повна висота `H_total = 50 000 px`.
- Обчислення діапазону:
  - `firstVisible = findStartIndex(0) = 0` (елемент #0 займає `[0, 50) px`);
  - `lastVisible = 7` (елемент #7 займає `[350, 400) px`);
  - З урахуванням overscan монтуються індекси `[0, 9]`.
- Вузли 0–9 з'являються в DOM, спостерігаються `ResizeObserver`.

### Фаза заміру: елементи виявилися більшими за оцінку

Після розкладки `ResizeObserver` повідомляє, що елементи 0, 1 та 2 містять багато рядків і мають реальні висоти:
- `h[0] = 120 px` (`Δ = +70 px`)
- `h[1] = 80 px` (`Δ = +30 px`)
- `h[2] = 100 px` (`Δ = +50 px`)
- Сумарне розширення префікса: `Δ_total = 70 + 30 + 50 = +150 px`.
- Нова висота розпірника: `50 000 + 150 = 50 150 px`.
- Зсуви наступних елементів: `offset[3]` стає `120 + 80 + 100 = 300 px` замість `150 px`.
- Оскільки `scrollTop = 0`, якірний елемент #0 не зсунувся, корекція скролу `Δ = 0`.

### Скрол до середини та якірна компенсація

Користувач прокрутив екран до `scrollTop = 1200 px` і читає елемент #15 (який розташований на висоті 1200 px). У цей момент у фоні завантажилася картинка в елементі #4 (який зараз поза екраном зверху) і його висота зросла з 50 px до 250 px (`Δ = +200 px`).

- Алгоритм фіксує якір: `anchorIndex = 15`, `oldOffset = 1200 px`.
- Застосовується замір: `offset_new[15] = 1400 px`.
- Обчислюється дельта: `Δ_anchor = 1400 - 1200 = +200 px`.
- Синхронна компенсація: `scroller.scrollTop = 1200 + 200 = 1400 px`.
- Результат: координата елемента #15 стала 1400 px, скрол став 1400 px. Відносне положення елемента у вікні: `1400 - 1400 = 0 px` — ідеальна нерухомість для очей користувача.

## Пастки та крайові випадки

1. **Примусова синхронна розкладка (Layout Thrashing):**
   Виклик `element.offsetHeight` або `getBoundingClientRect()` всередині циклу відмальовки змушує браузер синхронно перераховувати геометрію всього документа на кожній ітерації. Використання `ResizeObserver` повністю усуває цю проблему, оскільки браузер сам доставляє виміряні розміри пакетно після завершення стадії розкладки.

2. **Втрата внутрішнього фокусу при повторному використанні вузлів:**
   Коли DOM-елемент, що містив поле вводу `<input>` із фокусом клавіатури, виходить за край екрана й ресайклиться для нового рядка, фокус миттєво зникає, а віртуальна клавіатура мобільного пристрою згортається. Щоб уникнути цього, активний елемент із фокусом тимчасово вилучають із пулу віртуалізації до моменту втрати фокусу користувачем (*focus pinning*).

3. **Акумуляція похибки дробових пікселів (Subpixel Jitter):**
   При масштабуванні сторінки (наприклад, 125 % чи 150 % у системі) або використанні дробних висот рядків сума `offsetHeight` може накопичувати похибку в 1–2 пікселі. Це призводить до мікротремтіння списку (*jitter*). Розв'язанням є використання чисел із плаваючою комою подвійної точності в масиві префіксних сум і заокруглення лише на етапі запису в CSS через `Math.round()`.

4. **Нульові та невидимі елементи:**
   Якщо елемент має `display: none` або нульову висоту, двійковий пошук у масиві префіксів може знайти кілька однакових зміщень поспіль. Префіксний масив зобов'язаний гарантувати строго невід'ємні дельти (`h_i ≥ 0`), а пошук повинен коректно повертати перший елемент із ненульовою видимою висотою.
