# ⚙️ Автоматизація кодової археології: git forensics та гарячі точки

Коли інженер потрапляє в кодову базу розміром у мільйон рядків без актуальної документації, читати вихідний код послідовно файл за файлом — це тупиковий шлях. Мозок швидко втрачає фокус у плутанині викликів, а важливі деталі розчиняються в тисячах рядків банальних DTO та конфігурацій. Цифрова археологія спирається на математичні принципи й робочий інструментарій: автоматичне виявлення гарячих точок (Hotspots) на основі аналізу гіт-історії, побудову матриці структурного зчеплення (Structural Coupling) та практичну методологію створення безпечних «швів» (Seams) мовами C та C++ для обгортання legacy-коду характеристичними тестами.

## 1. Математика й автоматизація розрахунку гарячих точок (Git Churn × Complexity)

Не всі файли у великому репозиторії вимагають однакової уваги. У будь-якому довгоживучому проєкті спостерігається виражений розподіл Парето: приблизно 80% багів, аварій і затримок зосереджено в 5% модулів. Щоб знайти ці 5% без суб'єктивних здогадок, використовується комбінований показник **Hotspots** (гарячі точки), який поєднує частоту змін коду та його логічну складність.

### Теорія аналізу гіт-історії (Git Forensics)

Метрика **Churn** вимірює обсяг модифікацій у кодовій базі за обраний часовий проміжок (найчастіше за останні 90–180 днів). Вона обчислюється як сума доданих і видалених рядків коду в усіх комітах, що зачіпають конкретний файл. Якщо файл змінюється щодня, це означає одне з двох: або в ньому постійно виправляють баги, або до нього постійно додають нові бізнес-вимоги, оскільки він став монолітним «корисним центром» системи.

Метрика **Complexity** вимірює внутрішню складність модуля. Найпростішою приблизною оцінкою є загальна кількість рядків коду (`LOC`), проте набагато точнішою є цикльоматична складність за Маккейбом (Cyclomatic Complexity). Вона рахує кількість лінійно незалежних шляхів крізь програму, орієнтуючись на кількість управляючих операторів розгалуження (`if`, `else`, `for`, `while`, `switch`, `case`, `catch`, `&&`, `||`).

Добуток цих двох величин утворює математичну оцінку гарячої точки:

```
Hotspot Score = Churn × Complexity
```

Модуль із високою складністю, але нульовим `Churn` (наприклад, складний парсер протоколу, написаний 4 роки тому, який стабільно працює і не редагується), має відносно низький пріоритет для негайного рефакторингу. Модуль із високим `Churn`, але низькою складністю (наприклад, файл мапінгу словника) не несе високого ризику. Але файл, який має високу складність І часто змінюється — це абсолютна зона ризику, де кожна наступна зміна з високою ймовірністю спричинить регресію.

### Готовий аналітичний скрипт для виявлення Hotspots

Нижченаведений скрипт на Python виконує аналіз репозиторію за допомогою утиліти `git log --numstat`, автоматично обчислює `Churn` для кожного файлу, оцінює його цикльоматичну складність та виводить відсортований рейтинг небезпечних точок у кодовій базі.

```py
#!/usr/bin/env python3
import subprocess
import sys
import os
import re

def get_git_churn(days=90):
    """Збирає кількість модифікацій (додано + видалено рядків) по кожному файлу за N днів."""
    cmd = ["git", "log", f"--since={days}.days.ago", "--numstat", "--pretty=format:"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    churn_map = {}
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) == 3:
            added, deleted, filepath = parts
            if added == '-' or deleted == '-':
                continue  # Пропускаємо бінарні файли (зображення, бінарники)
            changes = int(added) + int(deleted)
            churn_map[filepath] = churn_map.get(filepath, 0) + changes
    return churn_map

def get_file_complexity(filepath):
    """Оцінка складності за кількістю рядків коду та розгалужень (if/for/while/switch)."""
    if not os.path.exists(filepath):
        return 0
    complexity = 1
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Рахуємо ключові слова управляючих конструкцій
                if re.search(r'\b(if|else|for|while|switch|case|catch)\b', line):
                    complexity += 1
    except Exception:
        pass
    return complexity

def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    churn = get_git_churn(days)
    results = []

    for filepath, churn_score in churn.items():
        # Фільтруємо теки тестування, генерований код та вендорські залежності
        if filepath.startswith("vendor/") or filepath.startswith("node_modules/") or filepath.startswith("build/"):
            continue
        complexity = get_file_complexity(filepath)
        hotspot_score = churn_score * complexity
        results.append((filepath, churn_score, complexity, hotspot_score))

    # Сортуємо за спаданням Hotspot Score
    results.sort(key=lambda x: x[3], reverse=True)

    print(f"{'File Path':<60} | {'Churn':<8} | {'Complexity':<10} | {'Hotspot Score':<12}")
    print("-" * 98)
    for path, ch, comp, score in results[:20]:
        print(f"{path:<60} | {ch:<8} | {comp:<10} | {score:<12}")

if __name__ == "__main__":
    main()
```

Запуск цього інструмента в корені репозиторію дає точний орієнтир для архітектора. Замість того, щоб гадати, який модуль починати покривати тестами або переписувати, інженер отримує топ-5 найбільш небезпечних модулів чужої системи.

## 2. Аналіз прихованого зчеплення (Temporal Coupling)

Окрім аналізу окремих файлів, git-історія дає змогу виявити приховане **часове зчеплення (Temporal / Structural Coupling)** — ситуацію, коли два або більше файлів системно модифікуються в одних і тих самих комітах, хоча між ними немає прямих викликів коду чи імпортів.

Наприклад, якщо при кожній зміні у `hub/telemetry_parser.c` розробники змушені редагувати `cloud/billing_adapter.go`, це свідчить про наявність невираженого дублювання констант, неявного протоколу або злам меж контекстів. Виявлення часового зчеплення дозволяє архітектору зрозуміти невидимі залежності чужої системи ще до того, як вони зламаються під час рефакторингу.

## 3. Практична виділення швів (Seam Architecture) у системному коді

Коли гарячу точку знайдено (наприклад, критичний модуль `hub_telemetry.c` у контролері IoT-хаба DH), його не можна модифікувати без створення гарантійної сітки. Спроба відразу переписати логіку призводить до втрати прихованих інваріантів. Потрібно створити «шов» (Seam) — точку в архітектурі або коді, де поведінку програми можна підмінити або перехопити без редагування самого легасі-коду.

У системному програмуванні на C та C++ існує три основні типи швів:
1. **Препроцесорні шви (Preprocessor Seams):** використання директив `#ifdef TEST_MOCK` для підміни викликів системних функцій на етапі компіляції.
2. **Компонувальні шви (Linker Seams):** використання слабких символів (`#pragma weak` або `__attribute__((weak))`) для перехоплення функцій на етапі збирання.
3. **Об'єктні шви (Object / Pointer Seams):** використання таблиць вказівників на функції у C або абстрактних класів/інтерфейсів у C++ для підміни залежностей під час виконання.

Нижче наведено приклад об'єктного шва для чужої функції обробки телеметрії давачів на C та C++.

:::tabs
```c
/* Legacy C code: hub_telemetry.h / hub_telemetry.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Офіційний доменний тип легасі-системи */
typedef struct {
    int device_id;
    float raw_temperature;
    int status_flags;
} telemetry_packet_t;

/* Вказівник на функцію відправки сповіщень — це і є наш ШОВ (Seam).
   У продакшні він вказує на реальну мережу, у тесті — на заглушку. */
typedef void (*notification_sink_t)(int device_id, const char* message);

static void default_network_sink(int device_id, const char* message) {
    /* Реальна відправка в мережевий сокет */
    printf("[NET-SEND] Device %d: %s\n", device_id, message);
}

/* Глобальний або контекстний шов */
notification_sink_t g_notification_seam = default_network_sink;

/* Легасі-функція з невідомими інваріантами */
int process_device_telemetry(const telemetry_packet_t* pkt) {
    if (!pkt) return -1;

    /* Заплутана легасі-логіка перевірки порогів */
    if (pkt->raw_temperature > 85.0f && (pkt->status_flags & 0x01)) {
        g_notification_seam(pkt->device_id, "CRITICAL_OVERHEAT");
        return 2; /* Критичний стан */
    } else if (pkt->raw_temperature < -20.0f) {
        g_notification_seam(pkt->device_id, "SENSOR_FREEZE");
        return 1; /* Попередження */
    }

    return 0; /* Норма */
}
```
```cpp
// Idiomatic C++ Seam: HubTelemetrySeam.hpp
#include <iostream>
#include <string>
#include <functional>
#include <memory>

struct TelemetryPacket {
    int device_id;
    float raw_temperature;
    int status_flags;
};

// Інтерфейс шва для підміни залежностей у характеристичних тестах (RAII / DI)
class INotificationSink {
public:
    virtual ~INotificationSink() = default;
    virtual void send(int device_id, std::string_view message) = 0;
};

class DefaultNetworkSink : public INotificationSink {
public:
    void send(int device_id, std::string_view message) override {
        std::cout << "[NET-SEND] Device " << device_id << ": " << message << "\n";
    }
};

class TelemetryProcessor {
private:
    std::shared_ptr<INotificationSink> sink_;

public:
    // Конструктор приймає шов (за замовчуванням — мережевий Sink)
    explicit TelemetryProcessor(std::shared_ptr<INotificationSink> sink = std::make_shared<DefaultNetworkSink>())
        : sink_(std::move(sink)) {}

    int process(const TelemetryPacket& pkt) {
        if (pkt.raw_temperature > 85.0f && (pkt.status_flags & 0x01)) {
            sink_->send(pkt.device_id, "CRITICAL_OVERHEAT");
            return 2;
        } else if (pkt.raw_temperature < -20.0f) {
            sink_->send(pkt.device_id, "SENSOR_FREEZE");
            return 1;
        }
        return 0;
    }
};
```
:::

## 4. Написання характеристичних тестів (Characterization Testing)

Після виділення шову ми пишемо характеристичний тест (Characterization Test). Головна відмінність характеристичного тесту від звичайного модульного тесту полягає у цілі:
- **Модульний тест (Unit Test)** перевіряє, чи відповідає код *технічному завданню* та специфікації (перевірка правильності).
- **Характеристичний тест (Characterization Test)** фіксує *фактичну поведінку існуючого коду*, незалежно від того, вважається вона правильною чи помилковою з точки зору бізнес-логіки.

Якщо чужа функція при передачі `NULL` повертає `-99` замість викидання винятку — характеристичний тест записує `-99` як фіксований інваріант. Це створює «заморожений злімок» системи, який буде сигналізувати про будь-які ненавмисні регресії під час майбутнього рефакторингу.

:::tabs
```c
/* Characterization Test у C: test_telemetry_seam.c */
#include <assert.h>
#include <string.h>

static char g_last_log[128] = {0};
static int g_last_device = -1;

/* Тестовий шов — перехоплює виклики замість мережі */
static void test_capture_sink(int device_id, const char* message) {
    g_last_device = device_id;
    strncpy(g_last_log, message, sizeof(g_last_log) - 1);
}

void run_characterization_tests(void) {
    /* Підміняємо шов тестовим перехоплювачем */
    g_notification_seam = test_capture_sink;

    telemetry_packet_t pkt1 = { .device_id = 101, .raw_temperature = 90.0f, .status_flags = 0x01 };
    int res1 = process_device_telemetry(&pkt1);
    
    /* Фіксуємо поточну поведінку як незмінний факт */
    assert(res1 == 2);
    assert(g_last_device == 101);
    assert(strcmp(g_last_log, "CRITICAL_OVERHEAT") == 0);

    /* Тест на випадок, коли прапор 0x01 НЕ встановлено при високій температурі */
    telemetry_packet_t pkt2 = { .device_id = 102, .raw_temperature = 90.0f, .status_flags = 0x00 };
    int res2 = process_device_telemetry(&pkt2);
    
    /* Відкриття: без прапора 0x01 температура 90C вважається НОРМОЮ (res == 0)!
       Ми фіксуємо цю дивну поведінку тестом, щоб не зламати її випадково. */
    assert(res2 == 0);

    printf("Усі характеристичні тести пройдено успішно!\n");
}
```
```cpp
// Characterization Test у C++: TestTelemetrySeam.cpp
#include <cassert>
#include <vector>

class MockNotificationSink : public INotificationSink {
public:
    int last_device = -1;
    std::string last_message;

    void send(int device_id, std::string_view message) override {
        last_device = device_id;
        last_message = std::string(message);
    }
};

void run_cpp_characterization_tests() {
    auto mock_sink = std::make_shared<MockNotificationSink>();
    TelemetryProcessor processor(mock_sink);

    TelemetryPacket pkt1{201, 90.0f, 0x01};
    int res1 = processor.process(pkt1);
    assert(res1 == 2);
    assert(mock_sink->last_device == 201);
    assert(mock_sink->last_message == "CRITICAL_OVERHEAT");

    // Зафіксований несподіваний інваріант: без прапора status_flags=0x01 перегрів ігнорується
    TelemetryPacket pkt2{202, 90.0f, 0x00};
    int res2 = processor.process(pkt2);
    assert(res2 == 0);

    std::cout << "C++ характеристичні тести успішно зафіксували стабільність шову!\n";
}
```
:::

### Борня з недетермінізмом у легасі-тестах

Найбільшою перешкодою при написанні характеристичних тестів є недетермінована поведінка — використання системного часу (`time()`, `gettimeofday()`), генераторів випадкових чисел (`rand()`) або поточних мережевих відповідей.

Щоб зробити характеристичний тест детермінованим, недетерміновані виклики виносяться за додаткові препроцесорні або інтерфейсні шви:
- Замість прямого виклику `time(NULL)` у коді використовується шов `clock_get_time()`, який у тестах повертає константне зафіксоване значення (Freeze Time pattern).
- Замість системного генератора випадкових чисел підключається зафіксований Seed або масив передзаписаних псевдовипадкових значень.

Поєднання аналізу гіт-історії для виявлення гарячих точок та виділення швів для характеристичного тестування створює математично обґрунтовану й надійну систему навігації у будь-якій чужій кодовій базі.
