# ⚙️ Практика розробки та вбудовування політик: від тестів Rego до C++ та Go

Розгортання надійної системи політик безпеки як коду вимагає трьох взаємопов'язаних інженерних компонентів: декларативного опису правил на мові Rego з урахуванням моделі [найменших привілеїв](root:sf-security/least-privilege), повного набору модульних тестів для верифікації граничних умов та надійного клієнтського коду, що зв'язує точку застосування (PEP) із точкою ухвалення рішень (PDP).

Нижче розглянуто повний цикл створення політики контролю допуску для кластера Kubernetes, організацію тестового набору в Rego, налагодження трасування обчислень через утиліти командного рядка, а також реалізацію високопродуктивних клієнтських обгорток на мовах Go, C та C++ з детальним аналізом керування ресурсами, пам'яттю, багатопотоковістю та обробкою виняткових ситуацій.

---

### 1. Декларативна політика безпеки робочих навантажень

Створимо виробничий файл політики `kubernetes_security.rego`, призначений для контролера допуску (*Admission Controller*). Політика розв'язує три критичні задачі захисту контейнерного середовища:
1. Забороняє запуск контейнерів у привілейованому режимі (`securityContext.privileged = true`), який дозволяє процесу отримати доступ до всіх пристроїв хостової операційної системи;
2. Вимагає монтування кореневої файлової системи виключно в режимі читання (`readOnlyRootFilesystem = true`), що унеможливлює завантаження шкідливих бінарних файлів зловмисником у разі зламу вебдодатка;
3. Блокує завантаження образів із публічних неконтрольованих реєстрів (наприклад, Docker Hub), дозволяючи лише внутрішні довірені сховища організації.

```rego
package kubernetes.admission

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# За замовчуванням блокуємо запит, якщо не спрацювало жодне правило дозволу
default allow := false

# Дозволяємо запит, лише якщо немає жодного зафіксованого порушення
allow if count(deny) == 0

# Множина дозволених внутрішніх реєстрів образів
trusted_registries := {"registry.internal.corp/", "harbor.internal.corp/production/"}

# Допоміжне правило: уніфікований витяг усіх контейнерів (основних та ініціалізаційних)
containers contains container if {
    some container in input.request.object.spec.containers
}

containers contains container if {
    some container in input.request.object.spec.initContainers
}

# 1. Заборона привілейованого режиму
deny contains msg if {
    some container in containers
    container.securityContext.privileged == true
    msg := sprintf("Контейнер '%v' не може запускатися у привілейованому режимі (securityContext.privileged=true)", [container.name])
}

# 2. Вимога запису лише для читання на кореневу файлову систему
deny contains msg if {
    some container in containers
    not container.securityContext.readOnlyRootFilesystem == true
    msg := sprintf("Контейнер '%v' повинен мати увімкнений прапорець securityContext.readOnlyRootFilesystem=true", [container.name])
}

# 3. Перевірка довіреного реєстру образів
deny contains msg if {
    some container in containers
    image := container.image
    not is_trusted_image(image)
    msg := sprintf("Образ '%v' для контейнера '%v' походить з ненадійного реєстру", [image, container.name])
}

# Допоміжна функція перевірки префікса образу
is_trusted_image(image) if {
    some registry in trusted_registries
    startswith(image, registry)
}
```

У цій політиці використовується ключовий механізм мови Rego — генерація множин порушень (`deny contains msg`). Коли рушій OPA обчислює правило, він виконує операцію реляційного обходу (*relational search*): для кожного контейнера у списку `containers` перевіряються всі наведені умови. Якщо контейнер порушує декілька правил одночасно, у множину `deny` додаються всі відповідні текстові описи, що дозволяє надати розробнику повний звіт про всі дефекти маніфесту за один запит.

Зверніть увагу на перевірку кореневої файлової системи: вираз `not container.securityContext.readOnlyRootFilesystem == true` надійно перехоплює як випадки, коли поле явно встановлено у `false`, так і випадки, коли блок `securityContext` взагалі відсутній у маніфесті (стан `undefined`).

---

### 2. Модульне тестування та налагодження правил у Rego

Усі політики безпеки повинні проходити автоматизоване тестування перед тим, як потрапити до головної гілки репозиторію. Утиліта `opa test` забезпечує виконання тестів за принципом *Test-Driven Development* (TDD), де за допомогою конструкції `with ... as` здійснюється підміна вхідного документа `input`.

Створимо файл `kubernetes_security_test.rego`, де покриємо як позитивні сценарії успішного допуску, так і комбіновані негативні сценарії з багатьма одночасними порушеннями:

```rego
package kubernetes.admission_test

import future.keywords.if
import data.kubernetes.admission

# Тестовий маніфест безпечного контейнера
mock_valid_pod := {
    "request": {
        "kind": {"kind": "Pod", "version": "v1"},
        "object": {
            "metadata": {"name": "secure-payment-service"},
            "spec": {
                "containers": [
                    {
                        "name": "payment-api",
                        "image": "registry.internal.corp/finance/payment:v2.1.0",
                        "securityContext": {
                            "privileged": false,
                            "readOnlyRootFilesystem": true
                        }
                    }
                ]
            }
        }
    }
}

# Тестовий маніфест з порушенням привілеїв
mock_privileged_pod := {
    "request": {
        "kind": {"kind": "Pod", "version": "v1"},
        "object": {
            "metadata": {"name": "unsafe-service"},
            "spec": {
                "containers": [
                    {
                        "name": "hacker-debug",
                        "image": "docker.io/library/ubuntu:latest",
                        "securityContext": {
                            "privileged": true,
                            "readOnlyRootFilesystem": false
                        }
                    }
                ]
            }
        }
    }
}

# Тест 1: Валідний маніфест повинен повертати allow = true та порожній deny
test_valid_pod_allowed if {
    admission.allow with input as mock_valid_pod
    count(admission.deny) == 0 with input as mock_valid_pod
}

# Тест 2: Привілейований контейнер з недовіреного реєстру генерує три порушення
test_privileged_untrusted_pod_denied if {
    not admission.allow with input as mock_privileged_pod
    violations := admission.deny with input as mock_privileged_pod
    count(violations) == 3
}
```

Запуск тестів здійснюється однією командою в терміналі або на кроці CI/CD:

```bash
$ opa test . -v --coverage
data.kubernetes.admission_test.test_valid_pod_allowed: PASS (1.1ms)
data.kubernetes.admission_test.test_privileged_untrusted_pod_denied: PASS (0.9ms)
--------------------------------------------------------------------------------
PASS: 2/2
Coverage: 100.00%
```

Прапорець `--coverage` дозволяє переконатися, що в коді політики не залишилося жодної невиконаної гілки чи неперевіреної умови.

Якщо тест не проходить, інженер може увімкнути повне трасування дерева обчислення за допомогою команди:
```bash
$ opa eval --data kubernetes_security.rego --input mock_input.json "data.kubernetes.admission.deny" --explain=fails
```
Параметр `--explain=fails` відфільтрує успішні кроки та покаже точний номер рядка й підвираз, на якому обчислення повернуло хибне значення.

---

### 3. Вбудовування оцінки політик у бекенд-застосунки

Коли мікросервіс або API-шлюз виступає як точка застосування (PEP), він зобов'язаний сформувати запит до PDP, витримати жорсткий бюджет мережевої затримки (зазвичай не більше 1-2 мілісекунд) та надійно опрацювати потенційні збої мережі за правилом відмови *Fail-Closed*.

#### Реалізація мовою Go через In-Memory SDK

У мові Go розробники можуть вбудувати OPA безпосередньо в адресний простір свого процесу. Це усуває накладні витрати на передачу даних через TCP-сокети й серіалізацію HTTP:

:::code proj-rego-eval/go/main.go

Об'єкт `rego.PreparedEvalQuery` у Go є повністю безпечним для конкурентного виклику з багатьох паралельних горутин (*thread-safe*), що дозволяє обробляти десятки тисяч запитів авторизації на секунду на одному сервері з мікросекундними затримками без блокування м'ютексів.

---

#### Реалізація клієнта перевірки на C та C++

У системному програмуванні, телекомунікаційних серверах та мережевих проксі-демонах перевірка авторизації здійснюється шляхом надсилання компактного HTTP POST-запиту до локального демона OPA, запущеного у форматі сайдкара (`localhost:8181`).

Нижче наведено два варіанти реалізації клієнта: класичний процедурний підхід мовою C із ручним керуванням пам'яттю та сучасний ідіоматичний підхід мовою C++ з використанням концепції RAII, розумних вказівників `std::unique_ptr` та обгортки помилок `std::expected`.

В обох випадках реалізовано захист від зависання мережі за допомогою параметра `CURLOPT_TIMEOUT_MS` (500 мс), що запобігає блокуванню робочих потоків застосунку під час тимчасової недоступності демона OPA.

:::tabs
:::code proj-rego-eval/c/main.c
:::code proj-rego-eval/cpp/main.cpp
:::

У реалізації C++ використовується принцип нульових накладних витрат (*zero-overhead abstraction*): деструктори `std::unique_ptr` гарантують закриття дескрипторів та звільнення пам'яті заголовків навіть у разі викидання винятків чи дострокового повернення з функції. Завдяки `std::expected` код обробляє помилки зв'язку з PDP явно, не перериваючи виконання програми аварійними зупинками.

Крім того, використання `std::string_view` дозволяє передавати фрагменти JSON без зайвого копіювання рядків у купі (*heap allocations*), що забезпечує максимальну продуктивність на критичному шляху обробки мережевого трафіку. Для багатопотокових сервісів обов'язковим є встановлення опції `CURLOPT_NOSIGNAL = 1L`, яка вимикає використання сигналів POSIX функціями DNS-резолвінгу всередині `libcurl`, запобігаючи аварійним збоям процесів через міжпотокові гонки сигналів.
