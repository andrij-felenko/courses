# ⚙️ Диспетчер оптимістичних мутацій: черга намірів, перебазування й заміна Temp-ID

Оптимістичне оновлення інтерфейсу здається тривіальним лише до першого зіткнення з реальними умовами експлуатації: нестабільною мобільною мережею, швидкими послідовними діями користувача або каскадно залежними сутностями.

Якщо розробник обмежується наївною мутацією стану із подальшим відновленням за збереженим знімком у разі збою, система неминуче породжує дефекти узгодженості:
* **Аномалія втраченого оновлення (Lost Update):** якщо користувач виконав дії A, B і C, а дія A зазнала мережевої помилки, сліпе відновлення знімка до дії A затре оптимістичні результати дій B і C, хоча їхні запити вже успішно летять до сервера.
* **Каскадний розрив зв'язків (Broken References):** якщо дія A створює нову сутність із тимчасовим клієнтським ідентифікатором `temp-id`, а дія B створює дочірній елемент, що посилається на цей `temp-id`, вихід дії B у мережу без попередньої підміни ключа призведе до помилки `400 Bad Request` або створення сутності-сироти на бекенді.
* **Аномалія застарілого запису (Out-of-order Overwrite):** якщо користувач швидко вмикає і вимикає стан перемикача, повільна відповідь першого запиту може надійти пізніше за швидку відповідь другого й перетерти актуальний стан застарілими даними.

Для розв'язання цих проблем необхідний повноцінний **диспетчер оптимістичних мутацій**, побудований на принципах трьох шарів стану, черги намірів, перебазування журналу та динамічної трансляції ідентифікаторів.

## Архітектура диспетчера

Диспетчер мутацій розділяє керування станом на чотири скоординовані підсистеми:

1. **Канонічне сховище (`canonicalState`):** зберігає стан, верифікований і підтверджений сервером. Воно мутує виключно під час обробки відповідей бекенда `HTTP 2xx` або подій WebSocket.
2. **Впорядкована черга намірів (`pendingQueue`):** список активних мутацій, які застосовані локально, але ще чекають завершення мережевого циклу. Кожен запис містить унікальний ключ ідемпотентності, дельту операції, тимчасові ідентифікатори та екземпляр `AbortController`.
3. **Обчислювач стану подання (`getViewState`):** чиста функція згортки (*reduce*), яка накладає всі незавершені мутації з черги на канонічний стан. Інтерфейс підписується на цей стан і перемальовується миттєво при кожній зміні черги або канонічного сховища.
4. **Таблиця трансляції ключів (`Identity Map`):** глобальний мапінг `tempId ↦ serverId`. Коли сервер повертає постійний первинний ключ для новоствореної сутності, диспетчер автоматично оновлює посилання в усіх наступних мутаціях черги перед їхнім виходом у мережу.

Нижче наведено промислові реалізації диспетчера оптимістичних мутацій мовами TypeScript та C++.

:::tabs
```ts
/**
 * Диспетчер оптимістичних мутацій на TypeScript
 */

export interface Entity {
  id: string;
  title: string;
  completed: boolean;
  parentId?: string;
}

export interface State {
  entities: Record<string, Entity>;
}

export type MutationType = 'CREATE' | 'UPDATE' | 'DELETE';

export interface Mutation {
  id: string;              // Унікальний ID операції (UUID / Idempotency Key)
  type: MutationType;
  entityId: string;        // Цільовий ID сутності (може бути temp-id)
  tempId?: string;         // Якщо створюється нова сутність
  payload: Partial<Entity>;
  timestamp: number;
  abortController: AbortController;
  retries: number;
}

export interface ServerResponse {
  success: boolean;
  tempId?: string;
  serverId?: string;
  data?: Partial<Entity>;
  error?: { status: number; message: string };
}

export class OptimisticMutationManager {
  private canonicalState: State;
  private pendingQueue: Mutation[] = [];
  private idMap: Map<string, string> = new Map(); // tempId -> serverId
  private listeners: Array<(state: State) => void> = [];

  constructor(initialState: State = { entities: {} }) {
    this.canonicalState = JSON.parse(JSON.stringify(initialState));
  }

  /**
   * Підписка на оновлення стану подання (View State)
   */
  public subscribe(listener: (state: State) => void): () => void {
    this.listeners.push(listener);
    listener(this.getViewState());
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notify(): void {
    const state = this.getViewState();
    for (const listener of this.listeners) {
      listener(state);
    }
  }

  /**
   * Чистий редуктор: застосовує одну мутацію до стану
   */
  private applyMutation(state: State, mutation: Mutation): State {
    const nextState: State = {
      entities: { ...state.entities }
    };

    // Трансляція ID якщо сутність посилається на замінений temp-id
    const targetId = this.resolveId(mutation.entityId);
    const resolvedParentId = mutation.payload.parentId
      ? this.resolveId(mutation.payload.parentId)
      : undefined;

    switch (mutation.type) {
      case 'CREATE': {
        const id = mutation.tempId || targetId;
        nextState.entities[id] = {
          id,
          title: mutation.payload.title || '',
          completed: mutation.payload.completed || false,
          ...(resolvedParentId ? { parentId: resolvedParentId } : {})
        };
        break;
      }
      case 'UPDATE': {
        if (nextState.entities[targetId]) {
          nextState.entities[targetId] = {
            ...nextState.entities[targetId],
            ...mutation.payload,
            id: targetId,
            ...(resolvedParentId ? { parentId: resolvedParentId } : {})
          };
        }
        break;
      }
      case 'DELETE': {
        delete nextState.entities[targetId];
        break;
      }
    }

    return nextState;
  }

  /**
   * Обчислення View State як згортки черги поверх канонічного стану
   */
  public getViewState(): State {
    return this.pendingQueue.reduce(
      (state, mut) => this.applyMutation(state, mut),
      this.canonicalState
    );
  }

  public resolveId(id: string): string {
    return this.idMap.get(id) || id;
  }

  /**
   * Додавання нової оптимістичної дії
   */
  public async dispatch(
    type: MutationType,
    entityId: string,
    payload: Partial<Entity>,
    networkExecutor: (mut: Mutation, signal: AbortSignal) => Promise<ServerResponse>
  ): Promise<void> {
    const mutationId = `mut_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    const tempId = type === 'CREATE' ? entityId : undefined;
    const abortController = new AbortController();

    // Скасовуємо попередні незавершені мутації ДЛЯ ТІЄЇ САМОЇ СУТНОСТІ (захист від гонок)
    for (const prev of this.pendingQueue) {
      if (this.resolveId(prev.entityId) === this.resolveId(entityId) && prev.type === 'UPDATE') {
        prev.abortController.abort();
      }
    }

    const mutation: Mutation = {
      id: mutationId,
      type,
      entityId,
      tempId,
      payload,
      timestamp: Date.now(),
      abortController,
      retries: 0
    };

    // 1. Оптимістично додаємо в чергу
    this.pendingQueue.push(mutation);
    this.notify(); // UI оновлюється миттєво (<1 мс)

    // 2. Асинхронно відправляємо в мережу
    await this.executeMutation(mutation, networkExecutor);
  }

  private async executeMutation(
    mutation: Mutation,
    networkExecutor: (mut: Mutation, signal: AbortSignal) => Promise<ServerResponse>
  ): Promise<void> {
    try {
      // Підміняємо payload актуальними ID перед виходом у мережу
      const currentMutation: Mutation = {
        ...mutation,
        entityId: this.resolveId(mutation.entityId),
        payload: {
          ...mutation.payload,
          parentId: mutation.payload.parentId ? this.resolveId(mutation.payload.parentId) : undefined
        }
      };

      const response = await networkExecutor(currentMutation, mutation.abortController.signal);

      if (response.success) {
        this.handleSuccess(mutation, response);
      } else {
        this.handleFailure(mutation, response.error, networkExecutor);
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        // Запит було скасовано новішою мутацією — просто прибираємо з черги
        this.pendingQueue = this.pendingQueue.filter(m => m.id !== mutation.id);
        return;
      }
      // Мережевий таймаут або розрив з'єднання — переводимо в режим повтору
      this.handleNetworkError(mutation, networkExecutor);
    }
  }

  private handleSuccess(mutation: Mutation, res: ServerResponse): void {
    // Якщо створювали нову сутність і сервер повернув канонічний ID
    if (mutation.tempId && res.serverId) {
      this.idMap.set(mutation.tempId, res.serverId);
      // Оновлюємо посилання в канонічному та всіх очікуючих мутаціях
      mutation.entityId = res.serverId;
    }

    // 1. Фіксуємо зміну в канонічному стані сервера
    this.canonicalState = this.applyMutation(this.canonicalState, mutation);

    // 2. Видаляємо виконану мутацію з черги pending
    this.pendingQueue = this.pendingQueue.filter(m => m.id !== mutation.id);

    // 3. Сповіщаємо UI (згортка тепер спирається на оновлений канонічний стан)
    this.notify();
  }

  private handleFailure(
    mutation: Mutation,
    error: { status: number; message: string } | undefined,
    networkExecutor: (mut: Mutation, signal: AbortSignal) => Promise<ServerResponse>
  ): void {
    const status = error?.status || 500;

    // Фатальні помилки валідації або доступу (4xx окрім 408/429) -> REBASE ROLLBACK
    if (status >= 400 && status < 500 && status !== 408 && status !== 429) {
      console.warn(`[OptimisticManager] Fatal mutation failure (${status}): ${error?.message}`);
      // Видаляємо збійну мутацію з черги. Решта мутацій лишаються!
      this.pendingQueue = this.pendingQueue.filter(m => m.id !== mutation.id);
      this.notify(); // Rebase: UI автоматично перераховується без цієї дії
      return;
    }

    // Тимчасові помилки бекенда (5xx, 429) -> Повтор
    this.handleNetworkError(mutation, networkExecutor);
  }

  private handleNetworkError(
    mutation: Mutation,
    networkExecutor: (mut: Mutation, signal: AbortSignal) => Promise<ServerResponse>
  ): void {
    mutation.retries += 1;
    const maxRetries = 4;

    if (mutation.retries <= maxRetries) {
      const delayMs = Math.min(1000 * Math.pow(2, mutation.retries), 10000);
      console.log(`[OptimisticManager] Scheduling retry #${mutation.retries} in ${delayMs}ms`);
      setTimeout(() => {
        if (this.pendingQueue.some(m => m.id === mutation.id)) {
          this.executeMutation(mutation, networkExecutor);
        }
      }, delayMs);
    } else {
      // Вичерпано спроби — відкат за перебазуванням
      this.pendingQueue = this.pendingQueue.filter(m => m.id !== mutation.id);
      this.notify();
    }
  }
}
```
```cpp
/**
 * Диспетчер оптимістичних мутацій на C++ (Modern C++20)
 */

#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
#include <memory>
#include <functional>
#include <algorithm>
#include <chrono>
#include <optional>

struct Entity {
    std::string id;
    std::string title;
    bool completed{false};
    std::optional<std::string> parentId;
};

struct State {
    std::unordered_map<std::string, Entity> entities;
};

enum class MutationType { CREATE, UPDATE, DELETE_OP };

struct Mutation {
    std::string id;
    MutationType type;
    std::string entityId;
    std::optional<std::string> tempId;
    Entity payload;
    std::chrono::system_clock::time_point timestamp;
    bool aborted{false};
    int retries{0};
};

struct ServerResponse {
    bool success{false};
    std::optional<std::string> tempId;
    std::optional<std::string> serverId;
    int statusCode{200};
    std::string errorMessage;
};

class OptimisticMutationManager {
public:
    using StateListener = std::function<void(const State&)>;
    using NetworkExecutor = std::function<ServerResponse(const Mutation&)>;

    explicit OptimisticMutationManager(State initial = {})
        : canonicalState_(std::move(initial)) {}

    void subscribe(StateListener listener) {
        listeners_.push_back(listener);
        listener(getViewState());
    }

    std::string resolveId(const std::string& id) const {
        auto it = idMap_.find(id);
        if (it != idMap_.end()) return it->second;
        return id;
    }

    State getViewState() const {
        State view = canonicalState_;
        for (const auto& mut : pendingQueue_) {
            if (!mut.aborted) {
                applyMutation(view, mut);
            }
        }
        return view;
    }

    void dispatch(MutationType type,
                  const std::string& entityId,
                  Entity payload,
                  const NetworkExecutor& executor) {
        std::string mutId = "mut_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count());
        std::optional<std::string> tempId = (type == MutationType::CREATE) ? std::make_optional(entityId) : std::nullopt;

        // Захист від гонок: скасовуємо незавершені попередні UPDATE для тієї ж сутності
        std::string resolvedTarget = resolveId(entityId);
        for (auto& prev : pendingQueue_) {
            if (resolveId(prev.entityId) == resolvedTarget && prev.type == MutationType::UPDATE) {
                prev.aborted = true;
            }
        }

        Mutation mut{
            mutId,
            type,
            entityId,
            tempId,
            std::move(payload),
            std::chrono::system_clock::now(),
            false,
            0
        };

        // 1. Оптимістично додаємо в чергу
        pendingQueue_.push_back(mut);
        notify(); // UI оновлюється миттєво

        // 2. Виконання запиту в мережі
        executeMutation(pendingQueue_.back(), executor);
    }

private:
    State canonicalState_;
    std::vector<Mutation> pendingQueue_;
    std::unordered_map<std::string, std::string> idMap_;
    std::vector<StateListener> listeners_;

    void notify() {
        State currentView = getViewState();
        for (auto& l : listeners_) {
            l(currentView);
        }
    }

    void applyMutation(State& state, const Mutation& mutation) const {
        std::string targetId = resolveId(mutation.entityId);
        std::optional<std::string> resolvedParent = mutation.payload.parentId
            ? std::make_optional(resolveId(*mutation.payload.parentId))
            : std::nullopt;

        switch (mutation.type) {
            case MutationType::CREATE: {
                std::string id = mutation.tempId.value_or(targetId);
                state.entities[id] = Entity{
                    id,
                    mutation.payload.title,
                    mutation.payload.completed,
                    resolvedParent
                };
                break;
            }
            case MutationType::UPDATE: {
                auto it = state.entities.find(targetId);
                if (it != state.entities.end()) {
                    it->second.title = mutation.payload.title;
                    it->second.completed = mutation.payload.completed;
                    it->second.parentId = resolvedParent;
                }
                break;
            }
            case MutationType::DELETE_OP: {
                state.entities.erase(targetId);
                break;
            }
        }
    }

    void executeMutation(Mutation& mutation, const NetworkExecutor& executor) {
        if (mutation.aborted) {
            removeMutation(mutation.id);
            return;
        }

        ServerResponse resp = executor(mutation);

        if (resp.success) {
            if (mutation.tempId && resp.serverId) {
                idMap_[*mutation.tempId] = *resp.serverId;
                mutation.entityId = *resp.serverId;
            }
            // Фіксуємо зміну в канонічному стані
            applyMutation(canonicalState_, mutation);
            removeMutation(mutation.id);
            notify();
        } else {
            if (resp.statusCode >= 400 && resp.statusCode < 500 && resp.statusCode != 408) {
                // Фатальна помилка -> REBASE: просто видаляємо з черги
                std::cerr << "[OptimisticManager] Rollback: " << resp.errorMessage << "\n";
                removeMutation(mutation.id);
                notify();
            } else {
                // Мережевий збій -> повтор або відкат після ліміту
                mutation.retries++;
                if (mutation.retries > 3) {
                    removeMutation(mutation.id);
                    notify();
                }
            }
        }
    }

    void removeMutation(const std::string& id) {
        pendingQueue_.erase(
            std::remove_if(pendingQueue_.begin(), pendingQueue_.end(),
                           [&](const Mutation& m) { return m.id == id; }),
            pendingQueue_.end()
        );
    }
};
```
:::

## Покроковий розбір життєвого циклу

Розглянемо, як диспетчер обробляє складний сценарій: створення сутності, її негайне редагування та обробку збою другого запиту.

### 1. Ініціалізація та перша дія (Create)
Користувач створює завдання «Підготувати звіт». Клієнт генерує `temp_1`.
* Диспетчер додає мутацію `CREATE { tempId: "temp_1", title: "Підготувати звіт" }` у `pendingQueue`.
* `getViewState()` згортає `canonicalState` (порожній) із чергою та видає стан із сутністю `temp_1`.
* Інтерфейс рендерить картку із заголовком «Підготувати звіт» за 0.5 мілісекунди.
* У мережу надсилається `POST /api/tasks` із заголовком `X-Client-Temp-ID: temp_1`.

### 2. Друга дія до отримання першої відповіді (Update)
Користувач одразу виправляє заголовок на «Підготувати фінансовий звіт».
* Диспетчер викликає `dispatch('UPDATE', 'temp_1', { title: 'Підготувати фінансовий звіт' })`.
* Мутація додається другою в `pendingQueue`.
* `getViewState()` обчислює результат послідовного застосування `CREATE` та `UPDATE`. Інтерфейс миттєво показує оновлений текст.
* Якщо перший запит ще в мережі, другий запит чекає або вирушає із посиланням на `temp_1`.

### 3. Підтвердження створення (ACK Create)
Сервер повертає `HTTP 201 Created` із тілом `{ tempId: "temp_1", serverId: "srv_9901" }`.
* Диспетчер записує мапінг `temp_1 ↦ srv_9901` в `idMap`.
* Перша мутація фіксується в `canonicalState` із справжнім ID `srv_9901` і видаляється з черги `pendingQueue`.
* Під час наступного виконання черги мутація `UPDATE` через метод `resolveId()` автоматично спрямовується на `srv_9901`.
* Стан `getViewState()` залишається візуально незмінним, оскільки канонічний стан уже містить сутність.

### 4. Фатальний збій редагування (422 Error)
Сервер відхиляє другий запит (`HTTP 422: Заголовок занадто довгий`).
* Диспетчер розпізнає код `422` як фатальну бізнес-помилку і видаляє мутацію `UPDATE` із `pendingQueue`.
* `getViewState()` миттєво перераховується як згортка `canonicalState` (де заголовок «Підготувати звіт») із порожньою чергою.
* Інтерфейс плавно повертає початковий заголовок «Підготувати звіт» і виводить повідомлення про помилку валідації. Створена сутність `srv_9901` залишається на місці й не зникає.

## Підводні камені та захисні бар'єри

1. **Каскадна трансляція ідентифікаторів перед виходом у сокет:** Якщо користувач створює папку `temp_fld_1`, а в ній документ `temp_doc_2`, тіло запиту документа містить `parentId: "temp_fld_1"`. Якщо перший запит підтверджено до відправлення другого, функція `executeMutation()` зобов'язана викликати `resolveId()` над усіма полями `payload` безпосередньо перед формуванням HTTP-пакета. Без цього бекенд отримає неіснуючий `temp-id` і поверне `400 Bad Request`.
2. **Скасування застарілих сокетів через `AbortController`:** Якщо користувач кілька разів редагує один і той самий рядок, кожен наступний виклик `dispatch('UPDATE')` перериває попередній незавершений мережевий запит через `abortController.abort()`. Це запобігає марній витраті трафіку та унеможливлює ситуацію, коли застарілий повільний запит прийде пізніше і спричинить небажаний відкат.
3. **Обмеження розміру черги та захист від шторму повторів (Retry Storm):** Під час тривалого перебування в офлайні черга `pendingQueue` може накопичити сотні дій. Коли зв'язок відновлюється, застосунок не повинен відкривати сотні паралельних сокетів одночасно. Запити відправляються пачками по 2–3 з'єднання з випадковим часовим джитером (*jitter*) та обов'язковим заголовком `Idempotency-Key`, щоб сервер не створив дублікати при повторних спробах.
4. **Витік пам'яті в карті ідентифікаторів:** З часом таблиця `idMap` може розростатися. Оскільки після очищення черги `pendingQueue` зв'язки між тимчасовими і канонічними ID більше не потрібні, таблицю періодично очищають за принципом LRU-кешу або видаляють записи, для яких у черзі більше немає залежних мутацій.
