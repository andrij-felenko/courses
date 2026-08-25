# ⚙️ ADR-030: Перехід Digital Homes на топологію команд Team Topologies

Цей документ фіксує офіційне рішення про стратегічну реорганізацію інженерного штату платформи Digital Homes на основі фасетних патернів Team Topologies. Він визначає межі володіння доменними контекстами, стандарти оцінки когнітивного навантаження команд, суворий регламент режимів взаємодії та систему автоматизованого CI/CD-контролю за соціотехнічною ерозією комунікаційних зв'язків.

---

## 1. Контекст та передумови рішення

Платформа Digital Homes масштабувалася до 1.2 млн активних домогосподарств, 85 тисяч постійно підключених IoT-хабів та 14 хмарних мікросервісів. Початкова організаційна структура спиралася на традиційні технологічні «цехи» (functional silos):
- **Команда Backend (18 інженерів):** розробляла логіку для всіх 14 мікросервісів (Twin, Rules Engine, Telemetry, Video Stream, Billing, Identity).
- **Команда Infrastructure & Ops (6 інженерів):** вручну налаштовувала Kubernetes-кластери, брокери MQTT, базі даних PostgreSQL/TimescaleDB, Helm-чарти та пайплайни CI/CD.
- **Команда QA (8 інженерів):** виконувала ручне та напів-автоматизоване скрізне тестування (End-to-End) перед кожним релізом.
- **Команда Mobile & Web (10 інженерів):** реалізовувала інтерфейси для iOS, Android та Web-консолі.

### 1.1. Аналіз соціотехнічного колапсу та математика черг

Ця структура призвела до трьох системних катастроф, які блокували розвиток продукту:

1. **Міжкомандні черги (Handoff Bottlenecks):** будь-яка продуктова фіча вимагала послідовного ланцюжка з 4–5 міжкомандних передач. Згідно з теорією масового обслуговування (формули черг та закон Літтла), середній час очікування завдання в черзі обчислюється як:
   ```
   T_wait = (ρ / (1 - ρ)) · T_service
   ```
   При завантаженості команди інфраструктури на 85% (`ρ = 0.85`), коефіцієнт черги становить `0.85 / 0.15 = 5.66`. Завдання, яке вимагало 3 годин чистої роботи адміна (`T_service = 3 год`), висіло в черзі очікування понаднормові **17 годин**. У результаті середній Lead Time доставки фічі від ідеї до продакшену становив 28 днів.
2. **Перевантаження когнітивної ємності інженерів:** кожен розробник бекенду мусив одночасно тримати в голові специфікації протоколу MQTT shadow, розрахунки тарифних планів білінгу, транскодування H.264 відеопотоків, синтаксис Helm-чартів та конфігурації NGINX Ingress. До 65% часу витрачалося на стороннє когнітивне навантаження (extraneous load).
3. **Релізні блоки (Release Trains):** неможливість випустити зміну в сервісі автоматизацій без синхронного узгодження з командами пристроїв, мобільних додатків та інфраструктури. Кожен реліз перетворювався на ризиковану нічну операцію з високим індексом аварійності.

---

## 2. Прийняте рішення (Організаційний розкрій)

Згідно із [зворотним маневром Конвея](root:sf-apps/inverse-conway), прийнято рішення повністю розформувати функційні цехи та сформувати **5 автономних команд** чотирьох фундаментальних типів, прив'язаних до обмежених контекстів [карти контекстів DH](root:progarch/dh-contexts-map).

Декларативний маніфест організаційної структури описує межі володіння, ліміти когнітивної ємності та адреси відповідальних осіб.

```yaml
# org-topology-dh.yaml — Повна декларація топології команд Digital Homes
version: "1.0"
organization: "Digital Homes Engineering"
last_updated: "2026-08-18"

teams:
  - id: "team-twin-control"
    name: "Smart Home Twin & Control"
    type: "stream-aligned"
    domain_contexts:
      - "control.device"
      - "twin.state"
      - "command.routing"
    max_cognitive_capacity_services: 3
    interaction_default: "x-as-a-service"
    on_call_ownership: true
    lead: "alex.k@digitalhomes.io"

  - id: "team-automation-rules"
    name: "Automation & Intelligence"
    type: "stream-aligned"
    domain_contexts:
      - "rules.engine"
      - "triggers.processing"
      - "scene.execution"
    max_cognitive_capacity_services: 2
    interaction_default: "x-as-a-service"
    on_call_ownership: true
    lead: "olena.m@digitalhomes.io"

  - id: "team-video-subsystem"
    name: "Video & Media Engine"
    type: "complicated-subsystem"
    domain_contexts:
      - "video.transcoding"
      - "webrtc.signaling"
      - "rtsp.ingestion"
    sla_response_time_ms: 100
    interaction_default: "x-as-a-service"
    on_call_ownership: true
    lead: "taras.v@digitalhomes.io"

  - id: "team-platform-iot"
    name: "Core Platform & Infrastructure"
    type: "platform"
    products_provided:
      - "paved-road-ci-cd"
      - "mqtt-broker-cluster"
      - "telemetry-time-series-store"
      - "developer-idp-portal"
    interaction_default: "x-as-a-service"
    on_call_ownership: true
    lead: "dmytro.s@digitalhomes.io"

  - id: "team-sec-resilience"
    name: "Security & Resilience Enabling"
    type: "enabling"
    mission: "Upskill stream teams in threat modeling, chaos engineering, and zero-trust authz"
    max_engagement_weeks: 4
    interaction_default: "facilitating"
    on_call_ownership: false
    lead: "iryna.p@digitalhomes.io"
```

---

## 3. Статути та регламент режимів взаємодії команд

Кожен тип команд дістає суворий соціотехнічний статут, що регулює її права, обов'язки та межі відповідальності.

### 3.1. Статут Stream-aligned команд (You build it, you run it)

1. **Повна відповідальність за життєвий цикл:** Stream-команда володіє кодом, базами даних, конфігураціями розгортання, метриками спостережності та налаштуваннями надійності своїх сервісів.
2. **Скасування окремого QA-цеху:** Stream-команда самостійно пише модульні, інтеграційні та контрактні тести (Consumer-Driven Contracts). Заборонено передавати завдання «на тестування» іншій групі.
3. **Чергування On-Call:** інженери Stream-команди чергують у системі сповіщень PagerDuty для своїх сервісів. Це природним чином стимулює команду підвищувати надійність коду й усувати флейкі-помилки.

### 3.2. Статут Platform-команди (X-as-a-Service)

1. **Платформа як продукт:** Platform-команда ставиться до Stream-команд як до внутрішніх клієнтів. Вона збирає зворотний зв'язок через сатисфакційні опитування (NPS) та моніторить індекс когнітивного навантаження.
2. **Заборона ручних викликів:** Platform-команда не виконує ручних тікетів на розгортання ресурсів. Усе надається через самообслуговування (Self-Service API / CLI / Developer Portal).
3. **Золотий шлях (Golden Path):** платформа надає готові шаблони, але не забороняє альтернативи. Якщо Stream-команда обирає власне інфраструктурне рішення, вона бере на себе його повне обслуговування.

### 3.3. Статут Enabling-команди (Facilitating)

1. **Тимчасовість участь:** Enabling-команда інтегрується в Stream-команду на термін від 2 до 4 тижнів.
2. **Відсутність код-овнершипу:** Enabling-інженери не пишуть прод-код за Stream-команду. Вони працюють у режимі парного програмування, проводять архітектурні рев'ю, навчають інструментам та передають знання.
3. **Критерій виходу (Exit Criteria):** залучення вважається успішним, коли Stream-команда спроможна самостійно провадити аудит безпеки чи розгортати міграції без допомоги менторів.

### 3.4. Статут Complicated-subsystem команди (Складна підсистема)

1. **Ізоляція вузької експертизи:** команда володіє складною математичною/медійною доменою (кодеки H.264/H.265, WebRTC, WASM).
2. **Програмований API-контракт:** взаємодія зі Stream-командами відбувається виключно в режимі **X-as-a-Service** через gRPC/REST API.

---

## 4. Автоматизований CI/CD-контроль соціотехнічної ерозії

Для захисту соціотехнічних меж від ерозії впроваджується автоматичний інспектор залежностей, що запускається на етапі CI/CD збірки.

Аналізатор зчитує граф міжсервісних залежностей та перевіряє три ключові інваріанти:
- Жодна Stream-команда не має прямого доступ до баз даних чужої Stream-команди (`db_direct`).
- Тривалість режиму Collaboration між командами не перевищує 21 календарний день.
- Кількість доменних контекстів у володінні однієї команди не перевищує її когнітивний ліміт (`max_cognitive_capacity_services`).

:::tabs
```py
# scripts/check_team_boundaries.py — Повний автоматичний інспектор меж топології
import sys
import os
import yaml
import json
from typing import Dict, List, Any

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def audit_sociotechnical_boundaries(topology_path: str, arch_graph_path: str) -> None:
    """
    Автоматична перевірка соціотехнічних меж у CI/CD.
    Перевіряє заборонені прямі доступ до баз даних, тривалість Collaboration 
    та когнітивне перевантаження команд.
    """
    if not os.path.exists(topology_path) or not os.path.exists(arch_graph_path):
        print(f"⚠️ Файли топології ({topology_path}) або графа ({arch_graph_path}) не знайдені!")
        sys.exit(1)

    topology = load_yaml(topology_path)
    graph = load_json(arch_graph_path)

    errors: List[str] = []
    warnings: List[str] = []

    # 1. Мапування контекст -> команда
    context_to_team: Dict[str, str] = {}
    team_cognitive_limits: Dict[str, int] = {}
    team_context_counts: Dict[str, int] = {}

    for team in topology.get('teams', []):
        team_id = team['id']
        max_services = team.get('max_cognitive_capacity_services', 3)
        team_cognitive_limits[team_id] = max_services
        team_context_counts[team_id] = 0

        for ctx in team.get('domain_contexts', []):
            context_to_team[ctx] = team_id
            team_context_counts[team_id] += 1

    # 2. Перевірка когнітивного ліміту володіння контекстами
    for team_id, count in team_context_counts.items():
        limit = team_cognitive_limits.get(team_id, 3)
        if count > limit:
            errors.append(
                f"КОГНІТИВНЕ ПЕРЕВАНТАЖЕННЯ: Команда '{team_id}' володіє {count} контекстами "
                f"(встановлений суворий ліміт: {limit}). Необхідно розділити домен!"
            )

    # 3. Перевірка ребер графа залежностей
    for edge in graph.get('edges', []):
        source_ctx = edge.get('source_context')
        target_ctx = edge.get('target_context')
        edge_type = edge.get('type') # "api", "db_direct", "event"
        mode = edge.get('interaction_mode', 'x-as-a-service')
        duration_days = edge.get('collaboration_duration_days', 0)

        source_team = context_to_team.get(source_ctx, 'UNKNOWN_TEAM')
        target_team = context_to_team.get(target_ctx, 'UNKNOWN_TEAM')

        # Заборонено: прямий доступ до БД чужої команди
        if source_team != target_team and edge_type == 'db_direct':
            errors.append(
                f"КРИТИЧНА ЕРОЗІЯ: Контекст '{source_ctx}' (команда {source_team}) має прямий "
                f"доступ до БД контексту '{target_ctx}' (команда {target_team})! "
                f"Дозволено лише через API або Події."
            )

        # Заборонено: перевищення терміну Collaboration
        if mode == 'collaboration' and duration_days > 21:
            warnings.append(
                f"ТРИВАЛИЙ COLLABORATION: Взаємодія між {source_team} та {target_team} "
                f"триває {duration_days} днів (ліміт 21 день). Час фіксувати контракт X-as-a-Service!"
            )

    # Друк результатів
    print("=" * 60)
    print("РЕЗУЛЬТАТИ АУДИТУ СОЦІОТЕХНІЧНОЇ ТОПОЛОГІЇ КОМАНД")
    print("=" * 60)

    if warnings:
        print("\n⚠️ ПОПЕРЕДЖЕННЯ:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n❌ ПОРУШЕННЯ СУВОРИХ ПРАВИЛ ТА ЕРОЗІЯ:")
        for e in errors:
            print(f"  - {e}")
        print("\nЗбірку валиться через порушення соціотехнічних меж!")
        sys.exit(1)

    print("\n✅ Соціотехнічні межі топології команд дотримано успішно!")

if __name__ == "__main__":
    audit_sociotechnical_boundaries("org-topology-dh.yaml", "architecture-graph.json")
```
```ts
// scripts/check-team-boundaries.ts — Робочий TypeScript інспектор меж топології
import * as fs from 'fs';
import * as yaml from 'js-yaml';

interface TeamSpec {
  id: string;
  name: string;
  type: string;
  domain_contexts?: string[];
  max_cognitive_capacity_services?: number;
}

interface TopologyConfig {
  teams: TeamSpec[];
}

interface GraphEdge {
  source_context: string;
  target_context: string;
  type: 'api' | 'db_direct' | 'event';
  interaction_mode?: 'x-as-a-service' | 'facilitating' | 'collaboration';
  collaboration_duration_days?: number;
}

interface ArchitectureGraph {
  edges: GraphEdge[];
}

export function runSociotechnicalAudit(topologyPath: string, graphPath: string): void {
  const config = yaml.load(fs.readFileSync(topologyPath, 'utf8')) as TopologyConfig;
  const graph = JSON.parse(fs.readFileSync(graphPath, 'utf8')) as ArchitectureGraph;

  const contextToTeam = new Map<string, string>();
  const teamLimits = new Map<string, number>();
  const teamCounts = new Map<string, number>();

  for (const team of config.teams) {
    const limit = team.max_cognitive_capacity_services ?? 3;
    teamLimits.set(team.id, limit);
    teamCounts.set(team.id, 0);

    for (const ctx of team.domain_contexts || []) {
      contextToTeam.set(ctx, team.id);
      teamCounts.set(team.id, (teamCounts.get(team.id) || 0) + 1);
    }
  }

  const errors: string[] = [];
  const warnings: string[] = [];

  // Перевірка когнітивного ліміту
  teamCounts.forEach((count, teamId) => {
    const limit = teamLimits.get(teamId) || 3;
    if (count > limit) {
      errors.push(`КОГНІТИВНЕ ПЕРЕВАНТАЖЕННЯ: Команда '${teamId}' володіє ${count} контекстами (ліміт: ${limit})`);
    }
  });

  // Перевірка графа залежностей
  for (const edge of graph.edges) {
    const sourceTeam = contextToTeam.get(edge.source_context) || 'UNKNOWN';
    const targetTeam = contextToTeam.get(edge.target_context) || 'UNKNOWN';

    if (sourceTeam !== targetTeam && edge.type === 'db_direct') {
      errors.push(`КРИТИЧНА ЕРОЗІЯ: Прямий доступ до БД між ${sourceTeam} -> ${targetTeam} у контексті '${edge.target_context}'!`);
    }

    if (edge.interaction_mode === 'collaboration' && (edge.collaboration_duration_days || 0) > 21) {
      warnings.push(`ТРИВАЛИЙ COLLABORATION: ${sourceTeam} та ${targetTeam} співпрацюють ${edge.collaboration_duration_days} днів (ліміт 21)`);
    }
  }

  console.log('=' .repeat(60));
  console.log('РЕЗУЛЬТАТИ АУДИТУ СОЦІОТЕХНІЧНОЇ ТОПОЛОГІЇ');
  console.log('=' .repeat(60));

  if (warnings.length > 0) {
    console.log('\n⚠️ ПОПЕРЕДЖЕННЯ:');
    warnings.forEach((w) => console.log(`  - ${w}`));
  }

  if (errors.length > 0) {
    console.error('\n❌ ПОРУШЕННЯ ТА ЕРОЗІЯ:');
    errors.forEach((e) => console.error(`  - ${e}`));
    process.exit(1);
  }

  console.log('\n✅ Соціотехнічні межі дотримано успішно!');
}
```
:::

---

## 5. Порівняльні метрики ефекту реорганізації

Впровадження Team Topologies та платформного контракту оцінювалося за методологією DORA (DevOps Research and Assessment) через 6 місяців після реорганізації:

| Метрика DORA | До Team Topologies (Технологічні цехи) | Після Team Topologies (Автономні Stream + Platform) | Зміна / Покращення |
| :--- | :--- | :--- | :--- |
| **Lead Time for Changes** | **28 днів** (через міжкомандні черги) | **4.5 днів** (внутрішній автономний потік) | **Прискорення в 6.2 рази** |
| **Deployment Frequency** | 1 реліз на 2 тижні (нічний релізний поезд) | **12 релізів на день** (незалежно по сервісах) | **Зростання в 24 рази** |
| **Change Failure Rate (CFR)** | **24%** релізів викликали інцидент | **3.8%** релізів з помилками | **Зниження аварійності в 6.3 рази** |
| **Mean Time to Restore (MTTR)** | **4.5 години** (пошуки «чиє це поле») | **18 хвилин** (чітке володіння та ротація) | **Прискорення відновлення в 15 разів** |
| **Частка стороннього навантаження** | **65%** часу інженера на інфраструктуру | **15%** часу інженера (Golden Path) | **Звільнення 50% ємності під домен** |

Завдяки зафіксованому організаційному рішенням та інструментальному контролю, Digital Homes отримала високу швидкість розвитку продукту без втрати надійності та стійкості.
