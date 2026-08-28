package main

import (
	"fmt"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// Message описує подію в Pub/Sub
type Message struct {
	Topic      string
	Payload    string
	SequenceID uint64
}

// OverflowPolicy визначає стратегію обробки переповнення
type OverflowPolicy int

const (
	DropOldest OverflowPolicy = iota
	RejectNewest
)

// SubscriberQueue представляє буфер конкретного підписника
type SubscriberQueue struct {
	id       string
	capacity int
	policy   OverflowPolicy
	ch       chan Message
	dropped  uint64
	mu       sync.Mutex
}

func NewSubscriberQueue(id string, capacity int, policy OverflowPolicy) *SubscriberQueue {
	return &SubscriberQueue{
		id:       id,
		capacity: capacity,
		policy:   policy,
		ch:       make(chan Message, capacity),
	}
}

func (sq *SubscriberQueue) Push(msg Message) bool {
	sq.mu.Lock()
	defer sq.mu.Unlock()

	select {
	case sq.ch <- msg:
		return true
	default:
		// Буфер переповнений
		atomic.AddUint64(&sq.dropped, 1)
		if sq.policy == DropOldest {
			// Скидаємо старе повідомлення і записуємо нове
			select {
			case <-sq.ch:
			default:
			}
			select {
			case sq.ch <- msg:
				return true
			default:
				return false
			}
		}
		return false
	}
}

func (sq *SubscriberQueue) Pop() (Message, bool) {
	select {
	case msg := <-sq.ch:
		return msg, true
	default:
		return Message{}, false
	}
}

// TrieNode вузол дерева маршрутизації тем
type TrieNode struct {
	children    map[string]*TrieNode
	subscribers []*SubscriberQueue
}

func NewTrieNode() *TrieNode {
	return &TrieNode{
		children: make(map[string]*TrieNode),
	}
}

func (n *TrieNode) Insert(tokens []string, sub *SubscriberQueue) {
	if len(tokens) == 0 {
		n.subscribers = append(n.subscribers, sub)
		return
	}
	token := tokens[0]
	child, exists := n.children[token]
	if !exists {
		child = NewTrieNode()
		n.children[token] = child
	}
	child.Insert(tokens[1:], sub)
}

func (n *TrieNode) Match(tokens []string, result *[]*SubscriberQueue) {
	// Багаторівневий wildcard '>'
	if multi, exists := n.children[">"]; exists {
		*result = append(*result, multi.subscribers...)
	}

	if len(tokens) == 0 {
		*result = append(*result, n.subscribers...)
		return
	}

	token := tokens[0]

	// Точний збіг
	if exact, exists := n.children[token]; exists {
		exact.Match(tokens[1:], result)
	}

	// Однорівневий wildcard '*'
	if single, exists := n.children["*"]; exists {
		single.Match(tokens[1:], result)
	}
}

// Broker центральний диспетчер Pub/Sub
type Broker struct {
	root       *TrieNode
	seqCounter uint64
	mu         sync.RWMutex
}

func NewBroker() *Broker {
	return &Broker{
		root: NewTrieNode(),
	}
}

func (b *Broker) Subscribe(pattern string, sub *SubscriberQueue) {
	b.mu.Lock()
	defer b.mu.Unlock()
	tokens := strings.Split(pattern, "/")
	b.root.Insert(tokens, sub)
}

func (b *Broker) Publish(topic string, payload string) int {
	seq := atomic.AddUint64(&b.seqCounter, 1)
	msg := Message{
		Topic:      topic,
		Payload:    payload,
		SequenceID: seq,
	}

	b.mu.RLock()
	var targets []*SubscriberQueue
	tokens := strings.Split(topic, "/")
	b.root.Match(tokens, &targets)
	b.mu.RUnlock()

	delivered := 0
	for _, sub := range targets {
		if sub.Push(msg) {
			delivered++
		}
	}
	return delivered
}

func main() {
	broker := NewBroker()

	fastSub := NewSubscriberQueue("FastAnalytics", 1000, DropOldest)
	slowSub := NewSubscriberQueue("SlowPDFExporter", 5, DropOldest)

	broker.Subscribe("orders/eu/*", fastSub)
	broker.Subscribe("orders/>", slowSub)

	fmt.Println("[Broker] Запуск публікації 20 подій...")
	for i := 1; i <= 20; i++ {
		broker.Publish("orders/eu/ua", fmt.Sprintf("OrderData_#%d", i))
	}

	time.Sleep(10 * time.Millisecond)

	fmt.Printf("FastAnalytics: в черзі %d, скинуто %d\n", len(fastSub.ch), atomic.LoadUint64(&fastSub.dropped))
	fmt.Printf("SlowPDFExporter: в черзі %d, скинуто %d\n", len(slowSub.ch), atomic.LoadUint64(&slowSub.dropped))

	fmt.Println("\n[SlowPDFExporter] Збережені повідомлення (останні 5):")
	for {
		msg, ok := slowSub.Pop()
		if !ok {
			break
		}
		fmt.Printf("  -> seq=%d payload=%s\n", msg.SequenceID, msg.Payload)
	}
}
