# 📋 Специфікація та контракт декларативного опису пайплайну

Декларативний опис конвеєра неперервної інтеграції та доставлення є машинно-читабельним контрактом між інженерною кодовою базою та розподіленим рушієм виконання задач. Специфікація визначає семантику тригерів подій, топологію спрямованого графу виконання, параметри матричних збірок, політики кешування проміжних шарів, криптографічні атестації ланцюга постачання та протоколи безпарольної автентифікації через OIDC.

Нижче наведено формальний контракт специфікації промислового пайплайну.

## 1. Коренева синтаксична схема AST (Pipeline Definition)

Кореневий маніфест конвеєра описується у форматі YAML/JSON та транслюється синтаксичним аналізатором у внутрішнє абстрактне синтаксичне дерево (AST).

```yaml
# Специфікація кореневого маніфесту конвеєра (pipeline.spec.yaml)
version: "2.1"
name: "production-build-and-deliver"

# Блок визначення вхідних тригерів виконання
on:
  push:
    branches:
      - "main"
      - "release/v*"
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"
    paths-ignore:
      - "docs/**"
      - "*.md"
  pull_request:
    branches:
      - "main"
    types: [opened, synchronize, reopened]
  schedule:
    - cron: "0 2 * * *" # Щоденна нічна глибока санітизація та бенчмаркінг
  workflow_dispatch:
    inputs:
      target_env:
        description: "Цільове середовище розгортання"
        required: true
        default: "staging"
        type: "choice"
        options:
          - "staging"
          - "canary"
          - "production"

# Глобальні змінні середовища, доступні всім задачам конвеєра
env:
  CI: "true"
  LANG: "C.UTF-8"
  DEFAULT_REGISTRY: "registry.internal.net/courses/backend"

# Політика контролю конкурентності для запобігання гонкам розгортання
concurrency:
  group: "${{ github.workflow }}-${{ github.ref }}"
  cancel-in-progress: true

# Політика прав доступу за замовчуванням (найменші привілеї)
permissions:
  contents: "read"
  id-token: "none"
  issues: "none"
  packages: "none"

# Граф виконання задач
jobs:
  lint-and-types:
    runs-on: ["self-hosted", "linux-amd64", "tier-compute"]
    timeout-minutes: 10
    steps:
      - uses: "actions/checkout@v4"
      - name: "Static Analysis"
        run: "./scripts/lint.sh"

  matrix-test:
    needs: [lint-and-types]
    runs-on: "ubuntu-latest"
    timeout-minutes: 25
    strategy:
      fail-fast: false
      matrix:
        os: ["ubuntu-22.04", "ubuntu-24.04"]
        compiler: ["gcc-13", "clang-18"]
        build_type: ["Release", "RelWithDebInfo"]
        exclude:
          - os: "ubuntu-22.04"
            compiler: "clang-18"
    steps:
      - uses: "actions/checkout@v4"
      - name: "Run Unit & Integration Tests"
        run: |
          cmake -B build -DCMAKE_BUILD_TYPE=${{ matrix.build_type }} -DCMAKE_C_COMPILER=${{ matrix.compiler }}
          cmake --build build -j$(nproc)
          ctest --test-dir build --output-on-failure
```

### Поля кореневої структури

| Поле | Тип | Обов'язкове | Опис |
| :--- | :--- | :--- | :--- |
| `version` | `string` | Так | Версія специфікації конвеєра (`2.0`, `2.1`). |
| `name` | `string` | Ні | Читабельна назва пайплайну в панелі моніторингу. |
| `on` | `TriggerRule` | Так | Умови та події запуску конвеєра (webhook події VCS, cron, ручний виклик). |
| `env` | `Map<string, string>` | Ні | Глобальні несекретні змінні оточення для всіх воркерів. |
| `concurrency` | `ConcurrencyPolicy` | Ні | Політика блокування паралельних запусків у межах однієї гілки чи релізу. |
| `permissions` | `PermissionsSpec` | Ні | Базовий набір привілеїв безпеки згідно з принципом найменших привілеїв. |
| `jobs` | `Map<string, JobSpec>` | Так | Асоціативний масив задач, що утворюють вузли DAG-графу. |

### Механіка фільтрації подій та усунення брязкоту (Debounce)
Тригерний рушій обробляє вебхуки від системи контролю версій. Для запобігання надмірному навантаженню під час швидкої серії комітів (англ. *git push storm*) застосовується алгоритм дебаунсу з вікном у 5 секунд. Якщо за цей час надходять нові коміти в ту саму гілку, попередній запланований запуск скасовується, а конвеєр запускається для найновішого стану `HEAD`.

Фільтрація шляхів (`paths` та `paths-ignore`) обчислює перетин множини змінених у коміті файлів із заданими glob-масками. Якщо всі змінені файли підпадають під правила `paths-ignore` (наприклад, документація Markdown), виконання конвеєра повністю пропускається без виділення обчислювальних ресурсів воркерів.

Політика контролю конкурентності (`concurrency`) забезпечує взаємне блокування або скасування застарілих білдів у межах однієї гілки. Параметр `cancel-in-progress: true` негайно перериває активний прогін на застарілому коміті при надходженні нового коміту в той самий Pull Request, зберігаючи до 40% обчислювальних ресурсів кластера.

---

## 2. Специфікація задачі (JobSpec) та життєвий цикл кроків (StepSpec)

Задача (`JobSpec`) є неподільною одиницею планування, яка призначається окремому ізольованому воркеру (контейнеру або віртуальній машині).

```yaml
JobSpec:
  name: "Build and Package OCI"
  runs-on: ["self-hosted", "k8s-arm64"]
  needs: ["matrix-test"]
  timeout-minutes: 30
  continue-on-error: false
  permissions:
    id-token: "write"
    contents: "read"
    packages: "write"
  container:
    image: "cgr.dev/chainguard/wolfi-base:latest"
    options: "--cpus 4 --memory 8g"
  strategy:
    matrix:
      arch: ["amd64", "arm64"]
    max-parallel: 4
    fail-fast: true
  outputs:
    image_digest: "${{ steps.build-step.outputs.digest }}"
  steps:
    - name: "Checkout Repository"
      uses: "actions/checkout@v4"
      with:
        fetch-depth: 1
    - name: "Build OCI Image"
      id: "build-step"
      shell: "bash"
      env:
        DOCKER_BUILDKIT: "1"
      run: |
        DIGEST=$(docker buildx build --platform linux/${{ matrix.arch }} -t app:${{ github.sha }} --push --output type=image,annotation-index.org.opencontainers.image.source=https://github.com/courses/backend -q .)
        echo "digest=${DIGEST}" >> "$GITHUB_OUTPUT"
```

### Специфікація життєвого циклу окремого кроку (`StepSpec`)

Кожен крок у межах задачі виконується послідовно в єдиному робочому просторі (`$GITHUB_WORKSPACE`).

| Поле кроку | Тип | Опис та семантика виконання |
| :--- | :--- | :--- |
| `name` | `string` | Читабельна назва операції, що відображається в журналі виводу. |
| `id` | `string` | Унікальний ідентифікатор кроку для експорту вихідних змінних (`outputs`). |
| `if` | `Expression` | Умовний вираз запуску: `success()`, `always()`, `failure()`, `cancelled()`. |
| `uses` | `string` | Зовнішня дія у форматі `owner/repo@version` або локальний шлях `./.ci/actions/custom`. |
| `with` | `Map<string, string>` | Вхідні параметри (`inputs`), що передаються в зазначену дію. |
| `run` | `string` | Багаторядковий командний скрипт, що виконується в зазначеній оболонці `shell`. |
| `shell` | `string` | Оболонка виконання: `bash`, `sh`, `python`, `pwsh`. |
| `working-directory` | `string` | Робоча директорія виконання відносно кореня репозиторію. |
| `timeout-minutes` | `integer` | Максимальний ліміт часу виконання кроку перед надсиланням `SIGKILL`. |

### Механіка матричних стратегій (Matrix Strategy Mechanics)
Блок `strategy.matrix` дозволяє визначити декартовий добуток параметрів збірки (наприклад, операційні системи, компілятори, цільові архітектури). Рушій генерує N_1 × N_2 × ... × N_k паралельних задач. 

Директива `exclude` видаляє несумісні або надлишкові комбінації, а директива `include` додає специфічні конфігурації. При `fail-fast: false` падіння одного екземпляра матриці (наприклад, на нестандартному компіляторі) не зупиняє виконання решти варіантів, дозволяючи інженеру отримати повну діагностичну матрицю сумісності за один прогін.

### Безпечна передача вихідних змінних між кроками
Для передачі динамічних даних між кроками (наприклад, скомпільованого хешу або версії) рушій надає спеціальний ізольований файл виводу `$GITHUB_OUTPUT`. Для захисту від атак ін'єкції коду (англ. *command injection*) запис багаторядкових значень здійснюється за протоколом розділювачів (англ. *delimiter token syntax*):

```bash
EOF=$(openssl rand -hex 16)
echo "result<<$EOF" >> "$GITHUB_OUTPUT"
echo "$COMPLEX_OUTPUT" >> "$GITHUB_OUTPUT"
echo "$EOF" >> "$GITHUB_OUTPUT"
```

---

## 3. Контракт кешування та CAS (Content-Addressable Storage)

Для прискорення повторних прогонів конвеєр використовує детерміноване контентно-адресоване сховище кешу залежностей та скомпільованих об'єктів.

```yaml
- name: "Cache Compiler Objects and Package Artifacts"
  uses: "actions/cache@v4"
  with:
    path: |
      ~/.cache/ccache
      ~/.cargo/registry
      node_modules
    key: "${{ runner.os }}-${{ runner.arch }}-ccache-${{ hashFiles('**/CMakeLists.txt', '**/package-lock.json') }}"
    restore-keys: |
      ${{ runner.os }}-${{ runner.arch }}-ccache-
      ${{ runner.os }}-${{ runner.arch }}-
```

### Алгоритм розв'язання кешу
1. **Точний збіг (Exact Match)**: рушій обчислює SHA-256 від вмісту файлів замків залежностей. Якщо ключ `key` присутній у CAS-сховищі, архів вивантажується та розпаковується у робочу директорію воркера.
2. **Частковий збіг (Prefix Match Fallback)**: якщо точного збігу не знайдено, рушій перевіряє список `restore-keys` зверху вниз, завантажуючи найновіший за часом створення кеш із відповідним префіксом.
3. **Політика інвалідації**: максимальний розмір кешу репозиторію обмежений квотою (наприклад, 10 ГБ). При перевищенні ліміту застосовується алгоритм LRU (Least Recently Used) з автоматичним видаленням об'єктів, які не запитувалися понад 7 діб.

Стиснення архівів кешу виконується алгоритмом Zstandard (`zstd`) з адаптивним рівнем компресії (рівень 3 для швидкого пакування або рівень 19 для довготривалого збереження базових залежностей).

---

## 4. Специфікація криптографічної атестації та SLSA Provenance

Усі зібрані виконувані файли та OCI-образи підлягають генерації декларативного підписаного маніфесту походження (англ. *Supply-chain Levels for Software Artifacts*, SLSA Provenance v1.0).

### Рівні гарантій SLSA v1.0
* **SLSA Build Level 1**: наявність базового маніфесту походження, згенерованого автоматично системою збірки.
* **SLSA Build Level 2**: захист від підробки походження; збірка виконується на окремому виділеному сервісі збірки, а атестація підписується криптографічним ключем, недоступним коду користувача.
* **SLSA Build Level 3**: повна герметичність збірки; середовище виконання ізольоване від зовнішнього інтернету, залежності мають фіксовані криптографічні хеші, а сам процес збірки гарантує детермінізм та відтворюваність.

### Структура атестації SLSA v1.0 (JSON-LD)

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    {
      "name": "registry.internal.net/courses/backend",
      "digest": {
        "sha256": "8f4b5a3c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a"
      }
    }
  ],
  "predicateType": "https://slsa.dev/provenance/v1",
  "predicate": {
    "buildDefinition": {
      "buildType": "https://actions.github.com/v1/workflow",
      "externalParameters": {
        "workflow": ".github/workflows/production.yaml",
        "repository": "https://github.com/courses/backend",
        "ref": "refs/tags/v2.4.0"
      },
      "internalParameters": {
        "runnerId": "worker-pool-compute-node-42",
        "triggerEvent": "push"
      },
      "resolvedDependencies": [
        {
          "uri": "git+https://github.com/courses/backend@3b2a1c0d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b",
          "digest": {
            "gitCommit": "3b2a1c0d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b"
          }
        },
        {
          "uri": "pkg:docker/chainguard/wolfi-base@sha256:7d8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a"
        }
      ]
    },
    "runDetails": {
      "builder": {
        "id": "https://ci.internal.net/agents/v2"
      },
      "metadata": {
        "invocationId": "7f8e9d0c-1b2a-3c4d-5e6f-7a8b9c0d1e2f",
        "startedOn": "2026-08-20T10:15:30Z",
        "finishedOn": "2026-08-20T10:22:45Z"
      }
    }
  }
}
```

Атестація підписується за допомогою ефемерного сертифіката Fulcio/Cosign з публікацією підпису в прозорому журналі аудиту Rekor. Верифікація полягає у звірці криптографічного дерева Меркла (англ. *Merkle inclusion proof*), що унеможливлює підміну артефакту після збірки.

---

## 5. Контракт автентифікації OIDC та федерації ідентичності

Конвеєр повністю відмовляється від зберігання довготривалих статичних секретів (англ. *static long-lived API keys*). Автентифікація на хмарних провайдерах (AWS, GCP, Azure, HashiCorp Vault) здійснюється через стандарт OpenID Connect (OIDC).

### Формат токена OIDC JWT Claims

```json
{
  "iss": "https://token.actions.githubusercontent.com",
  "sub": "repo:courses/backend:environment:production",
  "aud": "https://iam.amazonaws.com/courses-platform",
  "repository": "courses/backend",
  "repository_owner": "courses",
  "ref": "refs/heads/main",
  "sha": "3b2a1c0d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b",
  "environment": "production",
  "actor": "octocat",
  "workflow": "production-deploy",
  "exp": 1787227200,
  "iat": 1787226600
}
```

### Протокол обміну токенів з AWS STS (AssumeRoleWithWebIdentity)

```http
POST / HTTP/1.1
Host: sts.amazonaws.com
Content-Type: application/x-www-form-urlencoded

Action=AssumeRoleWithWebIdentity
&Version=2011-06-15
&RoleArn=arn:aws:iam::123456789012:role/CoursesProductionDeployRole
&RoleSessionName=CI-Pipeline-Run-7f8e9d
&WebIdentityToken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
&DurationSeconds=900
```

### Відповідь AWS STS з тимчасовими обліковими даними

```xml
<AssumeRoleWithWebIdentityResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/">
  <AssumeRoleWithWebIdentityResult>
    <Credentials>
      <AccessKeyId>ASIAIOSFODNN7EXAMPLE</AccessKeyId>
      <SecretAccessKey>wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY</SecretAccessKey>
      <SessionToken>AQoDYXdzEJr1...EXAMPLETOKEN</SessionToken>
      <Expiration>2026-08-20T10:37:45Z</Expiration>
    </Credentials>
    <AssumedRoleUser>
      <Arn>arn:aws:sts::123456789012:assumed-role/CoursesProductionDeployRole/CI-Pipeline-Run-7f8e9d</Arn>
      <AssumedRoleId>AROAEXAMPLE:CI-Pipeline-Run-7f8e9d</AssumedRoleId>
    </AssumedRoleUser>
  </AssumeRoleWithWebIdentityResult>
</AssumeRoleWithWebIdentityResponse>
```

### Специфікація маскування секретів (Stream Secret Masking)
Будь-які секретні змінні, передані в процес виконання, підлягають автоматичній фільтрації потоку `stdout` та `stderr` агента. Маскувальник будує регулярний вираз для кожного зареєстрованого секрету, а також його Base64 та URL-encoded варіацій:

```text
Regex Masking Contract:
Input Token: "super_secret_db_password_xyz123"
Transformations:
  - Exact:   super_secret_db_password_xyz123       -> ***
  - Base64:  c3VwZXJfc2VjcmV0X2RiX3Bhc3N3b3Jk... -> ***
  - URL-enc: super_secret_db_password_xyz123       -> ***
```

Маскування реалізується через потоковий алгоритм Ахо-Корасік зі ковзним вікном (англ. *sliding window*), що гарантує перехоплення секрету навіть у разі його розбиття між сусідніми мережевими буферами виводу.

---

## 6. Специфікація захисту середовищ та контролю релізів (Environment Gates)

Для продакшен-середовищ конвеєр визначає декларативні бар'єри ручного затвердження (англ. *manual approval gates*) та захисту секретів:

```yaml
environment:
  name: "production"
  url: "https://courses.internal.net"
  reviewers:
    - "team:operations-leads"
    - "user:security-officer"
  wait-timer-minutes: 15
  deployment-branch-policy:
    protected-branches: true
    custom-branch-policies: false
```

### Поля специфікації середовища (`EnvironmentSpec`)

| Поле | Тип | Опис призначення |
| :--- | :--- | :--- |
| `name` | `string` | Цільове середовище розгортання (`production`, `staging`, `canary`). |
| `url` | `string` | URL-адреса живої системи після завершення розгортання. |
| `reviewers` | `Array<string>` | Список обов'язкових рецензентів або груп, чий підпис необхідний для старту задачі. |
| `wait-timer-minutes` | `integer` | Затримка перед розгортанням для завершення прогріву або попереднього аналізу. |
| `deployment-branch-policy` | `BranchPolicy` | Правила обмеження гілок: лише захищені гілки `main` або теги випусків. |

---

## 7. Специфікація ієрархії пріоритетів змінних середовища

Якщо одна й та сама змінна оголошена на різних рівнях конвеєра, рушій застосовує суворий каскадний пріоритет перекриття (англ. *precedence hierarchy*):

```text
1. Локальний рівень кроку (Step-level `env`)              [Найвищий пріоритет]
2. Рівень матриці задачі (Matrix-level values)
3. Рівень окремої задачі (Job-level `env`)
4. Рівень захищеного середовища (Environment-level `env`)
5. Глобальний рівень пайплайну (Workflow-level `env`)
6. Системні змінні агента (Runner host default env)       [Найнижчий пріоритет]
```

---

## 8. Схема JSON подій зворотних викликів (Webhooks)

Зовнішні системи моніторингу та платформи доставки отримують телеметричні повідомлення про стан виконання через Webhook-контракт.

### Подія початку конвеєра (`pipeline.started`)

```json
{
  "event_type": "pipeline.started",
  "timestamp": "2026-08-20T10:15:30.000Z",
  "pipeline_id": "pipe_9b2a7c4e_81f0",
  "pipeline_name": "production-build-and-deliver",
  "trigger": {
    "event": "push",
    "sender": "developer_01",
    "commit": {
      "sha": "3b2a1c0d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b",
      "message": "feat(api): add high-throughput buffer stream",
      "author": "dev@courses.internal"
    }
  },
  "total_jobs": 6
}
```

### Подія завершення задачі (`job.completed`)

```json
{
  "event_type": "job.completed",
  "timestamp": "2026-08-20T10:22:45.128Z",
  "pipeline_id": "pipe_9b2a7c4e_81f0",
  "job_id": "job_e2e_integration_03",
  "job_name": "e2e-integration",
  "status": "FAILURE",
  "duration_ms": 14520,
  "runner": {
    "id": "agent-linux-amd64-07",
    "ip": "10.240.12.88",
    "os": "Linux 6.8.0-generic"
  },
  "error": {
    "step_name": "Run End-to-End Tests",
    "exit_code": 137,
    "reason": "OOMKilled: Process exceeded memory limit of 8192MB",
    "log_snippet": "FATAL: Out of memory during browser allocation. Terminating."
  }
}
```

### Подія завершення конвеєра (`pipeline.finished`)

```json
{
  "event_type": "pipeline.finished",
  "timestamp": "2026-08-20T10:25:10.512Z",
  "pipeline_id": "pipe_9b2a7c4e_81f0",
  "status": "FAILED",
  "total_duration_ms": 580512,
  "summary": {
    "total": 6,
    "success": 4,
    "failed": 1,
    "skipped": 1
  }
}
```

### Протокол криптографічної перевірки підпису Webhook
Для захисту приймального ендпоінту від підробки запитів кожен HTTP-запит підписується заголовком `X-Hub-Signature-256`, що містить HMAC-SHA256 хеш тіла повідомлення, обчислений за допомогою спільного секретного ключа `webhook_secret`:

```text
Header: X-Hub-Signature-256: sha256=d57b2...
Algorithm: HMAC-SHA256(payload_bytes, shared_secret_key)
```

Приймач зобов'язаний проводити перевірку підпису у константному часі (англ. *constant-time comparison*) для запобігання атакам за часом виконання (англ. *timing attacks*).
