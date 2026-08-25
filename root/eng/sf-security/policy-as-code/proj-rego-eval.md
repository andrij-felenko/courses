# ⚙️ Практика розробки та вбудовування політик: від тестів Rego до C++ та Go

Розгортання надійної системи політик безпеки як коду вимагає трьох взаємопов'язаних інженерних компонентів: декларативного опису правил на мові Rego з урахуванням моделі [найменших привілеїв](topic:sf-security/least-privilege), повного набору модульних тестів для верифікації граничних умов та надійного клієнтського коду, що зв'язує точку застосування (PEP) із точкою ухвалення рішень (PDP).

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

```go
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/open-policy-agent/opa/rego"
)

type UserContext struct {
	User string `json:"user"`
	Role string `json:"role"`
	MFA  bool   `json:"mfa"`
}

type RequestContext struct {
	Method string      `json:"method"`
	Path   string      `json:"path"`
	User   UserContext `json:"user"`
}

func checkAuthorization(ctx context.Context, req RequestContext) (bool, error) {
	// Попередня підготовка та компіляція AST запиту
	query, err := rego.New(
		rego.Query("data.authz.allow"),
		rego.Module("authz.rego", `
			package authz
			import future.keywords.if
			default allow := false

			# Адміністратор з увімкненим MFA має повний доступ
			allow if {
				input.user.role == "admin"
				input.user.mfa == true
			}

			# Звичайний спостерігач має доступ лише на читання
			allow if {
				input.method == "GET"
				input.user.role == "viewer"
			}
		`),
	).PrepareForEval(ctx)
	if err != nil {
		return false, fmt.Errorf("помилка компіляції політики: %w", err)
	}

	// Виконання оцінки для конкретного входу (потокобезпечно)
	results, err := query.Eval(ctx, rego.EvalInput(req))
	if err != nil {
		return false, fmt.Errorf("помилка виконання запиту: %w", err)
	}

	if len(results) > 0 && len(results[0].Expressions) > 0 {
		if allowed, ok := results[0].Expressions[0].Value.(bool); ok {
			return allowed, nil
		}
	}

	return false, nil
}

func main() {
	ctx := context.Background()
	req := RequestContext{
		Method: "POST",
		Path:   "/api/v1/transfer",
		User: UserContext{
			User: "alice",
			Role: "admin",
			MFA:  true,
		},
	}

	allowed, err := checkAuthorization(ctx, req)
	if err != nil {
		log.Fatalf("Збій перевірки: %v", err)
	}

	if allowed {
		fmt.Println("Вердикт PDP: Доступ надано (200 OK)")
	} else {
		fmt.Println("Вердикт PDP: Доступ заборонено (403 Forbidden)")
	}
}
```

Об'єкт `rego.PreparedEvalQuery` у Go є повністю безпечним для конкурентного виклику з багатьох паралельних горутин (*thread-safe*), що дозволяє обробляти десятки тисяч запитів авторизації на секунду на одному сервері з мікросекундними затримками без блокування м'ютексів.

---

#### Реалізація клієнта перевірки на C та C++

У системному програмуванні, телекомунікаційних серверах та мережевих проксі-демонах перевірка авторизації здійснюється шляхом надсилання компактного HTTP POST-запиту до локального демона OPA, запущеного у форматі сайдкара (`localhost:8181`).

Нижче наведено два варіанти реалізації клієнта: класичний процедурний підхід мовою C із ручним керуванням пам'яттю та сучасний ідіоматичний підхід мовою C++ з використанням концепції RAII, розумних вказівників `std::unique_ptr` та обгортки помилок `std::expected`.

В обох випадках реалізовано захист від зависання мережі за допомогою параметра `CURLOPT_TIMEOUT_MS` (500 мс), що запобігає блокуванню робочих потоків застосунку під час тимчасової недоступності демона OPA.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <curl/curl.h>

/* Буфер для динамічного накопичення відповіді від HTTP-сервера OPA */
struct MemoryBuffer {
    char *response;
    size_t size;
};

/* Функція зворотного виклику для запису отриманих байтів у буфер */
static size_t write_callback(void *data, size_t size, size_t nmemb, void *userp) {
    size_t total_size = size * nmemb;
    struct MemoryBuffer *mem = (struct MemoryBuffer *)userp;

    char *ptr = realloc(mem->response, mem->size + total_size + 1);
    if (!ptr) {
        return 0; // Помилка виділення пам'яті: libcurl перерве передачу
    }

    mem->response = ptr;
    memcpy(&(mem->response[mem->size]), data, total_size);
    mem->size += total_size;
    mem->response[mem->size] = '\0';

    return total_size;
}

/* Відправка запиту до точки ухвалення рішень OPA через локальний сокет */
bool opa_check_access(const char *opa_url, const char *json_payload) {
    CURL *curl = curl_easy_init();
    if (!curl) {
        return false;
    }

    struct MemoryBuffer chunk = { .response = malloc(1), .size = 0 };
    if (!chunk.response) {
        curl_easy_cleanup(curl);
        return false;
    }
    chunk.response[0] = '\0';

    struct curl_slist *headers = NULL;
    headers = curl_slist_append(headers, "Content-Type: application/json");

    curl_easy_setopt(curl, CURLOPT_URL, opa_url);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_payload);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
    
    // Жорсткий ліміт очікування відповіді: 500 мс
    curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, 500L);
    // Вимикаємо сигнали для повної потокобезпечності у багатопотокових серверах
    curl_easy_setopt(curl, CURLOPT_NOSIGNAL, 1L);

    CURLcode res = curl_easy_perform(curl);
    bool allowed = false;

    if (res == CURLE_OK) {
        long http_code = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
        if (http_code == 200 && chunk.response) {
            // Перевіряємо наявність поля "result":true у JSON-відповіді OPA
            if (strstr(chunk.response, "\"result\":true") != NULL) {
                allowed = true;
            }
        }
    }

    // Ручне звільнення всіх виділених системних ресурсів
    free(chunk.response);
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    return allowed;
}

int main(void) {
    const char *url = "http://localhost:8181/v1/data/authz/allow";
    const char *payload = "{\"input\":{\"user\":{\"role\":\"admin\",\"mfa\":true},\"method\":\"POST\"}}";

    bool allowed = opa_check_access(url, payload);
    if (allowed) {
        printf("C Client: Доступ дозволено OPA PDP (200 OK)\n");
    } else {
        printf("C Client: Доступ відхилено OPA PDP (403 Forbidden)\n");
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <expected>
#include <chrono>
#include <curl/curl.h>

/* RAII-обгортка над дескриптором CURL для автоматичного звільнення ресурсу */
class CurlSession {
public:
    CurlSession() : handle_(curl_easy_init(), curl_easy_cleanup) {}

    [[nodiscard]] CURL* get() const noexcept { return handle_.get(); }
    [[nodiscard]] bool isValid() const noexcept { return handle_ != nullptr; }

private:
    std::unique_ptr<CURL, decltype(&curl_easy_cleanup)> handle_;
};

/* Клієнт взаємодії з точкою ухвалення рішень OPA (PDP) */
class OpaClient {
public:
    explicit OpaClient(std::string endpoint) : endpoint_(std::move(endpoint)) {}

    [[nodiscard]] std::expected<bool, std::string> evaluate(std::string_view jsonInput) const {
        CurlSession session;
        if (!session.isValid()) {
            return std::unexpected("Не вдалося ініціалізувати CURL сесію");
        }

        std::string responseBody;
        struct curl_slist* rawHeaders = nullptr;
        rawHeaders = curl_slist_append(rawHeaders, "Content-Type: application/json");
        std::unique_ptr<curl_slist, decltype(&curl_slist_free_all)> headers(rawHeaders, curl_slist_free_all);

        // Формуємо обгортку кореневого об'єкта {"input": ...}
        std::string wrappedPayload = "{\"input\":" + std::string(jsonInput) + "}";

        auto writeCallback = [](char* ptr, size_t size, size_t nmemb, void* userdata) -> size_t {
            auto* target = static_cast<std::string*>(userdata);
            const size_t totalBytes = size * nmemb;
            target->append(ptr, totalBytes);
            return totalBytes;
        };

        curl_easy_setopt(session.get(), CURLOPT_URL, endpoint_.c_str());
        curl_easy_setopt(session.get(), CURLOPT_POSTFIELDS, wrappedPayload.c_str());
        curl_easy_setopt(session.get(), CURLOPT_HTTPHEADER, headers.get());
        curl_easy_setopt(session.get(), CURLOPT_WRITEFUNCTION, +writeCallback);
        curl_easy_setopt(session.get(), CURLOPT_WRITEDATA, &responseBody);
        curl_easy_setopt(session.get(), CURLOPT_TIMEOUT_MS, 500L);
        curl_easy_setopt(session.get(), CURLOPT_NOSIGNAL, 1L);

        const CURLcode code = curl_easy_perform(session.get());
        if (code != CURLE_OK) {
            return std::unexpected(std::string("Мережевий збій запиту до PDP: ") + curl_easy_strerror(code));
        }

        long httpCode = 0;
        curl_easy_getinfo(session.get(), CURLINFO_RESPONSE_CODE, &httpCode);
        if (httpCode != 200) {
            return std::unexpected("PDP повернув статус помилки HTTP: " + std::to_string(httpCode));
        }

        // Перевіряємо наявність булевого результату у відповіді
        const bool isAllowed = (responseBody.find("\"result\":true") != std::string::npos);
        return isAllowed;
    }

private:
    std::string endpoint_;
};

int main() {
    const OpaClient client("http://localhost:8181/v1/data/authz/allow");
    const std::string_view userPayload = R"({"user":{"role":"admin","mfa":true},"method":"POST"})";

    auto result = client.evaluate(userPayload);
    if (!result) {
        std::cerr << "Помилка комунікації з OPA: " << result.error() << '\n';
        return 1;
    }

    if (*result) {
        std::cout << "C++ Client: Доступ дозволено OPA PDP (200 OK)\n";
    } else {
        std::cout << "C++ Client: Доступ відхилено OPA PDP (403 Forbidden)\n";
    }

    return 0;
}
```
:::

У реалізації C++ використовується принцип нульових накладних витрат (*zero-overhead abstraction*): деструктори `std::unique_ptr` гарантують закриття дескрипторів та звільнення пам'яті заголовків навіть у разі викидання винятків чи дострокового повернення з функції. Завдяки `std::expected` код обробляє помилки зв'язку з PDP явно, не перериваючи виконання програми аварійними зупинками.

Крім того, використання `std::string_view` дозволяє передавати фрагменти JSON без зайвого копіювання рядків у купі (*heap allocations*), що забезпечує максимальну продуктивність на критичному шляху обробки мережевого трафіку. Для багатопотокових сервісів обов'язковим є встановлення опції `CURLOPT_NOSIGNAL = 1L`, яка вимикає використання сигналів POSIX функціями DNS-резолвінгу всередині `libcurl`, запобігаючи аварійним збоям процесів через міжпотокові гонки сигналів.
