package main

import (
	"fmt"
	"hash/fnv"
	"sync"
)

type EventType int

const (
	WorkflowStarted EventType = iota
	WorkflowSignaled
	ContinuedAsNew
)

type HistoryEvent struct {
	EventID int64
	Type    EventType
	Name    string
	Payload string
}

type WorkflowExecution struct {
	WorkflowID     string
	RunID          string
	CurrentBalance int64
	History        []HistoryEvent
	IsClosed       bool
}

type HistoryShard struct {
	ShardID             uint32
	CompactionThreshold int
	Mu                  sync.Mutex
	Executions          map[string]*WorkflowExecution
}

func NewHistoryShard(id uint32, threshold int) *HistoryShard {
	return &HistoryShard{
		ShardID:             id,
		CompactionThreshold: threshold,
		Executions:          make(map[string]*WorkflowExecution),
	}
}

func (s *HistoryShard) ExecuteSignal(workflowID string, amount int64) {
	s.Mu.Lock()
	defer s.Mu.Unlock()

	wf, exists := s.Executions[workflowID]
	if !exists {
		wf = &WorkflowExecution{
			WorkflowID:     workflowID,
			RunID:          "run_001",
			CurrentBalance: 0,
			History: []HistoryEvent{
				{EventID: 1, Type: WorkflowStarted, Name: "Onboarding", Payload: "{}"},
			},
		}
		s.Executions[workflowID] = wf
	}

	if wf.IsClosed {
		return
	}

	wf.History = append(wf.History, HistoryEvent{
		EventID: int64(len(wf.History) + 1),
		Type:    WorkflowSignaled,
		Name:    "DepositSignal",
		Payload: fmt.Sprintf("%d", amount),
	})
	wf.CurrentBalance += amount

	fmt.Printf("[Шард #%d] %s (Run: %s): +%d грн. Баланс: %d | Історія: %d подій\n",
		s.ShardID, wf.WorkflowID, wf.RunID, amount, wf.CurrentBalance, len(wf.History))

	if len(wf.History) >= s.CompactionThreshold {
		fmt.Printf(">>> [Шард #%d] Відсікання Continue-As-New для %s <<<\n", s.ShardID, wf.WorkflowID)
		wf.IsClosed = true

		newWf := &WorkflowExecution{
			WorkflowID:     wf.WorkflowID,
			RunID:          "run_002",
			CurrentBalance: wf.CurrentBalance,
			History: []HistoryEvent{
				{EventID: 1, Type: WorkflowStarted, Name: "Onboarding", Payload: fmt.Sprintf("{\"balance\":%d}", wf.CurrentBalance)},
			},
		}
		s.Executions[workflowID] = newWf
	}
}

type DurableCluster struct {
	NumShards uint32
	Shards    []*HistoryShard
}

func NewDurableCluster(numShards uint32) *DurableCluster {
	shards := make([]*HistoryShard, numShards)
	for i := uint32(0); i < numShards; i++ {
		shards[i] = NewHistoryShard(i, 10)
	}
	return &DurableCluster{NumShards: numShards, Shards: shards}
}

func (c *DurableCluster) SendSignal(workflowID string, amount int64) {
	h := fnv.New32a()
	h.Write([]byte(workflowID))
	shardIdx := h.Sum32() % c.NumShards
	c.Shards[shardIdx].ExecuteSignal(workflowID, amount)
}

func main() {
	cluster := NewDurableCluster(4)
	for i := 1; i <= 12; i++ {
		cluster.SendSignal("user_101", 100)
	}
}
