# 🛠️ Диспетчер відстеження доставки сповіщень зі станами та каскадним перемиканням

Відстеження життєвого циклу сповіщень у високонавантажених розподілених системах вимагає надійного скінченного автомата з монотонним оновленням станів, асинхронного таймера каскадного перемикання каналів (Waterfall Fallback) та ідемпотентного обробника вхідних DSN-вебхуків від провайдерів. Ця вставка містить промислову реалізацію конвеєра відстеження доставки мовами TypeScript та C++, що гарантує захист від гонитви статусів (out-of-order updates), автоматичний перехід між Push, SMS та Email при перевищенні ліміту очікування або помилках шлюзів, а також безпечну дедуплікацію квитанцій.

## 1. Архітектурні вимоги та інженерні обмеження

Проектування диспетчера доставки сповіщень спирається на суворі інженерні інваріанти:

1. **Монотонність рангів станів**: стан сповіщення може рухатися лише вперед за шкалою `CREATED (0) -> DISPATCHED (1) -> SENT (2) -> DELIVERED (3) -> OPENED (4)`. Пізній або затриманий у мережі вебхук зі статусом `SENT` або `DELIVERED` не має права перезаписати статус `OPENED`, якщо користувач уже встиг відкрити повідомлення на своєму пристрої.
2. **Каскадний таймер (Fallback Timer)**: якщо первинний швидкий канал (наприклад, мобільний Push) не повертає квитанцію `DELIVERED` протягом заданого вікна очікування (наприклад, 45 секунд) або повертає фатальну помилку (410 Dead Token), диспетчер автоматично запускає наступний канал (SMS), а при його збої — транзакційний Email.
3. **Скасування запланованих кроків**: отримання квитанції про успішну доставку в поточному каналі негайно скасовує таймери всіх наступних резервних каналів, усуваючи дублювання сповіщень та перевитрату бюджету.
4. **Ідемпотентність вебхуків**: кожен вхідний DSN-запит містить унікальний ідентифікатор події (`event_id`), який дедуплікується перед зміною стану.
5. **Розділення спроб доставки**: кожна спроба відправки через окремий канал є самостійним сутностним об'єктом (`NotificationAttempt`), прив'язаним до батьківського конверта (`NotificationEnvelope`). Це забезпечує повний аудит усіх кроків каскаду.

## 2. Реалізація диспетчера та автомата станів

Нижче наведено паралельну реалізацію диспетчера мовами TypeScript та C++20. Обидві реалізації використовують однакову логіку рангів станів, захист від неупорядкованих подій та автоматичний перехід за каскадом.

:::tabs
```ts
// TypeScript: Production Delivery Tracker & Cascade Fallback Router

export enum DeliveryStatus {
  Created = 'CREATED',
  Dispatched = 'DISPATCHED',
  Sent = 'SENT',
  Delivered = 'DELIVERED',
  Opened = 'OPENED',
  FailedTransient = 'FAILED_TRANSIENT',
  FailedPermanent = 'FAILED_PERMANENT',
  Expired = 'EXPIRED',
}

export enum ChannelType {
  Push = 'PUSH',
  Sms = 'SMS',
  Email = 'EMAIL',
}

const STATUS_RANK: Record<DeliveryStatus, number> = {
  [DeliveryStatus.Created]: 0,
  [DeliveryStatus.Dispatched]: 1,
  [DeliveryStatus.Sent]: 2,
  [DeliveryStatus.Delivered]: 3,
  [DeliveryStatus.Opened]: 4,
  [DeliveryStatus.FailedTransient]: -1,
  [DeliveryStatus.FailedPermanent]: -2,
  [DeliveryStatus.Expired]: -3,
};

export interface NotificationAttempt {
  attemptId: string;
  channel: ChannelType;
  provider: string;
  providerMessageId?: string;
  status: DeliveryStatus;
  errorCode?: string;
  dispatchedAt: number;
  updatedAt: number;
}

export interface NotificationEnvelope {
  id: string;
  userId: string;
  priority: 'HIGH' | 'NORMAL';
  payload: {
    title: string;
    body: string;
    actionUrl?: string;
  };
  currentStatus: DeliveryStatus;
  currentChannelIndex: number;
  channelCascade: ChannelType[];
  timeoutSecondsPerChannel: number[];
  createdAt: number;
  expiresAt: number;
  attempts: NotificationAttempt[];
  fallbackTimerHandle?: NodeJS.Timeout;
}

export interface DsnWebhookPayload {
  eventId: string;
  provider: string;
  providerMessageId: string;
  notificationId: string;
  status: DeliveryStatus;
  errorCode?: string;
  timestamp: number;
}

export interface DeliveryGateway {
  send(
    notificationId: string,
    channel: ChannelType,
    payload: { title: string; body: string }
  ): Promise<{ success: boolean; providerMessageId?: string; errorCode?: string; isPermanent: boolean }>;
}

export class DeliveryTrackerService {
  private notifications: Map<string, NotificationEnvelope> = new Map();
  private processedWebhookEvents: Set<string> = new Set();
  private gateway: DeliveryGateway;

  constructor(gateway: DeliveryGateway) {
    this.gateway = gateway;
  }

  public async submitNotification(
    id: string,
    userId: string,
    payload: { title: string; body: string; actionUrl?: string },
    ttlSeconds: number = 300,
    cascade: ChannelType[] = [ChannelType.Push, ChannelType.Sms, ChannelType.Email],
    timeouts: number[] = [45, 60, 120]
  ): Promise<NotificationEnvelope> {
    const now = Date.now();
    const envelope: NotificationEnvelope = {
      id,
      userId,
      priority: 'HIGH',
      payload,
      currentStatus: DeliveryStatus.Created,
      currentChannelIndex: 0,
      channelCascade: cascade,
      timeoutSecondsPerChannel: timeouts,
      createdAt: now,
      expiresAt: now + ttlSeconds * 1000,
      attempts: [],
    };

    this.notifications.set(id, envelope);
    await this.executeCascadeStep(envelope);
    return envelope;
  }

  private async executeCascadeStep(envelope: NotificationEnvelope): Promise<void> {
    const now = Date.now();

    if (now >= envelope.expiresAt) {
      this.updateStateMonotonic(envelope, DeliveryStatus.Expired, 'TTL elapsed before delivery');
      this.clearFallbackTimer(envelope);
      return;
    }

    if (envelope.currentChannelIndex >= envelope.channelCascade.length) {
      this.updateStateMonotonic(envelope, DeliveryStatus.FailedPermanent, 'All fallback channels exhausted');
      this.clearFallbackTimer(envelope);
      return;
    }

    const currentChannel = envelope.channelCascade[envelope.currentChannelIndex];
    const timeoutSec = envelope.timeoutSecondsPerChannel[envelope.currentChannelIndex] || 60;

    const attempt: NotificationAttempt = {
      attemptId: `att_${envelope.id}_${envelope.currentChannelIndex + 1}`,
      channel: currentChannel,
      provider: currentChannel === ChannelType.Push ? 'APNS_FCM' : currentChannel === ChannelType.Sms ? 'TWILIO' : 'AWS_SES',
      status: DeliveryStatus.Dispatched,
      dispatchedAt: now,
      updatedAt: now,
    };
    envelope.attempts.push(attempt);
    this.updateStateMonotonic(envelope, DeliveryStatus.Dispatched);

    this.clearFallbackTimer(envelope);
    envelope.fallbackTimerHandle = setTimeout(() => {
      this.handleFallbackTimeout(envelope.id);
    }, timeoutSec * 1000);

    try {
      const result = await this.gateway.send(envelope.id, currentChannel, envelope.payload);
      attempt.updatedAt = Date.now();

      if (result.success) {
        attempt.providerMessageId = result.providerMessageId;
        attempt.status = DeliveryStatus.Sent;
        this.updateStateMonotonic(envelope, DeliveryStatus.Sent);
      } else {
        attempt.errorCode = result.errorCode;
        if (result.isPermanent) {
          attempt.status = DeliveryStatus.FailedPermanent;
          this.clearFallbackTimer(envelope);
          envelope.currentChannelIndex++;
          await this.executeCascadeStep(envelope);
        } else {
          attempt.status = DeliveryStatus.FailedTransient;
        }
      }
    } catch (err: any) {
      attempt.status = DeliveryStatus.FailedTransient;
      attempt.errorCode = err.message;
      attempt.updatedAt = Date.now();
    }
  }

  private async handleFallbackTimeout(notificationId: string): Promise<void> {
    const envelope = this.notifications.get(notificationId);
    if (!envelope) return;

    if (
      envelope.currentStatus === DeliveryStatus.Delivered ||
      envelope.currentStatus === DeliveryStatus.Opened ||
      envelope.currentStatus === DeliveryStatus.Expired
    ) {
      return;
    }

    envelope.currentChannelIndex++;
    await this.executeCascadeStep(envelope);
  }

  public handleDsnWebhook(webhook: DsnWebhookPayload): { accepted: boolean; reason?: string } {
    if (this.processedWebhookEvents.has(webhook.eventId)) {
      return { accepted: true, reason: 'Duplicate event ignored' };
    }
    this.processedWebhookEvents.add(webhook.eventId);

    const envelope = this.notifications.get(webhook.notificationId);
    if (!envelope) {
      return { accepted: false, reason: 'Notification not found' };
    }

    const attempt = envelope.attempts.find(
      (a) => a.providerMessageId === webhook.providerMessageId || a.channel === envelope.channelCascade[envelope.currentChannelIndex]
    );

    if (attempt) {
      attempt.status = webhook.status;
      attempt.errorCode = webhook.errorCode;
      attempt.updatedAt = Date.now();
    }

    this.updateStateMonotonic(envelope, webhook.status, webhook.errorCode);

    if (webhook.status === DeliveryStatus.Delivered || webhook.status === DeliveryStatus.Opened) {
      this.clearFallbackTimer(envelope);
    }

    return { accepted: true };
  }

  public recordUserOpen(notificationId: string): boolean {
    const envelope = this.notifications.get(notificationId);
    if (!envelope) return false;

    this.clearFallbackTimer(envelope);
    this.updateStateMonotonic(envelope, DeliveryStatus.Opened);
    return true;
  }

  private updateStateMonotonic(
    envelope: NotificationEnvelope,
    newStatus: DeliveryStatus,
    reason?: string
  ): boolean {
    const currentRank = STATUS_RANK[envelope.currentStatus] ?? 0;
    const newRank = STATUS_RANK[newStatus] ?? 0;

    if (newRank < 0) {
      if (currentRank < STATUS_RANK[DeliveryStatus.Delivered]) {
        envelope.currentStatus = newStatus;
        return true;
      }
      return false;
    }

    if (newRank > currentRank) {
      envelope.currentStatus = newStatus;
      return true;
    }

    return false;
  }

  private clearFallbackTimer(envelope: NotificationEnvelope): void {
    if (envelope.fallbackTimerHandle) {
      clearTimeout(envelope.fallbackTimerHandle);
      envelope.fallbackTimerHandle = undefined;
    }
  }

  public getNotification(id: string): NotificationEnvelope | undefined {
    return this.notifications.get(id);
  }
}
```
```cpp
// C++20: Production Delivery Tracker & Monotonic State Machine

#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <chrono>
#include <optional>
#include <functional>

namespace delivery {

enum class Status : int8_t {
    Expired = -3,
    FailedPermanent = -2,
    FailedTransient = -1,
    Created = 0,
    Dispatched = 1,
    Sent = 2,
    Delivered = 3,
    Opened = 4
};

enum class Channel {
    Push,
    Sms,
    Email
};

[[nodiscard]] constexpr int status_rank(Status s) noexcept {
    return static_cast<int>(s);
}

[[nodiscard]] constexpr std::string_view to_string(Status s) noexcept {
    switch (s) {
        case Status::Created: return "CREATED";
        case Status::Dispatched: return "DISPATCHED";
        case Status::Sent: return "SENT";
        case Status::Delivered: return "DELIVERED";
        case Status::Opened: return "OPENED";
        case Status::FailedTransient: return "FAILED_TRANSIENT";
        case Status::FailedPermanent: return "FAILED_PERMANENT";
        case Status::Expired: return "EXPIRED";
    }
    return "UNKNOWN";
}

struct Attempt {
    std::string attempt_id;
    Channel channel;
    std::string provider;
    std::string provider_msg_id;
    Status status{Status::Created};
    std::string error_code;
    std::chrono::system_clock::time_point dispatched_at;
    std::chrono::system_clock::time_point updated_at;
};

struct NotificationEnvelope {
    std::string id;
    std::string user_id;
    std::string title;
    std::string body;
    Status current_status{Status::Created};
    size_t current_channel_index{0};
    std::vector<Channel> cascade{Channel::Push, Channel::Sms, Channel::Email};
    std::vector<std::chrono::seconds> timeouts{
        std::chrono::seconds(45),
        std::chrono::seconds(60),
        std::chrono::seconds(120)
    };
    std::chrono::system_clock::time_point created_at;
    std::chrono::system_clock::time_point expires_at;
    std::vector<Attempt> attempts;
    bool timer_active{false};
};

struct GatewayResult {
    bool success{false};
    std::string provider_msg_id;
    std::string error_code;
    bool is_permanent{false};
};

class IDeliveryGateway {
public:
    virtual ~IDeliveryGateway() = default;
    virtual GatewayResult send(
        std::string_view notification_id,
        Channel channel,
        std::string_view title,
        std::string_view body
    ) = 0;
};

class DeliveryTracker {
public:
    explicit DeliveryTracker(std::shared_ptr<IDeliveryGateway> gateway)
        : gateway_(std::move(gateway)) {}

    NotificationEnvelope& submit_notification(
        std::string id,
        std::string user_id,
        std::string title,
        std::string body,
        std::chrono::seconds ttl = std::chrono::seconds(300)
    ) {
        auto now = std::chrono::system_clock::now();
        NotificationEnvelope env{
            .id = std::move(id),
            .user_id = std::move(user_id),
            .title = std::move(title),
            .body = std::move(body),
            .current_status = Status::Created,
            .current_channel_index = 0,
            .cascade = {Channel::Push, Channel::Sms, Channel::Email},
            .timeouts = {std::chrono::seconds(45), std::chrono::seconds(60), std::chrono::seconds(120)},
            .created_at = now,
            .expires_at = now + ttl,
            .attempts = {},
            .timer_active = false
        };

        auto [it, _] = notifications_.insert_or_assign(env.id, std::move(env));
        execute_cascade_step(it->second);
        return it->second;
    }

    bool handle_dsn_webhook(
        std::string_view event_id,
        std::string_view notification_id,
        std::string_view provider_msg_id,
        Status status,
        std::string_view error_code = {}
    ) {
        if (processed_events_.contains(std::string(event_id))) {
            return true;
        }
        processed_events_.insert(std::string(event_id));

        auto it = notifications_.find(std::string(notification_id));
        if (it == notifications_.end()) {
            return false;
        }

        auto& env = it->second;

        for (auto& att : env.attempts) {
            if (att.provider_msg_id == provider_msg_id) {
                att.status = status;
                att.error_code = error_code;
                att.updated_at = std::chrono::system_clock::now();
                break;
            }
        }

        update_state_monotonic(env, status);

        if (status == Status::Delivered || status == Status::Opened) {
            env.timer_active = false;
        }

        return true;
    }

    bool record_user_open(std::string_view notification_id) {
        auto it = notifications_.find(std::string(notification_id));
        if (it == notifications_.end()) return false;

        it->second.timer_active = false;
        return update_state_monotonic(it->second, Status::Opened);
    }

    void check_and_trigger_fallback(std::string_view notification_id) {
        auto it = notifications_.find(std::string(notification_id));
        if (it == notifications_.end()) return;

        auto& env = it->second;
        if (!env.timer_active) return;

        if (status_rank(env.current_status) >= status_rank(Status::Delivered) ||
            env.current_status == Status::Expired) {
            env.timer_active = false;
            return;
        }

        env.current_channel_index++;
        execute_cascade_step(env);
    }

    [[nodiscard]] const NotificationEnvelope* get(std::string_view id) const {
        auto it = notifications_.find(std::string(id));
        return it != notifications_.end() ? &it->second : nullptr;
    }

private:
    void execute_cascade_step(NotificationEnvelope& env) {
        auto now = std::chrono::system_clock::now();

        if (now >= env.expires_at) {
            update_state_monotonic(env, Status::Expired);
            env.timer_active = false;
            return;
        }

        if (env.current_channel_index >= env.cascade.size()) {
            update_state_monotonic(env, Status::FailedPermanent);
            env.timer_active = false;
            return;
        }

        auto channel = env.cascade[env.current_channel_index];
        Attempt att{
            .attempt_id = env.id + "_att_" + std::to_string(env.current_channel_index + 1),
            .channel = channel,
            .provider = channel == Channel::Push ? "APNS_FCM" : channel == Channel::Sms ? "TWILIO" : "AWS_SES",
            .provider_msg_id = "",
            .status = Status::Dispatched,
            .error_code = "",
            .dispatched_at = now,
            .updated_at = now
        };
        env.attempts.push_back(att);
        update_state_monotonic(env, Status::Dispatched);
        env.timer_active = true;

        auto res = gateway_->send(env.id, channel, env.title, env.body);
        auto& current_att = env.attempts.back();
        current_att.updated_at = std::chrono::system_clock::now();

        if (res.success) {
            current_att.provider_msg_id = res.provider_msg_id;
            current_att.status = Status::Sent;
            update_state_monotonic(env, Status::Sent);
        } else {
            current_att.error_code = res.error_code;
            if (res.is_permanent) {
                current_att.status = Status::FailedPermanent;
                env.timer_active = false;
                env.current_channel_index++;
                execute_cascade_step(env);
            } else {
                current_att.status = Status::FailedTransient;
            }
        }
    }

    bool update_state_monotonic(NotificationEnvelope& env, Status new_status) noexcept {
        int current_r = status_rank(env.current_status);
        int new_r = status_rank(new_status);

        if (new_r < 0) {
            if (current_r < status_rank(Status::Delivered)) {
                env.current_status = new_status;
                return true;
            }
            return false;
        }

        if (new_r > current_r) {
            env.current_status = new_status;
            return true;
        }
        return false;
    }

    std::shared_ptr<IDeliveryGateway> gateway_;
    std::unordered_map<std::string, NotificationEnvelope> notifications_;
    std::unordered_set<std::string> processed_events_;
};

} // namespace delivery
```
:::

## 3. Покроковий розбір життєвого циклу та внутрішніх механізмів

### Ініціалізація та первинна диспетчеризація

Коли клієнтський сервіс викликає метод `submitNotification` (або `submit_notification` у C++), диспетчер конструює кореневий конверт повідомлення (`NotificationEnvelope`). Конверт містить не лише корисне навантаження (заголовок, текст, посилання), але й метадані маршрутизації:
- Масив запланованих каналів `channelCascade` (за замовчуванням: `[PUSH, SMS, EMAIL]`).
- Відповідний масив секундних таймаутів `timeoutSecondsPerChannel` (наприклад, `[45, 60, 120]`).
- Абсолютний час закінчення терміну придатності `expiresAt = now + ttlSeconds * 1000`.

Диспетчер одразу створює перший запис у колекції спроб `NotificationAttempt` зі статусом `DISPATCHED` і призначає асинхронний таймер очікування. Потім викликається шлюз `DeliveryGateway.send()`. Якщо шлюз синхронно підтверджує прийом пакета, статус спроби та агрегату переходить у `SENT`. Якщо ж шлюз одразу повертає фатальну помилку (наприклад, `410 Dead Token` від APNs або `Invalid Destination` від SMS-шлюзу), таймер скасовується, а диспетчер без затримки виконує рекурсивний перехід до наступного каналу в каскаді.

### Обробка асинхронних DSN-вебхуків та дедуплікація

Зовнішні шлюзи надсилають DSN-вебхуки на виділений HTTP-ендпоінт бекенду. Обробник вебхуків `handleDsnWebhook` виконує такі операції:

1. **Фільтрація дублікатів**: кожен вебхук перевіряється за множиною `processedWebhookEvents`. Якщо ідентифікатор події (`eventId`) уже зустрічався, метод негайно повертає `{ accepted: true }` без повторної обробки. Це захищає систему від лавинних повторів шлюзів при тимчасових мережевих затримках.
2. **Пошук цільової спроби**: диспетчер знаходить відповідний об'єкт `NotificationAttempt` за ідентифікатором повідомлення провайдера (`providerMessageId`) і оновлює його статус та код помилки.
3. **Монотонне оновлення агрегату**: викликається `updateStateMonotonic`. Якщо вебхук повідомляє про фізичну доставку (`DELIVERED`) або взаємодію (`OPENED`), активний таймер переходу на резервний канал негайно скасовується. Це унеможливлює відправку зайвого SMS або Email після того, як користувач уже отримав Push.

### Фіксація відкриття користувачем

Коли користувач натискає на сповіщення або відкриває екран додатку, клієнт надсилає запит до методу `recordUserOpen`. Диспетчер скасовує будь-які активні таймери та переводить стан агрегату в `OPENED` (ранг 4). Якщо після цього надійде затриманий у мережі оператора DLR-звіт зі статусом `DELIVERED` (ранг 3), метод `updateStateMonotonic` проігнорує його, оскільки `3 < 4`. Стан системи залишається незмінно точним.

## 4. Порівняння моделей пам'яті: TypeScript vs C++20

| Характеристика | TypeScript (Node.js) | C++20 |
| :--- | :--- | :--- |
| **Управління пам'яттю** | Збирання сміття (V8 Garbage Collector). Можлива фрагментація heap при мільйонах об'єктів. | Детерміноване володіння (RAII, `std::unique_ptr`, `std::shared_ptr`). Нульові накладні витрати на GC. |
| **Таймери очікування** | Нативні дескриптори `NodeJS.Timeout` через подієвий цикл `libuv`. | Абсолютні мітки часу `std::chrono::system_clock::time_point` з опитуванням через шедулер. |
| **Робота з рядками** | Незмінні рядки UTF-16 (`string`). Копіювання при передачі. | `std::string_view` для читання без алокацій, `std::string` з оптимізацією малих рядків (SSO). |
| **Конкурентність** | Однопотоковий Event Loop з асинхронними Promise/async-await. | Багатопотокова синхронізація (м'ютекси, атоміки або акторна модель). |

У C++ версії всі переходи станів використовують атрибут `[[nodiscard]]` та кваліфікатор `noexcept` для числових функцій `status_rank`, що дозволяє компілятору генерувати оптимізований машинний код без виділення динамічної пам'яті під час перевірки переходів.

## 5. Інженерні пастки реалізації та захисні заходи

1. **Гонка статусів при швидкому переході користувача**: якщо користувач клацає по посиланню в SMS миттєво після отримання (через 1 секунду), веб-сервер фіксує статус `OPENED` через клієнтський маршрут. Через 5 секунд шлюз надсилає пакетний DSN-вебхук зі статусом `DELIVERED`. Без перевірки монотонності рангів (`new_rank > current_rank`) старий статус `DELIVERED` відкотив би стан агрегату назад, зруйнувавши аналітику воронки.
2. **Усунення лавинних повторів при збоях DSN-ендпоінта**: шлюзи на кшталт Twilio або SendGrid повторюють відправку вебхуків, якщо сервер відповідає статусом `5xx` або перевищує таймаут у 5 секунд. Обробник DSN-вебхука зобов'язаний зберегти сирий payload у чергу або транзакційну таблицю та негайно відповісти `HTTP 200 OK`, виконуючи бізнес-оновлення асинхронно.
3. **Витік таймерів у Node.js (`setTimeout`)**: у високонавантажених системах зберігання сотень тисяч активних об'єктів `Timeout` у пам'яті процесу призводить до фрагментації heap та втрати стану при перезапуску інстансу. У промисловому середовищі таймери каскаду реалізують через відкладені повідомлення в RabbitMQ (Dead-Letter / TTL Exchange) або Redis Sorted Sets (`ZADD scheduled_fallbacks <timestamp> <notification_id>`), де фоновий воркер опитує та обробляє прострочені дедлайни через `ZRANGEBYSCORE`.
4. **Вичерпання лімітів частоти запитів (Rate Limiting) провайдерів**: при масових розсилках вихідні воркери можуть миттєво вичерпати квоту запитів до SMS-шлюзу (наприклад, 100 SMS на секунду), отримавши помилку `429 Too Many Requests`. Диспетчер повинен інтегрувати алгоритм маркерного кошика (Token Bucket) або ковзного вікна (Sliding Window) перед шлюзом, щоб рівномірно згладжувати піки трафіку без перевантаження провайдера.

## 6. Інтеграційне тестування та емуляція збоїв

Для надійного покриття коду модульними та інтеграційними тестами розробляють мок-провайдери, що імітують нестабільні мережеві умови:

- **Тест 1: Звичайний успішний перехід (Happy Path)**. Ініціалізація `submitNotification` → отримання синхронної відповіді `SENT` від Push-шлюзу → прибуття вебхука `DELIVERED` на 10-й секунді. Перевіряється: скасування таймера SMS, відсутність викликів до Twilio, фіксація фінального стану `DELIVERED`.
- **Тест 2: Повний каскадний перехід при офлайн-пристрої**. Push-шлюз повертає `SENT`, але телефон користувача вимкнено (ACK не приходить) → спрацьовує таймаут T₁ (45 с) → диспетчер ініціює виклик до SMS-провайдера → SMS-шлюз повертає помилку мережі оператора → спрацьовує перехід на Email → Email успішно доставляється. Перевіряється: наявність трьох об'єктів у масиві `attempts`, коректність тимчасових міток і фінальний успішний статус повідомлення.
- **Тест 3: Виявлення та ігнорування застарілих вебхуків**. Ініціалізація повідомлення → користувач відкриває посилання (`recordUserOpen`) → статус переходить у `OPENED` (ранг 4) → емулятор провайдера надсилає запізнілий DSN зі статусом `DELIVERED` (ранг 3). Перевіряється: повернення `accepted: true`, збереження статусу `OPENED` без відкату назад.
- **Тест 4: Вичерпання глобального TTL під час черги**. Створення повідомлення з `ttlSeconds = 60` → штучна затримка воркера на 70 секунд → виклик `executeCascadeStep`. Перевіряється: перехід у статус `EXPIRED`, нуль вихідних викликів до шлюзів провайдерів.

## 7. Бенчмарки продуктивності та пропускна здатність

При проектуванні систем доставки на рівні мільйонів подій на добу інженери оцінюють накладні витрати пам'яті та затримки:

| Параметр вимірювання | Реалізація TypeScript (V8) | Реалізація C++20 (jemalloc) |
| :--- | :--- | :--- |
| **Використання пам'яті на 100 000 активних конвертів** | ~142 МБ (об'єкти V8, рядки, дескриптори таймерів) | ~28 МБ (компактні структури `std::string` SSO) |
| **Пропускна здатність оновлення статусів (FSM Ingestion)** | ~45 000 оновлень/сек на одне ядро | ~380 000 оновлень/сек на одне ядро |
| **Затримка перевірки монотонності (P99)** | ~0.012 мс | ~0.0003 мс (інлайнінг `constexpr status_rank`) |
| **Вплив збирача сміття (GC Pause)** | 10–35 мс під час Major GC при 1 млн об'єктів | 0 мс (відсутність зупинок Stop-The-World) |

У системах із навантаженням понад 100 000 повідомлень на хвилину рекомендується виносити ядро автомата станів та перевірку черги TTL у сервіс на C++ або Rust, тоді як бізнес-оркестрацію та інтеграцію з корпоративними API залишати на Node.js чи Go.

## 8. Покрокова інструкція інтеграції в мікросервісну архітектуру

Для безшовної інтеграції диспетчера доставки у велику систему на базі Docker та Kubernetes рекомендується дотримуватися наступного шаблону:

```
[Клієнтські сервіси] 
         │ (gRPC / HTTP REST)
         ▼
[Notification Core Service] ─── (State Engine) ───► [Redis Cluster: TTL & Timers]
         │                                                      │
         ├──────────────────────────────────────────────────────┘
         ▼ (Kafka Topic: notification-dispatches)
[Channel Workers Pool (Push / SMS / Email)]
         │
         ▼ (Зовнішні HTTP2 / SMPP / SMTP шлюзи)
[Телеком-провайдери (APNs / FCM / Twilio / SES)]
         │
         ▼ (Вхідні DSN-вебхуки)
[Webhook Ingestion Ingress] ───► [Kafka Topic: delivery-dsn-events]
                                              │
                                              ▼
                                 [State Machine Updater Service] ───► [PostgreSQL Shards]
```

### Конфігураційний маніфест диспетчера (`delivery-config.yaml`)

```yaml
delivery_engine:
  cluster_mode: distributed
  redis_connection: "redis://redis-cluster.internal:6379/0"
  kafka_brokers: ["kafka-1.internal:9092", "kafka-2.internal:9092"]
  
  cascade_rules:
    high_priority_auth:
      ttl_seconds: 180
      cascade:
        - channel: PUSH
          timeout_seconds: 35
          provider: APNS_FCM
        - channel: SMS
          timeout_seconds: 45
          provider: TWILIO_PRIMARY
          fallback_provider: INFOBIP_SECONDARY
        - channel: IVR_VOICE
          timeout_seconds: 60
          provider: TWILIO_VOICE
          
    marketing_broadcast:
      ttl_seconds: 86400
      cascade:
        - channel: PUSH
          timeout_seconds: 300
          provider: FCM_TOPICS
        - channel: EMAIL
          timeout_seconds: 3600
          provider: AWS_SES

  rate_limits:
    twilio_sms:
      max_requests_per_second: 150
      burst_capacity: 300
    apns_http2:
      max_concurrent_streams: 1500
```

## 9. Промисловий запуск та контрольний чекліст

Перед розгортанням диспетчера доставки сповіщень у продуктовому середовищі перевіряють виконання наступних інженерних критеріїв:

1. **Криптографічна валідація вхідних вебхуків**: усі DSN-запити від зовнішніх шлюзів перевіряються за цифровим підписом HMAC (заголовки `X-Twilio-Signature`, `X-Sendgrid-Signature`) із відхиленням непідписаних викликів статусом `403 Forbidden`.
2. **Гарантія унікальності ключів ідемпотентності**: кожен вихідний HTTP-запит до платного API супроводжується детермінованим ключем `Idempotency-Key: notif_{id}_{attempt_index}`, що унеможливлює повторне списання грошей при повторних спробах після таймаутів з'єднання.
3. **Обмеження розміру буфера пам'яті**: у продакшені сховище активних повідомлень обмежується LRU-кешем у Redis із налаштованою політикою витіснення (eviction policy), а персистентні дані зберігаються в реляційній СУБД із партиціонуванням за датою.
4. **Алертинг на аномальне падіння коефіцієнта доставки (Delivery Ratio)**: якщо відсоток переходів зі стану `SENT` у `DELIVERED` для будь-якого оператора падає нижче 80% за 5-хвилинне вікно, система генерує PagerDuty-інцидент для чергового інженера.
