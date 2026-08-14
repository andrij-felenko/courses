# ⚙️ Реалізація алгоритму RSTP та обробка BPDU мовами C та C++

Програмна реалізація порівняння векторів пріоритетів **BPDU (Bridge Protocol Data Unit)** та кінцевого автомата портів у протоколі **Rapid Spanning Tree Protocol (RSTP / IEEE 802.1w)**. Код демонструє алгоритм вибору найкращого BPDU, визначення ролей портів (Root Port, Designated Port, Alternate Port, Backup Port) та переключення станів (Discarding, Learning, Forwarding).

---

## 1. Алгоритмічний принцип порівняння векторів пріоритету

Серцем протоколу Spanning Tree є математично строго впорядковане порівняння векторів пріоритетів. Кожен комутатор підтримує системну інформацію про поточний найкращий вектор і порівнює з ним кожен новий кадр BPDU, що надходить через мережевий інтерфейс.

Вектор пріоритету є кортежем із чотирьох елементів:

```
V = (Root_ID, Root_Path_Cost, Designated_Bridge_ID, Designated_Port_ID)
```

Порівняння двох векторів `V_A` та `V_B` виконується за принципом лексикографічного порядку від найважливішого елемента до найменш важливого. Вектор `V_A` вважається **суворішим (кращим, вищим за пріоритетом)**, ніж `V_B` (`V_A < V_B`), якщо виконується перша з умов у такій ієрархії:

1. **Root ID (8 байт)**: менше значення ідентифікатора кореня перемагає. Комутатор із найменшим значенням Bridge ID оголошується Кореневим Комутатором (Root Bridge).
2. **Root Path Cost (4 байти)**: якщо ідентифікатори кореня однакові, перевага надається вектору з меншою сумарною вартістю шляху до кореня.
3. **Designated Bridge ID (8 байт)**: якщо вартість однакова, перемагає сусідній комутатор із меншим власним Bridge ID (комутатор із кращою апаратною адресою чи пріоритетом).
4. **Designated Port ID (2 байти)**: якщо два вектори отримані від того самого сусіднього комутатора через різні лінії, перемагає його порт із меншим логічним номером.

Якщо вхідний вектор BPDU виявляється кращим за поточний активний вектор порту, комутатор приймає нову топологію, оновлює свої ролі портів і негайно розпочинає процедуру перерахунку або активного рукостискання **Proposal / Agreement**.

---

## 2. Модель кінцевого автомата портів (Port State Machine)

Кожен порт комутатора у RSTP знаходиться під управлінням кінцевого автомата, який визначає дві незалежні характеристики: **роль порту (Port Role)** та **стан порту (Port State)**.

### Ролі портів (Port Roles):
* **Root Port (RP)**: один порт на комутаторі, який забезпечує найкоротший та найдешевший шлях до Root Bridge.
* **Designated Port (DP)**: один порт на кожному фізичному сегменті мережі, який просуває трафік від кореня до цього сегмента.
* **Alternate Port (AP)**: резервний порт, який отримує кращі BPDU від іншого комутатора. Він миттєво стає Root Port при відмові основного каналу.
* **Backup Port (BP)**: резервний порт, який отримує кращі BPDU від того самого комутатора (дубльовані лінії до хаба).

### Стани портів (Port States):
* **Discarding**: порт блокує увесь трафік користувачів і не вивчає MAC-адреси. Обробляються лише кадри BPDU.
* **Learning**: порт готується до просування даних — він не пересилає кадри користувачів, але вже вивчає MAC-адреси із вхідного трафіку для заповнення CAM-таблиці.
* **Forwarding**: порт повноцінно вивчає адреси та пересилає трафік користувачів.

---

## 3. Реалізація алгоритму мовою C

У реалізації мовою C використано чітке розмежування структур даних для Bridge ID, вектора пріоритетів та вхідного кадру BPDU. Функція `compare_bridge_id` виконує порівняння пріоритетів та MAC-адрес через `memcmp`, а функція `is_vector_superior` реалізує повну лексикографічну перевірку вектора.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Перелік ролей портів RSTP (IEEE 802.1w)
typedef enum {
    ROLE_DISABLED = 0,
    ROLE_ROOT,
    ROLE_DESIGNATED,
    ROLE_ALTERNATE,
    ROLE_BACKUP
} rstp_port_role_t;

// Перелік станів портів RSTP
typedef enum {
    STATE_DISCARDING = 0,
    STATE_LEARNING,
    STATE_FORWARDING
} rstp_port_state_t;

// Структура 8-байтового Bridge ID (пріоритет + MAC-адреса)
typedef struct {
    uint16_t priority;
    uint8_t  mac[6];
} bridge_id_t;

// Вектор пріоритету BPDU
typedef struct {
    bridge_id_t root_id;
    uint32_t    root_path_cost;
    bridge_id_t designated_bridge_id;
    uint16_t    designated_port_id;
} rstp_priority_vector_t;

// Вхідний кадр BPDU
typedef struct {
    uint16_t               protocol_id;
    uint8_t                version;
    uint8_t                bpdu_type;
    uint8_t                flags;
    rstp_priority_vector_t vector;
    uint16_t               message_age;
    uint16_t               max_age;
    uint16_t               hello_time;
    uint16_t               forward_delay;
} rstp_bpdu_t;

// Порівняння двох Bridge ID (повертає <0 якщо a < b, >0 якщо a > b, 0 якщо однакові)
static int compare_bridge_id(const bridge_id_t *a, const bridge_id_t *b) {
    if (a->priority != b->priority) {
        return (a->priority < b->priority) ? -1 : 1;
    }
    return memcmp(a->mac, b->mac, 6);
}

// Порівняння векторів пріоритету BPDU
// Повертає true, якщо vector_a кращий (має вищий пріоритет), ніж vector_b
bool is_vector_superior(const rstp_priority_vector_t *a, const rstp_priority_vector_t *b) {
    // 1. Порівняння Root ID
    int cmp_root = compare_bridge_id(&a->root_id, &b->root_id);
    if (cmp_root != 0) {
        return cmp_root < 0;
    }

    // 2. Порівняння Root Path Cost
    if (a->root_path_cost != b->root_path_cost) {
        return a->root_path_cost < b->root_path_cost;
    }

    // 3. Порівняння Designated Bridge ID
    int cmp_desig_bridge = compare_bridge_id(&a->designated_bridge_id, &b->designated_bridge_id);
    if (cmp_desig_bridge != 0) {
        return cmp_desig_bridge < 0;
    }

    // 4. Порівняння Designated Port ID
    return a->designated_port_id < b->designated_port_id;
}

// Обробка вхідного BPDU та визначення нової ролі порту
rstp_port_role_t process_incoming_bpdu(const rstp_bpdu_t *incoming_bpdu,
                                       const rstp_priority_vector_t *current_port_vector,
                                       const bridge_id_t *our_bridge_id) {
    // Якщо прийшов кращий BPDU, ніж наш поточний активний вектор
    if (is_vector_superior(&incoming_bpdu->vector, current_port_vector)) {
        // Якщо Root ID в BPDU менший за наш власний BID, ми стаємо транзитним вузлом (Root Port)
        if (compare_bridge_id(&incoming_bpdu->vector.root_id, our_bridge_id) < 0) {
            return ROLE_ROOT;
        } else {
            // Інакше ми програли вибори на цьому сегменті і блокуємо порт (Alternate Port)
            return ROLE_ALTERNATE;
        }
    }

    // Якщо наш власний BPDU кращий, наш порт залишається Designated Port
    return ROLE_DESIGNATED;
}

int main(void) {
    bridge_id_t root_bridge = { .priority = 4096, .mac = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55} };
    bridge_id_t our_bridge  = { .priority = 32768, .mac = {0x00, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE} };

    rstp_priority_vector_t current_vector = {
        .root_id = our_bridge,
        .root_path_cost = 0,
        .designated_bridge_id = our_bridge,
        .designated_port_id = 0x8001
    };

    rstp_bpdu_t rx_bpdu = {
        .protocol_id = 0,
        .version = 2,
        .bpdu_type = 2,
        .flags = 0x3E, // Proposal + Designated Role + Forwarding
        .vector = {
            .root_id = root_bridge,
            .root_path_cost = 4,
            .designated_bridge_id = root_bridge,
            .designated_port_id = 0x8002
        }
    };

    rstp_port_role_t new_role = process_incoming_bpdu(&rx_bpdu, &current_vector, &our_bridge);

    printf("Результат виборів RSTP (C):\n");
    if (new_role == ROLE_ROOT) {
        printf("Статус: Порт обрано як Root Port (найкоротший шлях до Root Bridge)\n");
    } else if (new_role == ROLE_ALTERNATE) {
        printf("Статус: Порт обрано як Alternate Port (блокування для усунення петлі)\n");
    } else {
        printf("Статус: Порт залишається Designated Port\n");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <span>
#include <optional>
#include <algorithm>

namespace rstp {

// Строго типізовані переліки (C++11 enum class)
enum class PortRole {
    Disabled,
    Root,
    Designated,
    Alternate,
    Backup
};

enum class PortState {
    Discarding,
    Learning,
    Forwarding
};

// Структура Bridge ID з тристороннім порівнянням (C++20 spaceship operator)
struct BridgeId {
    uint16_t priority{32768};
    std::array<uint8_t, 6> mac{};

    // Автоматичне комбіноване лексикографічне порівняння поля priority, а потім елементів mac
    auto operator<=>(const BridgeId& other) const = default;
};

// Вектор пріоритету BPDU з перевизначеним оператором менше
struct PriorityVector {
    BridgeId root_id{};
    uint32_t root_path_cost{0};
    BridgeId designated_bridge_id{};
    uint16_t designated_port_id{0};

    // Оператор порівняння векторів пріоритетів
    bool operator<(const PriorityVector& other) const noexcept {
        if (root_id != other.root_id) {
            return root_id < other.root_id;
        }
        if (root_path_cost != other.root_path_cost) {
            return root_path_cost < other.root_path_cost;
        }
        if (designated_bridge_id != other.designated_bridge_id) {
            return designated_bridge_id < other.designated_bridge_id;
        }
        return designated_port_id < other.designated_port_id;
    }
};

// Модель кадру BPDU у стилі Modern C++
struct BpduFrame {
    uint16_t protocol_id{0};
    uint8_t version{2};
    uint8_t bpdu_type{2};
    uint8_t flags{0};
    PriorityVector vector{};
    uint16_t message_age{0};
    uint16_t max_age{20};
    uint16_t hello_time{2};
    uint16_t forward_delay{15};
};

// Клас контролера порту (RAII та інкапсуляція стану)
class RstpPortController {
public:
    explicit RstpPortController(uint16_t port_id, BridgeId own_bridge_id)
        : port_id_(port_id), own_bridge_id_(own_bridge_id) {}

    // Обробка вхідного BPDU та оновлення ролі порту
    PortRole evaluate_bpdu(const BpduFrame& bpdu, const PriorityVector& active_vector) noexcept {
        // Якщо вхідний BPDU має вищий пріоритет (bpdu.vector < active_vector)
        if (bpdu.vector < active_vector) {
            if (bpdu.vector.root_id < own_bridge_id_) {
                current_role_ = PortRole::Root;
                current_state_ = PortState::Forwarding; // Миттєве сходження RSTP
            } else {
                current_role_ = PortRole::Alternate;
                current_state_ = PortState::Discarding; // Захист від петлі
            }
        } else {
            current_role_ = PortRole::Designated;
            current_state_ = PortState::Forwarding;
        }
        return current_role_;
    }

    [[nodiscard]] PortRole role() const noexcept { return current_role_; }
    [[nodiscard]] PortState state() const noexcept { return current_state_; }

private:
    uint16_t port_id_;
    BridgeId own_bridge_id_;
    PortRole current_role_{PortRole::Designated};
    PortState current_state_{PortState::Discarding};
};

} // namespace rstp

int main() {
    using namespace rstp;

    BridgeId root_bridge{.priority = 4096, .mac = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55}};
    BridgeId local_bridge{.priority = 32768, .mac = {0x00, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE}};

    RstpPortController port_controller(0x8001, local_bridge);

    PriorityVector current_best{
        .root_id = local_bridge,
        .root_path_cost = 0,
        .designated_bridge_id = local_bridge,
        .designated_port_id = 0x8001
    };

    BpduFrame incoming_bpdu{
        .vector = {
            .root_id = root_bridge,
            .root_path_cost = 4,
            .designated_bridge_id = root_bridge,
            .designated_port_id = 0x8002
        }
    };

    PortRole role = port_controller.evaluate_bpdu(incoming_bpdu, current_best);

    std::cout << "Аналіз RSTP C++20:\n";
    if (role == PortRole::Root) {
        std::cout << "Статус: Роль [Root Port], Стан [Forwarding]\n";
    } else if (role == PortRole::Alternate) {
        std::cout << "Статус: Роль [Alternate Port], Стан [Discarding]\n";
    }

    return 0;
}
```
:::

---

## 4. Особливості реалізації в Modern C++20

Версія на мові C++20 демонструє сучасні підходи до безпеки та виразності коду при роботі з системними протоколами:

1. **Оператор тристороннього порівняння (`operator<=>`)**:
   Завдяки генерації оператора spaceship за замовчуванням (`auto operator<=> = default`), компілятор автоматично створює оптимізовані лексикографічні порівняння для `BridgeId` по всіх його полях у порядку їх оголошення (спочатку `priority`, потім елементи масиву `mac`).
2. **Типобезпечні переліки (`enum class`)**:
   Використання `enum class PortRole` та `enum class PortState` повністю виключає можливість неявного приведення типів до цілих чисел або випадкового порівняння несумісних констант.
3. **Безпечне управління ресурсами (RAII)**:
   Клас `RstpPortController` повністю інкапсулює внутрішній стан порту та унеможливлює його неузгоджені модифікації ззовні.
4. **Відсутність динамічної пам'яті (`Zero-Allocation`)**:
   Використання `std::array` замість динамічних векторів гарантує відсутність накладних витрат на виділення пам'яті в купі (`heap`), що є критичним вимогам для мережевих даймонів та систем реального часу.

---

## 5. Крайові випадки та тонкощі системного програмування RSTP

При розробці або налагодженні прошивок комутаторів та даймонів управління мостами (наприклад, у Linux bridge чи Open vSwitch) розробники зіштовхуються з низкою крайових випадків:

### Джиттер таймерів та розсіювання Hello
Якщо всі комутатори в мережі генеруватимуть кадри BPDU суворо кожні 2.000 секунди, у великих топологіях може виникнути ефект синхронізації пачок (packet burst), що викликає пікові навантаження на процесори комутаторів. Для запобігання цьому у виклик таймера додається випадковий джиттер (±10% від `Hello Time`).

### Згасання інформації (Message Age Degradation)
Кожен транзитний комутатор при ретрансляції BPDU обов'язково збільшує значення поля `Message Age` на 1 секунду. Якщо через затримки в мережі або неправильну конфігурацію діаметр мережі перевищує 20 хопів (`Message Age >= Max Age`), BPDU відкидається як застарілий. Це запобігає зацикленню службового трафіку у надто великих топологіях.

### Захист від односпрямованого зв'язку (Unidirectional Links)
Якщо при пошкодженні кабелю прийом (RX) працює, а передача (TX) обірвана, порт припиняє надсилати свої BPDU, але продовжує слухати сусіда. Це може змусити сусідній комутатор вирішити, що порт вільний, і перевести його у Forwarding, створивши петлю. Для запобігання цьому реалізують алгоритми **UDLD** та **Loop Guard**, які перевіряють двосторонню симетричність обміну BPDU.
