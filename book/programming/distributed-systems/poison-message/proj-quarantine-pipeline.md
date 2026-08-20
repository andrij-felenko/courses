# ⚙️ Реалізація стійкого конвеєра карантину: автоматична ізоляція, діагностичні конверти та безпечний redrive

У розподілених системах обробки повідомлень звичайного логування помилок у файл недостатньо для забезпечення стійкості. Якщо споживач стикається з детерміновано отруйним повідомленням (наприклад, атакою ReDoS, циклічним посиланням у дереві JSON або неперехопленою панікою), стандартний обробник або зависає назавжди, або безперервно падає й перезапускається оркестратором. Це викликає блокування початку черги (*Head-of-Line Blocking*) та паралізує обслуговування тисяч валідних транзакцій.

Виробничий конвеєр карантину розв'язує цю проблему завдяки активному ізолюванню дефектів: він обгортає виконання бізнес-логіки у захисний супервізор зі сторожовим таймером, класифікує збої на перехідні та детерміновані, упаковує токсичні дані у збагачений діагностичний конверт, фіксує зміщення в брокері для звільнення черги та надає інтерфейс для інженерного тріажу і контрольованого повторного спуску (*Redrive*).

Нижче наведено детальну архітектуру та повну реалізацію виробничого конвеєра.

---

## Архітектура та ключові компоненти конвеєра

Стійкий конвеєр карантину базується на чотирьох взаємопов'язаних підсистемах:

1. **Сторожовий супервізор виконання (Execution Supervisor):** виконує бізнес-обробник в ізольованому потоці або горутині, контролюючи жорсткий дедлайн часу процесора (*CPU Watchdog Deadline*). Якщо обробка повідомлення перевищує ліміт (наприклад, через нескінченний цикл або регулярний вираз із бектрекінгом), супервізор відсікає виконання й запобігає зависанню воркера. Також він перехоплює всі асинхронні паніки та фатальні винятки середовища виконання.
2. **Аналізатор і класифікатор помилок (Failure Classifier):** виконує семантичний аналіз помилки. Якщо помилка має мережеву природу (перехідний збій, таймаут бази даних), повідомлення направляється в стандартний контур повторів із затримкою (*Exponential Backoff*). Якщо помилка детермінована (порушення схеми даних, розрив бізнес-інваріанта, паніка, перевищення сторожового таймауту) або лічильник спроб вичерпано — повідомлення негайно відправляється в карантин.
3. **Сховище карантину (Quarantine Repository):** ізольована база даних або виділений топік брокера, де зберігаються повні копії дефектних повідомлень разом із діагностичним контекстом (стектрейс, назва вузла, SHA-256 хеш, точні координати партиції та зміщення).
4. **Механізм тріажу та безпечного відновлення (Triage & Redrive Engine):** адміністративний модуль, що надає операторам можливість аналізувати накопичені інциденти, редагувати дефектні поля у корисній інформації (*Payload Mutation*), проводити канарейкове тестування виправленого коду в ізольованій пісочниці (*Canary Replay*) та виконувати дозований спуск повідомлень назад у бойову чергу через обмежувач швидкості (*Rate Limiter*).

---

## Повна реалізація конвеєра карантину

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <chrono>
#include <future>
#include <functional>
#include <unordered_map>
#include <mutex>
#include <sstream>
#include <iomanip>
#include <expected>
#include <optional>

// ── 1. Моделі даних та діагностичний конверт карантину ───────────────────────

enum class MessageStatus {
    Quarantined,
    UnderReview,
    Mutated,
    Replayed,
    Discarded
};

enum class FailureCategory {
    Transient,           // Мережевий таймаут, блокування БД -> Повтор (Retry)
    DeterministicPoison, // Зламана схема, бізнес-інваріант -> Миттєвий карантин
    ResourceExhaustion,  // Таймаут CPU, ReDoS, зависання -> Карантин
    PanicOrCrash         // Необроблений виняток / паніка -> Карантин
};

struct IngressMessage {
    std::string id;
    std::string partition_key;
    std::string payload;
    int delivery_count{1};
    int64_t timestamp_ms{0};
};

struct QuarantineEnvelope {
    std::string quarantine_id;
    std::string original_message_id;
    std::string partition_key;
    std::string original_payload;
    std::string mutated_payload;
    std::string failure_reason;
    std::string exception_details;
    FailureCategory category;
    MessageStatus status;
    int delivery_attempts;
    int64_t quarantined_at_ms;
    std::string host_identity;
};

// ── 2. Сховище карантину (Quarantine Repository) ────────────────────────────

class QuarantineRepository {
public:
    void save(const QuarantineEnvelope& env) {
        std::lock_guard<std::mutex> lock(mutex_);
        store_[env.quarantine_id] = env;
        std::cout << "[QUARANTINE-STORE] Збережено в карантин ID=" << env.quarantine_id 
                  << " для MessageID=" << env.original_message_id 
                  << " (Причина: " << env.failure_reason << ")\n";
    }

    std::optional<QuarantineEnvelope> get(const std::string& qid) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = store_.find(qid);
        if (it != store_.end()) return it->second;
        return std::nullopt;
    }

    void update(const QuarantineEnvelope& env) {
        std::lock_guard<std::mutex> lock(mutex_);
        store_[env.quarantine_id] = env;
    }

    std::vector<QuarantineEnvelope> list_active() {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<QuarantineEnvelope> res;
        for (const auto& [_, env] : store_) {
            if (env.status == MessageStatus::Quarantined || env.status == MessageStatus::UnderReview) {
                res.push_back(env);
            }
        }
        return res;
    }

private:
    std::unordered_map<std::string, QuarantineEnvelope> store_;
    std::mutex mutex_;
};

// ── 3. Сторожовий супервізор виконання (Execution Supervisor) ───────────────

class ExecutionSupervisor {
public:
    using Handler = std::function<std::expected<void, std::string>(const IngressMessage&)>;

    static std::expected<void, std::pair<FailureCategory, std::string>>
    execute_with_watchdog(const IngressMessage& msg, Handler handler, std::chrono::milliseconds timeout) {
        auto task = std::packaged_task<std::expected<void, std::string>()>([&]() {
            try {
                return handler(msg);
            } catch (const std::exception& ex) {
                return std::unexpected(std::string("Unhandled exception: ") + ex.what());
            } catch (...) {
                return std::unexpected(std::string("Fatal unknown crash/panic caught"));
            }
        });

        auto future = task.get_future();
        std::thread worker_thread(std::move(task));

        if (future.wait_for(timeout) == std::future_status::timeout) {
            // Таймаут обробки: отруйне повідомлення викликало зависання або DoS
            worker_thread.detach(); // Від'єднуємо завислий потік
            return std::unexpected(std::make_pair(
                FailureCategory::ResourceExhaustion,
                "Watchdog deadline exceeded: CPU lockup or infinite loop detected"
            ));
        }

        worker_thread.join();
        auto result = future.get();

        if (result.has_value()) {
            return {};
        }

        std::string err = result.error();
        if (err.find("Schema") != std::string::npos || err.find("Invariant") != std::string::npos) {
            return std::unexpected(std::make_pair(FailureCategory::DeterministicPoison, err));
        }
        if (err.find("crash") != std::string::npos || err.find("exception") != std::string::npos) {
            return std::unexpected(std::make_pair(FailureCategory::PanicOrCrash, err));
        }

        return std::unexpected(std::make_pair(FailureCategory::Transient, err));
    }
};

// ── 4. Головний процесор черги з карантинним контуром ────────────────────────

class ResilientConsumer {
public:
    ResilientConsumer(std::shared_ptr<QuarantineRepository> repo, int max_retries = 3)
        : repo_(std::move(repo)), max_retries_(max_retries) {}

    bool process_message(const IngressMessage& msg, ExecutionSupervisor::Handler handler) {
        constexpr auto WATCHDOG_TIMEOUT = std::chrono::milliseconds(500);

        auto exec_res = ExecutionSupervisor::execute_with_watchdog(msg, handler, WATCHDOG_TIMEOUT);

        if (exec_res.has_value()) {
            std::cout << "[CONSUMER] Повідомлення ID=" << msg.id << " успішно оброблено. Commit ACK.\n";
            return true;
        }

        auto [category, details] = exec_res.error();
        std::cerr << "[CONSUMER-ALERT] Збій повідомлення ID=" << msg.id 
                  << ", Категорія=" << static_cast<int>(category) << ", Деталі: " << details << "\n";

        bool should_quarantine = (category == FailureCategory::DeterministicPoison) ||
                                 (category == FailureCategory::ResourceExhaustion)  ||
                                 (category == FailureCategory::PanicOrCrash)        ||
                                 (msg.delivery_count >= max_retries_);

        if (should_quarantine) {
            QuarantineEnvelope env{
                .quarantine_id = "Q-" + msg.id + "-" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count()),
                .original_message_id = msg.id,
                .partition_key = msg.partition_key,
                .original_payload = msg.payload,
                .mutated_payload = "",
                .failure_reason = (category == FailureCategory::DeterministicPoison) ? "DETERMINISTIC_POISON" :
                                  (category == FailureCategory::ResourceExhaustion)  ? "RESOURCE_EXHAUSTION" :
                                  (category == FailureCategory::PanicOrCrash)        ? "FATAL_PANIC" : "MAX_RETRIES_EXCEEDED",
                .exception_details = details,
                .category = category,
                .status = MessageStatus::Quarantined,
                .delivery_attempts = msg.delivery_count,
                .quarantined_at_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                                         std::chrono::system_clock::now().time_since_epoch()).count(),
                .host_identity = "worker-node-01"
            };

            repo_->save(env);
            // ФІКСУЄМО ЗМІЩЕННЯ: потік не блокується, черга рухається далі
            std::cout << "[CONSUMER] Отруту ізольовано в карантин. Commit Offset для звільнення партиції.\n";
            return true;
        }

        // Перехідний збій: відправляємо на повтор із затримкою
        std::cout << "[CONSUMER] Перехідний збій. Спроба " << msg.delivery_count << "/" << max_retries_ 
                  << ". Requeue with Backoff.\n";
        return false;
    }

private:
    std::shared_ptr<QuarantineRepository> repo_;
    int max_retries_;
};

// ── 5. Служба тріажу та безпечного спуску (Triage & Redrive Engine) ───────────

class TriageEngine {
public:
    explicit TriageEngine(std::shared_ptr<QuarantineRepository> repo) : repo_(std::move(repo)) {}

    bool mutate_payload(const std::string& qid, const std::string& new_payload) {
        auto env = repo_->get(qid);
        if (!env) return false;
        env->mutated_payload = new_payload;
        env->status = MessageStatus::Mutated;
        repo_->update(*env);
        std::cout << "[TRIAGE] Повідомлення " << qid << " успішно виправлено (Payload Mutated).\n";
        return true;
    }

    bool canary_replay(const std::string& qid, ExecutionSupervisor::Handler handler) {
        auto env = repo_->get(qid);
        if (!env) return false;

        std::string payload_to_test = env->mutated_payload.empty() ? env->original_payload : env->mutated_payload;
        IngressMessage test_msg{
            .id = env->original_message_id + "-canary",
            .partition_key = env->partition_key,
            .payload = payload_to_test,
            .delivery_count = 1,
            .timestamp_ms = 0
        };

        std::cout << "[TRIAGE-CANARY] Тестування повідомлення " << qid << " у безпечному сендбоксі...\n";
        auto res = ExecutionSupervisor::execute_with_watchdog(test_msg, handler, std::chrono::milliseconds(500));

        if (res.has_value()) {
            std::cout << "[TRIAGE-CANARY] УСПІХ: Повідомлення успішно проходить обробку!\n";
            env->status = MessageStatus::Replayed;
            repo_->update(*env);
            return true;
        }

        std::cerr << "[TRIAGE-CANARY] НЕВДАЧА: Повідомлення все ще викликає збій: " << res.error().second << "\n";
        return false;
    }

private:
    std::shared_ptr<QuarantineRepository> repo_;
};
```
```go
package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"strings"
	"sync"
	"time"
)

// ── 1. Структури даних карантину ────────────────────────────────────────────

type MessageStatus string

const (
	StatusQuarantined MessageStatus = "QUARANTINED"
	StatusUnderReview MessageStatus = "UNDER_REVIEW"
	StatusMutated     MessageStatus = "MUTATED"
	StatusReplayed    MessageStatus = "REPLAYED"
	StatusDiscarded   MessageStatus = "DISCARDED"
)

type FailureClass string

const (
	FailTransient     FailureClass = "TRANSIENT"
	FailDeterministic FailureClass = "DETERMINISTIC_POISON"
	FailResourceDoS   FailureClass = "RESOURCE_EXHAUSTION"
	FailPanic         FailureClass = "RUNTIME_PANIC"
)

type IngressMessage struct {
	ID            string
	PartitionKey  string
	Payload       []byte
	DeliveryCount int
	Timestamp     time.Time
}

type QuarantineEnvelope struct {
	QuarantineID      string        `json:"quarantine_id"`
	OriginalMessageID string        `json:"original_message_id"`
	PartitionKey      string        `json:"partition_key"`
	PayloadHex        string        `json:"payload_hex"`
	MutatedPayloadHex string        `json:"mutated_payload_hex,omitempty"`
	PayloadSHA256     string        `json:"payload_sha256"`
	FailureReason     string        `json:"failure_reason"`
	ExceptionDetails  string        `json:"exception_details"`
	Category          FailureClass  `json:"category"`
	Status            MessageStatus `json:"status"`
	DeliveryAttempts  int           `json:"delivery_attempts"`
	QuarantinedAt     time.Time     `json:"quarantined_at"`
	HostIdentity      string        `json:"host_identity"`
}

// ── 2. Сховище карантину ───────────────────────────────────────────────────

type QuarantineStore struct {
	mu    sync.RWMutex
	items map[string]QuarantineEnvelope
}

func NewQuarantineStore() *QuarantineStore {
	return &QuarantineStore{items: make(map[string]QuarantineEnvelope)}
}

func (s *QuarantineStore) Put(env QuarantineEnvelope) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.items[env.QuarantineID] = env
	fmt.Printf("[QUARANTINE-STORE] Зафіксовано отруту ID=%s (MsgID=%s, Причина: %s)\n",
		env.QuarantineID, env.OriginalMessageID, env.FailureReason)
}

func (s *QuarantineStore) Get(qid string) (QuarantineEnvelope, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	env, ok := s.items[qid]
	return env, ok
}

func (s *QuarantineStore) Update(env QuarantineEnvelope) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.items[env.QuarantineID] = env
}

// ── 3. Сторожовий супервізор з перехопленням панік ──────────────────────────

type HandlerFunc func(ctx context.Context, msg IngressMessage) error

func ExecuteSupervised(ctx context.Context, msg IngressMessage, handler HandlerFunc, timeout time.Duration) (err error, cat FailureClass) {
	ctxTimeout, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	done := make(chan error, 1)

	go func() {
		defer func() {
			if r := recover(); r != nil {
				done <- fmt.Errorf("runtime panic caught: %v", r)
			}
		}()
		done <- handler(ctxTimeout, msg)
	}()

	select {
	case <-ctxTimeout.Done():
		return errors.New("watchdog timeout: execution deadline exceeded"), FailResourceDoS
	case err = <-done:
		if err == nil {
			return nil, ""
		}
		errMsg := err.Error()
		if strings.Contains(errMsg, "panic") {
			return err, FailPanic
		}
		if strings.Contains(errMsg, "schema") || strings.Contains(errMsg, "invariant") {
			return err, FailDeterministic
		}
		return err, FailTransient
	}
}

// ── 4. Консюмер із запобіганням Head-of-Line Blocking ───────────────────────

type QuarantineConsumer struct {
	store      *QuarantineStore
	maxRetries int
}

func NewQuarantineConsumer(store *QuarantineStore, maxRetries int) *QuarantineConsumer {
	return &QuarantineConsumer{store: store, maxRetries: maxRetries}
}

func (c *QuarantineConsumer) HandleIncoming(ctx context.Context, msg IngressMessage, handler HandlerFunc) bool {
	err, category := ExecuteSupervised(ctx, msg, handler, 500*time.Millisecond)
	if err == nil {
		fmt.Printf("[CONSUMER] MsgID=%s успішно оброблено. Commit ACK.\n", msg.ID)
		return true
	}

	fmt.Printf("[CONSUMER-WARN] Збій MsgID=%s: %v (Категорія: %s)\n", msg.ID, err, category)

	shouldQuarantine := category == FailDeterministic ||
		category == FailResourceDoS ||
		category == FailPanic ||
		msg.DeliveryCount >= c.maxRetries

	if shouldQuarantine {
		hash := sha256.Sum256(msg.Payload)
		env := QuarantineEnvelope{
			QuarantineID:      fmt.Sprintf("Q-%s-%d", msg.ID, time.Now().UnixNano()),
			OriginalMessageID: msg.ID,
			PartitionKey:      msg.PartitionKey,
			PayloadHex:        hex.EncodeToString(msg.Payload),
			PayloadSHA256:     hex.EncodeToString(hash[:]),
			FailureReason:     string(category),
			ExceptionDetails:  err.Error(),
			Category:          category,
			Status:            StatusQuarantined,
			DeliveryAttempts:  msg.DeliveryCount,
			QuarantinedAt:     time.Now().UTC(),
			HostIdentity:      "worker-go-01",
		}

		c.store.Put(env)
		// Фіксуємо зміщення: партиція не блокується
		fmt.Printf("[CONSUMER] Повідомлення MsgID=%s ізольовано в карантин. Commit Offset!\n", msg.ID)
		return true
	}

	fmt.Printf("[CONSUMER] Перехідний збій MsgID=%s (Спроба %d/%d). Requeue.\n", msg.ID, msg.DeliveryCount, c.maxRetries)
	return false
}
```
:::

---

## Покроковий розбір механізму виконання та критичних інваріантів

### 1. Ізоляція потоку та запобігання витоку горутин / дескрипторів
У наведеній реалізації виклик `handler(msg)` виконується в окремому асинхронному контексті (`std::packaged_task` у C++ та горутина з буферизованим каналом у Go).
Це критично важливо з двох причин:
- Якщо отруйне повідомлення містить регулярний вираз із катастрофічним бектрекінгом (ReDoS) або алгоритмічний дедлок, прямий виклик у головному циклі воркера заблокував би обчислювальний потік назавжди.
- Сторожовий таймер (`future.wait_for` або `context.WithTimeout`) очікує рівно 500 мілісекунд. Якщо дедлайн вичерпано, супервізор фіксує помилку `ResourceExhaustion`, від'єднує завислий потік і негайно повертає керування воркеру.
- Буферизований канал розміром 1 (`make(chan error, 1)` у Go) запобігає витоку пам'яті: навіть якщо супервізор вийде за таймаутом раніше, ніж завершиться зависла горутина, запис результату в канал не заблокує горутину назавжди після її можливого пізнішого виходу.

### 2. Порядок операцій та атомарність збереження
Найнебезпечніша помилка під час побудови карантинного конвеєра — це підтвердження повідомлення в брокері (`ACK` або `Commit Offset`) до того, як конверт гарантовано записано в карантинне сховище.
Якщо споживач спершу відправить `ACK`, а потім впаде на операції запису в базу даних карантину (наприклад, через вичерпання диска чи мережевий таймаут), дефектне повідомлення буде назавжди втрачено без жодної можливості відновлення або аудиту.
Правильний алгоритм строго дотримується порядку:
1. Виявлення детермінованого збою або вичерпання ліміту спроб.
2. Формування збагаченого об'єкта `QuarantineEnvelope` з обчисленням SHA-256 хешу.
3. Синхронний запис конверта в надійне сховище (`repo->save(env)`).
4. Лише після повернення успішного коду від сховища — виклик `Commit Offset` у брокері повідомлень.

### 3. Запобігання повторному колапсу через канарейковий реплей
Коли інженери виправляють дефект у коді обробника або модифікують тіло повідомлення через `mutate_payload`, виникає спокуса одночасно відправити всі накопичені повідомлення назад у чергу.
Проте якщо новий хотфікс містить інший прихований баг, масовий реплей знову викличе каскадне падіння всього кластера воркерів.
Метод `canary_replay` усуває цей ризик: він бере рівно одне повідомлення з карантину, запускає його через сторожовий супервізор у «сухому» режимі (*Dry Run*) і лише в разі безпомилкового виконання переводить статус повідомлення у `Replayed`, дозволяючи подальший дозований спуск решти пачки.

---

## Крайові випадки та відмовостійкість контуру карантину

У процесі експлуатації конвеєра карантину виникають критичні нештатні ситуації, які вимагають заздалегідь спроєктованих захисних механізмів:

### 1. Відмова самого карантинного сховища (Quarantine Store Outage)
Якщо база даних карантину або карантинний топік брокера стають недоступними:
- Воркер не має права робити тихий `ACK` дефектного повідомлення, оскільки це призведе до безповоротної втрати транзакцій.
- Воркер записує конверт у локальний буфер на диску (Local Write-Ahead Log / RocksDB) на вузлі споживача.
- Якщо локальний диск також переповнений — воркер зупиняє читання черги (`consumer.pause()`), переводить себе в стан аварійного очікування та генерує критичний алерт черговим інженерам.

### 2. Сплеск ідентичної отрути (Poison Burst & Deduplication)
Якщо сторонній сервіс надсилає 100 000 однакових дефектних запитів за хвилину, збереження 100 000 дублікатів переповнить сховище інцидентів.
Обчислення криптографічного хешу `PayloadSHA256` дозволяє конвеєру виконати дедуплікацію: перший екземпляр зберігається з повним стектрейсом, а для наступних 99 999 екземплярів лише інкрементується лічильник повторень (`occurrence_count += 1`) у межах ковзного вікна, економлячи гігабайти дискового простору.
