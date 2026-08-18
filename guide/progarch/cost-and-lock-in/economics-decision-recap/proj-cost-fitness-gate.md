# ⚙️ Сторож економічних бюджетів та unit-cost у CI/CD

Автоматизована фітнес-функція витрат перетворює економічні обмеження на синтетичний тест у конвеєрі CI/CD. Інструмент розраховує віртуальну вартість виконання API-ендпойнта на основі спожитих CPU-мілісекунд, кількості запитів до бази даних та обсягу виведеного egress-трафіку. Якщо новий коміт збільшує питому вартість `Unit Cost` понад заданий відсоток регресії, збірка червоніє, запобігаючи мовчазному архітектурному дрейфу.

Покажемо реалізацію автоматичного сторожа екології витрат двома мовами — TypeScript та Go. Обидва варіанти приймають матрицю цінності ресурсів хмари, оцінюють профіль тесту й порівнюють результат із еталонним бюджетом.

## Механізм збору метрик та оцінки витрат

Сторож витрат працює як проксі-обгортка або middleware навколо HTTP-ендпойнта під час виконання інтеграційних або характеристичних тестів. У процесі обробки тесту система зчитує чотири первинні ресурси:

1. **Процесорний час (CPU time):** вимірюється через процесорні таймери потоку або процесів (`process.cpuUsage()` у Node.js чи `runtime.ReadMemStats()` / execution tracing у Go). Це ізолює чисті обчислення коду від затримок очікування мережі.
2. **Запити до баз даних (DB Queries):** збираються через проксі-драйвер бази даних або ORM-інтерсептор, який підраховує кількість виконаних SQL/NoSQL операцій у межах контексту запиту.
3. **Обсяг виведеного трафіку (Egress Bytes):** підраховується як сума байтів заголовків та тіла відповіді HTTP, виставленого клієнту.
4. **Використання пам'яті (Memory Heap Allocation):** обсяг нововиділеної оперативної пам'яті під час виконання виклику.

На основі отриманих метрик та конфігураційної матриці цін хмарного постачальника обчислюється нормалізована вартість обробки 1 000 запитів (`Unit Cost per 1k`).

## Реалізація сторожа бюджету витрат

Нижче наведено повністю робочий код сторожа витрат мовами TypeScript та Go, що включає інструментаційні проксі для збору метрик, статистичний аналізатор регресій та CLI-запускник.

:::tabs
```ts
// cost-guard.ts — Сторож бюджету Unit Cost у CI/CD конвеєрі

export interface ResourceUsage {
  cpuMs: number;
  dbQueries: number;
  memoryMb: number;
  egressBytes: number;
}

export interface CloudPricing {
  costPerCpuMs: number;       // $ / ms CPU (наприклад, $0.00000002)
  costPerDbQuery: number;     // $ / query (наприклад, $0.000005)
  costPerEgressGb: number;    // $ / GB (наприклад, $0.09)
}

export interface BudgetConfig {
  maxUnitCostUsd: number;     // Максимально припустима вартість 1,000 запитів
  maxRegressionPct: number;   // Пороговий відсоток регресії (наприклад, 15%)
  minSampleRuns: number;      // Мінімальна кількість прогонів для усереднення
}

export interface TestProfile {
  endpoint: string;
  baselineCostUsd: number;
  runs: ResourceUsage[];
}

export interface GuardVerdict {
  ok: boolean;
  endpoint: string;
  currentCostUsd: number;
  baselineCostUsd: number;
  deltaPct: number;
  message: string;
}

export class CostFitnessGuard {
  constructor(
    private pricing: CloudPricing,
    private config: BudgetConfig
  ) {}

  /**
   * Обчислює точну вартість одного запиту на основі використаних ресурсів
   */
  public calculateSingleCost(usage: ResourceUsage): number {
    const cpuCost = usage.cpuMs * this.pricing.costPerCpuMs;
    const dbCost = usage.dbQueries * this.pricing.costPerDbQuery;
    const egressGb = usage.egressBytes / (1024 * 1024 * 1024);
    const egressCost = egressGb * this.pricing.costPerEgressGb;

    return cpuCost + dbCost + egressCost;
  }

  /**
   * Обчислює усереднену питому вартість 1,000 запитів із видаленням крайніх викидів
   */
  public calculateUnitCostPerK(runs: ResourceUsage[]): number {
    if (runs.length === 0) return 0;

    // Сортуємо прогони за вартістю для відсікання сплесків GC або мережі
    const costs = runs.map(r => this.calculateSingleCost(r)).sort((a, b) => a - b);
    
    // Якщо прогонів достатньо, відкидаємо найгірший 10% результат (викиди)
    const validCosts = costs.length >= 5 ? costs.slice(0, Math.floor(costs.length * 0.9)) : costs;
    const avgSingleCost = validCosts.reduce((sum, c) => sum + c, 0) / validCosts.length;

    return avgSingleCost * 1000;
  }

  /**
   * Перевіряє коміт на відповідність економічному бюджету й відсотку регресії
   */
  public evaluateCommit(profile: TestProfile): GuardVerdict {
    if (profile.runs.length < this.config.minSampleRuns) {
      return {
        ok: false,
        endpoint: profile.endpoint,
        currentCostUsd: 0,
        baselineCostUsd: profile.baselineCostUsd,
        deltaPct: 0,
        message: `[ERROR] Недостатньо прогонів тесту: отримано ${profile.runs.length}, потрібно щонайменше ${this.config.minSampleRuns}`,
      };
    }

    const currentCostUsd = this.calculateUnitCostPerK(profile.runs);

    // 1. Перевірка абсолютного ліміту бюджету
    if (currentCostUsd > this.config.maxUnitCostUsd) {
      return {
        ok: false,
        endpoint: profile.endpoint,
        currentCostUsd,
        baselineCostUsd: profile.baselineCostUsd,
        deltaPct: ((currentCostUsd - profile.baselineCostUsd) / profile.baselineCostUsd) * 100,
        message: `[FAIL] ${profile.endpoint}: Unit Cost $${currentCostUsd.toFixed(4)}/1k перевищує стелю $${this.config.maxUnitCostUsd.toFixed(4)}`,
      };
    }

    // 2. Перевірка відносного порогу регресії порівняно з еталоном (Baseline)
    const deltaPct = profile.baselineCostUsd > 0
      ? ((currentCostUsd - profile.baselineCostUsd) / profile.baselineCostUsd) * 100
      : 0;

    if (deltaPct > this.config.maxRegressionPct) {
      return {
        ok: false,
        endpoint: profile.endpoint,
        currentCostUsd,
        baselineCostUsd: profile.baselineCostUsd,
        deltaPct,
        message: `[FAIL] ${profile.endpoint}: Регресія витрат +${deltaPct.toFixed(1)}% перевищує поріг +${this.config.maxRegressionPct}% (база: $${profile.baselineCostUsd.toFixed(4)}, поточна: $${currentCostUsd.toFixed(4)})`,
      };
    }

    return {
      ok: true,
      endpoint: profile.endpoint,
      currentCostUsd,
      baselineCostUsd: profile.baselineCostUsd,
      deltaPct,
      message: `[PASS] ${profile.endpoint}: Unit Cost $${currentCostUsd.toFixed(4)}/1k (динаміка: ${deltaPct > 0 ? '+' : ''}${deltaPct.toFixed(1)}%)`,
    };
  }
}
```
```go
// cost_guard.go — Сторож бюджету Unit Cost у CI/CD конвеєрі

package main

import (
	"fmt"
	"sort"
)

type ResourceUsage struct {
	CpuMs       float64
	DbQueries   int
	MemoryMb    float64
	EgressBytes int64
}

type CloudPricing struct {
	CostPerCpuMs    float64 // $ / ms CPU
	CostPerDbQuery  float64 // $ / query
	CostPerEgressGb float64 // $ / GB
}

type BudgetConfig struct {
	MaxUnitCostUsd   float64 // Максимальна вартість 1,000 запитів
	MaxRegressionPct float64 // Поріг регресії у відсотках
	MinSampleRuns    int     // Мінімальна кількість вимірів
}

type TestProfile struct {
	Endpoint        string
	BaselineCostUsd float64
	Runs            []ResourceUsage
}

type GuardVerdict struct {
	Ok              bool
	Endpoint        string
	CurrentCostUsd  float64
	BaselineCostUsd float64
	DeltaPct        float64
	Message         string
}

type CostFitnessGuard struct {
	Pricing CloudPricing
	Config  BudgetConfig
}

func NewCostFitnessGuard(p CloudPricing, c BudgetConfig) *CostFitnessGuard {
	return &CostFitnessGuard{Pricing: p, Config: c}
}

func (g *CostFitnessGuard) CalculateSingleCost(u ResourceUsage) float64 {
	cpuCost := u.CpuMs * g.Pricing.CostPerCpuMs
	dbCost := float64(u.DbQueries) * g.Pricing.CostPerDbQuery
	egressGb := float64(u.EgressBytes) / (1024.0 * 1024.0 * 1024.0)
	egressCost := egressGb * g.Pricing.CostPerEgressGb

	return cpuCost + dbCost + egressCost
}

func (g *CostFitnessGuard) CalculateUnitCostPerK(runs []ResourceUsage) float64 {
	if len(runs) == 0 {
		return 0
	}

	costs := make([]float64, len(runs))
	for i, r := range runs {
		costs[i] = g.CalculateSingleCost(r)
	}

	sort.Float64s(costs)

	// Відсікаємо 10% найгірших викидів при достатній вибірці
	validCount := len(costs)
	if validCount >= 5 {
		validCount = int(float64(len(costs)) * 0.9)
	}

	var sum float64
	for i := 0; i < validCount; i++ {
		sum += costs[i]
	}

	avgSingle := sum / float64(validCount)
	return avgSingle * 1000.0
}

func (g *CostFitnessGuard) EvaluateCommit(p TestProfile) GuardVerdict {
	if len(p.Runs) < g.Config.MinSampleRuns {
		return GuardVerdict{
			Ok:       false,
			Endpoint: p.Endpoint,
			Message:  fmt.Sprintf("[ERROR] Недостатньо вимірів: %d з необхідних %d", len(p.Runs), g.Config.MinSampleRuns),
		}
	}

	currentCostUsd := g.CalculateUnitCostPerK(p.Runs)
	var deltaPct float64
	if p.BaselineCostUsd > 0 {
		deltaPct = ((currentCostUsd - p.BaselineCostUsd) / p.BaselineCostUsd) * 100.0
	}

	if currentCostUsd > g.Config.MaxUnitCostUsd {
		return GuardVerdict{
			Ok:              false,
			Endpoint:        p.Endpoint,
			CurrentCostUsd:  currentCostUsd,
			BaselineCostUsd: p.BaselineCostUsd,
			DeltaPct:        deltaPct,
			Message:         fmt.Sprintf("[FAIL] %s: Unit Cost $%.4f/1k перевищує ліміт $%.4f", p.Endpoint, currentCostUsd, g.Config.MaxUnitCostUsd),
		}
	}

	if deltaPct > g.Config.MaxRegressionPct {
		return GuardVerdict{
			Ok:              false,
			Endpoint:        p.Endpoint,
			CurrentCostUsd:  currentCostUsd,
			BaselineCostUsd: p.BaselineCostUsd,
			DeltaPct:        deltaPct,
			Message:         fmt.Sprintf("[FAIL] %s: Регресія Unit Cost +%.1f%% перевищує поріг +%.1f%% (база: $%.4f, поточна: $%.4f)", p.Endpoint, deltaPct, g.Config.MaxRegressionPct, p.BaselineCostUsd, currentCostUsd),
		}
	}

	return GuardVerdict{
		Ok:              true,
		Endpoint:        p.Endpoint,
		CurrentCostUsd:  currentCostUsd,
		BaselineCostUsd: p.BaselineCostUsd,
		DeltaPct:        deltaPct,
		Message:         fmt.Sprintf("[PASS] %s: Unit Cost $%.4f/1k (динаміка: %+.1f%%)", p.Endpoint, deltaPct),
	}
}
```
:::

## Детальний розбір архітектури реалізації

Клас `CostFitnessGuard` інкапсулює логіку оцінки економічної ефективності коду. Його структура складається з трьох ключових блоків:

1. **Конфігураційні матриці `CloudPricing` та `BudgetConfig`:** Матриця цін зберігає актуальні значення тарифів хмари (наприклад, ціну за процесорну мілісекунду у бессерверних обчисленнях AWS Lambda чи EC2, ціну read/write юнітів СУБД DynamoDB/Postgres та тариф за гігабайт виведеного в інтернет трафіку). Бюджет задає два пороги: абсолютний ліміт `maxUnitCostUsd` (верхня межа, перетин якої порушує економічну модель продукту) та відносний ліміт `maxRegressionPct` (допустимий відсоток подорожчання в межах одного pull request).

2. **Нормалізатор витрат `calculateUnitCostPerK`:** Оскільки вимірювання окремого виклику API оперує мікродоларами, вартість приводять до відрізка у 1 000 операцій (`Unit Cost per 1k`). Для усунення впливу фонових процесів операційної системи, сплесків мережевої затримки чи роботи збирача сміття (Garbage Collector) алгоритм відсікає найгірші 10% вимірювань і розраховує середнє значення на очищеній вибірці.

3. **Вердикт `evaluateCommit`:** Формує фінальне рішення для конвеєра CI/CD. Якщо стелю витрат або поріг регресії перевищено, повертається вердикт `ok: false` із докладним повідомленням про те, який саме ресурс спричинив здорожчання.

## Простеження виконання: Анатомія виявлення N+1 запиту

Розглянемо покрокове простеження (англ. *step-by-step tracing*) реального сценарію, у якому розробник Digital Homes додав новий функціонал до ендпойнта `GET /api/v1/homes/{id}/devices`.

### Етап 1: Базовий стан (Baseline)

До змін ендпойнт повертав список пристроїв дому одним SQL-запитом `JOIN` між таблицями `homes` та `devices`. Базовий профіль ресурсомісткості на 1 000 запитів мав такий вигляд:
- `cpuMs`: 4.2 ms
- `dbQueries`: 1 запит (базовий `JOIN`)
- `egressBytes`: 1 200 байтів
- **Базовий Unit Cost per 1k:** `0.0051 $`

### Етап 2: Внесення регресії (Pull Request)

У новому pull request розробник вирішив збагатити відповідь даними про статус батареї кожного пристрою. Замість оновлення SQL-запиту він додав цикл у коді застосунку, який для кожного з 50 пристроїв дому виконує окремий виклик `db.query('SELECT * FROM battery_status WHERE device_id = ?')`.

Під час прогону характеристичного тесту сторож витрат зняв нові метрики ресурсомісткості:
- `cpuMs`: 18.5 ms (+340% через серіалізацію 50 об'єктів у циклі)
- `dbQueries`: 51 запит (1 початковий + 50 у циклі N+1)
- `egressBytes`: 4 800 байтів (додано нові поля статусу)

### Етап 3: Обчислення та вердикт Сторожа

Сторож витрат проводить розрахунок нової вартості:

```
cpuCost     = 18.5 ms · $0.00000002 = $0.00000037
dbCost      = 51 query · $0.000005  = $0.00025500
egressCost  = (4800 / 1e9) · $0.09  = $0.00000043

singleCost  = $0.00025580
unitCost/1k = $0.25580
```

Порівняння з еталоном дає наступну динаміку:

```
deltaPct = ((0.25580 - 0.0051) / 0.0051) · 100% = +4 915.6%
```

Сторож витрат миттєво генерує помилку у CI/CD:

```
[FAIL] GET /api/v1/homes/{id}/devices: Регресія Unit Cost +4915.6% перевищує поріг +15.0% (база: $0.0051, поточна: $0.2558)
```

Збірка зупиняється. Розробник бачить лог сторожа, замінює цикл N+1 на один batch-запит `WHERE device_id IN (...)`, повертаючи `dbQueries` до 2, а `Unit Cost` — до `0.0058 $` (+13.7%), що вкладається у порогові 15% регресії й успішно проходить перевірку.

## Крайові випадки та подолання шуму вимірювань

При застосуванні фітнес-функцій витрат у реальних конвеєрах виникають три класи хибних спрацьовувань, які вимагають спеціальної обробки:

### 1. Холодний старт та збирач сміття (GC Spikes)

У середовищах з віртуальною машиною або JIT-компіляцією (Java, Node.js, Go) перший запит витрачає в 5–10 разів більше процесорного часу через ініціалізацію модулів, компіляцію байткоду та холодний збір пам'яті. 

**Рішення:** Перед початком запису вимірювань харнес виконує 10–20 «розігрівальних» запитів (англ. *warm-up requests*), результати яких відкидаються. Для підрахунку фінального Unit Cost застосовується триммер перцентилів: 10% найвищих результатів (викиди під час спрацювання Garbage Collector) відсікаються від вибірки.

### 2. Параметрична залежність складності (Parameter-dependent loads)

Деякі ендпойнти змінюють ресурсомісткість залежно від вхідних параметрів. Наприклад, `GET /api/v1/telemetry?limit=10` коштує `0.001 $`, тоді як `GET /api/v1/telemetry?limit=1000` робить пагінаційне вибирання і коштує `0.05 $`. Якщо тест випадково змінить дефолтні параметри, сторож заблокує збірку.

**Рішення:** Тестові профілі параметризуються фіксованими датасетами. Для кожного ендпойнта задаються три фіксовані сценарії: `small` (мінімальний), `typical` (середньозважений) та `edge` (граничний). Бюджет рахується окремо для кожного сценарію.

### 3. Різниця вартості Egress між регіонами (Data Transfer Nuances)

Передача даних всередині однієї зони доступності (Intra-AZ) у хмарі AWS коштує `0.00 $`, між зонами (Inter-AZ) — `0.01 $` за ГБ, а вивід у публічний інтернет — від `0.08 $` до `0.12 $` за ГБ. Якщо тестове середовище не враховує реальний маршрут трафіку, підсумкова оцінка буде викривленою.

**Рішення:** Матриця цін `CloudPricing` повинна явно моделювати цільовий продакшн-контур. Обсяг виведеного трафіку множиться саме на ціну публічного Egress-трафіку, оскільки саме він створює основний ризик неконтрольованого зростання рахунку при збільшенні розміру JSON-відповідей.

## Інтеграція в CI/CD конвеєр (GitHub Actions)

Нижче наведено приклад конфігураційного кроку GitHub Actions, який запускає сторожа витрат після проходження функціональних тестів:

```yaml
name: Architecture Cost Fitness Gate

on:
  pull_request:
    branches: [ main ]

jobs:
  cost-guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'

      - name: Run Performance Instrumentation Tests
        run: |
          go test -v -run TestCostGuardProfiles ./tests/cost_test.go | tee test_output.log

      - name: Evaluate Cost Regressions
        run: |
          go run ./cmd/cost-guard-cli/main.go --input test_output.log --baseline baseline_costs.json --max-regression 15
```

Застосування такого кроку робить економіку рішення жорстким інженерним обмеженням. Мовчазне подвоєння кількості SQL-запитів чи невдала розпаковка DTO зупиняють розгортання ще до потрапляння в staging-середовище.
