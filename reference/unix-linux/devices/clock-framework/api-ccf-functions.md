### Основні API-функції CCF для споживачів

Драйвери-споживачі використовують функції з заголовку `<linux/clk.h>`:

*   **`struct clk *clk_get(struct device *dev, const char *id);`**
    Запит тактового сигналу за його іменем (з Device Tree або таблиці).
*   **`void clk_put(struct clk *clk);`**
    Звільнення дескриптора тактового сигналу. У сучасному коді частіше використовують `devm_clk_get()`, яка не потребує ручного виклику `clk_put()`.
*   **`int clk_prepare(struct clk *clk);`**
    Підготовка генератора до роботи (може викликати засинання `sleep`, працює з повільними шинами типу I2C).
*   **`void clk_unprepare(struct clk *clk);`**
    Скасування підготовки (також може засинати).
*   **`int clk_enable(struct clk *clk);`**
    Атомарне увімкнення генератора/ключа (без засинання, використовує `spinlock`).
*   **`void clk_disable(struct clk *clk);`**
    Атомарне вимкнення.
*   **`unsigned long clk_get_rate(struct clk *clk);`**
    Отримання поточної частоти (у герцах).
*   **`int clk_set_rate(struct clk *clk, unsigned long rate);`**
    Спроба встановити нову частоту `rate`. Повертає 0 у разі успіху.
*   **`long clk_round_rate(struct clk *clk, unsigned long rate);`**
    Запит "якщо я попрошу `rate`, яку найближчу частоту ти реально зможеш видати?". Корисно для перевірки можливостей апаратури без фактичної зміни частоти.
*   **`int clk_set_parent(struct clk *clk, struct clk *parent);`**
    Перемикання мультиплексора: вибір нового батьківського джерела для вузла `clk`.
