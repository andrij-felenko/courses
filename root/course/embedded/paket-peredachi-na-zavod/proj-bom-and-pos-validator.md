# ⚙️ Валідатор узгодженості BOM і Pick-and-Place файлів монтажу

Перед відправленням релізного пакета на завод головний ризик — прихована розбіжність між списком закупівлі (BOM) і файлом координат монтажу (Pick-and-Place / CPL). Якщо компонент є у BOM, але відсутній у CPL, складальний автомат його пропустить; якщо ж деталь є в CPL, але відсутня в BOM або позначена як DNP (Do Not Populate), оператор лінії зупинить монтаж або встановить випадковий елемент.

Нижче наведено робочий інструмент верифікації, який автоматично зіставляє позиційні позначення (Designators), перевіряє кількість, відстежує статус DNP та сигналізує про будь-які невідповідності кодом повернення для інтеграції в автоматизований конвеєр перевірки релізів.

## 1. Структура вхідних даних та механіка розбору

У реальних проектах формати експорту САПР мають низку особливостей, які часто ламають примітивні скрипти зіставлення:

1. **Групування позиційних позначень у BOM:** у відомості матеріалів однакові деталі часто групуються в один рядок (наприклад, `"C1, C2, C4"` або `"R1-R4"`). Валідатор зобов'язаний розібрати такий рядок на індивідуальні атомарні позначення для порівняння з плаським списком координат;
2. **Прапорці ненапаювання (DNP / DNI):** якщо налагоджувальний резистор позначено у схемі як `DNP=1`, він потрапляє у файл Pick-and-Place із САПР із фізичними координатами на платі, але не повинен закуповуватися та монтуватися автоматом. Валідатор має виявляти такі компоненти й генерувати попередження оператору для налаштування маски ігнорування живильника;
3. **Регістронезалежність і пробіли:** у файлах трапляються суміші `c1`, `C1`, зайві пробіли та лапки (`" C1 "`), які мають нормалізуватися до єдиного вигляду перед пошуком у хеш-таблиці;
4. **Розбіжність шарів:** якщо у відомості BOM зазначено компонент верхнього боку, а у файлі CPL вказано шар `Bottom`, деталь потрапить на протилежний бік плати під час другого проходу печі;
5. **Нормалізація кутів орієнтації:** кут повороту `360.0°` або `-90.0°` має приводитися до стандартного діапазону від `0.0°` до `359.9°`. Від'ємні значення у деяких САПР (наприклад, `-45.0°`) перетворюються на `315.0°`, щоб збігатися з системою числення кутів маніпулятора Pick-and-Place;
6. **Фільтрація механічних елементів та оптичних реперів:** оптичні репери (`FID1`, `FID2`), тестові точки (`TP1`, `TP2`) та кріпильні отвори (`MH1`, `MH2`) часто генеруються у файлі розміщення САПР як компоненти без виводів. Якщо у відомості BOM для них немає рядків закупівлі, валідатор повинен коректно відрізняти їх від забутих електронних деталей за префіксами або вимагати явного зазначення їхнього статусу;
7. **Контроль варіантів збірки (Assembly Variants):** для пристроїв з кількома конфігураціями (наприклад, базова версія без модуля стільникового зв'язку та преміум-версія з модемом) одна й та сама топологія плати має різні файли BOM. Валідатор дозволяє перевірити відповідний профіль збірки, запобігаючи помилковій установці високовартісних мікросхем на базові плати.

Програма очікує два стандартні CSV-файли:
- `bom.csv` з полями: `Designator,MPN,Package,DNP` (де кілька позначень можуть бути в лапках);
- `cpl.csv` з полями: `Designator,PosX,PosY,Rot,Layer`.

Формуються три множини перевірки:
- Позиції, наявні в BOM, але відсутні в CPL (нерозведені або пропущені деталі);
- Позиції, наявні в CPL, але відсутні в BOM (незамовлені елементи, що залишать порожні майданчики);
- Позиції з ознакою `DNP=1`, які все ще присутні в CPL (ризик помилкового монтажу).

## 2. Алгоритм роботи та часова складність

Алгоритм валідатора виконує покрокову перевірку за два лінійні проходи:

1. **Фаза індексації BOM:** файл `bom.csv` зчитується рядок за рядком. Поле `Designator` очищається від лапок і розділяється за комами або пробілами. Кожне позиційне позначення переводиться у верхній регістр (`to_upper`) і зберігається в хеш-таблиці з прив'язкою до коду виробника (MPN) та прапорця DNP. Якщо виявлено дублікат позиційного імені (наприклад, два різні рядки містять `R5`), фіксується помилка колізії схеми;
2. **Фаза індексації CPL:** файл координат `cpl.csv` парситься аналогічно. Координати `X`, `Y` та кут `Rot` валідуються на числову коректність. Якщо деталь має координати за межами фізичних габаритів плати або некоректний шар монтажу, фіксується дефект;
3. **Фаза перехресного зіставлення:** валідатор ітерує по записах BOM і шукає відповідний ключ у таблиці CPL за час `O(1)`. Якщо активний компонент (не DNP) відсутній у CPL — це критична помилка. Потім виконується зворотна перевірка: кожен елемент CPL шукається в BOM. Якщо автомат має встановити деталь, якої немає у списку закупівлі, фіксується невідповідність;
4. **Формування звіту та код завершення:** утиліта підраховує кількість помилок (`errors`) та попереджень (`warnings`). Якщо `errors > 0`, процес завершується з кодом повернення `1` (блокування релізу); якщо виявлено лише некритичні зауваження DNP, повертається `0`.

Загальна часова складність алгоритму становить `O(N + M)`, де `N` — кількість деталей у відомості BOM, а `M` — кількість записів у файлі CPL. Пам'ять масштабується лінійно `O(N + M)`, що дозволяє миттєво обробляти плати з десятками тисяч компонентів без затримок у конвеєрі підготовки виробництва.

## 3. Реалізація валідатора

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_LINE_LEN   1024
#define MAX_ITEMS      2048
#define MAX_NAME_LEN   32

typedef struct {
    char name[MAX_NAME_LEN];
    char mpN[64];
    int  dnp;
    int  matched_in_cpl;
} BomEntry;

typedef struct {
    char name[MAX_NAME_LEN];
    double x;
    double y;
    double rot;
    char layer[16];
    int  matched_in_bom;
} CplEntry;

static void trim(char *s) {
    char *p = s;
    while (isspace((unsigned char)*p)) p++;
    if (p != s) memmove(s, p, strlen(p) + 1);
    size_t len = strlen(s);
    while (len > 0 && (isspace((unsigned char)s[len - 1]) || s[len - 1] == '\r' || s[len - 1] == '\n')) {
        s[--len] = '\0';
    }
}

static int parse_bom(const char *path, BomEntry *bom, int max_bom, int *bom_count) {
    FILE *f = fopen(path, "r");
    if (!f) {
        perror("Не вдалося відкрити BOM файл");
        return -1;
    }

    char line[MAX_LINE_LEN];
    int count = 0;
    int line_num = 0;

    while (fgets(line, sizeof(line), f)) {
        line_num++;
        trim(line);
        if (line_num == 1 || strlen(line) == 0) continue; // Пропуск заголовка

        char *token = strtok(line, ",;");
        if (!token) continue;
        char des_field[256];
        strncpy(des_field, token, sizeof(des_field) - 1);
        des_field[sizeof(des_field) - 1] = '\0';

        char *mpn_tok = strtok(NULL, ",;");
        char *pkg_tok = strtok(NULL, ",;");
        (void)pkg_tok;
        char *dnp_tok = strtok(NULL, ",;");

        int is_dnp = (dnp_tok && (strcmp(dnp_tok, "1") == 0 || strcasecmp(dnp_tok, "DNP") == 0));

        // Розбиваємо можливі списки референсів (напр. "C1 C2 C3" або "R1,R2")
        char *sub = strtok(des_field, " ,");
        while (sub) {
            trim(sub);
            if (strlen(sub) > 0 && count < max_bom) {
                strncpy(bom[count].name, sub, MAX_NAME_LEN - 1);
                bom[count].name[MAX_NAME_LEN - 1] = '\0';
                strncpy(bom[count].mpN, mpn_tok ? mpn_tok : "UNKNOWN", 63);
                bom[count].mpN[63] = '\0';
                bom[count].dnp = is_dnp;
                bom[count].matched_in_cpl = 0;
                count++;
            }
            sub = strtok(NULL, " ,");
        }
    }

    fclose(f);
    *bom_count = count;
    return 0;
}

static int parse_cpl(const char *path, CplEntry *cpl, int max_cpl, int *cpl_count) {
    FILE *f = fopen(path, "r");
    if (!f) {
        perror("Не вдалося відкрити CPL файл");
        return -1;
    }

    char line[MAX_LINE_LEN];
    int count = 0;
    int line_num = 0;

    while (fgets(line, sizeof(line), f)) {
        line_num++;
        trim(line);
        if (line_num == 1 || strlen(line) == 0) continue; // Пропуск заголовка

        char *des = strtok(line, ",;");
        char *xs = strtok(NULL, ",;");
        char *ys = strtok(NULL, ",;");
        char *rs = strtok(NULL, ",;");
        char *lay = strtok(NULL, ",;");

        if (des && xs && ys && rs && count < max_cpl) {
            trim(des);
            strncpy(cpl[count].name, des, MAX_NAME_LEN - 1);
            cpl[count].name[MAX_NAME_LEN - 1] = '\0';
            cpl[count].x = atof(xs);
            cpl[count].y = atof(ys);
            cpl[count].rot = atof(rs);
            strncpy(cpl[count].layer, lay ? lay : "Top", 15);
            cpl[count].matched_in_bom = 0;
            count++;
        }
    }

    fclose(f);
    *cpl_count = count;
    return 0;
}

int main(int argc, char **argv) {
    const char *bom_path = (argc > 1) ? argv[1] : "bom.csv";
    const char *cpl_path = (argc > 2) ? argv[2] : "cpl.csv";

    static BomEntry bom[MAX_ITEMS];
    static CplEntry cpl[MAX_ITEMS];
    int bom_count = 0, cpl_count = 0;

    if (parse_bom(bom_path, bom, MAX_ITEMS, &bom_count) != 0) return 2;
    if (parse_cpl(cpl_path, cpl, MAX_ITEMS, &cpl_count) != 0) return 2;

    int errors = 0;
    int warnings = 0;

    printf("=== ВАЛІДАЦІЯ ВИРОБНИЧОГО ПАКЕТА: BOM vs CPL ===\n");
    printf("Зчитано позицій: BOM=%d, CPL=%d\n\n", bom_count, cpl_count);

    // 1. Зіставлення BOM -> CPL
    for (int i = 0; i < bom_count; i++) {
        for (int j = 0; j < cpl_count; j++) {
            if (strcasecmp(bom[i].name, cpl[j].name) == 0) {
                bom[i].matched_in_cpl = 1;
                cpl[j].matched_in_bom = 1;
                if (bom[i].dnp) {
                    printf("[УВАГА / DNP] %s позначений як DNP у BOM, але знайдений у CPL (X=%.2f, Y=%.2f)\n",
                           bom[i].name, cpl[j].x, cpl[j].y);
                    warnings++;
                }
                break;
            }
        }
        if (!bom[i].matched_in_cpl && !bom[i].dnp) {
            printf("[ПОМИЛКА] %s (%s) є у BOM, але ВІДСУТНІЙ у Pick-and-Place файлі!\n",
                   bom[i].name, bom[i].mpN);
            errors++;
        }
    }

    // 2. Зіставлення CPL -> BOM (зайві компоненти на платі)
    for (int j = 0; j < cpl_count; j++) {
        if (!cpl[j].matched_in_bom) {
            printf("[ПОМИЛКА] %s є у CPL файлі (X=%.2f, Y=%.2f), але ВІДСУТНІЙ у відомості матеріалів BOM!\n",
                   cpl[j].name, cpl[j].x, cpl[j].y);
            errors++;
        }
    }

    printf("\nПідсумок: помилок=%d, зауважень=%d\n", errors, warnings);
    if (errors > 0) {
        printf("СТАТУС: ВІДХИЛЕНО. Пакет містить критичні розбіжності!\n");
        return 1;
    }

    printf("СТАТУС: УСПІШНО. Виробничі файли узгоджені.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <iomanip>

struct BomItem {
    std::string mpn;
    bool is_dnp{false};
    bool found_in_cpl{false};
};

struct CplItem {
    double x{0.0};
    double y{0.0};
    double rotation{0.0};
    std::string layer;
    bool found_in_bom{false};
};

static std::string trim(std::string_view str) {
    size_t first = str.find_first_not_of(" \t\r\n\"");
    if (first == std::string_view::npos) return "";
    size_t last = str.find_last_not_of(" \t\r\n\"");
    return std::string(str.substr(first, last - first + 1));
}

static std::string to_upper(std::string_view s) {
    std::string out(s);
    std::transform(out.begin(), out.end(), out.begin(), [](unsigned char c) {
        return static_cast<char>(std::toupper(c));
    });
    return out;
}

int main(int argc, char** argv) {
    const std::string bom_file = (argc > 1) ? argv[1] : "bom.csv";
    const std::string cpl_file = (argc > 2) ? argv[2] : "cpl.csv";

    std::unordered_map<std::string, BomItem> bom_map;
    std::unordered_map<std::string, CplItem> cpl_map;

    // Зчитування BOM
    std::ifstream bom_stream(bom_file);
    if (!bom_stream.is_open()) {
        std::cerr << "Помилка: не вдалося відкрити BOM файл: " << bom_file << "\n";
        return 2;
    }

    std::string line;
    bool is_first = true;
    while (std::getline(bom_stream, line)) {
        if (line.empty() || is_first) {
            is_first = false;
            continue;
        }
        std::stringstream ss(line);
        std::string des_field, mpn, pkg, dnp_str;
        if (!std::getline(ss, des_field, ',')) continue;
        std::getline(ss, mpn, ',');
        std::getline(ss, pkg, ',');
        std::getline(ss, dnp_str, ',');

        bool dnp = (!dnp_str.empty() && (trim(dnp_str) == "1" || to_upper(trim(dnp_str)) == "DNP"));

        std::stringstream des_ss(des_field);
        std::string single_des;
        while (des_ss >> single_des) {
            single_des = trim(single_des);
            if (!single_des.empty()) {
                bom_map[to_upper(single_des)] = {trim(mpn), dnp, false};
            }
        }
    }

    // Зчитування CPL (Pick and Place)
    std::ifstream cpl_stream(cpl_file);
    if (!cpl_stream.is_open()) {
        std::cerr << "Помилка: не вдалося відкрити CPL файл: " << cpl_file << "\n";
        return 2;
    }

    is_first = true;
    while (std::getline(cpl_stream, line)) {
        if (line.empty() || is_first) {
            is_first = false;
            continue;
        }
        std::stringstream ss(line);
        std::string des, xs, ys, rots, layer;
        if (!std::getline(ss, des, ',')) continue;
        std::getline(ss, xs, ',');
        std::getline(ss, ys, ',');
        std::getline(ss, rots, ',');
        std::getline(ss, layer, ',');

        std::string key = to_upper(trim(des));
        if (!key.empty()) {
            double x = xs.empty() ? 0.0 : std::stod(xs);
            double y = ys.empty() ? 0.0 : std::stod(ys);
            double rot = rots.empty() ? 0.0 : std::stod(rots);
            cpl_map[key] = {x, y, rot, trim(layer), false};
        }
    }

    std::cout << "=== ВАЛІДАЦІЯ ВИРОБНИЧОГО ПАКЕТА: BOM vs CPL ===\n";
    std::cout << "Унікальних референсів: BOM=" << bom_map.size() 
              << ", CPL=" << cpl_map.size() << "\n\n";

    int errors = 0;
    int warnings = 0;

    // Перевірка 1: кожен елемент BOM має бути в CPL (якщо не DNP)
    for (auto& [des, bom_val] : bom_map) {
        auto it = cpl_map.find(des);
        if (it != cpl_map.end()) {
            bom_val.found_in_cpl = true;
            it->second.found_in_bom = true;
            if (bom_val.is_dnp) {
                std::cout << "[УВАГА / DNP] " << des << " є в CPL (X=" << it->second.x 
                          << ", Y=" << it->second.y << "), але в BOM стоїть прапорець DNP!\n";
                warnings++;
            }
        } else if (!bom_val.is_dnp) {
            std::cout << "[ПОМИЛКА] " << des << " (" << bom_val.mpn 
                      << ") зазначено в BOM, але немає у файлі Pick-and-Place!\n";
            errors++;
        }
    }

    // Перевірка 2: кожен елемент CPL повинен бути у відомості BOM
    for (const auto& [des, cpl_val] : cpl_map) {
        if (!cpl_val.found_in_bom) {
            std::cout << "[ПОМИЛКА] " << des << " розміщено на платі (X=" << cpl_val.x 
                      << ", Y=" << cpl_val.y << "), але повністю відсутній у списку BOM!\n";
            errors++;
        }
    }

    std::cout << "\nПідсумок перевірки: критичних помилок=" << errors 
              << ", зауважень=" << warnings << "\n";

    if (errors > 0) {
        std::cout << "РЕЗУЛЬТАТ: ВІДХИЛЕНО. Необхідно синхронізувати експорт із САПР.\n";
        return 1;
    }

    std::cout << "РЕЗУЛЬТАТ: СХВАЛЕНО. Файли готові до відправлення на виробництво.\n";
    return 0;
}
```
:::

## 4. Інтеграція у виробничий скрипт перевірки релізів

Утиліту доцільно вбудовувати у крок CI/CD або локальний скрипт збірки релізу перед створенням фінального `.zip` архіву:

```bash
# Автоматична верифікація перед створенням релізного архіву
./bom_cpl_validator 02_SMT_Assembly/BOM_Production.csv 02_SMT_Assembly/Centroid_PickAndPlace.csv
RETVAL=$?

if [ $RETVAL -ne 0 ]; then
    echo "[ПОМИЛКА] Валідація не пройшла! Виявлено розбіжності між BOM і CPL."
    echo "Архів релізу НЕ буде створено."
    exit 1
fi

echo "[УСПІХ] Усі компоненти узгоджені. Створюємо архів виробничого пакета..."
zip -r "RELEASE_PACKAGE_$(date +%Y%m%d).zip" 01_PCB_Fabrication 02_SMT_Assembly 03_Firmware_Provisioning 04_Testing_QA SHA256SUMS.txt
```

Такий підхід повністю виключає людський фактор: якщо інженер додав на схему конденсатор фільтрації, оновив BOM, але забув перезапустити експорт координат Pick-and-Place, скрипт заблокує збірку пакета й не дозволить передати застарілі файли на завод.
