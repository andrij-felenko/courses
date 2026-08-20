# ⚙️ Побудова графа стовпчикового lineage через розбір SQL AST

Статичний аналіз SQL-запитів є найдешевшим, найшвидшим та найбільш масштабованим способом отримання графа залежностей між стовпцями (англ. *Column-Level Lineage*). Він не вимагає прямого підключення до працюючої бази даних, наявності прав адміністратора на читання виробничих таблиць чи фактичного виконання ресурсомістких обчислень. Замість виконання запиту аналізатор розбирає вихідний текст у структуру синтаксичного дерева (англ. *Abstract Syntax Tree* — AST), зіставляє вирази проекцій у секції `SELECT` із вхідними полями базових таблиць і будує орієнтований ациклічний граф походження даних.

---

### Архітектура та етапи розбору синтаксичного дерева

Процес побудови графа стовпчикового походження розбивається на п'ять строго визначених послідовних кроків:

```
   SQL Текст
      │
      ▼
 ┌───────────────┐      ┌─────────────────────────┐
 │  SQL Парсер   │ ───► │  Синтаксичне дерево AST │
 └───────────────┘      └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │ Резолюція CTE й аліасів │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │ Трасування виразів      │
                        │ (Проекції, агрегати)    │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │ Побудова графа стовпців │
                        │  (Column Lineage Graph) │
                        └─────────────────────────┘
```

1. **Лексичний та синтаксичний розбір (Parsing):** перетворення плоского рядка SQL-запиту в ієрархічне синтаксичне дерево. Кожен оператор (`SELECT`, `FROM`, `JOIN`, `WHERE`, `GROUP BY`) стає вузлом дерева, а вирази над стовпцями — дочірніми гілками. На цьому етапі синтаксичний аналізатор нормалізує діалектні відмінності (наприклад, специфічні лапки для екранування імен полів у PostgreSQL, Snowflake чи BigQuery).
2. **Створення таблиці символів та резолюція CTE (Common Table Expressions):** виділення блоків `WITH name AS (...)`. Тіло кожного CTE парситься рекурсивно як автономний підзапит, формуючи віртуальну таблицю в локальному просторі імен, яка потім підставляється у місця її виклику.
3. **Резолюція аліасів таблиць (Table Aliasing):** виявлення зв'язків між короткими псевдонімами та повними іменами фізичних таблиць у секціях `FROM` та `JOIN` (наприклад, конструкція `FROM raw_orders AS o` зв'язує псевдонім `o` з базовою таблицею `raw_orders`).
4. **Трасування проекцій та класифікація трансформацій:** для кожного елемента у списку `SELECT` вилучаються всі ідентифікатори стовпців, що входять до математичних виразів, агрегатних функцій (`SUM`, `AVG`), віконних функцій (`OVER (PARTITION BY ... ORDER BY ...)`) чи конструкцій умовного вибору (`CASE WHEN ... THEN ... ELSE ... END`). Визначається тип зв'язку: пряме копіювання (`IDENTITY`), агрегація (`AGGREGATION`) або складне перетворення (`TRANSFORMATION`).
5. **Формування ребер графа залежностей:** створення орієнтованих дуг від кожного виявленого вхідного стовпця джерела `source_table.source_column` до цільового поля створюваної таблиці `target_table.target_column`. Кожне ребро супроводжується метаданими: тип трансформації, вихідний SQL-вираз та ознака прямого чи непрямого предикатного впливу.

---

### Робоча реалізація екстрактора

Нижче наведено повнофункціональний приклад екстрактора стовпчикового лініджу двома мовами: на Python (типова мова конвеєрів даних та оркестрації) та високоефективному ідіоматичному C++20 (для високонавантажених сервісів індексації метаданих).

:::tabs
```py
from dataclasses import dataclass, field
from typing import Dict, List, Set
import re

@dataclass
class ColumnDependency:
    target_table: str
    target_column: str
    source_table: str
    source_column: str
    expression_type: str = "DIRECT"

class SimpleSQLLineageExtractor:
    """Екстрактор стовпчикового lineage для запитів із CTE та аліасами."""
    
    def __init__(self):
        self.dependencies: List[ColumnDependency] = []
        self.table_aliases: Dict[str, str] = {}
        self.cte_definitions: Dict[str, str] = {}

    def extract(self, sql_query: str, target_table_name: str) -> List[ColumnDependency]:
        self.dependencies.clear()
        self.table_aliases.clear()
        self.cte_definitions.clear()
        
        # 1. Очищення коментарів та нормалізація пробілів
        clean_sql = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
        clean_sql = " ".join(clean_sql.split())
        
        # 2. Виділення CTE: WITH name AS (SELECT ...)
        cte_matches = re.finditer(r'WITH\s+([a-zA-Z_0-9]+)\s+AS\s*\((.*?)\)\s*(SELECT.*)', clean_sql, re.IGNORECASE)
        main_query = clean_sql
        for match in cte_matches:
            cte_name = match.group(1).strip()
            cte_body = match.group(2).strip()
            main_query = match.group(3).strip()
            self.cte_definitions[cte_name] = cte_body

        # 3. Витяг аліасів таблиць з секцій FROM та JOIN
        from_match = re.search(r'FROM\s+([a-zA-Z0-9_\.]+)(?:\s+(?:AS\s+)?([a-zA-Z0-9_]+))?', main_query, re.IGNORECASE)
        if from_match:
            real_tbl = from_match.group(1)
            alias = from_match.group(2) or real_tbl
            self.table_aliases[alias] = real_tbl

        join_matches = re.finditer(r'JOIN\s+([a-zA-Z0-9_\.]+)(?:\s+(?:AS\s+)?([a-zA-Z0-9_]+))?', main_query, re.IGNORECASE)
        for jm in join_matches:
            real_tbl = jm.group(1)
            alias = jm.group(2) or real_tbl
            self.table_aliases[alias] = real_tbl

        # 4. Витяг виразів секції SELECT ... FROM
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', main_query, re.IGNORECASE)
        if not select_match:
            return self.dependencies

        select_body = select_match.group(1).strip()
        projections = self._split_projections(select_body)

        for proj in projections:
            self._analyze_projection(proj, target_table_name)

        return self.dependencies

    def _split_projections(self, select_str: str) -> List[str]:
        """Розбиває вирази проекцій з урахуванням вкладених дужок функцій."""
        items = []
        current = []
        depth = 0
        for char in select_str:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == ',' and depth == 0:
                items.append("".join(current).strip())
                current.clear()
                continue
            current.append(char)
        if current:
            items.append("".join(current).strip())
        return items

    def _analyze_projection(self, proj_expr: str, target_table: str):
        # Визначення імені вихідного стовпця (аліас через AS або пряме ім'я)
        as_match = re.search(r'\s+AS\s+([a-zA-Z0-9_]+)$', proj_expr, re.IGNORECASE)
        if as_match:
            target_col = as_match.group(1)
            expr_body = proj_expr[:as_match.start()].strip()
        else:
            target_col = proj_expr.split('.')[-1].strip()
            expr_body = proj_expr

        # Класифікація типу перетворення
        expr_type = "AGGREGATION" if re.search(r'\b(SUM|AVG|COUNT|MIN|MAX)\b', expr_body, re.IGNORECASE) else "TRANSFORM"
        if re.match(r'^[a-zA-Z0-9_\.]+$', expr_body):
            expr_type = "IDENTITY"

        # Пошук аргументів-стовпців формату alias.column_name
        col_refs = re.finditer(r'([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)', expr_body)
        found_sources = False
        for cr in col_refs:
            tbl_alias = cr.group(1)
            src_col = cr.group(2)
            src_table = self.table_aliases.get(tbl_alias, tbl_alias)
            self.dependencies.append(ColumnDependency(
                target_table=target_table,
                target_column=target_col,
                source_table=src_table,
                source_column=src_col,
                expression_type=expr_type
            ))
            found_sources = True

        if not found_sources and '.' not in expr_body:
            first_table = next(iter(self.table_aliases.values())) if self.table_aliases else "unknown"
            self.dependencies.append(ColumnDependency(
                target_table=target_table,
                target_column=target_col,
                source_table=first_table,
                source_column=target_col,
                expression_type=expr_type
            ))

if __name__ == "__main__":
    extractor = SimpleSQLLineageExtractor()
    sql = """
    SELECT
        o.order_id AS order_identifier,
        SUM(o.amount / fx.rate) AS total_revenue_usd,
        o.status
    FROM raw.orders AS o
    JOIN ref.fx_rates AS fx ON o.currency = fx.currency_code
    WHERE o.status = 'COMPLETED'
    """
    
    results = extractor.extract(sql, target_table_name="mart.fct_revenue")
    for dep in results:
        print(f"[{dep.expression_type}] {dep.source_table}.{dep.source_column} -> {dep.target_table}.{dep.target_column}")
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <regex>
#include <memory>

struct ColumnDependency {
    std::string target_table;
    std::string target_column;
    std::string source_table;
    std::string source_column;
    std::string expression_type;
};

class SQLLineageGraph {
public:
    std::vector<ColumnDependency> extract_lineage(
        std::string_view sql_query,
        std::string_view target_table
    ) {
        std::vector<ColumnDependency> results;
        std::unordered_map<std::string, std::string> aliases;

        std::string sql(sql_query);

        // 1. Пошук таблиць у секціях FROM та JOIN
        std::regex from_regex(R"(FROM\s+([a-zA-Z0-9_\.]+)(?:\s+(?:AS\s+)?([a-zA-Z0-9_]+))?)", std::regex::icase);
        std::smatch match;
        if (std::regex_search(sql, match, from_regex)) {
            std::string real_tbl = match[1].str();
            std::string alias = match[2].matched ? match[2].str() : real_tbl;
            aliases[alias] = real_tbl;
        }

        std::regex join_regex(R"(JOIN\s+([a-zA-Z0-9_\.]+)(?:\s+(?:AS\s+)?([a-zA-Z0-9_]+))?)", std::regex::icase);
        auto join_begin = std::sregex_iterator(sql.begin(), sql.end(), join_regex);
        auto join_end = std::sregex_iterator();
        for (auto it = join_begin; it != join_end; ++it) {
            std::string real_tbl = (*it)[1].str();
            std::string alias = (*it)[2].matched ? (*it)[2].str() : real_tbl;
            aliases[alias] = real_tbl;
        }

        // 2. Пошук виразів у SELECT ... FROM
        std::regex select_regex(R"(SELECT\s+([\s\S]*?)\s+FROM)", std::regex::icase);
        if (std::regex_search(sql, match, select_regex)) {
            std::string select_clause = match[1].str();
            auto projections = split_projections(select_clause);

            for (const auto& proj : projections) {
                analyze_projection(proj, target_table, aliases, results);
            }
        }

        return results;
    }

private:
    std::vector<std::string> split_projections(std::string_view clause) {
        std::vector<std::string> out;
        std::string cur;
        int depth = 0;
        for (char c : clause) {
            if (c == '(') ++depth;
            else if (c == ')') --depth;
            else if (c == ',' && depth == 0) {
                if (!cur.empty()) out.push_back(trim(cur));
                cur.clear();
                continue;
            }
            cur += c;
        }
        if (!cur.empty()) out.push_back(trim(cur));
        return out;
    }

    void analyze_projection(
        const std::string& proj,
        std::string_view target_table,
        const std::unordered_map<std::string, std::string>& aliases,
        std::vector<ColumnDependency>& out
    ) {
        std::regex as_regex(R"(\s+AS\s+([a-zA-Z0-9_]+)$)", std::regex::icase);
        std::smatch match;
        std::string target_col;
        std::string expr_body = proj;

        if (std::regex_search(proj, match, as_regex)) {
            target_col = match[1].str();
            expr_body = proj.substr(0, match.position());
        } else {
            auto dot_pos = proj.rfind('.');
            target_col = (dot_pos != std::string::npos) ? proj.substr(dot_pos + 1) : proj;
        }

        std::string expr_type = "TRANSFORM";
        if (std::regex_search(expr_body, std::regex(R"(\b(SUM|AVG|COUNT|MIN|MAX)\b)", std::regex::icase))) {
            expr_type = "AGGREGATION";
        } else if (std::regex_match(expr_body, std::regex(R"(^[a-zA-Z0-9_\.]+$)"))) {
            expr_type = "IDENTITY";
        }

        std::regex col_ref_regex(R"(([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+))");
        auto it_begin = std::sregex_iterator(expr_body.begin(), expr_body.end(), col_ref_regex);
        auto it_end = std::sregex_iterator();

        for (auto it = it_begin; it != it_end; ++it) {
            std::string alias = (*it)[1].str();
            std::string src_col = (*it)[2].str();
            std::string src_tbl = aliases.contains(alias) ? aliases.at(alias) : alias;

            out.push_back(ColumnDependency{
                .target_table = std::string(target_table),
                .target_column = target_col,
                .source_table = src_tbl,
                .source_column = src_col,
                .expression_type = expr_type
            });
        }
    }

    static std::string trim(std::string_view s) {
        size_t start = s.find_first_not_of(" \t\n\r");
        if (start == std::string::npos) return "";
        size_t end = s.find_last_not_of(" \t\n\r");
        return std::string(s.substr(start, end - start + 1));
    }
};

int main() {
    SQLLineageGraph graph;
    std::string query = 
        "SELECT o.order_id AS id, SUM(o.amount / fx.rate) AS revenue_usd "
        "FROM raw.orders AS o "
        "JOIN ref.fx_rates AS fx ON o.currency = fx.code";

    auto deps = graph.extract_lineage(query, "mart.fct_revenue");
    for (const auto& d : deps) {
        std::cout << "[" << d.expression_type << "] " 
                  << d.source_table << "." << d.source_column << " -> "
                  << d.target_table << "." << d.target_column << "\n";
    }
    return 0;
}
```
:::

---

### Обхід графа: пошук першопричини (Upstream) та оцінка впливу (Downstream)

Отриманий список залежностей `ColumnDependency` утворює орієнтований ациклічний граф (DAG), де вершинами є повністю кваліфіковані імена полів `schema.table.column`, а ребрами — спрямовані трансформації.

Над цим графом виконуються два класичних алгоритми обходу:

1. **Аналіз першопричин (Upstream Root-Cause Analysis via BFS/DFS):**
   Якщо аналітик виявляє некоректне значення у звітному полі `mart.fct_revenue.revenue_usd`, алгоритм запускає пошук у ширину (BFS) у зворотньому напрямку ребер. Він рекурсивно відвідує всі батьківські стовпці, доки не досягне первинних незмінних джерел (шару сирих даних `raw.orders.amount` та `ref.fx_rates.rate`). Це дозволяє за секунди локалізувати помилкове джерело без ручного перегляду коду сотень проміжних скриптів.

2. **Оцінка впливу змін (Downstream Impact Analysis):**
   Перед тим як інженер бази даних виконає міграцію `ALTER TABLE raw.orders DROP COLUMN currency`, граф обходиться у прямому напрямку ребер від модифікованого поля. Алгоритм збирає множину всіх залежних стовпців у вітринах та BI-дашбордах. Якщо хоча б один критичний фінансовий звіт знаходиться у зоні досяжності, автоматизований CI/CD-пайплайн блокує злиття змін у головну гілку репозиторію.

---

### Алгоритмічна складність та інженерні пастки розбору

Часова складність розбору синтаксичного дерева SQL-запиту є лінійною від довжини тексту запиту `O(N)`, де `N` — кількість лексем (токенів). Побудова та обхід графа залежностей для результуючої таблиці займає час `O(V + E)`, де `V` — множина унікальних стовпців і таблиць, а `E` — кількість виявлених ребер-залежностей. Просторова складність оцінюється як `O(V + E)` для збереження ребер у пам'яті графової структури.

Під час промислового використання статичних аналізаторів розробники стикаються з п'ятьма типовими інженерними викликами:

1. **Неоднозначні некваліфіковані стовпці (Unqualified Column Ambiguity):** якщо запит містить вибірку `SELECT amount, user_id FROM orders JOIN payments ON ...`, де стовпець `amount` не має явного префіксу таблиці (`orders.amount`), синтаксичний парсер без підключення до каталогу схем бази даних не може однозначно визначити, якій саме з двох з'єднаних таблиць належить це поле. Для вирішення цієї проблеми парсер інтегрують із реєстром схем (Schema Registry), який на етапі аналізу постачає список полів для кожної таблиці.
2. **Динамічне розкриття зірочки (`SELECT *`):** вираз `SELECT *` створює набір ребер, склад якого залежить від поточного фізичного стану схеми на момент виконання. Якщо у первинній таблиці з'являється новий стовпець, статичний граф без регулярного оновлення каталогу метаданих втрачає актуальність.
3. **Затінення імен у багаторівневих CTE (CTE Variable Shadowing):** якщо внутрішній підзапит або вираз `WITH` визначає ім'я таблиці, ідентичне фізичній таблиці у сховищі, аналізатор зобов'язаний суворо ізолювати локальну область видимості (Scope). Помилка пріоритету призводить до хибного зв'язування стовпців із глобальною таблицею замість проміжного CTE.
4. **Непрозорість користувацьких функцій (UDF Black Boxes):** якщо перетворення записано як виклик скомпільованої функції на Python чи Java (`SELECT my_custom_udf(col_a, col_b) AS col_c`), SQL-парсер фіксує лише факт передачі аргументів `col_a, col_b -> col_c`, але не бачить внутрішньої логіки розгалуження чи зовнішніх викликів. Для повного простеження такі вузли маркуються як непрозорі й доповнюються рантайм-інструментацією обчислювального рушія.
5. **Віконні функції та аналітичні вирази:** у виразах на зразок `ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC)` стовпці `user_id` та `created_at` не передають свої числові значення у вихідне поле рангу, але повністю визначають порядок його обчислення. Екстрактор повинен класифікувати такий зв'язок як залежність за керуванням (англ. *Control Dependency*), а не прямий потік даних.
