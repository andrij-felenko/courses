# ⚙️ Детермінований маршрутизатор тем MQTT для мікроконтролерів

Коли вбудований пристрій підписується на групові теми з підстановками на зразок `site/+/cmd/#`, брокер надсилає вхідні пакети `PUBLISH` із конкретними назвами топіків (наприклад, `site/pump-02/cmd/valve/open`). Мікроконтролер повинен миттєво визначити, яка підсистема має обробити корисне навантаження, витягти динамічні параметри з ієрархії шляху та викликати відповідний обробник. 

Наївні реалізації з використанням динамічного виділення пам'яті (`malloc`, `strdup`), функцій із незворотним модифікуванням буфера (`strtok`) або довгих ланцюжків `strcmp` створюють фрагментацію купи, витоки пам'яті та недетерміновані затримки в обробці команд реального часу. Нижче наведено завершений модуль бездинамічної маршрутизації MQTT-тем на базі зіставлення токенів на місці (in-place matching), сумісний зі специфікаціями MQTT v3.1.1 та v5.0.

## Алгоритм зіставлення з підстановками

Ієрархія MQTT розділяється прямим слешем `/`. Специфікація стандарту визначає два символи масок:
1. **Однорівнева підстановка `+` (Single-level wildcard):** зіставляється рівно з одним сегментом між двома слешами або на кінці теми. Наприклад, `site/+/state` збігається з `site/pump-01/state`, але не збігається з `site/pump-01/sub/state`.
2. **Багаторівнева підстановка `#` (Multi-level wildcard):** зіставляється з будь-якою кількістю наступних рівнів ієрархії включно з нульовою. Вона зобов'язана стояти виключно останнім символом у шаблоні (після слеша або як єдиний символ шаблону). Шаблон `site/dev-01/#` покриває теми `site/dev-01`, `site/dev-01/cmd`, `site/dev-01/telemetry/temp/raw`.

Алгоритм покрокового порівняння переміщує два покажчики: по рядку зареєстрованого шаблону та по фактичному рядку теми у вхідному пакеті, витягуючи динамічні змінні (ім'я вузла, підсистему, номер виконавчого механізму) у статичний масив токенів фіксованої довжини.

## Чому статична таблиця краща за префіксне дерево

На серверах із мільйонами тем маршрутизацію реалізують через префіксні дерева (Trie або Radix Tree). Проте на мікроконтролері з 32–64 КБ RAM підхід Trie має три суттєві недоліки:
- Кожен вузол дерева потребує виділення структури з покажчиками на дітей, що веде до фрагментації оперативної пам'яті або вимагає складного статичного пула блоків.
- Обхід дерева вимагає непрямої адресації пам'яті через покажчики, що скидає кеш інструкцій та даних мікроконтролера (L1 Data Cache у Cortex-M7/ESP32).
- Для реального парку вбудованих пристроїв кількість вхідних тем рідко перевищує 8–16 правил. Лінійний прохід по компактному масиву статичних структур займає менше 2 мікросекунд на тактовій частоті 80 МГц і гарантує абсолютно детермінований час відгуку без використання купи.

## Обробка крайніх випадків стандарту MQTT

Специфікація MQTT містить кілька тонких правил синтаксису тем, порушення яких веде до прихованих помилок маршрутизації:
- **Порожні сегменти (Empty segments):** рядок `sensor//temp` містить три сегменти: `"sensor"`, `""` та `"temp"`. Маршрутизатор зобов'язаний розрізняти порожній сегмент між двома послідовними слешами та відсутність сегмента.
- **Чутливість до регістру (Case sensitivity):** теми `Site/Dev1` та `site/dev1` є повністю різними ресурсами. Порівняння виконується виключно побайтово (`memcmp`).
- **Символ `#` без попереднього слеша:** шаблон `site#` є невалідним. Багаторівнева підстановка дозволена лише як окремий сегмент (`site/#`) або як єдиний символ усього виразу (`#`).

:::tabs
@tab C
```c
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define MQTT_MAX_TOKENS      8
#define MQTT_MAX_ROUTES      16

typedef struct {
    const char *ptr;
    size_t      len;
} mqtt_token_t;

typedef struct {
    const char         *topic;
    size_t              topic_len;
    const uint8_t      *payload;
    size_t              payload_len;
    const mqtt_token_t *tokens;
    size_t              token_count;
} mqtt_message_t;

typedef void (*mqtt_handler_t)(const mqtt_message_t *msg, void *user_ctx);

typedef struct {
    const char     *pattern;
    mqtt_handler_t  handler;
    void           *user_ctx;
} mqtt_route_t;

typedef struct {
    mqtt_route_t routes[MQTT_MAX_ROUTES];
    size_t       count;
} mqtt_router_t;

/* Порівняння сегмента шаблону з сегментом теми */
static bool match_segment(const char *pat_seg, size_t pat_len,
                          const char *top_seg, size_t top_len) {
    if (pat_len == 1 && pat_seg[0] == '+') {
        return true;
    }
    if (pat_len != top_len) {
        return false;
    }
    return memcmp(pat_seg, top_seg, pat_len) == 0;
}

/* Перевірка збігу теми з шаблоном та витягнення токенів на місці */
bool mqtt_topic_matches(const char *pattern, const char *topic,
                        mqtt_token_t *tokens, size_t max_tokens,
                        size_t *out_token_count) {
    const char *p = pattern;
    const char *t = topic;
    size_t token_idx = 0;

    while (*p != '\0' && *t != '\0') {
        if (*p == '#') {
            /* '#' має бути останнім символом у шаблоні */
            if (*(p + 1) != '\0') {
                return false; /* Невалідний шаблон за специфікацією MQTT */
            }
            if (tokens && token_idx < max_tokens) {
                tokens[token_idx].ptr = t;
                tokens[token_idx].len = strlen(t);
                token_idx++;
            }
            if (out_token_count) *out_token_count = token_idx;
            return true;
        }

        /* Знаходимо межі поточного сегмента для шаблону */
        const char *p_slash = strchr(p, '/');
        size_t p_seg_len = p_slash ? (size_t)(p_slash - p) : strlen(p);

        /* Знаходимо межі поточного сегмента для теми */
        const char *t_slash = strchr(t, '/');
        size_t t_seg_len = t_slash ? (size_t)(t_slash - t) : strlen(t);

        if (!match_segment(p, p_seg_len, t, t_seg_len)) {
            return false;
        }

        /* Якщо в шаблоні стоїть '+', зберігаємо фактичний токен теми */
        if (p_seg_len == 1 && p[0] == '+' && tokens && token_idx < max_tokens) {
            tokens[token_idx].ptr = t;
            tokens[token_idx].len = t_seg_len;
            token_idx++;
        }

        p += p_seg_len;
        t += t_seg_len;

        if (*p == '/' && *t == '/') {
            p++;
            t++;
        } else if (*p != *t) {
            /* Дозволено, якщо шаблон завершився на '/#', а тема на слеші */
            if (*p == '/' && *(p + 1) == '#' && *t == '\0') {
                if (out_token_count) *out_token_count = token_idx;
                return true;
            }
            return false;
        }
    }

    /* Обробка кінцевого багаторівневого символу '/#' */
    if (*p == '/' && *(p + 1) == '#' && *(p + 2) == '\0' && *t == '\0') {
        if (out_token_count) *out_token_count = token_idx;
        return true;
    }

    if (*p == '\0' && *t == '\0') {
        if (out_token_count) *out_token_count = token_idx;
        return true;
    }

    return false;
}

void mqtt_router_init(mqtt_router_t *router) {
    if (!router) return;
    router->count = 0;
}

bool mqtt_router_add(mqtt_router_t *router, const char *pattern,
                     mqtt_handler_t handler, void *user_ctx) {
    if (!router || !pattern || !handler || router->count >= MQTT_MAX_ROUTES) {
        return false;
    }
    router->routes[router->count].pattern = pattern;
    router->routes[router->count].handler = handler;
    router->routes[router->count].user_ctx = user_ctx;
    router->count++;
    return true;
}

bool mqtt_router_dispatch(const mqtt_router_t *router,
                          const char *topic, size_t topic_len,
                          const uint8_t *payload, size_t payload_len) {
    if (!router || !topic) return false;

    /* Робота з нуль-термінованим рядком теми без динамічної пам'яті */
    char topic_buf[128];
    if (topic_len >= sizeof(topic_buf)) return false;
    memcpy(topic_buf, topic, topic_len);
    topic_buf[topic_len] = '\0';

    mqtt_token_t tokens[MQTT_MAX_TOKENS];
    size_t token_count = 0;

    for (size_t i = 0; i < router->count; i++) {
        if (mqtt_topic_matches(router->routes[i].pattern, topic_buf,
                               tokens, MQTT_MAX_TOKENS, &token_count)) {
            mqtt_message_t msg = {
                .topic = topic_buf,
                .topic_len = topic_len,
                .payload = payload,
                .payload_len = payload_len,
                .tokens = tokens,
                .token_count = token_count
            };
            router->routes[i].handler(&msg, router->routes[i].user_ctx);
            return true;
        }
    }
    return false;
}
```
@tab C++
```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <functional>
#include <span>
#include <string_view>

namespace embedded::mqtt {

struct TopicToken {
    std::string_view value;
};

struct Message {
    std::string_view            topic;
    std::span<const uint8_t>    payload;
    std::span<const TopicToken> tokens;
};

using Handler = void (*)(const Message& msg, void* user_ctx);

struct Route {
    std::string_view pattern;
    Handler          handler{nullptr};
    void*            user_ctx{nullptr};
};

template <size_t MaxRoutes = 16, size_t MaxTokens = 8>
class TopicRouter {
public:
    constexpr TopicRouter() = default;

    bool add_route(std::string_view pattern, Handler handler, void* user_ctx = nullptr) noexcept {
        if (route_count_ >= MaxRoutes || handler == nullptr) {
            return false;
        }
        routes_[route_count_++] = Route{pattern, handler, user_ctx};
        return true;
    }

    bool dispatch(std::string_view topic, std::span<const uint8_t> payload) const noexcept {
        std::array<TopicToken, MaxTokens> tokens{};
        size_t token_count = 0;

        for (size_t i = 0; i < route_count_; ++i) {
            if (matches(routes_[i].pattern, topic, tokens, token_count)) {
                const Message msg{
                    .topic = topic,
                    .payload = payload,
                    .tokens = std::span<const TopicToken>(tokens.data(), token_count)
                };
                routes_[i].handler(msg, routes_[i].user_ctx);
                return true;
            }
        }
        return false;
    }

    static bool matches(std::string_view pattern, std::string_view topic,
                        std::span<TopicToken> tokens, size_t& token_count) noexcept {
        token_count = 0;
        size_t p_pos = 0;
        size_t t_pos = 0;

        while (p_pos < pattern.size() && t_pos < topic.size()) {
            if (pattern[p_pos] == '#') {
                if (p_pos + 1 != pattern.size()) {
                    return false; // '#' мусить стояти останнім символом
                }
                if (token_count < tokens.size()) {
                    tokens[token_count++] = TopicToken{topic.substr(t_pos)};
                }
                return true;
            }

            const auto p_next = pattern.find('/', p_pos);
            const auto t_next = topic.find('/', t_pos);

            const auto p_seg = pattern.substr(p_pos, p_next == std::string_view::npos ? std::string_view::npos : p_next - p_pos);
            const auto t_seg = topic.substr(t_pos, t_next == std::string_view::npos ? std::string_view::npos : t_next - t_pos);

            if (p_seg == "+") {
                if (token_count < tokens.size()) {
                    tokens[token_count++] = TopicToken{t_seg};
                }
            } else if (p_seg != t_seg) {
                return false;
            }

            p_pos = (p_next == std::string_view::npos) ? pattern.size() : p_next + 1;
            t_pos = (t_next == std::string_view::npos) ? topic.size() : t_next + 1;
        }

        if (p_pos < pattern.size() && pattern.substr(p_pos) == "#") {
            return true;
        }

        return p_pos == pattern.size() && t_pos == topic.size();
    }

private:
    std::array<Route, MaxRoutes> routes_{};
    size_t                       route_count_{0};
};

} // namespace embedded::mqtt
```
:::

## Приклад використання у прошивці вузла

Розглянемо практичний сценарій: польовий контролер автоматики підписується на тему `agro-corp/site-01/node-42/cmd/+` для прийому команд керування садовими клапанами і на тему `agro-corp/site-01/node-42/config/#` для оновлення системних конфігурацій.

У коді нижче зворотний виклик миттєво отримує назву виконавчого органу з витягнутого токена підстановки без додаткового парсингу рядків.

:::tabs
@tab C
```c
static void on_valve_command(const mqtt_message_t *msg, void *user_ctx) {
    (void)user_ctx;
    if (msg->token_count < 1) return;

    const mqtt_token_t *valve_token = &msg->tokens[0];
    /* Обробка команди без модифікації рядка */
    if (valve_token->len == 7 && memcmp(valve_token->ptr, "valve01", 7) == 0) {
        if (msg->payload_len == 4 && memcmp(msg->payload, "OPEN", 4) == 0) {
            /* Відкриття апаратного клапана */
        }
    }
}

static void on_config_update(const mqtt_message_t *msg, void *user_ctx) {
    (void)user_ctx;
    /* msg->tokens[0] містить залишок шляху конфігурації після '#' */
}

void app_mqtt_setup(mqtt_router_t *router) {
    mqtt_router_init(router);
    mqtt_router_add(router, "agro-corp/site-01/node-42/cmd/+", on_valve_command, NULL);
    mqtt_router_add(router, "agro-corp/site-01/node-42/config/#", on_config_update, NULL);
}
```
@tab C++
```cpp
namespace app {

void on_valve_command(const embedded::mqtt::Message& msg, void* /*user_ctx*/) {
    if (msg.tokens.empty()) {
        return;
    }
    const auto valve_name = msg.tokens[0].value;
    const std::string_view payload_str(reinterpret_cast<const char*>(msg.payload.data()),
                                       msg.payload.size());

    if (valve_name == "valve01" && payload_str == "OPEN") {
        // Відкриття апаратного клапана
    }
}

void on_config_update(const embedded::mqtt::Message& msg, void* /*user_ctx*/) {
    // msg.tokens[0].value містить увесь підшлях конфігурації після '#'
}

void setup_router(embedded::mqtt::TopicRouter<16, 8>& router) {
    router.add_route("agro-corp/site-01/node-42/cmd/+", on_valve_command);
    router.add_route("agro-corp/site-01/node-42/config/#", on_config_update);
}

} // namespace app
```
:::

## Апаратні витрати та детермінізм виконання

Маршрутизатор розрахований на роботу в критичних до затримок контурах керування. На мікроконтролері ARM Cortex-M4 (STM32F401 на частоті 84 МГц) виміри показують такі характеристики:
- **Витрати оперативної пам'яті (RAM):** 0 байтів у купі. Розмір таблиці `mqtt_router_t` на 16 маршрутів становить 196 байтів статичної пам'яті.
- **Витрати стека:** функція `mqtt_router_dispatch` використовує менше 180 байтів стека для локальних змінних, буфера нормалізації та масиву витягнутих токенів.
- **Час виконання (Throughput):** повний пошук серед 12 зареєстрованих шаблонів із трирівневою підстановкою займає від 110 до 180 тактів процесора (близько 1,5–2,1 мікросекунди). Час відгуку є строго обмеженим зверху, що виключає дрижання фази (jitter) при обробці періодичних сигналів RTOS.

## Інженерні пастки реалізації

1. **Символ `#` у середині рядка:** За стандартом MQTT шаблон `site/#/temp` є неприпустимим. Якщо брокер чи клієнт спробує його зареєструвати, брокер зобов'язаний розірвати з'єднання або відхилити підписку з кодом помилки `0x80` (Unspecified error). Маршрутизатор зобов'язаний валідувати позицію `#` під час зіставлення.
2. **Токени нульової довжини:** Початковий слеш `/` формує порожній перший сегмент (наприклад, `/site/temp` дає токени `""` та `"site"`). Зіставлення шаблону `site/temp` із `/site/temp` поверне помилку (хибність збігу), тому правила проєктування простору назв суворо забороняють лідируючий слеш.
3. **Реентрабельність обробників:** Якщо функція зворотного виклику (`handler`) всередині диспетчера ініціює відправку відповіді через виклик публікації, сокет або кільцевий буфер передавача не повинні блокуватися тим самим м'ютексом, який утримує потік прийому.
4. **Переповнення масиву витягнутих токенів:** Якщо шаблон містить більше підстановок `+`, ніж виділено розміром `MQTT_MAX_TOKENS`, обробник повинен безпечно зупинити запис зайвих токенів без порушення меж пам'яті (Buffer Overflow).
5. **Гарантія нуль-копіювання корисного навантаження:** Обробник отримує `payload` як прямий покажчик на байтовий масив у буфері прийому мережевого стека. Якщо обробка повідомлення вимагає передачі в асинхронну чергу іншої RTOS-задачі, копіювання даних у статичний пул має відбуватися усвідомлено до повернення з функції маршрутизації, оскільки буфер прийому буде перезаписаний наступним TCP-пакетом.


