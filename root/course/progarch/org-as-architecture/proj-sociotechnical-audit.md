# ⚙️ Практична автоматизація соціотехнічного аудиту кодової бази

Для запобігання соціотехнічному незбігу архітектор не може покладатися лише на суб'єктивні відчуття, наративи менеджменту чи усні заяви про автономність команд. У цій вставці розкрито математичний апарат, алгоритми аналізу історії систем керування версіями (VCS/Git) та повноцінний працездатний інструментарій для автоматичного обчислення метрик соціотехнічного зсуву та ерозії володіння кодом.

---

## Чому аналіз Git-історії дзеркалить реальну соціотехнічну структуру

Традиційні оргчарти та схеми підпорядкованості в HR-системах відображають лише адміністративні ієрархії: хто кого наймає, хто підписує відпустки та за якими підрозділами закріплені бюджети. Вони практично нічого не кажуть про реальний потік інженерних рішень та щоденне спілкування розробників.

Реальний соціальний граф організації живе в історії репозиторію Git. Кожен комміт, Pull Request, авторинґ рядка коду (`git blame`) та перехресна зміна файлів у межах однієї транзакції закарбовують фактичну комунікаційну та операційну топологію. Якщо оргчарт каже, що Команда A володіє сервісом `PaymentService`, але аналіз `git log` виявляє, що 60% правок у репозиторії виконуються інженерами з Команди B, реальним соціотехнічним господарем системи є Команда B, або ж сервіс перебуває у стані руйнівного розриву володіння.

---

## Математичний апарат соціотехнічних метрик

Для числового вимірювання відповідності коду та організаційної структури застосовуються три фундаментальні метрики.

### 1. Коефіцієнт володіння кодом (Team Ownership Ratio, TOR)

Метрика TOR визначає рівень концентрації відповідальності за конкретний файл, модуль або сервіс у руках основної команди-господаря. Вона обчислюється як відношення кількості змінених рядків (доданих і видалених) членами основної команди до загального обсягу змін у даному артефакті за визначений часовий інтервал (зазвичай 90 або 180 днів):

```
TOR(f) = (∑_{c ∈ Commits(f, Team_main)} Changes(c)) / (∑_{c ∈ Commits(f, All)} Changes(c))
```

*Нормативні значення TOR:*
- `TOR ≥ 0.80` (80% і більше): **Здорове володіння.** Модуль повністю контролюється автономною Stream-командою. Втрата контексту мінімальна.
- `0.50 ≤ TOR < 0.80`: **Слабке володіння / InnerSource.** Модуль має команду-хранителя, але відчуває високе навантаження сторонніх контриб'юторів. Потрібен контроль якості PR.
- `TOR < 0.50`: **Трагедія спільного володіння (Tragedy of the Commons).** Жодна команда не контролює модуль. Високий ризик накопичення технічного боргу та виникнення прихованих дефектів.

### 2. Індекс соціотехнічного незбігу (Conway Mismatch Index, CMI)

Метрика CMI оцінює глобальний стан всієї кодової бази системи. Вона обчислюється як частка файлів у проекті, які впродовж розрахункового періоду зазнали суттєвих правок від інженерів з двох або більше різних команд:

```
CMI = |{ f ∈ Files | DistinctTeams(f) > 1 }| / |Files|
```

*Нормативні значення CMI:*
- `CMI ≤ 0.10` (менше 10%): **Соціотехнічна гармонія.** Межі коду відповідають межам команд.
- `0.10 < CMI ≤ 0.20`: **Помірне тертя.** Окремі сервіси потребують рефакторингу або уточнення меж контекстів.
- `CMI > 0.20` (понад 20%): **Критичний розрив.** Система деградує у розподілений моноліт. Необхідно терміново застосувати зворотний маневр Конвея.

### 3. Соціотехнічна зв'язаність (Sociotechnical Coupling Ratio, SCR)

Метрика SCR оцінює логічне зчеплення між файлами, які належать різним командам. Якщо при зміні файла `A` (яким володіє Команда 1) у більшості коммітів або PR одночасно змінюється файл `B` (яким володіє Команда 2), між цими файлами існує прихована соціотехнічна залежність:

```
SCR(A, B) = |Commits(A ∩ B)| / |Commits(A ∪ B)|
```

Якщо `SCR(A, B) > 0.40` для файлів із різних сервісів, це означає, що розподілена архітектура є фікцією: зміни в одному сервісі силоміць розривають межі іншого.

---

## Алгоритми та крайові випадки аудиту

Під час практичної автоматизації аудиту необхідно враховувати низку крайових випадків та спотворень даних:

1. **Великі автоматизовані рефакторинги та форматування коду:** Масові правки (наприклад, запуск `clang-format`, `prettier` або оновлення заголовків ліцензій) можуть штучно змінити баланс правок. Алгоритм аудит-інструменту мусить фільтрувати комміти від ботів-форматувальників або ігнорувати комміти, де змінюється понад 50 файлів одночасно.
2. **Ротація інженерів та зміна команд:** Якщо розробник переходить із Команди A в Команду B, його історичні комміти повинні відноситися до тієї команди, у якій він перебував на момент здійснення комміту. Для цього конфігурація соціо-структури мусить підтримувати часові інтервали авторизації або зчитувати файли псевдонімів `.mailmap`.
3. **Злиття гілок (Merge Commits):** Комміти злиття можуть дублювати зміни. Аналіз повинен проводитися по лінійній історії коммітів (`git log --first-parent` або через розпакування `--no-merges --numstat`).
4. **Бінарні файли та автоматично згенерований код:** Файли автогенерації (protobuf, gRPC stubs, ORM-міграції) створюють хибні сплески правок. Вони виключаються за списком масок `.gitattributes` чи шаблонами глобів.

---

## Матриця перехресного міжкомандного тертя (Cross-Team Friction Matrix)

На основі розрахованих метрик алгоритм будує симетричну матрицю міжкомандного тертя розміром `K × K`, де `K` — кількість розробницьких команд у компанії. Кожен елемент `M[i][j]` показує загальну кількість спільних коммітів або обсяг правок, виконаних Командою `i` у модулях, якими володіє Команда `j`:

```
Матриця міжкомандного тертя M[i][j] (обсяг правок у чужих модулях):

               TwinTeam   AutoTeam   EnergyTeam  PlatformTeam
TwinTeam      [  94.5%       3.2%       1.8%        0.5%   ]
AutoTeam      [   4.1%      89.2%       5.7%        1.0%   ]
EnergyTeam    [   2.0%       4.8%      92.1%        1.1%   ]
PlatformTeam  [   0.1%       0.2%       0.1%       99.6%   ]
```

Значення на головній діагоналі відображають коефіцієнт внутрішньокомандної автономності. Позадіагональні значення, що перевищують `5%`, вказують на конкретні зони міжкомандного тертя, де необхідно проводити рефакторинг API або зміну меж володіння.

---

## Практична реалізація утиліти соціотехнічного аудиту

Нижче наведено повноцінні працездатні реалізації інструменту соціотехнічного аудиту мовами Python, C та C++. Кожен варіант виконує читання потоку `git log`, обчислення метрик TOR і CMI та генерацію інженерного звіту.

:::tabs
```py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Утиліта аналізу соціотехнічного незбігу (Conway Mismatch Audit) мовою Python."""

import subprocess
import sys
import json
from collections import defaultdict
from typing import Dict, Set, Tuple

def parse_team_mapping(mapping_file: str) -> Dict[str, str]:
    """Зчитує відповідність email -> команда з JSON-файлу."""
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def analyze_git_history(team_map: Dict[str, str]) -> Tuple[Dict[str, Dict[str, int]], Dict[str, Set[str]]]:
    """Парсить git log та обчислює внесок кожної команди у файли."""
    cmd = ["git", "log", "--numstat", "--no-merges", "--format=COMMIT|%ae"]
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception as e:
        print(f"Помилка запуску git log: {e}", file=sys.stderr)
        sys.exit(1)

    file_team_lines: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    file_teams: Dict[str, Set[str]] = defaultdict(set)

    current_team = "Unknown"

    for line in process.stdout:
        line = line.strip()
        if not line:
            continue

        if line.startswith("COMMIT|"):
            email = line.split("|")[1].lower()
            current_team = team_map.get(email, "ExternalTeam")
        else:
            parts = line.split("\t")
            if len(parts) == 3:
                added, deleted, filepath = parts
                if added != "-" and deleted != "-":
                    changes = int(added) + int(deleted)
                    file_team_lines[filepath][current_team] += changes
                    file_teams[filepath].add(current_team)

    process.wait()
    return file_team_lines, file_teams

def calculate_cmi(file_team_lines: Dict[str, Dict[str, int]], file_teams: Dict[str, Set[str]]):
    """Обчислює метрики TOR та CMI й виводить соціотехнічний звіт."""
    total_files = len(file_teams)
    mismatched_files = 0

    print("=== СОЦІОТЕХНІЧНИЙ АУДИТ КОДОВОЇ БАЗИ (Python) ===")
    print(f"Загалом аналізовано файлів: {total_files}\n")

    for filepath, teams in file_teams.items():
        if len(teams) > 1:
            mismatched_files += 1

        lines_per_team = file_team_lines[filepath]
        total_changes = sum(lines_per_team.values())
        top_team, top_lines = max(lines_per_team.items(), key=lambda item: item[1])
        tor = top_lines / total_changes if total_changes > 0 else 0.0

        if tor < 0.60 and len(teams) > 1:
            print(f"[УВАГА: ТРАГЕДІЯ СПІЛЬНОГО] {filepath}")
            print(f"  Головний власник: {top_team} (TOR = {tor:.2%})")
            print(f"  Усі команди: {', '.join(teams)}\n")

    cmi = (mismatched_files / total_files) if total_files > 0 else 0.0
    print(f"Індекс соціотехнічного незбігу (CMI): {cmi:.2%}")
    if cmi > 0.15:
        print("РЕЗУЛЬТАТ: Небезпечно високий соціотехнічний розрив! Необхідний маневр Конвея.")
    else:
        print("РЕЗУЛЬТАТ: Соціотехнічний стан кодової бази в межах норми.")

if __name__ == "__main__":
    fake_map = {
        "alice@dh.org": "TwinTeam",
        "bob@dh.org": "AutomationTeam",
        "charlie@dh.org": "PlatformTeam"
    }
    lines, teams = analyze_git_history(fake_map)
    calculate_cmi(lines, teams)
```
```c
/* Утиліта аналізу соціотехнічного незбігу мовою C (POSIX API, чітке управління пам'яттю) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 1024
#define MAX_FILES 500

typedef struct {
    char filepath[256];
    char main_team[64];
    int main_team_changes;
    int total_changes;
    int distinct_teams_count;
} FileSociotechnicalStat;

static FileSociotechnicalStat g_stats[MAX_FILES];
static int g_stat_count = 0;

static FileSociotechnicalStat* find_or_create_file(const char* path) {
    for (int i = 0; i < g_stat_count; ++i) {
        if (strcmp(g_stats[i].filepath, path) == 0) {
            return &g_stats[i];
        }
    }
    if (g_stat_count < MAX_FILES) {
        FileSociotechnicalStat* st = &g_stats[g_stat_count++];
        strncpy(st->filepath, path, 255);
        st->filepath[255] = '\0';
        st->main_team[0] = '\0';
        st->main_team_changes = 0;
        st->total_changes = 0;
        st->distinct_teams_count = 1;
        return st;
    }
    return NULL;
}

int main(void) {
    FILE* fp = popen("git log --numstat --no-merges --format=COMMIT|%ae", "r");
    if (!fp) {
        perror("Не вдалося запустити git log");
        return 1;
    }

    char buffer[MAX_LINE];
    char current_team[64] = "Unknown";

    while (fgets(buffer, sizeof(buffer), fp)) {
        buffer[strcspn(buffer, "\r\n")] = 0;
        if (strlen(buffer) == 0) continue;

        if (strncmp(buffer, "COMMIT|", 7) == 0) {
            char* email = buffer + 7;
            if (strstr(email, "twin")) {
                strncpy(current_team, "TwinTeam", 63);
            } else if (strstr(email, "auto")) {
                strncpy(current_team, "AutoTeam", 63);
            } else {
                strncpy(current_team, "CoreTeam", 63);
            }
            current_team[63] = '\0';
        } else {
            int added = 0, deleted = 0;
            char path[256];
            if (sscanf(buffer, "%d\t%d\t%255s", &added, &deleted, path) == 3) {
                FileSociotechnicalStat* st = find_or_create_file(path);
                if (st) {
                    int changes = added + deleted;
                    st->total_changes += changes;
                    if (changes > st->main_team_changes) {
                        st->main_team_changes = changes;
                        strncpy(st->main_team, current_team, 63);
                        st->main_team[63] = '\0';
                    }
                }
            }
        }
    }
    pclose(fp);

    printf("=== ЗВІТ СОЦІОТЕХНІЧНОГО АУДИТУ (C-реалізація) ===\n");
    int mismatched = 0;
    for (int i = 0; i < g_stat_count; ++i) {
        double tor = (double)g_stats[i].main_team_changes / (g_stats[i].total_changes ? g_stats[i].total_changes : 1);
        if (tor < 0.60) {
            mismatched++;
            printf("Файл: %s | Головний власник: %s | TOR: %.2f%%\n",
                   g_stats[i].filepath, g_stats[i].main_team, tor * 100.0);
        }
    }
    double cmi = (double)mismatched / (g_stat_count ? g_stat_count : 1);
    printf("Аналізовано файлів: %d\n", g_stat_count);
    printf("Індекс соціотехнічного незбігу (CMI): %.2f%%\n", cmi * 100.0);

    return 0;
}
```
```cpp
// Утиліта аналізу соціотехнічного незбігу мовою C++20 (RAII, std::string_view, std::expected)
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <array>
#include <numeric>
#include <algorithm>
#include <expected>

struct FileTeamMetric {
    std::unordered_map<std::string, std::size_t> team_changes{};
    std::unordered_set<std::string> distinct_teams{};

    [[nodiscard]] std::size_t total_changes() const noexcept {
        std::size_t total = 0;
        for (const auto& [team, count] : team_changes) {
            total += count;
        }
        return total;
    }

    [[nodiscard]] std::pair<std::string_view, double> primary_owner() const noexcept {
        if (team_changes.empty()) return {"Unknown", 0.0};
        
        auto max_it = std::max_element(team_changes.begin(), team_changes.end(),
            [](const auto& a, const auto& b) { return a.second < b.second; });
        
        const double total = static_cast<double>(total_changes());
        const double tor = total > 0.0 ? static_cast<double>(max_it->second) / total : 0.0;
        return {max_it->first, tor};
    }
};

class SociotechnicalAuditor {
public:
    using TeamMap = std::unordered_map<std::string, std::string>;

    explicit SociotechnicalAuditor(TeamMap team_mapping) 
        : team_map_(std::move(team_mapping)) {}

    [[nodiscard]] std::expected<void, std::string> run_audit_stream(FILE* pipe) {
        if (!pipe) {
            return std::unexpected("Некоректний дескриптор потоку git log");
        }

        std::array<char, 1024> buffer{};
        std::string current_team = "Unknown";

        while (fgets(buffer.data(), static_cast<int>(buffer.size()), pipe)) {
            std::string_view line(buffer.data());
            if (line.back() == '\n') line.remove_suffix(1);
            if (line.back() == '\r') line.remove_suffix(1);
            if (line.empty()) continue;

            if (line.starts_with("COMMIT|")) {
                auto email = line.substr(7);
                auto it = team_map_.find(std::string(email));
                current_team = (it != team_map_.end()) ? it->second : "ExternalTeam";
            } else {
                parse_numstat_line(line, current_team);
            }
        }
        return {};
    }

    void print_report() const {
        std::cout << "=== СОЦІОТЕХНІЧНИЙ АУДИТ КОДОВОЇ БАЗИ (C++20) ===\n";
        std::size_t total_files = metrics_.size();
        std::size_t mismatched_files = 0;

        for (const auto& [filepath, metric] : metrics_) {
            if (metric.distinct_teams.size() > 1) {
                mismatched_files++;
            }
            auto [owner, tor] = metric.primary_owner();
            if (tor < 0.60 && metric.distinct_teams.size() > 1) {
                std::cout << "[УВАГА: НИЗЬКИЙ TOR] " << filepath 
                          << " | Головний власник: " << owner 
                          << " (" << (tor * 100.0) << "%)\n";
            }
        }

        const double cmi = total_files > 0 ? static_cast<double>(mismatched_files) / static_cast<double>(total_files) : 0.0;
        std::cout << "\nЗагалом файлів: " << total_files << "\n";
        std::cout << "Індекс соціотехнічного незбігу (CMI): " << (cmi * 100.0) << "%\n";
    }

private:
    void parse_numstat_line(std::string_view line, std::string_view current_team) {
        auto tab1 = line.find('\t');
        auto tab2 = line.find('\t', tab1 + 1);
        if (tab1 != std::string_view::npos && tab2 != std::string_view::npos) {
            auto added_str = line.substr(0, tab1);
            auto deleted_str = line.substr(tab1 + 1, tab2 - (tab1 + 1));
            auto path = line.substr(tab2 + 1);

            if (added_str != "-" && deleted_str != "-") {
                std::size_t changes = std::stoul(std::string(added_str)) + std::stoul(std::string(deleted_str));
                auto& metric = metrics_[std::string(path)];
                metric.team_changes[std::string(current_team)] += changes;
                metric.distinct_teams.insert(std::string(current_team));
            }
        }
    }

    TeamMap team_map_;
    std::unordered_map<std::string, FileTeamMetric> metrics_{};
};

int main() {
    SociotechnicalAuditor::TeamMap team_map{
        {"dev1@dh.org", "TwinTeam"},
        {"dev2@dh.org", "AutomationTeam"}
    };

    SociotechnicalAuditor auditor(std::move(team_map));
    
    // RAII для автоматичного закриття popen
    struct PipeCloser {
        void operator()(FILE* p) const { if (p) pclose(p); }
    };
    std::unique_ptr<FILE, PipeCloser> pipe(popen("git log --numstat --no-merges --format=COMMIT|%ae", "r"));

    if (auto res = auditor.run_audit_stream(pipe.get()); !res) {
        std::cerr << "Помилка аудиту: " << res.error() << '\n';
        return 1;
    }

    auditor.print_report();
    return 0;
}
```
:::

---

## Інтеграція аудиту у CI/CD конвеєри та соціотехнічний флайвіл

Автоматичне обчислення соціотехнічних метрик не повинно бути разовою процедурою під час кризи. Найкраща інженерна практика полягає в автоматичному запуску аналізатора на етапі CI/CD під час збирання релізів чи створення Pull Requests:

1. **Gate перевірки Pull Request:** Якщо PR вносить зміни у файли з низьким `TOR (< 0.50)` або розширює перелік команд-власників для кричущого модуля, CI-система автоматично залучає техліда команди-хранителя для обов'язкового схвалення (*Code Owners Integration*).
2. **Дашборд соціотехнічного здоров'я (Sociotechnical Fitness Dashboard):** Індекси CMI та TOR виводяться поруч із метриками надійності (SLO/SLI) та покриття коду тестами. Зростання CMI слугує підставою для закладання соціотехнічного рефакторингу в наступний інженерний спринт.
3. **Соціотехнічний флайвіл:** Низький CMI забезпечує чітку автономність команд -> висока автономність зменшує черги очікування -> короткі черги забезпечують низький Lead Time -> стабільний потік випуску фіч дозволяє безболісно адаптувати архітектуру під нові бізнес-потреби.
