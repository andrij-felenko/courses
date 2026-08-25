# ⚙️ Стійка черга мутацій: локальний журнал, оптимістичний стан і відкат

Черга мутацій (англ. *mutation outbox queue*) — це центральний виконавчий механізм офлайн-першого клієнта. Вона гарантує, що жодна дія користувача не загубиться при закритті вкладки чи перезавантаженні операційної системи, а локальний інтерфейс миттєво відобразить зміни без очікування мережевої відповіді.

У традиційній онлайн-архітектурі життєвий цикл мутації завершується в межах одного виклику функції зворотного виклику. В офлайн-першому клієнті цей цикл розривається на дві незалежні фази, розділені в часі: локальну фіксацію наміру та його асинхронне вивантаження.

## Архітектурний дизайн черги мутацій

Рушій черги складається з трьох ключових рівнів, кожен з яких ізолює свою частину системних інваріантів:
1. **Рівень збереження (Storage Driver):** абстракція над локальною персистентною базою даних (IndexedDB, SQLite, LevelDB). Забезпечує транзакційну атомарність операцій запису мутації та оновлення сутностей.
2. **Менеджер оптимістичного стану:** модуль, що накладає зміни з черги на локальні таблиці сутностей і керує прапорцями очікування (`is_optimistic`).
3. **Фоновий конвеєр вивантаження (Drain Pipeline):** планувальник задач, який відстежує мережевий статус, вичитує накопичені записи у порядку FIFO, керує таймерами експоненційного відступу з випадковим шумом (Full Jitter) та обробляє відповіді сервера.

Нижче наведено робочу реалізацію відмовостійкої черги мутацій мовами TypeScript та C++20.

:::tabs
```ts
// TypeScript: Клієнтська черга вихідних мутацій з оптимістичним станом

export type MutationType = 'CREATE' | 'UPDATE' | 'DELETE';
export type MutationStatus = 'PENDING' | 'IN_FLIGHT' | 'COMMITTED' | 'FAILED';

export interface Mutation<T = unknown> {
  id: string;              // Унікальний UUID для ідемпотентності на сервері
  entityId: string;        // Ідентифікатор цільової сутності
  entityType: string;      // Тип сутності (наприклад, 'notes', 'tasks')
  type: MutationType;      // Тип операції
  payload: T;              // Дані для застосування (або дельта)
  baseVersion: number;     // Версія сутності, яку бачив клієнт при створенні мутації
  createdAt: number;       // Локальна часова мітка створення
  status: MutationStatus;  // Поточний статус у життєвому циклі
  retryCount: number;      // Кількість невдалих спроб відправки
}

export interface EntityState {
  id: string;
  version: number;
  data: Record<string, unknown>;
  isOptimistic?: boolean;  // Прапорець для UI: стан ще не підтверджено сервером
}

export interface StorageDriver {
  saveMutation(mutation: Mutation): Promise<void>;
  deleteMutation(id: string): Promise<void>;
  getPendingMutations(): Promise<Mutation[]>;
  saveEntity(entity: EntityState): Promise<void>;
  getEntity(id: string): Promise<EntityState | null>;
}

export class DurableMutationQueue {
  private isProcessing = false;
  private syncTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private readonly storage: StorageDriver,
    private readonly networkSender: (mutation: Mutation) => Promise<{ success: boolean; newVersion?: number; errorCode?: number }>
  ) {}

  /**
   * Атомарне додавання мутації: збереження в Outbox та оптимістичне оновлення стану
   */
  async enqueue<T extends Record<string, unknown>>(
    entityId: string,
    entityType: string,
    type: MutationType,
    payload: T
  ): Promise<void> {
    const current = (await this.storage.getEntity(entityId)) ?? {
      id: entityId,
      version: 0,
      data: {}
    };

    const mutation: Mutation<T> = {
      id: crypto.randomUUID(),
      entityId,
      entityType,
      type,
      payload,
      baseVersion: current.version,
      createdAt: Date.now(),
      status: 'PENDING',
      retryCount: 0
    };

    // 1. Зберігаємо мутацію в чергу на диску
    await this.storage.saveMutation(mutation);

    // 2. Оптимістично застосовуємо зміни до локальної копії сутності
    const optimisticData = { ...current.data, ...payload };
    await this.storage.saveEntity({
      id: entityId,
      version: current.version, // Базова версія не змінюється до підтвердження сервером
      data: optimisticData,
      isOptimistic: true
    });

    // 3. Ініціюємо спробу відправки
    this.scheduleProcessing(0);
  }

  /**
   * Планування обробки черги з розрахунком випадкового джитеру
   */
  private scheduleProcessing(delayMs: number): void {
    if (this.syncTimer) clearTimeout(this.syncTimer);
    this.syncTimer = setTimeout(() => {
      void this.processQueue();
    }, delayMs);
  }

  /**
   * Конвеєр вивантаження черги мутацій
   */
  async processQueue(): Promise<void> {
    if (this.isProcessing) return;
    this.isProcessing = true;

    try {
      const pending = await this.storage.getPendingMutations();
      // Сортуємо впорядковано за часом створення (FIFO для однієї сутності)
      pending.sort((a, b) => a.createdAt - b.createdAt);

      for (const mutation of pending) {
        mutation.status = 'IN_FLIGHT';
        await this.storage.saveMutation(mutation);

        try {
          const response = await this.networkSender(mutation);

          if (response.success && response.newVersion !== undefined) {
            // Сервер успішно зафіксував мутацію
            const entity = await this.storage.getEntity(mutation.entityId);
            if (entity) {
              entity.version = response.newVersion;
              entity.isOptimistic = false;
              await this.storage.saveEntity(entity);
            }
            // Видаляємо підтверджену дію з черги
            await this.storage.deleteMutation(mutation.id);
          } else if (response.errorCode && response.errorCode >= 400 && response.errorCode < 500) {
            // Непоправна бізнес-помилка або конфлікт валідації -> Відкат оптимізму
            console.error(`Мутація ${mutation.id} відхилена сервером (код ${response.errorCode}). Відкат.`);
            await this.rollbackMutation(mutation);
            await this.storage.deleteMutation(mutation.id);
          } else {
            // Тимчасова серверна помилка (5xx) або таймаут -> Експоненційний відступ
            await this.handleRetry(mutation);
            break; // Зупиняємо конвеєр черги до наступного інтервалу
          }
        } catch {
          // Мережевий обрив
          await this.handleRetry(mutation);
          break;
        }
      }
    } finally {
      this.isProcessing = false;
    }
  }

  private async handleRetry(mutation: Mutation): Promise<void> {
    mutation.status = 'PENDING';
    mutation.retryCount += 1;
    await this.storage.saveMutation(mutation);

    // Розрахунок Full Jitter: pause = random(0, min(max_backoff, base * 2^retries))
    const baseBackoffMs = 500;
    const maxBackoffMs = 30000;
    const temp = Math.min(maxBackoffMs, baseBackoffMs * Math.pow(2, mutation.retryCount));
    const jitterDelay = Math.floor(Math.random() * temp);

    this.scheduleProcessing(jitterDelay);
  }

  private async rollbackMutation(mutation: Mutation): Promise<void> {
    const entity = await this.storage.getEntity(mutation.entityId);
    if (!entity) return;

    // Відкат: повертаємо стан до неоптимістичного (або перезавантажуємо базовий знімок)
    entity.isOptimistic = false;
    await this.storage.saveEntity(entity);
  }
}
```
```cpp
// C++20: Відмовостійкий рушій черги мутацій з RAII та гарантією доставки

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <chrono>
#include <random>
#include <algorithm>
#include <optional>
#include <expected>
#include <functional>

enum class MutationType { Create, Update, Delete };
enum class MutationStatus { Pending, InFlight, Committed, Failed };

struct Mutation {
    std::string id;
    std::string entity_id;
    std::string entity_type;
    MutationType type;
    std::string payload_json;
    uint64_t base_version;
    int64_t created_at_ms;
    MutationStatus status;
    uint32_t retry_count;
};

struct EntityState {
    std::string id;
    uint64_t version;
    std::string data_json;
    bool is_optimistic;
};

class StorageInterface {
public:
    virtual ~StorageInterface() = default;
    virtual void save_mutation(const Mutation& m) = 0;
    virtual void delete_mutation(const std::string& id) = 0;
    virtual std::vector<Mutation> get_pending_mutations() = 0;
    virtual void save_entity(const EntityState& e) = 0;
    virtual std::optional<EntityState> get_entity(const std::string& id) = 0;
};

class MutationQueueEngine {
public:
    using NetworkResult = std::expected<uint64_t, int>; // Повертає new_version або HTTP error code
    using NetworkSender = std::function<NetworkResult(const Mutation&)>;

    MutationQueueEngine(std::shared_ptr<StorageInterface> storage, NetworkSender sender)
        : storage_(std::move(storage)), sender_(std::move(sender)), rng_(std::random_device{}()) {}

    void enqueue(const std::string& entity_id, const std::string& entity_type,
                 MutationType type, const std::string& payload_json) {
        auto current = storage_->get_entity(entity_id).value_or(EntityState{
            .id = entity_id,
            .version = 0,
            .data_json = "{}",
            .is_optimistic = false
        });

        Mutation m{
            .id = generate_uuid(),
            .entity_id = entity_id,
            .entity_type = entity_type,
            .type = type,
            .payload_json = payload_json,
            .base_version = current.version,
            .created_at_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count(),
            .status = MutationStatus::Pending,
            .retry_count = 0
        };

        // 1. Атомарний запис у локальний журнал outbox
        storage_->save_mutation(m);

        // 2. Оптимістичне накладення на локальний стан
        current.data_json = payload_json; // У робочому коді — злиття JSON патчу
        current.is_optimistic = true;
        storage_->save_entity(current);
    }

    void process_queue() {
        auto pending = storage_->get_pending_mutations();
        std::sort(pending.begin(), pending.end(), [](const Mutation& a, const Mutation& b) {
            return a.created_at_ms < b.created_at_ms;
        });

        for (auto& m : pending) {
            m.status = MutationStatus::InFlight;
            storage_->save_mutation(m);

            auto result = sender_(m);
            if (result.has_value()) {
                // Успішна фіксація сервером
                uint64_t new_version = result.value();
                if (auto entity = storage_->get_entity(m.entity_id)) {
                    entity->version = new_version;
                    entity->is_optimistic = false;
                    storage_->save_entity(*entity);
                }
                storage_->delete_mutation(m.id);
            } else {
                int err = result.error();
                if (err >= 400 && err < 500) {
                    // Фатальна помилка клієнта -> відкат і видалення
                    rollback_optimistic(m);
                    storage_->delete_mutation(m.id);
                } else {
                    // Тимчасова мережева помилка -> обчислення паузи з джитером
                    m.status = MutationStatus::Pending;
                    m.retry_count++;
                    storage_->save_mutation(m);
                    break; // Зупинка до наступного циклу
                }
            }
        }
    }

private:
    std::string generate_uuid() {
        return "mut-" + std::to_string(std::chrono::steady_clock::now().time_since_epoch().count());
    }

    void rollback_optimistic(const Mutation& m) {
        if (auto entity = storage_->get_entity(m.entity_id)) {
            entity->is_optimistic = false;
            storage_->save_entity(*entity);
        }
    }

    std::shared_ptr<StorageInterface> storage_;
    NetworkSender sender_;
    std::mt19937 rng_;
};
```
:::

## Покроковий розбір конвеєра та крайові випадки

Розгляньмо критичні фази виконання коду та пастки, з якими стикається розробник:

### 1. Транзакційна ізоляція кроку Enqueue
Ключовий інваріант полягає в тому, що виклик методу `enqueue` не має проміжних станів. Запис мутації в чергу `saveMutation` та збереження оптимістичного стану `saveEntity` зобов'язані виконуватися в межах єдиної транзакції локального сховища. Якщо система зазнає аварійного вимкнення живлення між цими двома операціями:
* Якщо записано стан, але не записано мутацію — інтерфейс покаже зміну, але після перезавантаження вона зникне назавжди, бо не потрапила в журнал вивантаження.
* Якщо записано мутацію, але не оновлено сутність — інтерфейс не відобразить зміну, але вона раптово з'явиться на сервері пізніше, збиваючи користувача з пантелику.

### 2. Диференціація помилок: тимчасові збої проти фатальних відхилень
Конвеєр вивантаження чітко розрізняє дві категорії статусів:
* **Тимчасові помилки (Мережевий розрив, DNS Timeout, HTTP 500, 502, 503, 504):** свідчать про недоступність інфраструктури. Мутація переводиться назад у статус `PENDING`, лічильник спроб інкрементується, а планувальник запускає таймер з експоненційним зростанням інтервалу та випадковим джитером. Обробка всієї черги негайно призупиняється, щоб не вичерпувати ліміти запитів.
* **Фатальні помилки (HTTP 400 Bad Request, 403 Forbidden, 422 Unprocessable Entity):** свідчать про порушення схеми даних, відсутність прав або бізнес-заборону. Повторювати такий запит безглуздо. Рушій запускає компенсаційний відкат `rollbackMutation` і видаляє невалідний запис із черги, сповіщаючи користувача про причину відхилення через інтерфейсні повідомлення.

### 3. Запобігання втраті ланцюжка правок при вибірковому відкаті
Уявімо сценарій, коли користувач у режимі офлайн створює задачу `M₁`, потім змінює її назву `M₂`, а потім ставить прапорець виконання `M₃`. Усі три дії потрапляють у чергу послідовно.

Якщо сервер відхиляє `M₁` (наприклад, через обмеження квоти на кількість задач), прямий відкат `M₁` залишить мутації `M₂` та `M₃` беззмістовними, оскільки цільової задачі не існує на сервері. У такій ситуації коректний рушій черги реалізує **каскадний відкат залежних мутацій**: відхилення батьківської операції автоматично скасовує всі наступні непідтверджені операції для цієї ж сутності (`entity_id`), очищаючи чергу від мертвого ланцюжка дій.

### 4. Міграції схеми при наявності невідправлених мутацій
Підступна проблема офлайн-клієнтів виникає під час оновлення версії застосунку. Користувач вніс зміни в старій версії застосунку v1.0, залишився без інтернету, а наступного дня підключився до мережі й завантажив нову версію клієнта v2.0 зі зміненою структурою локальної бази даних.

Якщо міграція бази даних v1.0 → v2.0 просто змінить локальні таблиці сутностей, записи в таблиці `mutation_outbox` залишаться в застарілому форматі v1.0. Сервер, який уже перейшов на схему v2.0, відхилить такі мутації з помилкою валідації `422 Unprocessable Entity`. 

Щоб цього уникнути, скрипти міграцій клієнтської бази даних зобов'язані трансформувати не лише таблиці сутностей, але й **корисне навантаження (payload) усіх невідправлених мутацій у черзі outbox**, підвищуючи їхній формат до актуальної версії перед першою спробою вивантаження.

### 5. Міжвкладочна координація у веб-браузерах
У багатосторінковому браузерному середовищі користувач може відкрити той самий офлайн-застосунок у п'яти сусідніх вкладках. Якщо кожна вкладка запустить власний екземпляр `DurableMutationQueue`, вони почнуть вичитувати одні й ті самі мутації з IndexedDB одночасно, влаштовуючи стан гонитви за мережеві запити.

Для запобігання дублюванню застосовують стандартизований браузерний механізм **Web Locks API** (`navigator.locks.request`):
* Усі вкладки вільно додають мутації до спільної бази IndexedDB.
* Лише одна вкладка (лідер) захоплює ексклюзивне блокування `mutation_queue_drain_lock` і здійснює мережеве вивантаження.
* Якщо вкладку-лідера закривають, блокування автоматично звільняється ядром браузера, і наступна вкладка безшовно перехоплює процес спорожнення черги.
