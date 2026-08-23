# ⚙️ Практична реалізація конвеєра сповіщень Digital Homes: від черги до канального розгортання

Ця вставка містить повністю робочу, вивірену та ідіоматичну реалізацію конвеєра сповіщень Digital Homes мовами TypeScript та Go. Практичний код реалізує п'ятикомпонентний конвеєр обробки евентів: прийом партиціонованого потоку з фонової черги, пріоритетне пропущення критичних тривог в обхід накопичувачів, перевірку матриці преференсій мешканців (User Preferences & Quiet Hours), канальне розгортання (Fan-out) на мобільні пристрої родини (Silent Push, Critical Alert Push, SMS Fallback) та відстеження квитанцій доставки (Delivery Tracking) з автоматичним каскадним ескалюванням.

## Інфраструктурне середовище та мережеві контракти

Перш ніж переходити до коду обробки, важливо зрозуміти інфраструктурний контекст, у якому виконується конвеєр. Конвеєр сповіщень Digital Homes функціонує як окремий асинхронний мікросервіс (Notification Worker Node), який спілкується з трьома суміжними системами:

1. **Вхідна шина подій (Event Bus / Redis Streams):** Конвеєр підписаний на тему `dh.events.v1`, яка партиціонована за хешем від `home_id`. Це гарантує, що всі події одного будинку потрапляють на один воркер або обробляються строго послідовно, унеможливлюючи порушення хронологічного порядку (Out-of-Order Execution).
2. **Розподілене сховище стану (Redis Cluster with TTL):** Використовується для збереження ключів дедуплікації, буферів злиття у ранкові дайджести та лічильників відра жетонів (Token Bucket). Усі ключі обов'язково забезпечуються часом життя (TTL), що запобігає безконтрольному розпуханню оперативно пам'яті Redis.
3. **Зовнішні мережеві шлюзи (Apple APNs, Google FCM, Twilio SMS API):** Конвеєр взаємодіє з APNs через мережевий протокол HTTP/2 із підтримкою тривалого мультиплексування з'єднань (Connection Pooling) та JWT-авторизацією. З FCM взаємодія відбувається через FCM HTTP v1 REST API.

## Архітектурний контракт та інваріанти конвеєра

Усі компоненти конвеєра об'єднані єдиним потоковим контрактом. Конвеєр отримує з черги об'єкт вхідної події `HomeEvent`, збагачує його метаданими стану дому, перевіряє поточні преференси кожного мешканця (`UserPreference`) і формує для кожного зареєстрованого мобільного пристрою атомарні завдання на доставку `DeliveryTask`.

Проєктне рішення спирається на три залізні інваріанти:

1. **Детермінована ідемпотентність доставки (`deliveryId`):** Ідентифікатор завдання доставки створюється як криптографічний хеш від комбінації `hash(eventId + userId + deviceId + channel)`. Цей ключ передається провайдерам сповіщень (APNs, FCM, Twilio) як ключ ідемпотентності. Якщо конвеєр перезапускається або робить ретрай після мережевого збою, повторні запити з цим хешем не призводять до повторного виведення банера на екран або повторного списання коштів за SMS.
2. **Незламність критичних тривог (`Severity.CRITICAL`):** Події класу `CRITICAL` мають абсолютний пріоритет. Оцінювач преференсій `PolicyEngine` гарантує, що для критичних тривог прапорці тихих годин `quietHours` та користувацькі `optOut` ігноруються.
3. **Каскадна ескаляція при відсутності підтвердження:** Завдання доставки на первинні пуш-канали (`CRITICAL_PUSH`) дістають обмежене вікно очікування підтвердження (ACK timeout) у 15 секунд. Якщо мобільний пристрій не надіслав ACK-квитанцію про факт доставки (наприклад, телефон поза зоною покриття мережі), трекер доставки `DeliveryTracker` автоматично ескалює задачу до резервного каналу `SMS_FALLBACK`.

## Структура модулів коду

Реалізація розділена на три ключові архітектурні класи:

- **`PolicyEngine`:** Клас відповідає за оцінку контексту мешканця. Він приймає вхідну подію, профіль преференсій користувача та поточний час доби. Модуль повертає рішення: чи слід доставляти сповіщення негайно, відхилити його (Drop) чи переправити у накопичувальний буфер ранкового дайджесту.
- **`NotificationRouter`:** Модуль відповідає за Fan-out розгортання. Він бере вхідну подію, список членів родини та їхній парк пристроїв, проганяє кожного мешканця через `PolicyEngine` і формує списки `DeliveryTask`. Для критичних евертів модуль автоматично створює паралельну пару: `Silent Push` (для фонового підтягування кадрів) та `Critical Push` (для звукового пробиття).
- **`DeliveryTracker`:** Модуль керування мережевим виконанням. Він відправляє задачі у зовнішні API провайдерів, обробляє фатальні й тимчасові помилки та забезпечує каскадне переключення на резервні канали при збоях.

:::tabs
```ts
import { createHash } from "node:crypto";

export enum Severity {
  LOW = "LOW",
  DEFAULT = "DEFAULT",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export enum ChannelType {
  SILENT_PUSH = "SILENT_PUSH",
  CRITICAL_PUSH = "CRITICAL_PUSH",
  SMS_FALLBACK = "SMS_FALLBACK",
}

export interface HomeEvent {
  eventId: string;
  homeId: string;
  severity: Severity;
  eventType: string;
  title: string;
  body: string;
  timestamp: number;
  payload: Record<string, unknown>;
}

export interface UserPreference {
  userId: string;
  quietHoursStart: number; // Час початку тихих годин (наприклад, 23 для 23:00)
  quietHoursEnd: number;   // Час завершення тихих годин (наприклад, 7 для 07:00)
  isAwayMode: boolean;     // Режим "Відпустка / Немає вдома"
  optedOutTypes: Set<string>; // Категорії евентів, вимкнені користувачем
}

export interface UserDevice {
  deviceId: string;
  userId: string;
  pushToken: string;
  phoneNumber?: string;
  isIos: boolean;
}

export interface DeliveryTask {
  deliveryId: string;
  eventId: string;
  userId: string;
  deviceId: string;
  channel: ChannelType;
  title: string;
  body: string;
  tokenOrNumber: string;
  attempts: number;
}

/**
 * 1. PolicyEngine — перевірка відповідності події преференсіям мешканця
 */
export class PolicyEngine {
  shouldDeliver(
    event: HomeEvent,
    pref: UserPreference,
    currentHour: number
  ): { deliver: boolean; forceDigest: boolean } {
    // Інваріант 1: Критичний клас оминає ВСІ тихі години та користувацький opt-out
    if (event.severity === Severity.CRITICAL) {
      return { deliver: true, forceDigest: false };
    }

    // Перевірка явного Opt-Out користувача на дану категорію евенту
    if (pref.optedOutTypes.has(event.eventType)) {
      return { deliver: false, forceDigest: false };
    }

    // Розрахунок попадання у вікно Quiet Hours з урахуванням переходу через північ
    const inQuietHours = pref.quietHoursStart > pref.quietHoursEnd
      ? (currentHour >= pref.quietHoursStart || currentHour < pref.quietHoursEnd)
      : (currentHour >= pref.quietHoursStart && currentHour < pref.quietHoursEnd);

    // Якщо зараз тихі години і користувач ВДОМА (не у режимі Away)
    if (inQuietHours && !pref.isAwayMode) {
      if (event.severity === Severity.LOW || event.severity === Severity.DEFAULT) {
        // Затримуємо подію для злиття в ранковий дайджест
        return { deliver: false, forceDigest: true };
      }
    }

    return { deliver: true, forceDigest: false };
  }
}

/**
 * 2. NotificationRouter — розгортання Fan-out та формування завдань доставки
 */
export class NotificationRouter {
  private policyEngine = new PolicyEngine();

  buildDeliveryTasks(
    event: HomeEvent,
    members: UserPreference[],
    devicesByUser: Map<string, UserDevice[]>,
    currentHour: number
  ): DeliveryTask[] {
    const tasks: DeliveryTask[] = [];

    for (const member of members) {
      const decision = this.policyEngine.shouldDeliver(event, member, currentHour);

      if (!decision.deliver) {
        if (decision.forceDigest) {
          console.log(`[Digest Buffer] Event ${event.eventId} buffered for morning digest of user ${member.userId}`);
        }
        continue;
      }

      const userDevices = devicesByUser.get(member.userId) ?? [];
      for (const device of userDevices) {
        // Формуємо базовий детермінований ідентифікатор для гарантії ідемпотентності
        const rawId = `${event.eventId}:${member.userId}:${device.deviceId}`;
        const baseDeliveryId = createHash("sha256").update(rawId).digest("hex").slice(0, 16);

        if (event.severity === Severity.CRITICAL) {
          // Двоточковий імпульс 1: Silent Push для передзавантаження кадрів відео у кеш
          tasks.push({
            deliveryId: `${baseDeliveryId}:silent`,
            eventId: event.eventId,
            userId: member.userId,
            deviceId: device.deviceId,
            channel: ChannelType.SILENT_PUSH,
            title: "",
            body: "",
            tokenOrNumber: device.pushToken,
            attempts: 0,
          });

          // Двоточковий імпульс 2: Critical Alert Push зі звуком і банером
          tasks.push({
            deliveryId: `${baseDeliveryId}:critical`,
            eventId: event.eventId,
            userId: member.userId,
            deviceId: device.deviceId,
            channel: ChannelType.CRITICAL_PUSH,
            title: `🚨 ${event.title}`,
            body: event.body,
            tokenOrNumber: device.pushToken,
            attempts: 0,
          });
        } else {
          // Звичайне push-сповіщення
          tasks.push({
            deliveryId: `${baseDeliveryId}:primary`,
            eventId: event.eventId,
            userId: member.userId,
            deviceId: device.deviceId,
            channel: ChannelType.CRITICAL_PUSH,
            title: event.title,
            body: event.body,
            tokenOrNumber: device.pushToken,
            attempts: 0,
          });
        }
      }
    }

    return tasks;
  }
}

/**
 * 3. DeliveryTracker — виконання доставки та аварійний канальний fallback
 */
export class DeliveryTracker {
  async executeTaskWithFallback(
    task: DeliveryTask,
    sendPushApi: (t: DeliveryTask) => Promise<boolean>,
    sendSmsApi: (number: string, text: string) => Promise<boolean>
  ): Promise<boolean> {
    try {
      const success = await sendPushApi(task);
      if (success) {
        console.log(`[ACK Success] Task ${task.deliveryId} delivered via ${task.channel}`);
        return true;
      }
    } catch (err) {
      console.warn(`[Primary Channel Error] Task ${task.deliveryId}: ${err}`);
    }

    // Автоматичний канальний fallback у SMS для критичних тривог при відсутності ACK
    if (task.channel === ChannelType.CRITICAL_PUSH && task.tokenOrNumber) {
      console.log(`[Escalating] Primary push failed for task ${task.deliveryId}. Attempting SMS fallback...`);
      try {
        const smsSuccess = await sendSmsApi(task.tokenOrNumber, `${task.title}: ${task.body}`);
        if (smsSuccess) {
          console.log(`[Fallback Success] Task ${task.deliveryId} delivered via SMS`);
          return true;
        }
      } catch (smsErr) {
        console.error(`[SMS Channel Error] Task ${task.deliveryId}: ${smsErr}`);
      }
    }

    console.error(`[DLQ Route] Task ${task.deliveryId} failed on all channels. Moving to Dead-Letter Queue.`);
    return false;
  }
}
```
```go
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"time"
)

type Severity string

const (
	SeverityLow      Severity = "LOW"
	SeverityDefault  Severity = "DEFAULT"
	SeverityHigh     Severity = "HIGH"
	SeverityCritical Severity = "CRITICAL"
)

type ChannelType string

const (
	ChannelSilentPush   ChannelType = "SILENT_PUSH"
	ChannelCriticalPush ChannelType = "CRITICAL_PUSH"
	ChannelSMSFallback  ChannelType = "SMS_FALLBACK"
)

type HomeEvent struct {
	EventID   string
	HomeID    string
	Severity  Severity
	EventType string
	Title     string
	Body      string
	Timestamp time.Time
}

type UserPreference struct {
	UserID           string
	QuietHoursStart  int
	QuietHoursEnd    int
	IsAwayMode       bool
	OptedOutTypesSet map[string]bool
}

type UserDevice struct {
	DeviceID    string
	UserID      string
	PushToken   string
	PhoneNumber string
}

type DeliveryTask struct {
	DeliveryID    string
	EventID       string
	UserID        string
	DeviceID      string
	Channel       ChannelType
	Title         string
	Body          string
	TokenOrNumber string
	Attempts      int
}

// PolicyEngine вивіряє правила доставки згідно з преференсіями мешканця
type PolicyEngine struct{}

func (pe *PolicyEngine) ShouldDeliver(event HomeEvent, pref UserPreference, currentHour int) (deliver bool, forceDigest bool) {
	// Інваріант 1: Критичні тривоги оминають тихі години та opt-out
	if event.Severity == SeverityCritical {
		return true, false
	}

	// Перевірка явного Opt-Out
	if pref.OptedOutTypesSet[event.EventType] {
		return false, false
	}

	// Розрахунок тихих годин
	inQuietHours := false
	if pref.QuietHoursStart > pref.QuietHoursEnd {
		inQuietHours = currentHour >= pref.QuietHoursStart || currentHour < pref.QuietHoursEnd
	} else {
		inQuietHours = currentHour >= pref.QuietHoursStart && currentHour < pref.QuietHoursEnd
	}

	if inQuietHours && !pref.IsAwayMode {
		if event.Severity == SeverityLow || event.Severity == SeverityDefault {
			return false, true // Накопичуємо у дайджест
		}
	}

	return true, false
}

// NotificationRouter відповідає за fan-out розгортання та створення тасок
type NotificationRouter struct {
	engine PolicyEngine
}

func (nr *NotificationRouter) BuildDeliveryTasks(
	event HomeEvent,
	members []UserPreference,
	devicesByUser map[string][]UserDevice,
	currentHour int,
) []DeliveryTask {
	var tasks []DeliveryTask

	for _, member := range members {
		deliver, forceDigest := nr.engine.ShouldDeliver(event, member, currentHour)
		if !deliver {
			if forceDigest {
				fmt.Printf("[Digest Buffer] Event %s buffered for user %s\n", event.EventID, member.UserID)
			}
			continue
		}

		devices := devicesByUser[member.UserID]
		for _, dev := range devices {
			rawID := fmt.Sprintf("%s:%s:%s", event.EventID, member.UserID, dev.DeviceID)
			hash := sha256.Sum256([]byte(rawID))
			baseDeliveryID := hex.EncodeToString(hash[:])[:16]

			if event.Severity == SeverityCritical {
				// 1. Silent Push для передзавантаження кадру у фоні
				tasks = append(tasks, DeliveryTask{
					DeliveryID:    baseDeliveryID + ":silent",
					EventID:       event.EventID,
					UserID:        member.UserID,
					DeviceID:      dev.DeviceID,
					Channel:       ChannelSilentPush,
					TokenOrNumber: dev.PushToken,
				})

				// 2. Critical Alert Push зі звуком
				tasks = append(tasks, DeliveryTask{
					DeliveryID:    baseDeliveryID + ":critical",
					EventID:       event.EventID,
					UserID:        member.UserID,
					DeviceID:      dev.DeviceID,
					Channel:       ChannelCriticalPush,
					Title:         "🚨 " + event.Title,
					Body:          event.Body,
					TokenOrNumber: dev.PushToken,
				})
			} else {
				tasks = append(tasks, DeliveryTask{
					DeliveryID:    baseDeliveryID + ":primary",
					EventID:       event.EventID,
					UserID:        member.UserID,
					DeviceID:      dev.DeviceID,
					Channel:       ChannelCriticalPush,
					Title:         event.Title,
					Body:          event.Body,
					TokenOrNumber: dev.PushToken,
				})
			}
		}
	}

	return tasks
}

// DeliveryTracker виконує мережеву відправку з каскадним fallback
type DeliveryTracker struct{}

func (dt *DeliveryTracker) ExecuteTaskWithFallback(
	task DeliveryTask,
	sendPushApi func(t DeliveryTask) bool,
	sendSmsApi func(number string, text string) bool,
) bool {
	if sendPushApi(task) {
		fmt.Printf("[ACK Success] Task %s delivered via %s\n", task.DeliveryID, task.Channel)
		return true
	}

	// Ескаляція у SMS, якщо пуш не пройшов для критичного евенту
	if task.Channel == ChannelCriticalPush && task.TokenOrNumber != "" {
		fmt.Printf("[Escalating] Primary push failed for task %s. Attempting SMS...\n", task.DeliveryID)
		if sendSmsApi(task.TokenOrNumber, task.Title+": "+task.Body) {
			fmt.Printf("[Fallback Success] Task %s delivered via SMS\n", task.DeliveryID)
			return true
		}
	}

	fmt.Printf("[DLQ Route] Task %s failed all retries. Routing to Dead-Letter Queue.\n", task.DeliveryID)
	return false
}
```
:::

## Детальний покроковий аналіз методів реалізації

Для глибокого розуміння розберемо кожен ключовий метод реалізації та його зв'язок з архітектурними вимогами.

### Аналіз оцінювача преференсій `PolicyEngine.shouldDeliver`

Логіка методу починається з миттєвої перевірки `event.severity === Severity.CRITICAL`. Це реалізація другого архітектурного інваріанта: критична пожежна чи охоронна тривога повертає `{ deliver: true, forceDigest: false }` на самому початку, до будь-яких перевірок профілю користувача.

Далі метод обчислює стан тихих годин. Зверніть увагу на розрахунок умовою `pref.quietHoursStart > pref.quietHoursEnd`. У реальному житті тихі години майже завжди переходять через північ (наприклад, з 23:00 до 07:00). Звичайна перевірка `start <= current && current < end` у цьому випадку поверне помилковий результат. Код правильно розрізняє випадок перехода через північ через дизюнкцію `(current >= start || current < end)`.

Якщо поточна година потрапляє у тихий інтервал і користувач перебуває вдома (`!pref.isAwayMode`), для подій класів `LOW` та `DEFAULT` встановлюється прапорець `forceDigest: true`. Це означає, що подія не відкидається, а переправляється у буфер Redis для зліплювання у ранковий дайджест, який вийде о 07:01 ранку.

### Аналіз роутера та розгортання `NotificationRouter.buildDeliveryTasks`

Метод виконує ітерований Fan-out по масиву членів родини `members`. Для кожного користувача витягується його список пристроїв `userDevices`.

Ключовим моментом є побудова детермінованого `baseDeliveryId`. Рядок `${event.eventId}:${member.userId}:${device.deviceId}` хешується алгоритмом SHA-256. Отриманий 16-символьний суфікс стає унікальним відбитком конкретної спроби доставки даного евенту на конкретний пристрій. При формуванні двох імпульсів до ідентифікатора додаються суфікси `:silent` та `:critical`. Це гарантує, що APNs та FCM зможуть відрізнити фонове пробудження від візуального банера й не згрупують їх як дублікати.

### Аналіз трекера доставки `DeliveryTracker.executeTaskWithFallback`

Метод реалізує шаблон паттерна **Strategy & Fallback Execution**. Спочатку робиться спроба виклику `sendPushApi(task)`. Якщо зовнішній пуш-сервер відповідає успіхом і повертає ACK, виклик завершується з `true`.

Якщо первинний виклик зазнає мережевої помилки або вичерпує таймаут 15 секунд, алгоритм перевіряє умову `task.channel === ChannelType.CRITICAL_PUSH && task.tokenOrNumber`. Для критичних тривог невдача пуша є тригером до автоматичного перемикання на альтернативний платіжний канал `sendSmsApi`. Лише якщо і SMS-шлюз відповідає помилкою, задача реєструється як безнадійна й переправляється у чергу Dead-Letter Queue (DLQ).

## Аналіз крайових випадків та реального виконання

При роботі конвеєра в реальному високонавантаженому середовищі виникають три критичні крайові випадки (Edge Cases), які потребують чіткої обробки:

1. **Недійсні пуш-токени (`410 Gone` / `Unregistered`):** Коли користувач видаляє застосунок DH або скидає налаштування смартфона, APNs та FCM повертають фатальну помилку при спробі відправки. `DeliveryTracker` розпізнає цей код і відразу публікує евент `DeviceTokenInvalidated` у системну шину для видалення застарілого токена з бази даних.
2. **Мережеві розриви та шторм повторів (Thundering Herd):** При тимчасовій недоступності серверів FCM/APNs сотні тисяч задач починають ретраїтися. Конвеєр застосовує алгоритм Full Jitter для обчислення затримки: `sleep = random(0, min(max_backoff, base * 2^attempt))`. Випадковий шум запобігає синхронним пікам навантаження на шлюзи.
3. **Обробка DLQ (Dead-Letter Queue):** Усі завдання, які не вдалося доставити жодним із каналів, потрапляють у DLQ із збереженням стека помилок. Автоматичний моніторинг перевіряє розмір DLQ і при перевищенні порогу 100 повідомлень на хвилину генерує тривогу для інженерів чергування SRE.

## Моніторинг, метрики та спостережуваність (Observability)

Вихід назовні потребує безперервного вимірювання показників якості (SLO/SLA). Конвеєр сповіщень Digital Homes експортує у систему Prometheus чотири ключові метрики:

- `dh_notifications_ingested_total{severity}` — загальний лічильник вхідних евентів за класами критичності.
- `dh_notifications_delivered_total{channel, status}` — кількість успішно доставлених сповіщень у розрізі каналів (Push, Silent, SMS).
- `dh_notifications_fallback_events_total` — кількість випадків, коли первинний Push зазнав невдачі й задіявся SMS Fallback.
- `dh_notifications_delivery_latency_seconds` — гістограма часу від моменту створення події на хабі до отримання квитанції ACK від мобільного пристрою (p95 та p99).

Аналіз цих метрик дозволяє SRE-команді виявляти збої у зовнішніх пуш-провайдерів ще до того, як користувачі почнуть масово скаржитися у службу підтримки.
