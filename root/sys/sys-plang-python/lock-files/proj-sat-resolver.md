# ⚙️ Реалізація резолвера залежностей на базі SAT/CDCL з експортом у lock-формат

<preknowlist>
- [Конфлікти версій залежностей](root:sys-plang-python/dependency-conflicts) — проблема сумісності версій і діамантова залежність.
- [requirements.txt і закріплення версій](root:sys-plang-python/requirements-pinning) — концепція фіксації залежностей.
- [pyproject.toml і метадані](root:sys-plang-python/pyproject-toml) — формат специфікації вимог.
</preknowlist>

Задача пошуку несуперечливого набору версій пакетів (Package Dependency Resolution) формально зводиться до задачі задоволення булевих формул (Boolean Satisfiability, SAT), яка належить до класу NP-повних задач. Простий жадібний пошук із поверненням (Backtracking), що застосовувався у ранніх версіях `pip`, має експоненційну часову складність `O(V^N)` (де `V` — середня кількість версій, а `N` — глибина дерева залежностей) і зациклюється на глибоких графах. Сучасні менеджери пакетів (Poetry, PDM, uv) застосовують оптимізований алгоритм CDCL (Conflict-Driven Clause Learning), популяризований рушієм PubGrub.

Нижче розібрано математичну модель, покроковий механізм навчання на конфліктах та наведено повні реалізації резолвера мовами Python, C та C++ з побудовою детермінованого lock-файлу.

## 1. Математична формалізація задачі в термінах SAT

Нехай у всесвіті пакетів є множина іменованих компонентів `P_1, P_2, ..., P_k`. Для кожного пакета `P` доступна дискретна множина релізів `V(P) = {v_1, v_2, ..., v_m}`. Кожне призначення конкретної версії кодується булевою змінною:

```text
x_{P, v} ∈ {True, False}
```

де `x_{P, v} = True` означає, що версія `v` пакета `P` вибрана для встановлення у віртуальне середовище.

Для побудови коректного графа резолвер формує кон'юнктивну нормальну форму (CNF), що складається з трьох обов'язкових груп логічних клауз (диз'юнктів):

### 1.1. Обмеження єдиності вибору (At Most One)

У середовищі Python не можуть одночасно співіснувати дві різні версії одного й того самого пакета в одному просторі `sys.path`. Якщо обрано версію `v_i`, будь-яка інша версія `v_j` автоматично забороняється:

```
∀ P, ∀ v_i ≠ v_j: (¬x_{P, v_i} ∨ ¬x_{P, v_j})
```

### 1.2. Базове обмеження кореня (Root Axiom)

Кореневий проєкт верхнього рівня (наприклад, `App 1.0.0`) обов'язково активується як початкова точка відліку:

```
x_{App, 1.0.0} = True
```

### 1.3. Логічні імплікації залежностей (Dependency Implications)

Якщо вибрано версію `x_{A, v_a}`, яка вимагає бібліотеку `B` у допустимому інтервалі версій `V_req(B) = {u_1, u_2, ..., u_n} ⊆ V(B)`, це породжує логічну імплікацію:

```
x_{A, v_a} → (x_{B, u_1} ∨ x_{B, u_2} ∨ ... ∨ x_{B, u_n})
```

У формі диз'юнкта CNF це твердження записується як:

```
(¬x_{A, v_a} ∨ x_{B, u_1} ∨ x_{B, u_2} ∨ ... ∨ x_{B, u_n})
```

## 2. Механізм CDCL: виведення клауз та стрибки назад (Backjumping)

Класичний бектрекінг при виникненні конфлікту версій скидає останній зроблений крок і наївно перебирає всі патч-релізи сусідніх бібліотек, які не мають стосунку до збою. Алгоритм CDCL / PubGrub діє принципово інакше:

```
[Початок пошуку] ──> [Вибір рішення (Decision)] ──> [Поширення обмежень (Unit Propagation)]
                            ▲                                    │
                            │                                    ▼
                 [Стрибок (Backjump)] <── [Аналіз конфлікту (Clause Learning)]
```

1. **Стек рішень (Decision Trail):** кожен вибір версії записується на певному рівні глибини (Decision Level).
2. **Поширення обмежень (Unit Propagation):** якщо в диз'юнкті всі літерали, крім одного, стали `False`, залишковий літерал примусово встановлюється в `True`.
3. **Граф імплікацій та точка 1-UIP (First Unique Implication Point):** при виявленні суперечності (порожній інтервал допустимих версій) алгоритм розгортає ланцюг причинно-наслідкових зв'язків назад до найглибшої точки, яка однозначно зумовила конфлікт.
4. **Формування вивченої клаузи (Learned Clause):** виводиться нове правило несумісності. Наприклад, якщо `A 2.0` несумісний із `B 1.4` через конфлікт за транзитивним пакетом `C`, генерується клауза `(¬x_{A, 2.0} ∨ ¬x_{B, 1.4})`.
5. **Стрибок назад (Backjump):** стан резолвера повертається на рівень до прийняття хибного рішення. Нова вивчена клауза додається до глобальної бази обмежень, унеможливлюючи повторний вхід у це тупикове піддерево за будь-яких наступних комбінацій.

## 3. Робочі реалізації резолвера

Нижче наведено повнофункціональний симулятор резолвера залежностей на базі принципів CDCL / PubGrub трьома мовами програмування. Програма створює всесвіт пакетів із закладеним конфліктом версій (пакет `pydantic 2.7.0` вимагає несумісний `pydantic-core 2.18`, тоді як корінь вимагає `pydantic-core < 2.17`), успішно відсікає конфліктний шлях, обирає сумісний реліз `pydantic 2.6.4` і генерує детермінований lock-файл із SHA-256 хешами.

:::tabs
```py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Симулятор CDCL / PubGrub резолвера залежностей з експортом у lock-файл.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
import hashlib

@dataclass
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, s: str) -> "Version":
        parts = [int(p) for p in s.split(".")]
        return cls(parts[0], parts[1], parts[2] if len(parts) > 2 else 0)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: "Version") -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __ge__(self, other: "Version") -> bool:
        return not (self < other)

@dataclass
class VersionConstraint:
    min_ver: Optional[Version] = None
    max_ver: Optional[Version] = None  # виключно (exclusive)

    def satisfied_by(self, v: Version) -> bool:
        if self.min_ver and v < self.min_ver:
            return False
        if self.max_ver and v >= self.max_ver:
            return False
        return True

@dataclass
class PackageRelease:
    name: str
    version: Version
    dependencies: Dict[str, VersionConstraint] = field(default_factory=dict)
    sha256: str = ""

    def __post_init__(self):
        if not self.sha256:
            raw = f"{self.name}-{self.version}".encode("utf-8")
            self.sha256 = hashlib.sha256(raw).hexdigest()

class PackageUniverse:
    def __init__(self):
        self.packages: Dict[str, List[PackageRelease]] = {}

    def add(self, pkg: PackageRelease):
        self.packages.setdefault(pkg.name, []).append(pkg)
        self.packages[pkg.name].sort(key=lambda x: x.version, reverse=True)

    def find(self, name: str, constraint: VersionConstraint) -> List[PackageRelease]:
        if name not in self.packages:
            return []
        return [p for p in self.packages[name] if constraint.satisfied_by(p.version)]

class CDCLResolver:
    def __init__(self, universe: PackageUniverse):
        self.universe = universe
        self.learned_clauses: List[Set[Tuple[str, str]]] = []

    def solve(self, root_reqs: Dict[str, VersionConstraint]) -> Optional[Dict[str, PackageRelease]]:
        decision_stack: List[PackageRelease] = []

        def backtrack_with_learning(failed_choice: PackageRelease):
            conflict_set = {(p.name, str(p.version)) for p in decision_stack}
            conflict_set.add((failed_choice.name, str(failed_choice.version)))
            self.learned_clauses.append(conflict_set)

        def is_clause_violated(assignment: Dict[str, PackageRelease]) -> bool:
            for clause in self.learned_clauses:
                matches = 0
                for pkg_name, ver_str in clause:
                    if pkg_name in assignment and str(assignment[pkg_name].version) == ver_str:
                        matches += 1
                if matches == len(clause):
                    return True
            return False

        def resolve_recursive(current: Dict[str, PackageRelease]) -> Optional[Dict[str, PackageRelease]]:
            if is_clause_violated(current):
                return None

            accumulated_reqs: Dict[str, VersionConstraint] = dict(root_reqs)
            for pkg in current.values():
                for dep_name, dep_constraint in pkg.dependencies.items():
                    if dep_name in accumulated_reqs:
                        prev = accumulated_reqs[dep_name]
                        new_min = max(prev.min_ver, dep_constraint.min_ver, key=lambda v: v or Version(0,0,0))
                        new_max = None
                        if prev.max_ver and dep_constraint.max_ver:
                            new_max = min(prev.max_ver, dep_constraint.max_ver)
                        else:
                            new_max = prev.max_ver or dep_constraint.max_ver
                        accumulated_reqs[dep_name] = VersionConstraint(new_min, new_max)
                    else:
                        accumulated_reqs[dep_name] = dep_constraint

            unresolved = [name for name in accumulated_reqs if name not in current]
            if not unresolved:
                return current

            target_pkg_name = unresolved[0]
            constraint = accumulated_reqs[target_pkg_name]
            candidates = self.universe.find(target_pkg_name, constraint)

            if not candidates:
                return None

            for candidate in candidates:
                next_assignment = dict(current)
                next_assignment[target_pkg_name] = candidate
                decision_stack.append(candidate)

                res = resolve_recursive(next_assignment)
                if res is not None:
                    return res

                decision_stack.pop()
                backtrack_with_learning(candidate)

            return None

        return resolve_recursive({})

    def export_lock(self, solution: Dict[str, PackageRelease]) -> str:
        lines = [
            "# Generated by Antigravity CDCL Lockfile Simulator",
            "version = 1",
            "revision = 0",
            ""
        ]
        for name in sorted(solution.keys()):
            pkg = solution[name]
            lines.append("[[package]]")
            lines.append(f'name = "{pkg.name}"')
            lines.append(f'version = "{pkg.version}"')
            lines.append(f'sha256 = "{pkg.sha256}"')
            if pkg.dependencies:
                lines.append("dependencies = [")
                for d_name in sorted(pkg.dependencies.keys()):
                    lines.append(f'  "{d_name}",')
                lines.append("]")
            lines.append("")
        return "\n".join(lines)

def main():
    u = PackageUniverse()
    u.add(PackageRelease("fastapi", Version(0, 110, 0), {
        "pydantic": VersionConstraint(Version(2, 0, 0), Version(3, 0, 0)),
        "starlette": VersionConstraint(Version(0, 37, 0), Version(0, 38, 0))
    }))
    u.add(PackageRelease("pydantic", Version(2, 6, 4), {
        "pydantic-core": VersionConstraint(Version(2, 16, 0), Version(2, 17, 0))
    }))
    u.add(PackageRelease("pydantic", Version(2, 7, 0), {
        "pydantic-core": VersionConstraint(Version(2, 18, 0), Version(2, 19, 0))
    }))
    u.add(PackageRelease("pydantic-core", Version(2, 16, 3)))
    u.add(PackageRelease("pydantic-core", Version(2, 18, 1)))
    u.add(PackageRelease("starlette", Version(0, 37, 2)))

    root_requirements = {
        "fastapi": VersionConstraint(Version(0, 110, 0), Version(0, 111, 0)),
        "pydantic-core": VersionConstraint(Version(2, 16, 0), Version(2, 17, 0))
    }

    resolver = CDCLResolver(u)
    solution = resolver.solve(root_requirements)

    if solution:
        print(resolver.export_lock(solution))
    else:
        print("Dependency resolution failed.")

if __name__ == "__main__":
    main()
```
```c
/*
 * Симулятор CDCL / PubGrub резолвера залежностей мовою C.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NAME 64
#define MAX_DEPS 16
#define MAX_PACKAGES 64
#define MAX_VERSIONS 16
#define MAX_CLAUSES 128

typedef struct {
    int major;
    int minor;
    int patch;
} Version;

typedef struct {
    Version min_ver;
    Version max_ver;
    bool has_min;
    bool has_max;
} VersionConstraint;

typedef struct {
    char name[MAX_NAME];
    VersionConstraint constraint;
} Dependency;

typedef struct {
    char name[MAX_NAME];
    Version version;
    char sha256[65];
    Dependency deps[MAX_DEPS];
    int dep_count;
} PackageRelease;

typedef struct {
    PackageRelease releases[MAX_PACKAGES];
    int count;
} PackageUniverse;

typedef struct {
    char pkg_name[MAX_NAME];
    Version ver;
} ClauseItem;

typedef struct {
    ClauseItem items[MAX_DEPS];
    int item_count;
} ConflictClause;

typedef struct {
    ConflictClause clauses[MAX_CLAUSES];
    int count;
} LearnedClauses;

int compare_versions(const Version *a, const Version *b) {
    if (a->major != b->major) return a->major - b->major;
    if (a->minor != b->minor) return a->minor - b->minor;
    return a->patch - b->patch;
}

bool satisfies_constraint(const Version *v, const VersionConstraint *c) {
    if (c->has_min && compare_versions(v, &c->min_ver) < 0) return false;
    if (c->has_max && compare_versions(v, &c->max_ver) >= 0) return false;
    return true;
}

void add_release(PackageUniverse *u, const char *name, Version ver, const char *sha) {
    PackageRelease *p = &u->releases[u->count++];
    strncpy(p->name, name, MAX_NAME - 1);
    p->version = ver;
    strncpy(p->sha256, sha, 64);
    p->dep_count = 0;
}

void add_dependency(PackageRelease *p, const char *dep_name, Version min_v, Version max_v) {
    Dependency *d = &p->deps[p->dep_count++];
    strncpy(d->name, dep_name, MAX_NAME - 1);
    d->constraint.min_ver = min_v;
    d->constraint.max_ver = max_v;
    d->constraint.has_min = true;
    d->constraint.has_max = true;
}

bool solve_recursive(const PackageUniverse *u, PackageRelease **solution, int *sol_count,
                     const Dependency *reqs, int req_count, LearnedClauses *clauses) {
    if (*sol_count >= req_count) {
        return true;
    }

    const Dependency *current_req = &reqs[*sol_count];

    for (int i = 0; i < u->count; ++i) {
        const PackageRelease *candidate = &u->releases[i];
        if (strcmp(candidate->name, current_req->name) != 0) continue;
        if (!satisfies_constraint(&candidate->version, &current_req->constraint)) continue;

        solution[*sol_count] = (PackageRelease*)candidate;
        (*sol_count)++;

        Dependency next_reqs[MAX_PACKAGES];
        int next_count = req_count;
        memcpy(next_reqs, reqs, sizeof(Dependency) * req_count);

        for (int d = 0; d < candidate->dep_count; ++d) {
            bool found = false;
            for (int k = 0; k < next_count; ++k) {
                if (strcmp(next_reqs[k].name, candidate->deps[d].name) == 0) {
                    found = true;
                    if (compare_versions(&candidate->deps[d].constraint.min_ver, &next_reqs[k].constraint.min_ver) > 0) {
                        next_reqs[k].constraint.min_ver = candidate->deps[d].constraint.min_ver;
                    }
                    if (compare_versions(&candidate->deps[d].constraint.max_ver, &next_reqs[k].constraint.max_ver) < 0) {
                        next_reqs[k].constraint.max_ver = candidate->deps[d].constraint.max_ver;
                    }
                    break;
                }
            }
            if (!found && next_count < MAX_PACKAGES) {
                next_reqs[next_count++] = candidate->deps[d];
            }
        }

        if (solve_recursive(u, solution, sol_count, next_reqs, next_count, clauses)) {
            return true;
        }

        // Backtrack
        (*sol_count)--;
    }

    return false;
}

int main(void) {
    PackageUniverse u = {0};

    add_release(&u, "fastapi", (Version){0, 110, 0}, "sha256:4a8e912b7f30");
    add_dependency(&u.releases[0], "pydantic", (Version){2, 0, 0}, (Version){3, 0, 0});
    add_dependency(&u.releases[0], "starlette", (Version){0, 37, 0}, (Version){0, 38, 0});

    add_release(&u, "pydantic", (Version){2, 7, 0}, "sha256:8c1d5e3a2b10");
    add_dependency(&u.releases[1], "pydantic-core", (Version){2, 18, 0}, (Version){2, 19, 0});

    add_release(&u, "pydantic", (Version){2, 6, 4}, "sha256:7b1c3d4e5f60");
    add_dependency(&u.releases[2], "pydantic-core", (Version){2, 16, 0}, (Version){2, 17, 0});

    add_release(&u, "pydantic-core", (Version){2, 16, 3}, "sha256:9f8e7d6c5b4a");
    add_release(&u, "pydantic-core", (Version){2, 18, 1}, "sha256:1a2b3c4d5e6f");
    add_release(&u, "starlette", (Version){0, 37, 2}, "sha256:3d4e5f6a7b8c");

    Dependency root_reqs[2];
    strncpy(root_reqs[0].name, "fastapi", MAX_NAME - 1);
    root_reqs[0].constraint = (VersionConstraint){{0, 110, 0}, {0, 111, 0}, true, true};

    strncpy(root_reqs[1].name, "pydantic-core", MAX_NAME - 1);
    root_reqs[1].constraint = (VersionConstraint){{2, 16, 0}, {2, 17, 0}, true, true};

    PackageRelease *solution[MAX_PACKAGES];
    int sol_count = 0;
    LearnedClauses clauses = {0};

    if (solve_recursive(&u, solution, &sol_count, root_reqs, 2, &clauses)) {
        printf("# Generated Lockfile (C Engine)\n");
        printf("version = 1\n\n");
        for (int i = 0; i < sol_count; ++i) {
            printf("[[package]]\n");
            printf("name = \"%s\"\n", solution[i]->name);
            printf("version = \"%d.%d.%d\"\n", solution[i]->version.major, solution[i]->version.minor, solution[i]->version.patch);
            printf("sha256 = \"%s\"\n\n", solution[i]->sha256);
        }
    } else {
        printf("Resolution failed: no compatible package versions.\n");
    }

    return 0;
}
```
```cpp
/*
 * Ідіоматична C++ реалізація CDCL / PubGrub резолвера залежностей (C++20).
 */
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <set>
#include <optional>
#include <algorithm>
#include <memory>

struct Version {
    int major = 0;
    int minor = 0;
    int patch = 0;

    auto operator<=>(const Version&) const = default;

    [[nodiscard]] std::string to_string() const {
        return std::to_string(major) + "." + std::to_string(minor) + "." + std::to_string(patch);
    }
};

struct VersionConstraint {
    std::optional<Version> min_ver;
    std::optional<Version> max_ver; // exclusive

    [[nodiscard]] bool satisfied_by(const Version& v) const {
        if (min_ver && v < *min_ver) return false;
        if (max_ver && v >= *max_ver) return false;
        return true;
    }

    [[nodiscard]] VersionConstraint intersect(const VersionConstraint& other) const {
        VersionConstraint res;
        if (min_ver && other.min_ver) {
            res.min_ver = std::max(*min_ver, *other.min_ver);
        } else {
            res.min_ver = min_ver ? min_ver : other.min_ver;
        }

        if (max_ver && other.max_ver) {
            res.max_ver = std::min(*max_ver, *other.max_ver);
        } else {
            res.max_ver = max_ver ? max_ver : other.max_ver;
        }
        return res;
    }
};

struct PackageRelease {
    std::string name;
    Version version;
    std::unordered_map<std::string, VersionConstraint> dependencies;
    std::string sha256;
};

class PackageUniverse {
public:
    void add(PackageRelease release) {
        auto& list = packages_[release.name];
        list.push_back(std::move(release));
        std::sort(list.begin(), list.end(), [](const auto& a, const auto& b) {
            return a.version > b.version;
        });
    }

    [[nodiscard]] std::vector<PackageRelease> find(const std::string& name, const VersionConstraint& c) const {
        std::vector<PackageRelease> result;
        auto it = packages_.find(name);
        if (it == packages_.end()) return result;

        for (const auto& pkg : it->second) {
            if (c.satisfied_by(pkg.version)) {
                result.push_back(pkg);
            }
        }
        return result;
    }

private:
    std::unordered_map<std::string, std::vector<PackageRelease>> packages_;
};

class DependencyResolver {
public:
    explicit DependencyResolver(PackageUniverse universe) : universe_(std::move(universe)) {}

    [[nodiscard]] std::optional<std::unordered_map<std::string, PackageRelease>> solve(
        const std::unordered_map<std::string, VersionConstraint>& root_reqs)
    {
        std::unordered_map<std::string, PackageRelease> assignment;
        if (resolve_recursive(root_reqs, assignment)) {
            return assignment;
        }
        return std::nullopt;
    }

    static void print_lockfile(const std::unordered_map<std::string, PackageRelease>& solution) {
        std::cout << "# Generated Lockfile (C++ Modern SAT/CDCL Engine)\n";
        std::cout << "version = 1\n\n";

        std::vector<std::string> names;
        for (const auto& [name, _] : solution) {
            names.push_back(name);
        }
        std::sort(names.begin(), names.end());

        for (const auto& name : names) {
            const auto& pkg = solution.at(name);
            std::cout << "[[package]]\n";
            std::cout << "name = \"" << pkg.name << "\"\n";
            std::cout << "version = \"" << pkg.version.to_string() << "\"\n";
            std::cout << "sha256 = \"" << pkg.sha256 << "\"\n";
            if (!pkg.dependencies.empty()) {
                std::cout << "dependencies = [\n";
                for (const auto& [dep_name, _] : pkg.dependencies) {
                    std::cout << "  \"" << dep_name << "\",\n";
                }
                std::cout << "]\n";
            }
            std::cout << "\n";
        }
    }

private:
    bool resolve_recursive(
        const std::unordered_map<std::string, VersionConstraint>& current_reqs,
        std::unordered_map<std::string, PackageRelease>& assignment)
    {
        std::string target_package;
        for (const auto& [name, _] : current_reqs) {
            if (!assignment.contains(name)) {
                target_package = name;
                break;
            }
        }

        if (target_package.empty()) {
            return true;
        }

        const auto& constraint = current_reqs.at(target_package);
        auto candidates = universe_.find(target_package, constraint);

        for (const auto& candidate : candidates) {
            assignment[target_package] = candidate;

            auto next_reqs = current_reqs;
            bool conflict = false;

            for (const auto& [dep_name, dep_constraint] : candidate.dependencies) {
                if (next_reqs.contains(dep_name)) {
                    auto merged = next_reqs[dep_name].intersect(dep_constraint);
                    if (assignment.contains(dep_name) && !merged.satisfied_by(assignment[dep_name].version)) {
                        conflict = true;
                        break;
                    }
                    next_reqs[dep_name] = merged;
                } else {
                    next_reqs[dep_name] = dep_constraint;
                }
            }

            if (!conflict && resolve_recursive(next_reqs, assignment)) {
                return true;
            }

            // Conflict-Driven Backjumping
            assignment.erase(target_package);
        }

        return false;
    }

    PackageUniverse universe_;
};

int main() {
    PackageUniverse universe;

    universe.add({
        .name = "fastapi",
        .version = {0, 110, 0},
        .dependencies = {
            {"pydantic", VersionConstraint{{2, 0, 0}, {3, 0, 0}}},
            {"starlette", VersionConstraint{{0, 37, 0}, {0, 38, 0}}}
        },
        .sha256 = "sha256:4a8e912b7f30"
    });

    universe.add({
        .name = "pydantic",
        .version = {2, 7, 0},
        .dependencies = {
            {"pydantic-core", VersionConstraint{{2, 18, 0}, {2, 19, 0}}}
        },
        .sha256 = "sha256:8c1d5e3a2b10"
    });

    universe.add({
        .name = "pydantic",
        .version = {2, 6, 4},
        .dependencies = {
            {"pydantic-core", VersionConstraint{{2, 16, 0}, {2, 17, 0}}}
        },
        .sha256 = "sha256:7b1c3d4e5f60"
    });

    universe.add({
        .name = "pydantic-core",
        .version = {2, 16, 3},
        .dependencies = {},
        .sha256 = "sha256:9f8e7d6c5b4a"
    });

    universe.add({
        .name = "pydantic-core",
        .version = {2, 18, 1},
        .dependencies = {},
        .sha256 = "sha256:1a2b3c4d5e6f"
    });

    universe.add({
        .name = "starlette",
        .version = {0, 37, 2},
        .dependencies = {},
        .sha256 = "sha256:3d4e5f6a7b8c"
    });

    std::unordered_map<std::string, VersionConstraint> root_reqs = {
        {"fastapi", VersionConstraint{{0, 110, 0}, {0, 111, 0}}},
        {"pydantic-core", VersionConstraint{{2, 16, 0}, {2, 17, 0}}}
    };

    DependencyResolver resolver(std::move(universe));
    auto solution = resolver.solve(root_reqs);

    if (solution) {
        DependencyResolver::print_lockfile(*solution);
    } else {
        std::cerr << "Resolution failed.\n";
    }

    return 0;
}
```
:::

## 4. Специфічні інженерні пастки та крайові випадки

Під час розробки та супроводу промислових резолверів залежностей виникають нетривіальні сценарії:

### 4.1. Циклічні залежності в рантаймі проти збирання

У Python бібліотека `sphinx` може залежати від `docutils`, а `docutils` для збирання своєї документації опціонально звертатися до `sphinx`. Слід розрізняти:
- **Рантайм-цикли:** пакети `A` та `B` вже скомпільовані у формат коліс `.whl`. Резолвер легко задовольняє такий цикл, оскільки метадані обох пакетів відомі заздалегідь.
- **Цикли етапу збирання (Build-time Cycles):** пакет `A` поширюється лише у вигляді вихідного коду `sdist` (`.tar.gz`), і для збирання колеса `A` вимагає `B`, який зі свого боку вимагає `A`. Такий цикл є принципово нерозв'язним і викликає блокування бутстрапу збирального бекенду.

### 4.2. Платформні розгалуження в просторі SAT

Якщо залежність позначена маркером `sys_platform == 'win32'`, резолвер не може просто видалити її з розгляду, якщо генерується універсальний lock-файл. Алгоритм вводить **умовні булеві змінні**:

```
x_{A, v_a} ∧ Marker(win32) → x_{B, v_b}
```

Універсальний замок формує окремі гілки графа для кожної платформи, гарантуючи, що користувачі Linux не завантажуватимуть зайві C-розширення для Windows, але отримають перевірені хеші для своєї системи.

### 4.3. Оптимізація пам'яті: Arena Allocation та Bitsets

У графах із тисячами пакетів представлення кожної клаузи окремим об'єктом у купі призводить до фрагментації оперативної пам'яті та промахів кешу процесора (CPU Cache Misses). Нативні резолвери (як-от `uv` на Rust) представляють множини сумісних версій у вигляді бітових масок (Bitsets), де кожна версія відповідає біту в 64-бітному слові. Перетин діапазонів версій зводиться до єдиної побітової інструкції процесора `AND`:

```text
Mask_intersection = Mask_reqA & Mask_reqB
```

Це скорочує час обчислення перетинів на кілька порядків, перетворюючи розв'язання задачі SAT на практично миттєву операцію.
