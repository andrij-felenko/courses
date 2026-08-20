# ⚙️ Практична реалізація контролера узгодження стану

Контролер узгодження є фундаментальним будівельним блоком розподілених платформ оркестрації, систем інфраструктури як коду та фінансових процесорів. У цій вставці реалізовано повнофункціональне ядро контролера, що поєднує чергу завдань із коалесценцією (дедуплікацією подій), експоненційним бекофом, безпечним видаленням через механізм фіналізаторів (Finalizers) та захистом від гонок запису через оптимістичне блокування версій.

---

## 1. Архітектура та компоненти рушія

Реалізований контролер керує пулом віртуальних вузлів у хмарному середовищі. Його архітектура складається з чотирьох ключових компонентів:

```
[Потік подій Watch] ──> [WorkQueue (DirtySet + FIFO)] ──> [Worker Pool]
                                                             │
                             ┌───────────────────────────────┘
                             ▼
                    [Reconcile(Request)]
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
     1. Observe (Fetch)   2. Diff (Δ)    3. Act & Status (CAS)
```

1. **`WorkQueue`**: потокобезпечна черга завдань, що об'єднує багаторазові події для одного й того самого ключа в одну задачу (коалесценція через `dirty_set`), запобігає одночасній паралельній обробці одного об'єкта кількома воркерами (`processing_set`) та керує затримками повторних спроб.
2. **`Store`**: репліковане транзакційне сховище бажаного стану (`Spec`) та спостережуваного стану (`Status`) з оптимістичним контролем версій (`resource_version`).
3. **`CloudDriver`**: драйвер фізичного середовища, що виконує виклики до зовнішнього API хмари (створення, зупинка та перелік активних серверів).
4. **`Controller`**: виконавча логіка, що реалізує ідемпотентний метод `Reconcile(key)`.

---

## 2. Реалізація мовами C++ та Go

Нижче наведено повну реалізацію рушія мовою сучасного стандарту C++20 (із використанням RAII, потокових примітивів синхронізації та суворої типізації) та мовою Go (стандартної мови хмарних контролерів):

:::tabs
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <chrono>
#include <random>
#include <algorithm>
#include <memory>
#include <optional>

// --- Моделі даних ---
struct NodeSpec {
    int target_replicas{0};
    std::string instance_type{"standard-2cpu-4gb"};
};

struct NodeStatus {
    int available_replicas{0};
    std::string phase{"Pending"};
    std::vector<std::string> active_instance_ids;
};

struct ManagedCluster {
    std::string key;
    uint64_t resource_version{1};
    bool deletion_timestamp{false};
    std::vector<std::string> finalizers;
    NodeSpec spec;
    NodeStatus status;
};

// --- Результат звірки ---
struct ReconcileResult {
    bool requeue{false};
    std::chrono::milliseconds requeue_after{0};
};

// --- Потокобезпечна черга завдань із коалесценцією та бекофом ---
class RateLimitingWorkQueue {
public:
    void add(const std::string& key) {
        std::unique_lock<std::mutex> lock(mtx_);
        dirty_set_.insert(key);
        if (processing_set_.find(key) == processing_set_.end()) {
            if (queued_set_.find(key) == queued_set_.end()) {
                queue_.push(key);
                queued_set_.insert(key);
                cv_.notify_one();
            }
        }
    }

    std::optional<std::string> get() {
        std::unique_lock<std::mutex> lock(mtx_);
        while (queue_.empty() && !shutdown_) {
            cv_.wait(lock);
        }
        if (shutdown_ && queue_.empty()) return std::nullopt;

        std::string key = queue_.front();
        queue_.pop();
        queued_set_.erase(key);
        dirty_set_.erase(key);
        processing_set_.insert(key);
        return key;
    }

    void done(const std::string& key, bool success) {
        std::unique_lock<std::mutex> lock(mtx_);
        processing_set_.erase(key);

        if (!success) {
            int attempts = ++failure_counts_[key];
            // Експоненційний бекоф: base * 2^(attempts-1) + jitter
            int delay_ms = std::min(5000, 100 * (1 << std::min(attempts, 6)));
            std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms / 2));
            dirty_set_.insert(key);
        } else {
            failure_counts_.erase(key);
        }

        // Якщо за час обробки надійшли нові події, повертаємо ключ у чергу
        if (dirty_set_.find(key) != dirty_set_.end() && queued_set_.find(key) == queued_set_.end()) {
            queue_.push(key);
            queued_set_.insert(key);
            cv_.notify_one();
        }
    }

    void shutdown() {
        std::unique_lock<std::mutex> lock(mtx_);
        shutdown_ = true;
        cv_.notify_all();
    }

private:
    std::mutex mtx_;
    std::condition_variable cv_;
    std::queue<std::string> queue_;
    std::unordered_set<std::string> queued_set_;
    std::unordered_set<std::string> dirty_set_;
    std::unordered_set<std::string> processing_set_;
    std::unordered_map<std::string, int> failure_counts_;
    bool shutdown_{false};
};

// --- Імітатор хмарного провайдера (Cloud IaaS API) ---
class CloudProviderDriver {
public:
    std::vector<std::string> list_instances(const std::string& cluster_key) {
        std::lock_guard<std::mutex> lock(mtx_);
        return cloud_vms_[cluster_key];
    }

    std::string create_instance(const std::string& cluster_key, const std::string& type) {
        std::lock_guard<std::mutex> lock(mtx_);
        static uint64_t id_counter = 100;
        std::string vm_id = "vm-" + std::to_string(++id_counter);
        cloud_vms_[cluster_key].push_back(vm_id);
        std::cout << "  [Cloud API] Створено фізичну VM: " << vm_id 
                  << " (тип: " << type << ") для " << cluster_key << std::endl;
        return vm_id;
    }

    void delete_instance(const std::string& cluster_key, const std::string& vm_id) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto& vms = cloud_vms_[cluster_key];
        vms.erase(std::remove(vms.begin(), vms.end(), vm_id), vms.end());
        std::cout << "  [Cloud API] Видалено фізичну VM: " << vm_id 
                  << " з " << cluster_key << std::endl;
    }

private:
    std::mutex mtx_;
    std::unordered_map<std::string, std::vector<std::string>> cloud_vms_;
};

// --- Сховище стану (etcd-подібний транзакційний шар) ---
class ClusterStore {
public:
    std::optional<ManagedCluster> get(const std::string& key) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto it = store_.find(key);
        if (it == store_.end()) return std::nullopt;
        return it->second;
    }

    // Оптимістичне блокування (Compare-And-Swap)
    bool update(const ManagedCluster& cluster) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto it = store_.find(cluster.key);
        if (it == store_.end()) return false;
        if (it->second.resource_version != cluster.resource_version) {
            std::cout << "  [Store CAS] Конфлікт версій для " << cluster.key 
                      << " (очікувалась " << cluster.resource_version 
                      << ", знайдено " << it->second.resource_version << ")" << std::endl;
            return false;
        }
        ManagedCluster updated = cluster;
        updated.resource_version++;
        store_[cluster.key] = updated;
        return true;
    }

    void save_initial(const ManagedCluster& cluster) {
        std::lock_guard<std::mutex> lock(mtx_);
        store_[cluster.key] = cluster;
    }

    void remove(const std::string& key) {
        std::lock_guard<std::mutex> lock(mtx_);
        store_.erase(key);
    }

private:
    std::mutex mtx_;
    std::unordered_map<std::string, ManagedCluster> store_;
};

// --- Контролер узгодження ---
class ClusterReconciler {
public:
    ClusterReconciler(std::shared_ptr<ClusterStore> store,
                      std::shared_ptr<CloudProviderDriver> cloud,
                      std::shared_ptr<RateLimitingWorkQueue> queue)
        : store_(store), cloud_(cloud), queue_(queue) {}

    ReconcileResult reconcile(const std::string& key) {
        std::cout << "\n>>> [Reconcile] Початок звірки для ресурсу: " << key << std::endl;

        // 1. Спостереження (Observe)
        auto cluster_opt = store_->get(key);
        if (!cluster_opt.has_value()) {
            std::cout << "  [Observe] Об'єкт " << key << " видалено зі сховища. Завершення." << std::endl;
            return ReconcileResult{false};
        }
        ManagedCluster cluster = cluster_opt.value();

        const std::string finalizer_name = "infra.example.com/cleanup-vms";

        // Обробка безпечного видалення через фіналізатор
        if (cluster.deletion_timestamp) {
            std::cout << "  [Observe] Виявлено мітку видалення (DeletionTimestamp)." << std::endl;
            if (std::find(cluster.finalizers.begin(), cluster.finalizers.end(), finalizer_name) != cluster.finalizers.end()) {
                std::cout << "  [Act: Cleanup] Зупинка фізичних VM перед видаленням метаданих..." << std::endl;
                auto physical_vms = cloud_->list_instances(key);
                for (const auto& vm_id : physical_vms) {
                    cloud_->delete_instance(key, vm_id);
                }
                // Видаляємо фіналізатор
                cluster.finalizers.erase(
                    std::remove(cluster.finalizers.begin(), cluster.finalizers.end(), finalizer_name),
                    cluster.finalizers.end()
                );
                if (!store_->update(cluster)) {
                    return ReconcileResult{true, std::chrono::milliseconds(100)}; // Requeue на конфлікті
                }
                std::cout << "  [Cleanup] Фіналізатор видалено. Ресурс очищено повністю." << std::endl;
            }
            return ReconcileResult{false};
        }

        // Переконуємося, що фіналізатор присутній
        if (std::find(cluster.finalizers.begin(), cluster.finalizers.end(), finalizer_name) == cluster.finalizers.end()) {
            cluster.finalizers.push_back(finalizer_name);
            if (!store_->update(cluster)) {
                return ReconcileResult{true, std::chrono::milliseconds(100)};
            }
            return ReconcileResult{false};
        }

        // Читаємо стан фізичного світу
        std::vector<std::string> current_vms = cloud_->list_instances(key);

        // 2. Аналіз розбіжностей (Diff)
        int desired_count = cluster.spec.target_replicas;
        int actual_count = static_cast<int>(current_vms.size());
        int delta = desired_count - actual_count;

        std::cout << "  [Diff] Бажано: " << desired_count 
                  << " VM, Фактично працює: " << actual_count 
                  << " VM -> Дельта Δ = " << delta << std::endl;

        // 3. Дія (Act & Converge)
        if (delta > 0) {
            std::cout << "  [Act] Створення " << delta << " відсутніх VM..." << std::endl;
            for (int i = 0; i < delta; ++i) {
                cloud_->create_instance(key, cluster.spec.instance_type);
            }
        } else if (delta < 0) {
            int to_remove = -delta;
            std::cout << "  [Act] Видалення " << to_remove << " надлишкових VM..." << std::endl;
            for (int i = 0; i < to_remove; ++i) {
                cloud_->delete_instance(key, current_vms[i]);
            }
        }

        // Оновлюємо спостережуваний статус (Status)
        auto updated_vms = cloud_->list_instances(key);
        cluster.status.available_replicas = static_cast<int>(updated_vms.size());
        cluster.status.active_instance_ids = updated_vms;
        cluster.status.phase = (cluster.status.available_replicas == cluster.spec.target_replicas) ? "Ready" : "Scaling";

        if (!store_->update(cluster)) {
            std::cout << "  [Status] Помилка CAS при збереженні статусу. Відправка в чергу на повтор..." << std::endl;
            return ReconcileResult{true, std::chrono::milliseconds(200)};
        }

        std::cout << "  [Done] Звірку завершено успішно. Стан узгоджено (Phase=" << cluster.status.phase << ")" << std::endl;
        return ReconcileResult{false};
    }

private:
    std::shared_ptr<ClusterStore> store_;
    std::shared_ptr<CloudProviderDriver> cloud_;
    std::shared_ptr<RateLimitingWorkQueue> queue_;
};
```
```go
package main

import (
	"context"
	"fmt"
	"math"
	"math/rand"
	"sync"
	"time"
)

// NodeSpec описує бажаний стан пулу вузлів
type NodeSpec struct {
	TargetReplicas int
	InstanceType   string
}

// NodeStatus описує фактичний спостережуваний стан
type NodeStatus struct {
	AvailableReplicas int
	Phase             string
	ActiveInstanceIDs []string
}

// ManagedCluster — корінь агрегату кластера
type ManagedCluster struct {
	Key               string
	ResourceVersion   uint64
	DeletionTimestamp bool
	Finalizers        []string
	Spec              NodeSpec
	Status            NodeStatus
}

// ReconcileResult керує наступним кроком планування
type ReconcileResult struct {
	Requeue      bool
	RequeueAfter time.Duration
}

// RateLimitingWorkQueue реалізує коалесценцію подій та експоненційний бекоф
type RateLimitingWorkQueue struct {
	mu             sync.Mutex
	cond           *sync.Cond
	queue          []string
	queuedSet      map[string]struct{}
	dirtySet       map[string]struct{}
	processingSet  map[string]struct{}
	failureCounts  map[string]int
	shutdown       bool
}

func NewWorkQueue() *RateLimitingWorkQueue {
	q := &RateLimitingWorkQueue{
		queuedSet:     make(map[string]struct{}),
		dirtySet:      make(map[string]struct{}),
		processingSet: make(map[string]struct{}),
		failureCounts: make(map[string]int),
	}
	q.cond = sync.NewCond(&q.mu)
	return q
}

func (q *RateLimitingWorkQueue) Add(key string) {
	q.mu.Lock()
	defer q.mu.Unlock()
	q.dirtySet[key] = struct{}{}
	if _, processing := q.processingSet[key]; !processing {
		if _, queued := q.queuedSet[key]; !queued {
			q.queue = append(q.queue, key)
			q.queuedSet[key] = struct{}{}
			q.cond.Signal()
		}
	}
}

func (q *RateLimitingWorkQueue) Get() (string, bool) {
	q.mu.Lock()
	defer q.mu.Unlock()
	for len(q.queue) == 0 && !q.shutdown {
		q.cond.Wait()
	}
	if q.shutdown && len(q.queue) == 0 {
		return "", false
	}
	key := q.queue[0]
	q.queue = q.queue[1:]
	delete(q.queuedSet, key)
	delete(q.dirtySet, key)
	q.processingSet[key] = struct{}{}
	return key, true
}

func (q *RateLimitingWorkQueue) Done(key string, success bool) {
	q.mu.Lock()
	defer q.mu.Unlock()
	delete(q.processingSet, key)

	if !success {
		q.failureCounts[key]++
		attempts := q.failureCounts[key]
		backoff := time.Duration(math.Min(5000, float64(100*(1<<min(attempts, 6)))) * float64(time.Millisecond))
		time.AfterFunc(backoff+time.Duration(rand.Intn(50))*time.Millisecond, func() {
			q.Add(key)
		})
	} else {
		delete(q.failureCounts, key)
	}

	if _, dirty := q.dirtySet[key]; dirty {
		if _, queued := q.queuedSet[key]; !queued {
			q.queue = append(q.queue, key)
			q.queuedSet[key] = struct{}{}
			q.cond.Signal()
		}
	}
}

// ClusterReconciler реалізує бізнес-логіку узгодження
type ClusterReconciler struct {
	mu       sync.Mutex
	store    map[string]ManagedCluster
	cloudVMs map[string][]string
}

func (r *ClusterReconciler) Reconcile(ctx context.Context, key string) ReconcileResult {
	r.mu.Lock()
	cluster, exists := r.store[key]
	r.mu.Unlock()

	if !exists {
		return ReconcileResult{Requeue: false}
	}

	finalizer := "infra.example.com/cleanup-vms"

	// Обробка безпечного каскадного видалення
	if cluster.DeletionTimestamp {
		for i, f := range cluster.Finalizers {
			if f == finalizer {
				// Очищення фізичних VM
				r.mu.Lock()
				r.cloudVMs[key] = nil
				cluster.Finalizers = append(cluster.Finalizers[:i], cluster.Finalizers[i+1:]...)
				cluster.ResourceVersion++
				r.store[key] = cluster
				r.mu.Unlock()
				return ReconcileResult{Requeue: false}
			}
		}
		return ReconcileResult{Requeue: false}
	}

	// Читання стану фізичного світу
	r.mu.Lock()
	vms := append([]string{}, r.cloudVMs[key]...)
	r.mu.Unlock()

	// Diff
	delta := cluster.Spec.TargetReplicas - len(vms)

	// Act
	if delta > 0 {
		for i := 0; i < delta; i++ {
			vmID := fmt.Sprintf("vm-%d", rand.Intn(10000))
			vms = append(vms, vmID)
		}
	} else if delta < 0 {
		vms = vms[:cluster.Spec.TargetReplicas]
	}

	// Збереження фізичного стану та оновлення статусу через CAS
	r.mu.Lock()
	defer r.mu.Unlock()
	current := r.store[key]
	if current.ResourceVersion != cluster.ResourceVersion {
		return ReconcileResult{Requeue: true, RequeueAfter: 100 * time.Millisecond}
	}

	r.cloudVMs[key] = vms
	current.Status.AvailableReplicas = len(vms)
	current.Status.ActiveInstanceIDs = vms
	current.Status.Phase = "Ready"
	current.ResourceVersion++
	r.store[key] = current

	return ReconcileResult{Requeue: false}
}
```
:::

---

## 3. Механіка коалесценції та паралелізму в черзі завдань

Черга завдань `RateLimitingWorkQueue` розв'язує фундаментальну проблему узгодженості в умовах високої конкурентності: як дозволити паралельну обробку тисяч різних об'єктів пулом воркерів, гарантуючи при цьому, що один конкретний ключ ніколи не буде оброблятися двома потоками одночасно.

Для цього черга розділяє стан кожного ключа на три неперетинні множини:

1. **`queue_` та `queued_set_`**: впорядкований список ключів, що очікують на вільний потік у пулі воркерів.
2. **`dirty_set_`**: множина «брудних» ключів, які отримали нові оновлення від інформера. Якщо під час виконання тривалої операції `Reconcile()` (наприклад, очікування відповіді хмарного API протягом двох секунд) для цього ж кластера надходить ще п'ять подій зміни специфікації, вони не створюють п'ять паралельних завдань. Усі вони коалесцуються (згортаються) в єдиний прапорець у `dirty_set_`.
3. **`processing_set_`**: множина ключів, над якими саме зараз працює один із потоків. Жоден інший воркер не зможе отримати цей ключ із черги до виклику методу `done()`.

Коли потік завершує виконання `Reconcile()`, він викликає `done(key)`. Метод видаляє ключ із `processing_set_` і перевіряє `dirty_set_`. Якщо за час обробки надійшли нові оновлення, ключ негайно повертається в кінець черги `queue_` для чергової ітерації. Такий трифазний механізм усуває гонки стану в пам'яті без необхідності блокування всієї черги.

---

## 4. Двоетапне каскадне видалення через фіналізатори (Finalizers)

Класична помилка імперативних систем — видалення метаданих об'єкта до того, як будуть фізично вивільнені зовнішні ресурси. Якщо база даних видаляє рядок кластера, контролер втрачає контекст і більше ніколи не дізнається, які саме віртуальні машини, балансувальники навантаження чи дискові сховища належали цьому кластеру в хмарі AWS або Azure. Виникає незворотний витік ресурсів («зомбі-інфраструктура»).

Механізм фіналізаторів реалізує надійний шаблон двоетапного видалення:

1. **Фаза реєстрації обіцянки**: під час створення кластера контролер перевіряє наявність власного ідентифікатора у списку `finalizers` (наприклад, `infra.example.com/cleanup-vms`). Якщо його немає, він записує його в масив і фіксує зміну в сховищі.
2. **Фаза запиту на видалення**: коли користувач ініціює видалення об'єкта, сховище не видаляє запис фізично. Воно лише встановлює мітку часу видалення `deletionTimestamp = now()`.
3. **Фаза очищення реального світу**: цикл узгодження виявляє наявність `deletionTimestamp` і починає процедуру вивільнення інфраструктури: надсилає запити на видалення фізичних віртуальних машин до API хмари, чекає підтвердження віддаленого знищення серверів і лише після цього видаляє свій рядок зі списку `finalizers`.
4. **Фаза остаточного знищення**: коли масив `finalizers` стає порожнім, сховище автоматично стирає об'єкт метаданих.

Якщо в процесі очищення хмарне API повертає помилку 503, контролер повертає `ReconcileResult{Requeue: true}`, відкладає виконання на час бекофу і повторює спробу. Метадані в базі залишаються заблокованими фіналізатором, гарантуючи, що жоден ресурс не буде забутий або втрачений.

---

## 5. Оптимістичне блокування (OCC) та розв'язання конфліктів запису

Контролер працює в асинхронному середовищі, де користувач або інший сервіс може змінити поле `spec.target_replicas` саме в ту мілісекунду, коли контролер обчислює різницю `diff` або оновлює `status`.

Якщо контролер здійснить «сліпий» безумовний запис, він затре щойно внесені зміни користувача старою версією об'єкта, що зберігалася в локальній пам'яті на початку виклику функції.

Для захисту від втрачених оновлень (Lost Updates) рушій застосовує оптимістичне блокування версій:

- Кожен об'єкт у сховищі містить монотонний лічильник `resource_version`.
- Під час читання на фазі Observe контролер фіксує поточний номер версії (наприклад, `version = 42`).
- На фазі збереження статусу виконується атомарна операція Compare-And-Swap (CAS): сховище приймає оновлення лише за умови, що поточна версія в базі досі дорівнює `42`, і атомарно інкрементує її до `43`.
- Якщо версія змінилася (користувач оновив конфігурацію до `version = 43`), сховище відхиляє запис контролера.
- Контролер перехоплює помилку конфлікту CAS, повертає `ReconcileResult{Requeue: true}` і негайно завершує виклик. На наступній ітерації він перечитає свіжу версію `43` зі сховища і розрахує коригувальні дії за новими вимогами користувача.
