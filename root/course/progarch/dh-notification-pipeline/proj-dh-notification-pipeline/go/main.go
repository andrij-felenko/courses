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
