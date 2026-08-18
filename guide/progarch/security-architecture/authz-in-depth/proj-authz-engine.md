# ⚙️ Реалізація рушія авторизації: від правил до реляційного графа

Для глибокого розуміння механіки контролю доступу декларативних вимов недостатньо — архітектору необхідно бачити алгоритмічний скелет обходу графа стосунків та оцінки атрибутивних правил. Ця вставка розбирає конструкцію гібридного рушія авторизації (ReBAC + ABAC) та надає його повністю працюючу реалізацію чотирма мовами програмування (Python, TypeScript, C++ та Go).

## 1. Концепція та двофазний алгоритм перевірки

Запропонований рушій поєднує високу швидкість обходу реляційного графа у стилі Google Zanzibar із гнучкістю контекстних правил ABAC. Перевірка доступу виконується у дві послідовні фази, що забезпечують мінімальну затримку при обробці запитів:

1. **Фаза 1: Реляційний обхід графа (ReBAC)**. Рушій з'ясовує, чи існує структурний зв'язок між суб'єктом та ресурсом у графі стосунків. Замість прямих порівнянь ідентифікаторів рушій підтримує **перезапис множин користувачів (Userset Rewriting)**. Наприклад, якщо запис у графі каже `camera:704#viewer@home:101#owner`, то для перевірки права перегляду камери рушій рекурсивно запускає перевірку «чи є суб'єкт власником будинку 101».
2. **Фаза 2: Контекстна перевірка атрибутів (ABAC)**. Якщо граф стосунків дав ствердну відповідь (`ALLOW`), рушій переходить до перевірки динамічних умов оточення (Environment attributes). У нашому прикладі це часове вікно дозволеного доступу (наприклад, з 08:00 до 22:00 для тимчасових гостей). Якщо суб'єкт не має реляційних прав, фаза оцінки атрибутів взагалі не викликається.

Такий поділ дозволяє відсікти понад 95% невалідних запитів на першому етапі без обчислення важких атрибутивних функцій чи виконання додаткових зовнішніх запитів.

---

## 2. Глибокий розбір механізму Userset Rewriting та крайових випадків

Перед тим як перейти до коду, розберімо алгоритмічні нюанси обходу графа стосунків, які критичні для побудови надійного продакшн-рушія:

### Запобігання циклічним посиланням у графі
У реальних системах корпоративні чи домашні групи можуть легко утворити цикл (наприклад, `group:engineering#member@group:tech-leads#member`, а `group:tech-leads#member@group:engineering#member`). Якщо обходити такий граф без збереження стану, рекурсивний алгоритм швидко вичерпає стек викликів і призведе до аварійного завершення процесу (`StackOverflowError` або `RecursionError`). 

Для захисту від зациклення рушій зберігає множину вже відвіданих станів у форматі `visited = { "object#relation@subject" }`. Якщо стан повертається повторно, гілка вважається тупиковою й відразу віддає `false`.

### Обмеження глибини рекурсії (Search Depth Limit)
Окрім виявлення прямих циклів, вкладені групи можуть формувати дуже довгі ланцюги (наприклад, 100 рівнів вкладеності організаційних підрозділів). Кожен рівень рекурсії вимагає виділення пам'яті на стеку. Зрілий PDP встановлює жорсткий ліміт глибини обходу (наприклад, `MAX_DEPTH = 16`). Якщо обхід перевищує цю межу, перевірка переривається із поверненням безпечного `DENY`, а до системи моніторингу надсилається сповіщення про виявлення потенційно аномальної структури графів.

### Політика скороченого обчислення (Short-Circuit Evaluation)
Якщо об'єкт має кілька альтернативних правил (наприклад, переглядати камеру може і власник будинку, і технічний оператор, і служба охорони), рушій перевіряє ці гілки. У багатопотокових або асинхронних реалізаціях ці перевірки запускаються паралельно. Щойно одна з гілок повертає `true`, усі інші незавершені обходи негайно скасовуються (через скасування контексту `context.Context` у Go чи `AbortController` у TypeScript), зберігаючи ресурси процесора та мережі.

---

## 3. Повна реалізація рушія авторизації

Наведений нижче код показує тотожні за семантикою та ідіоматичні реалізації чотирма мовами. Кожна версія містить структуру кортежу `Tuple`, клас рушія з захистом від зациклення у графі (через множину `visited`) та демонстраційний тестовий сценарій для сервісу розумного дому Digital Homes.

:::tabs
```py
from dataclasses import dataclass
from typing import Dict, List, Set, Optional

@dataclass(frozen=True)
class Tuple:
    object_id: str   # Наприклад, "camera:704"
    relation: str    # Наприклад, "viewer"
    subject_id: str  # Наприклад, "user:alice" або "home:101#owner"

@dataclass
class EvalContext:
    current_time_hour: int
    allowed_start_hour: int = 8
    allowed_end_hour: int = 22

class RebacAbacEngine:
    def __init__(self):
        # Сховище кортежів: object_id -> список кортежів стосунків
        self._tuples: Dict[str, List[Tuple]] = {}

    def add_tuple(self, obj: str, relation: str, subject: str) -> None:
        t = Tuple(object_id=obj, relation=relation, subject_id=subject)
        self._tuples.setdefault(obj, []).append(t)

    def check_rebac(self, subject: str, relation: str, obj: str, visited: Optional[Set[str]] = None) -> bool:
        """Рекурсивний обхід графа стосунків з відстеженням відвіданих вузлів."""
        if visited is None:
            visited = set()
        
        state_key = f"{obj}#{relation}@{subject}"
        if state_key in visited:
            return False  # Запобігання циклам у реляційному графі
        visited.add(state_key)

        tuples = self._tuples.get(obj, [])
        for t in tuples:
            if t.relation != relation:
                continue
            
            # 1. Прямий збіг ідентифікатора суб'єкта
            if t.subject_id == subject:
                return True
            
            # 2. Непрямий зв'язок через Userset Rewrite (наприклад, home:101#owner)
            if "#" in t.subject_id:
                parent_obj, parent_rel = t.subject_id.split("#")
                if self.check_rebac(subject, parent_rel, parent_obj, visited):
                    return True
        
        return False

    def evaluate(self, subject: str, action: str, obj: str, ctx: EvalContext) -> bool:
        # Фаза 1: ReBAC перевірка зв'язку у графі
        if not self.check_rebac(subject, action, obj):
            return False
        
        # Фаза 2: ABAC перевірка часового вікна
        if not (ctx.allowed_start_hour <= ctx.current_time_hour <= ctx.allowed_end_hour):
            return False  # Доступ заборонено за часом
        
        return True

# --- Демонстраційний прогон ---
if __name__ == "__main__":
    engine = RebacAbacEngine()
    
    # 1. Аліса є власником будинку 101
    engine.add_tuple("home:101", "owner", "user:alice")
    # 2. Камера 704 належить будинку 101
    engine.add_tuple("camera:704", "parent", "home:101")
    # 3. Переглядачем камери є власник її батьківського будинку
    engine.add_tuple("camera:704", "viewer", "home:101#owner")

    # Перевірка о 14:00 (у дозволений час)
    ctx_day = EvalContext(current_time_hour=14)
    print("День 14:00 ->", engine.evaluate("user:alice", "viewer", "camera:704", ctx_day))  # True

    # Перевірка о 23:00 (поза вікном)
    ctx_night = EvalContext(current_time_hour=23)
    print("Ніч 23:00 ->", engine.evaluate("user:alice", "viewer", "camera:704", ctx_night))  # False
```
```ts
interface RelationTuple {
  objectId: string;   // e.g., "camera:704"
  relation: string;   // e.g., "viewer"
  subjectId: string;  // e.g., "user:alice" or "home:101#owner"
}

interface EvalContext {
  currentTimeHour: number;
  allowedStartHour: number;
  allowedEndHour: number;
}

export class RebacAbacEngine {
  private tuples: Map<string, RelationTuple[]> = new Map();

  public addTuple(objectId: string, relation: string, subjectId: string): void {
    const list = this.tuples.get(objectId) ?? [];
    list.push({ objectId, relation, subjectId });
    this.tuples.set(objectId, list);
  }

  public checkRebac(subjectId: string, relation: string, objectId: string, visited = new Set<string>()): boolean {
    const stateKey = `${objectId}#${relation}@${subjectId}`;
    if (visited.has(stateKey)) return false;
    visited.add(stateKey);

    const list = this.tuples.get(objectId) ?? [];
    for (const t of list) {
      if (t.relation !== relation) continue;

      if (t.subjectId === subjectId) return true;

      if (t.subjectId.includes("#")) {
        const [parentObj, parentRel] = t.subjectId.split("#");
        if (this.checkRebac(subjectId, parentRel, parentObj, visited)) {
          return true;
        }
      }
    }
    return false;
  }

  public evaluate(subjectId: string, action: string, objectId: string, ctx: EvalContext): boolean {
    if (!this.checkRebac(subjectId, action, objectId)) {
      return false;
    }
    if (ctx.currentTimeHour < ctx.allowedStartHour || ctx.currentTimeHour > ctx.allowedEndHour) {
      return false;
    }
    return true;
  }
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <string_view>

struct RelationTuple {
    std::string object_id;
    std::string relation;
    std::string subject_id;
};

struct EvalContext {
    int current_time_hour;
    int allowed_start_hour = 8;
    int allowed_end_hour = 22;
};

class RebacAbacEngine {
private:
    std::unordered_map<std::string, std::vector<RelationTuple>> tuples_;

public:
    void add_tuple(std::string_view obj, std::string_view rel, std::string_view subj) {
        tuples_[std::string(obj)].push_back(RelationTuple{
            std::string(obj), std::string(rel), std::string(subj)
        });
    }

    bool check_rebac(std::string_view subject, std::string_view relation, std::string_view obj,
                     std::unordered_set<std::string>& visited) const {
        std::string state_key = std::string(obj) + "#" + std::string(relation) + "@" + std::string(subject);
        if (visited.find(state_key) != visited.end()) {
            return false; // Запобігання цикли у графі
        }
        visited.insert(state_key);

        auto it = tuples_.find(std::string(obj));
        if (it == tuples_.end()) return false;

        for (const auto& t : it->second) {
            if (t.relation != relation) continue;

            if (t.subject_id == subject) return true;

            auto hash_pos = t.subject_id.find('#');
            if (hash_pos != std::string::npos) {
                std::string parent_obj = t.subject_id.substr(0, hash_pos);
                std::string parent_rel = t.subject_id.substr(hash_pos + 1);
                if (check_rebac(subject, parent_rel, parent_obj, visited)) {
                    return true;
                }
            }
        }
        return false;
    }

    bool evaluate(std::string_view subject, std::string_view action, std::string_view obj, const EvalContext& ctx) const {
        std::unordered_set<std::string> visited;
        if (!check_rebac(subject, action, obj, visited)) {
            return false;
        }
        if (ctx.current_time_hour < ctx.allowed_start_hour || ctx.current_time_hour > ctx.allowed_end_hour) {
            return false;
        }
        return true;
    }
};

int main() {
    RebacAbacEngine engine;
    engine.add_tuple("home:101", "owner", "user:alice");
    engine.add_tuple("camera:704", "parent", "home:101");
    engine.add_tuple("camera:704", "viewer", "home:101#owner");

    EvalContext ctx_day{14, 8, 22};
    std::cout << "Day 14:00 access: " << (engine.evaluate("user:alice", "viewer", "camera:704", ctx_day) ? "ALLOW" : "DENY") << "\n";

    EvalContext ctx_night{23, 8, 22};
    std::cout << "Night 23:00 access: " << (engine.evaluate("user:alice", "viewer", "camera:704", ctx_night) ? "ALLOW" : "DENY") << "\n";
    return 0;
}
```
```go
package main

import (
	"fmt"
	"strings"
)

type RelationTuple struct {
	ObjectID  string
	Relation  string
	SubjectID string
}

type EvalContext struct {
	CurrentTimeHour  int
	AllowedStartHour int
	AllowedEndHour   int
}

type RebacAbacEngine struct {
	tuples map[string][]RelationTuple
}

func NewEngine() *RebacAbacEngine {
	return &RebacAbacEngine{tuples: make(map[string][]RelationTuple)}
}

func (e *RebacAbacEngine) AddTuple(obj, relation, subject string) {
	e.tuples[obj] = append(e.tuples[obj], RelationTuple{
		ObjectID:  obj,
		Relation:  relation,
		SubjectID: subject,
	})
}

func (e *RebacAbacEngine) CheckRebac(subject, relation, obj string, visited map[string]bool) bool {
	stateKey := obj + "#" + relation + "@" + subject
	if visited[stateKey] {
		return false
	}
	visited[stateKey] = true

	tuples := e.tuples[obj]
	for _, t := range tuples {
		if t.Relation != relation {
			continue
		}
		if t.SubjectID == subject {
			return true
		}
		if strings.Contains(t.SubjectID, "#") {
			parts := strings.Split(t.SubjectID, "#")
			if e.CheckRebac(subject, parts[1], parts[0], visited) {
				return true
			}
		}
	}
	return false
}

func (e *RebacAbacEngine) Evaluate(subject, action, obj string, ctx EvalContext) bool {
	visited := make(map[string]bool)
	if !e.CheckRebac(subject, action, obj, visited) {
		return false
	}
	if ctx.CurrentTimeHour < ctx.AllowedStartHour || ctx.CurrentTimeHour > ctx.AllowedEndHour {
		return false
	}
	return true
}

func main() {
	engine := NewEngine()
	engine.AddTuple("home:101", "owner", "user:alice")
	engine.AddTuple("camera:704", "parent", "home:101")
	engine.AddTuple("camera:704", "viewer", "home:101#owner")

	ctxDay := EvalContext{CurrentTimeHour: 14, AllowedStartHour: 8, AllowedEndHour: 22}
	fmt.Println("Day access:", engine.Evaluate("user:alice", "viewer", "camera:704", ctxDay))

	ctxNight := EvalContext{CurrentTimeHour: 23, AllowedStartHour: 8, AllowedEndHour: 22}
	fmt.Println("Night access:", engine.Evaluate("user:alice", "viewer", "camera:704", ctxNight))
}
```
:::

---

## 4. Інтеграція з мікросервісним конвеєром та кешування

У реальному мікросервісному середовищі наведений рушій пакується в ізольований **Sidecar PDP** або виконується як внутрішній gRPC-сервіс. Процес обробки запиту виглядає наступним чином:

1. **Прийом запиту на PEP (API Gateway / Middleware)**: Перехоплювач формує структуру `CheckRequest` із заголовків HTTP (JWT identity, ID об'єкта з URL-параметрів).
2. **Перевірка локального кешу результатів (Decision Cache)**: Перехоплювач перевіряє кеш Redis чи вбудований LRU-кеш за ключем `hash(subject, action, resource, context_hash)`. Якщо є свіжий запис з непорушеним TTL (Time to Live), повертається готове `ALLOW` чи `DENY` без виклику PDP.
3. **Обхід графа на PDP**: Якщо результат у кеші відсутній, викликом gRPC запит передається до PDP, який виконує показаний вище алгоритм `evaluate()`.
4. **Асинхронне оновлення кешу стосунків (Tuple Replication)**: Сховище кортежів `_tuples` не лежить в пам'яті статично. При зміні прав (наприклад, коли Аліса надає доступ сусіду) сервіс прав публікує подію в Kafka/NATS, і всі Sidecar PDP у системі асинхронно оновлюють свої локальні структури даних.
5. **Стратегія інвалідації при відкликанні прав**: При видаленні кортежу (наприклад, вилученні інсталятора) сервіс публікує примусовий сигнал інвалідації (Cache Invalidation Event) з ідентифікатором токена Zookie, змушуючи локальні Sidecar PDP негайно вичищати закешовані версії цього графа.

Такий підхід забезпечує компроміс між гарантованою безпекою, автономністю сервісів та високою швидкістю перевірки прав.
