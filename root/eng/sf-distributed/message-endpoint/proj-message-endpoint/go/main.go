package main

import (
	"fmt"
	"hash/fnv"
	"sync"
	"time"
)

type MessageHeaders struct {
	ID           string
	PartitionKey string
	Destination  string
}

type PaymentEvent struct {
	AccountID   string
	Action      string
	AmountCents uint64
}

type Message struct {
	Headers MessageHeaders
	Payload PaymentEvent
}

type AckStatus string

const (
	AckStatusAck  AckStatus = "ACK"
	AckStatusNack AckStatus = "NACK"
	AckStatusDlq  AckStatus = "DLQ"
)

type AckCallback func(id string, status AckStatus, reason string)

type WorkerTask struct {
	Msg Message
	Cb  AckCallback
}

type GoPartitionedEndpoint struct {
	workerCount int
	queues      []chan WorkerTask
	inbox       sync.Map
	wg          sync.WaitGroup
}

func NewEndpoint(workerCount int, queueCap int) *GoPartitionedEndpoint {
	ep := &GoPartitionedEndpoint{
		workerCount: workerCount,
		queues:      make([]chan WorkerTask, workerCount),
	}

	for i := 0; i < workerCount; i++ {
		ep.queues[i] = make(chan WorkerTask, queueCap)
		ep.wg.Add(1)
		go ep.workerLoop(i, ep.queues[i])
	}
	return ep
}

func (ep *GoPartitionedEndpoint) workerLoop(id int, queue chan WorkerTask) {
	defer ep.wg.Done()
	for task := range queue {
		// 1. Дедуплікація Inbox
		if _, loaded := ep.inbox.LoadOrStore(task.Msg.Headers.ID, true); loaded {
			fmt.Printf("  [Go-Worker %d] ДУБЛІКАТ %s -> ACK\n", id, task.Msg.Headers.ID)
			task.Cb(task.Msg.Headers.ID, AckStatusAck, "")
			continue
		}

		// 2. Бізнес-обробка
		if task.Msg.Payload.AmountCents == 0 && task.Msg.Payload.Action != "CREATE" {
			fmt.Printf("  [Go-Worker %d] ОТРУЙНИЙ ПАКЕТ %s -> DLQ\n", id, task.Msg.Headers.ID)
			task.Cb(task.Msg.Headers.ID, AckStatusDlq, "Zero amount")
		} else {
			fmt.Printf("  [Go-Worker %d] Оброблено %s для %s -> ACK\n", id, task.Msg.Payload.Action, task.Msg.Payload.AccountID)
			task.Cb(task.Msg.Headers.ID, AckStatusAck, "")
		}
	}
}

func (ep *GoPartitionedEndpoint) Dispatch(msg Message, cb AckCallback) {
	hasher := fnv.New32a()
	hasher.Write([]byte(msg.Headers.PartitionKey))
	workerID := int(hasher.Sum32()) % ep.workerCount
	ep.queues[workerID] <- WorkerTask{Msg: msg, Cb: cb}
}

func (ep *GoPartitionedEndpoint) Stop() {
	for _, q := range ep.queues {
		close(q)
	}
	ep.wg.Wait()
}
