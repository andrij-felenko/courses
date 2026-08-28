package main

import (
	"fmt"
	"math"
)

type NotificationEvent struct {
	ID             string
	Title          string
	Body           string
	ScopeID        string
	RecipientCount int
	IsEmergency    bool
}

type FanOutStrategy int

const (
	FastTrackOnWrite FanOutStrategy = iota
	HybridBatched
	BroadcastOnRead
)

type DispatchDecision struct {
	Strategy    FanOutStrategy
	BatchSize   int
	RouteReason string
}

type FanOutRouter struct{}

const (
	MaxDirectOnWrite  = 10
	MaxCommunityHybrid = 5000
	PushBatchChunk    = 500
)

func (r *FanOutRouter) Route(event NotificationEvent) DispatchDecision {
	if event.IsEmergency || event.RecipientCount <= MaxDirectOnWrite {
		return DispatchDecision{
			Strategy:    FastTrackOnWrite,
			BatchSize:   event.RecipientCount,
			RouteReason: "Tier 1: Аварійний або локальний доступ (N <= 10). Пряма On-Write розсилка.",
		}
	}

	if event.RecipientCount <= MaxCommunityHybrid {
		return DispatchDecision{
			Strategy:    HybridBatched,
			BatchSize:   PushBatchChunk,
			RouteReason: "Tier 2: Подія ЖК (10 < N <= 5000). On-Read стрічка + push-батчі.",
		}
	}

	return DispatchDecision{
		Strategy:    BroadcastOnRead,
		BatchSize:   1,
		RouteReason: "Tier 3: Системна масова подія (N > 5000). Чистий On-Read + FCM Topic.",
	}
}

func (r *FanOutRouter) ExecuteDispatch(event NotificationEvent) {
	decision := r.Route(event)
	fmt.Printf("[ROUTER] Подія ID: %s | Стратегія: %d | Опис: %s\n", event.ID, decision.Strategy, decision.RouteReason)

	switch decision.Strategy {
	case FastTrackOnWrite:
		fmt.Printf("  └─ [Tier 1] Запис %d персональних inboxes у пам'ять + High-Priority Push.\n", event.RecipientCount)
	case HybridBatched:
		numChunks := int(math.Ceil(float64(event.RecipientCount) / float64(decision.BatchSize)))
		fmt.Printf("  └─ [Tier 2] Збережено 1 запис стрічки ЖК %s. Згенеровано %d push-батчів по %d рецепторів.\n",
			event.ScopeID, numChunks, decision.BatchSize)
	case BroadcastOnRead:
		fmt.Printf("  └─ [Tier 3] Збережено 1 глобальний запис у системну стрічку. Multicast push у root://%s\n", event.ScopeID)
	}
}

func main() {
	router := &FanOutRouter{}

	router.ExecuteDispatch(NotificationEvent{
		ID: "evt-001", Title: "Виявлено дим!", ScopeID: "home-1402", RecipientCount: 2, IsEmergency: true,
	})
	router.ExecuteDispatch(NotificationEvent{
		ID: "evt-002", Title: "Відключення води", ScopeID: "complex-oak", RecipientCount: 1200, IsEmergency: false,
	})
	router.ExecuteDispatch(NotificationEvent{
		ID: "evt-003", Title: "Оновлення оферти", ScopeID: "global-dh", RecipientCount: 500000, IsEmergency: false,
	})
}
