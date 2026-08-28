# ⚙️ Парсер списку з'єднань (Netlist / IPC-D-356) на C та C++

У сучасному виробництві друкованих плат та автоматизованих конвеєрах контролю якості (CI/CD) перевірка цілісності електричних кіл вимагає незалежного зіставлення фізичних шарів міді з логічною принциповою схемою. Коли контрактний завод готує цифрові виробничі файли до запуску лінії або проводить контроль електричного монтажу виготовленої голої плати на стенді рухомих щупів (англ. *Flying Probe Tester*), він не завантажує важкий графічний інтерфейс САПР. Запуск повноцінного графічного редактора на виробничому верстаті не лише надлишковий, а й створює ризик людської помилки під час експорту чи ручного вибору шарів.

Замість цього виробниче обладнання та серверні скрипти верифікації використовують стандартизовані машинні формати списків з'єднань — передусім міжнародний галузевий стандарт IPC-D-356 або текстові нетлісти САПР (зокрема формат S-виразів KiCad чи Protel Netlist).

Автоматизовані консольні утиліти парсять такі файли, будують у пам'яті граф електричних з'єднань і перевіряють два критичні класи дефектів:
1. **Топологічні розриви (Opens)**: випадок, коли два або більше контактних майданчиків, які за схемою належать до однієї мережі, виявляються фізично ізольованими через недотравлену доріжку, тріщину металізації у перехідному отворі або дефект свердління;
2. **Паразитні замикання (Shorts)**: ситуація, коли між двома різними електричними мережами (наприклад, шиною живлення 3.3 В та аналоговою землею) утворюється мікроскопічний місток припою або залишок мідної фольги, створюючи коротке замикання.

Розгляньмо будову формату IPC-D-356, математичну модель графа з'єднань та програмну реалізацію швидкого й надійного парсера списків з'єднань.

## Структура записів і синтаксис IPC-D-356

Стандарт IPC-D-356 було розроблено Асоціацією з'єднувальних електронних індустрій (IPC) як універсальну мову обміну даними для тестування друкованих плат без компонентів (англ. *bare-board testing*). Файл є звичайним текстовим ASCII-документом із фіксованою структурою колонок. Кожен рядок описує окремий фізичний контактний майданчик (SMD-пад), вивід наскрізного монтажу (Through-Hole) або тестову точку на платі:

```text
C  IPC-D-356 Bare Board Test Netlist File
P  UNITS CUST
317 VCC_3V3       U1   -14   M D0030A0050P0000X+010500Y+020000X0030Y0050
327 VCC_3V3       C1   -1    M D0020A0040P0000X+012000Y+019500X0020Y0040
327 VCC_3V3       R1   -2    M D0020A0040P0000X+015200Y+022100X0020Y0040
317 GND           U1   -7    M D0030A0050P0000X+010500Y+027000X0030Y0050
327 GND           C1   -2    M D0020A0040P0000X+012000Y+026500X0020Y0040
317 SPI_MOSI      U1   -5    M D0030A0050P0000X+010500Y+023000X0030Y0050
327 SPI_MOSI      R2   -1    M D0020A0040P0000X+018000Y+023000X0020Y0040
```

Поля кожного рядка несуть чітке семантичне значення відповідно до фіксованої позиції символів у рядку:
1. **Код операції (Record Type, колонки 1–3)**: тризначний код, що визначає тип геометрії. Код `317` позначає вивід наскрізного отвору з металізацією (Plated Through-Hole), код `327` — контактний майданчик поверхневого монтажу (SMD Pad), код `027` — глухий чи прихований перехідний отвір (Via), а префікс `C` — рядок коментаря;
2. **Ім'я мережі (Net Name, колонки 5–18)**: унікальний ідентифікатор еквіпотенціального кола (наприклад, `VCC_3V3`, `GND`, `RESET_N`). Усі точки з однаковою назвою мережі повинні мати гальванічний зв'язок на платі;
3. **Позиційне позначення (RefDes, колонки 21–26)**: маркування компонента, якому належить контактний майданчик (`U1`, `C1`, `R2`);
4. **Номер виводу (Pin Number, колонки 28–31)**: номер ніжки мікросхеми чи дискретного елемента, який за стандартом відокремлюється дефісом (`-14`, `-1`, `-A1`);
5. **Сторона доступу (колонки 33–34)**: прапорець доступу щупа тестера (`M` для верхньої сторони Mid-point/Primary, `A` для нижньої сторони Secondary);
6. **Координати середини площадки (колонки 43–60)**: точні геометричні координати X та Y центру площадки у форматі знака напрямку та десяткових часток одиниці вимірювання (наприклад, `X+010500 Y+020000` задає X = 10.500 мм або 1050.0 mils).

## Алгоритмічна побудова графа та структури даних

Для верифікації топології парсер повинен вирішити два ключові завдання:
1. **Лексичний розбір і токенізація**: зчитування текстового потоку рядок за рядком, відсікання коментарів та вилучення числових і рядкових полів без ризику переповнення буфера пам'яті;
2. **Агрегація в таблицю символів (Хеш-таблицю мереж)**: групування всіх контактних майданчиків за ключем назви мережі. Результатом роботи парсера є структура `NetlistDatabase`, де кожному імені мережі відповідає динамічний масив точок тестування з координатами та типами виводів.

Нижче наведено практичну реалізацію повнофункціонального парсера мовами C99 та сучасним C++20:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_NETS 128
#define MAX_PINS_PER_NET 64
#define MAX_NAME_LEN 32

typedef struct {
    char refdes[16];
    char pin[8];
    double x_mm;
    double y_mm;
    int is_smd;
} testpoint_t;

typedef struct {
    char net_name[MAX_NAME_LEN];
    testpoint_t points[MAX_PINS_PER_NET];
    size_t point_count;
} net_entry_t;

typedef struct {
    net_entry_t nets[MAX_NETS];
    size_t net_count;
} netlist_db_t;

static void trim_spaces(char *str) {
    char *end;
    while (isspace((unsigned char)*str)) str++;
    end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
}

static net_entry_t *find_or_add_net(netlist_db_t *db, const char *net_name) {
    for (size_t i = 0; i < db->net_count; ++i) {
        if (strcmp(db->nets[i].net_name, net_name) == 0) {
            return &db->nets[i];
        }
    }
    if (db->net_count >= MAX_NETS) return NULL;
    net_entry_t *entry = &db->nets[db->net_count++];
    strncpy(entry->net_name, net_name, MAX_NAME_LEN - 1);
    entry->net_name[MAX_NAME_LEN - 1] = '\0';
    entry->point_count = 0;
    return entry;
}

int parse_ipc_line(netlist_db_t *db, const char *line) {
    if (!line || line[0] == 'C' || line[0] == 'P' || line[0] == '\0' || isspace((unsigned char)line[0])) {
        return 0; // Пропуск коментарів, директив параметрів та порожніх рядків
    }

    int opcode = 0;
    char net_name[MAX_NAME_LEN] = {0};
    char refdes[16] = {0};
    char pin_raw[16] = {0};
    
    // Парсинг перших токенів: Опкод, Ім'я кола, RefDes, Pin
    if (sscanf(line, "%d %31s %15s %15s", &opcode, net_name, refdes, pin_raw) < 4) {
        return -1;
    }

    // Видалення дефісу з номера піна (наприклад, "-14" -> "14")
    const char *pin = (pin_raw[0] == '-') ? pin_raw + 1 : pin_raw;

    // Пошук координат X та Y у рядку (шаблон X+010500 Y+020000)
    double x_val = 0.0, y_val = 0.0;
    const char *x_ptr = strstr(line, "X+");
    if (!x_ptr) x_ptr = strstr(line, "X-");
    const char *y_ptr = strstr(line, "Y+");
    if (!y_ptr) y_ptr = strstr(line, "Y-");

    if (x_ptr) x_val = atof(x_ptr + 1) / 1000.0; // переведення у мм
    if (y_ptr) y_val = atof(y_ptr + 1) / 1000.0;

    net_entry_t *net = find_or_add_net(db, net_name);
    if (!net || net->point_count >= MAX_PINS_PER_NET) {
        return -1;
    }

    testpoint_t *pt = &net->points[net->point_count++];
    strncpy(pt->refdes, refdes, sizeof(pt->refdes) - 1);
    strncpy(pt->pin, pin, sizeof(pt->pin) - 1);
    pt->x_mm = x_val;
    pt->y_mm = y_val;
    pt->is_smd = (opcode == 327);

    return 1;
}

void print_netlist_summary(const netlist_db_t *db) {
    printf("=== Звіт розбору списку з'єднань (IPC-D-356) ===\n");
    printf("Знайдено унікальних мереж: %zu\n\n", db->net_count);
    for (size_t i = 0; i < db->net_count; ++i) {
        const net_entry_t *net = &db->nets[i];
        printf("Мережа [%s] — точок з'єднання: %zu\n", net->net_name, net->point_count);
        for (size_t p = 0; p < net->point_count; ++p) {
            const testpoint_t *pt = &net->points[p];
            printf("  -> Вузол %s.%s (%s) на (%.2f, %.2f) мм\n",
                   pt->refdes, pt->pin,
                   pt->is_smd ? "SMD" : "THT",
                   pt->x_mm, pt->y_mm);
        }
    }
}

int main(void) {
    const char *sample_ipc_data =
        "C  IPC-D-356 Test Netlist\n"
        "P  UNITS CUST\n"
        "317 VCC_3V3       U1   -14   M D0030A0050P0000X+010500Y+020000X0030Y0050\n"
        "327 VCC_3V3       C1   -1    M D0020A0040P0000X+012000Y+019500X0020Y0040\n"
        "327 VCC_3V3       R1   -2    M D0020A0040P0000X+015200Y+022100X0020Y0040\n"
        "317 GND           U1   -7    M D0030A0050P0000X+010500Y+027000X0030Y0050\n"
        "327 GND           C1   -2    M D0020A0040P0000X+012000Y+026500X0020Y0040\n"
        "317 SPI_MOSI      U1   -5    M D0030A0050P0000X+010500Y+023000X0030Y0050\n"
        "327 SPI_MOSI      R2   -1    M D0020A0040P0000X+018000Y+023000X0020Y0040\n";

    netlist_db_t db = {0};
    char buffer[256];
    const char *cursor = sample_ipc_data;

    while (*cursor) {
        size_t len = 0;
        while (cursor[len] && cursor[len] != '\n' && len < sizeof(buffer) - 1) {
            len++;
        }
        strncpy(buffer, cursor, len);
        buffer[len] = '\0';
        cursor += len + (cursor[len] == '\n' ? 1 : 0);

        parse_ipc_line(&db, buffer);
    }

    print_netlist_summary(&db);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <sstream>
#include <charconv>
#include <iomanip>

struct TestPoint {
    std::string refdes;
    std::string pin;
    double x_mm{0.0};
    double y_mm{0.0};
    bool is_smd{false};
};

struct NetlistDatabase {
    std::unordered_map<std::string, std::vector<TestPoint>> nets;

    bool parse_ipc_line(std::string_view line) {
        if (line.empty() || line.front() == 'C' || line.front() == 'P' || line.front() == '#') {
            return false;
        }

        std::istringstream stream{std::string(line)};
        int opcode = 0;
        std::string net_name, refdes, pin_raw;

        if (!(stream >> opcode >> net_name >> refdes >> pin_raw)) {
            return false;
        }

        std::string pin = (pin_raw.starts_with('-')) ? pin_raw.substr(1) : pin_raw;

        double x_val = 0.0;
        double y_val = 0.0;

        const auto x_pos = line.find("X+");
        const auto y_pos = line.find("Y+");

        if (x_pos != std::string_view::npos && x_pos + 8 <= line.size()) {
            std::from_chars(line.data() + x_pos + 2, line.data() + x_pos + 8, x_val);
            x_val /= 1000.0;
        }
        if (y_pos != std::string_view::npos && y_pos + 8 <= line.size()) {
            std::from_chars(line.data() + y_pos + 2, line.data() + y_pos + 8, y_val);
            y_val /= 1000.0;
        }

        nets[net_name].push_back(TestPoint{
            .refdes = std::move(refdes),
            .pin = std::move(pin),
            .x_mm = x_val,
            .y_mm = y_val,
            .is_smd = (opcode == 327)
        });

        return true;
    }

    void print_summary() const {
        std::cout << "=== Звіт розбору списку з'єднань (IPC-D-356) ===\n";
        std::cout << "Знайдено унікальних мереж: " << nets.size() << "\n\n";

        for (const auto& [net_name, points] : nets) {
            std::cout << "Мережа [" << net_name << "] — точок з'єднання: " << points.size() << "\n";
            for (const auto& pt : points) {
                std::cout << "  -> Вузол " << pt.refdes << "." << pt.pin
                          << " (" << (pt.is_smd ? "SMD" : "THT") << ")"
                          << " на (" << std::fixed << std::setprecision(2)
                          << pt.x_mm << ", " << pt.y_mm << ") мм\n";
            }
        }
    }
};

int main() {
    const std::string sample_ipc_data =
        "C  IPC-D-356 Test Netlist\n"
        "P  UNITS CUST\n"
        "317 VCC_3V3       U1   -14   M D0030A0050P0000X+010500Y+020000X0030Y0050\n"
        "327 VCC_3V3       C1   -1    M D0020A0040P0000X+012000Y+019500X0020Y0040\n"
        "327 VCC_3V3       R1   -2    M D0020A0040P0000X+015200Y+022100X0020Y0040\n"
        "317 GND           U1   -7    M D0030A0050P0000X+010500Y+027000X0030Y0050\n"
        "327 GND           C1   -2    M D0020A0040P0000X+012000Y+026500X0020Y0040\n"
        "317 SPI_MOSI      U1   -5    M D0030A0050P0000X+010500Y+023000X0030Y0050\n"
        "327 SPI_MOSI      R2   -1    M D0020A0040P0000X+018000Y+023000X0020Y0040\n";

    NetlistDatabase db;
    std::istringstream input_stream{sample_ipc_data};
    std::string line;

    while (std::getline(input_stream, line)) {
        db.parse_ipc_line(line);
    }

    db.print_summary();
    return 0;
}
```
:::

## Інженерні пастки при парсингу списків з'єднань

Під час практичної розробки утиліт обробки виробничих списків з'єднань інженери стикаються з кількома типовими проблемами:

1. **Неоднозначність одиниць вимірювання та масштабних коефіцієнтів**: стандарт IPC-D-356 допускає завдання координат як у дюймових мілах (команда `P  UNITS CUST`), так і в метричній системі в мікронах (`P  UNITS SI`). Якщо парсер жорстко зашиває дільник або ігнорує рядок конфігурації одиниць на початку файлу, розраховані координати зсунуться у 25.4 раза, що спричинить механічне пошкодження голчастої матриці тестера.
2. **Багатосекційні компоненти та термальні площадки (Exposed Pads)**: сучасні мікросхеми у безвивідних корпусах QFN, DFN чи BGA містять центральну відкриту площадку тепловідводу (Exposed Pad), яка у схемотехнічному символі може позначатися як пін `EP`, `PAD`, `0` або мати буквено-цифрові індекси (наприклад, `A1`, `B12`). Якщо парсер спирається на припущення, що всі номери пінів є виключно десятковими цілими числами, рядок буде відкинуто як помилковий, а лінія землі втратить критичний зв'язок.
3. **Ієрархічні простори імен та довжина рядків**: в ієрархічних проєктах САПР назви локальних шин доповнюються ієрархічним шляхом (наприклад, `/Power_Management/DCDC_Core/VCC_0V9`). Стандарт IPC-D-356 історично відводить під ім'я мережі фіксоване поле у 14 символів. При експорті довга назва мережі може бути обрізана або замінена сурогатним коротким псевдонімом (наприклад, `$$$NET0042`), що вимагає додаткового файлу відповідності (англ. *Net Cross-Reference Table*).
4. **Висячі ізольовані вузли (Single-Pin Nets)**: нетліст може містити поодинокі тестові точки або незадіяні виводи роз'ємів і мікроконтролера, підключені лише в одній точці. Парсер валідації повинен вміти коректно класифікувати легітимні одноточкові виводи та не генерувати помилкові попередження про топологічний розрив для кіл, де фізично передбачено лише один вузол.
