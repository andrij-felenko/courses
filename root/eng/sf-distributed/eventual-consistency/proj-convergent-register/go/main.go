package main

import (
	"fmt"
	"sync"
)

// ClockRelation визначає частковий порядок двох векторних годинників
type ClockRelation int

const (
	Equal ClockRelation = iota
	Ancestor
	Descendant
	Concurrent
)

// VectorClock реалізує векторний годинник версіонування
type VectorClock struct {
	versions map[string]uint64
}

func NewVectorClock() VectorClock {
	return VectorClock{versions: make(map[string]uint64)}
}

func (vc VectorClock) Clone() VectorClock {
	c := NewVectorClock()
	for k, v := range vc.versions {
		c.versions[k] = v
	}
	return c
}

func (vc VectorClock) Increment(nodeID string) {
	vc.versions[nodeID]++
}

func (vc VectorClock) Get(nodeID string) uint64 {
	return vc.versions[nodeID]
}

func (vc VectorClock) Merge(other VectorClock) VectorClock {
	res := vc.Clone()
	for node, ver := range other.versions {
		if ver > res.versions[node] {
			res.versions[node] = ver
		}
	}
	return res
}

func (vc VectorClock) Compare(other VectorClock) ClockRelation {
	hasGreater, hasLess := false, false
	allNodes := make(map[string]struct{})
	for k := range vc.versions {
		allNodes[k] = struct{}{}
	}
	for k := range other.versions {
		allNodes[k] = struct{}{}
	}

	for node := range allNodes {
		v1 := vc.Get(node)
		v2 := other.Get(node)
		if v1 > v2 {
			hasGreater = true
		}
		if v1 < v2 {
			hasLess = true
		}
	}

	if !hasGreater && !hasLess {
		return Equal
	}
	if hasGreater && !hasLess {
		return Descendant
	}
	if !hasGreater && hasLess {
		return Ancestor
	}
	return Concurrent
}

func (vc VectorClock) String() string {
	res := "{"
	first := true
	for k, v := range vc.versions {
		if !first {
			res += ", "
		}
		res += fmt.Sprintf("%s:%d", k, v)
		first = false
	}
	res += "}"
	return res
}

// VersionedValue представляє сутність даних із метаданими
type VersionedValue struct {
	Key         string
	Value       string
	Clock       VectorClock
	TimestampMS int64
	IsTombstone bool
}

func MergeConcurrent(a, b VersionedValue) VersionedValue {
	merged := VersionedValue{
		Key:   a.Key,
		Clock: a.Clock.Merge(b.Clock),
	}
	if a.TimestampMS >= b.TimestampMS {
		merged.Value = a.Value
		merged.TimestampMS = a.TimestampMS
		merged.IsTombstone = a.IsTombstone
	} else {
		merged.Value = b.Value
		merged.TimestampMS = b.TimestampMS
		merged.IsTombstone = b.IsTombstone
	}
	return merged
}

// StorageNode представляє локальний сервер зберігання
type StorageNode struct {
	nodeID string
	mu     sync.RWMutex
	store  map[string]VersionedValue
}

func NewStorageNode(nodeID string) *StorageNode {
	return &StorageNode{
		nodeID: nodeID,
		store:  make(map[string]VersionedValue),
	}
}

func (n *StorageNode) PutLocal(key, value string, clientClock VectorClock, ts int64) VersionedValue {
	n.mu.Lock()
	defer n.mu.Unlock()

	newClock := clientClock.Clone()
	newClock.Increment(n.nodeID)

	entry := VersionedValue{
		Key:         key,
		Value:       value,
		Clock:       newClock,
		TimestampMS: ts,
		IsTombstone: false,
	}
	n.store[key] = entry
	return entry
}

func (n *StorageNode) ApplyReplication(incoming VersionedValue) bool {
	n.mu.Lock()
	defer n.mu.Unlock()

	current, exists := n.store[incoming.Key]
	if !exists {
		n.store[incoming.Key] = incoming
		return true
	}

	rel := incoming.Clock.Compare(current.Clock)
	if rel == Descendant {
		n.store[incoming.Key] = incoming
		return true
	} else if rel == Concurrent {
		n.store[incoming.Key] = MergeConcurrent(current, incoming)
		return true
	}
	return false
}

func (n *StorageNode) GetLocal(key string) (VersionedValue, bool) {
	n.mu.RLock()
	defer n.mu.RUnlock()
	val, ok := n.store[key]
	if ok && !val.IsTombstone {
		return val, true
	}
	return VersionedValue{}, false
}

func (n *StorageNode) GetAll() map[string]VersionedValue {
	n.mu.RLock()
	defer n.mu.RUnlock()
	res := make(map[string]VersionedValue, len(n.store))
	for k, v := range n.store {
		res[k] = v
	}
	return res
}

// DistributedCluster керує координацією між вузлами
type DistributedCluster struct {
	nodes map[string]*StorageNode
}

func NewDistributedCluster() *DistributedCluster {
	return &DistributedCluster{nodes: make(map[string]*StorageNode)}
}

func (c *DistributedCluster) AddNode(node *StorageNode) {
	c.nodes[node.nodeID] = node
}

func (c *DistributedCluster) ReadWithRepair(key string, nodeIDs []string) (VersionedValue, bool) {
	var responses []VersionedValue
	var queried []*StorageNode

	for _, nid := range nodeIDs {
		node, ok := c.nodes[nid]
		if !ok {
			continue
		}
		queried = append(queried, node)
		if val, found := node.GetLocal(key); found {
			responses = append(responses, val)
		}
	}

	if len(responses) == 0 {
		return VersionedValue{}, false
	}

	canonical := responses[0]
	for i := 1; i < len(responses); i++ {
		rel := canonical.Clock.Compare(responses[i].Clock)
		if rel == Ancestor {
			canonical = responses[i]
		} else if rel == Concurrent {
			canonical = MergeConcurrent(canonical, responses[i])
		}
	}

	// Read-Repair для вузлів із застарілою версією
	for _, node := range queried {
		if cur, found := node.GetLocal(key); !found || cur.Clock.Compare(canonical.Clock) == Ancestor {
			fmt.Printf("  [Read-Repair] Вузол %s оновлено до актуального стану\n", node.nodeID)
			node.ApplyReplication(canonical)
		}
	}

	return canonical, true
}

func (c *DistributedCluster) AntiEntropySync(nodeAID, nodeBID string) {
	nodeA := c.nodes[nodeAID]
	nodeB := c.nodes[nodeBID]
	if nodeA == nil || nodeB == nil {
		return
	}

	for _, v := range nodeA.GetAll() {
		nodeB.ApplyReplication(v)
	}
	for _, v := range nodeB.GetAll() {
		nodeA.ApplyReplication(v)
	}
}

// ClientSession реалізує клієнтський контекст із гарантією RYW
type ClientSession struct {
	clientID     string
	cluster      *DistributedCluster
	sessionClock VectorClock
}

func NewClientSession(clientID string, cluster *DistributedCluster) *ClientSession {
	return &ClientSession{
		clientID:     clientID,
		cluster:      cluster,
		sessionClock: NewVectorClock(),
	}
}

func (cs *ClientSession) Write(preferredNode, key, value string, ts int64) {
	node := cs.cluster.nodes[preferredNode]
	if node == nil {
		panic("Node not found")
	}

	res := node.PutLocal(key, value, cs.sessionClock, ts)
	cs.sessionClock = cs.sessionClock.Merge(res.Clock)
	fmt.Printf("[Client %s Write] Ключ: %s -> %s, токен: %s\n", cs.clientID, key, preferredNode, cs.sessionClock.String())
}

func (cs *ClientSession) ReadWithGuarantee(targetNode, key string) (string, bool) {
	node := cs.cluster.nodes[targetNode]
	if node == nil {
		return "", false
	}

	val, found := node.GetLocal(key)
	if found {
		rel := val.Clock.Compare(cs.sessionClock)
		if rel == Ancestor {
			fmt.Printf("  [Попередження] Вузол %s відстає від сесії клієнта! Запуск Read-Repair.\n", targetNode)
		}
	}

	repaired, ok := cs.cluster.ReadWithRepair(key, []string{"Node-EU", "Node-US"})
	if ok {
		cs.sessionClock = cs.sessionClock.Merge(repaired.Clock)
		return repaired.Value, true
	}
	return "", false
}

func main() {
	cluster := NewDistributedCluster()
	nodeEU := NewStorageNode("Node-EU")
	nodeUS := NewStorageNode("Node-US")
	cluster.AddNode(nodeEU)
	cluster.AddNode(nodeUS)

	fmt.Println("=== 1. Одночасні записи в ізольовані вузли (Partition) ===")
	alice := NewClientSession("Alice", cluster)
	bob := NewClientSession("Bob", cluster)

	alice.Write("Node-EU", "config:theme", "dark-mode", 1000)
	bob.Write("Node-US", "config:theme", "light-mode", 1005)

	valEU, _ := nodeEU.GetLocal("config:theme")
	valUS, _ := nodeUS.GetLocal("config:theme")
	fmt.Printf("Node-EU стан: %s | Clock: %s\n", valEU.Value, valEU.Clock.String())
	fmt.Printf("Node-US стан: %s | Clock: %s\n", valUS.Value, valUS.Clock.String())

	fmt.Println("\n=== 2. Аліса читає з Node-US (Сесійний захист + Read-Repair) ===\n")
	resAlice, _ := alice.ReadWithGuarantee("Node-US", "config:theme")
	fmt.Printf("Аліса отримала зведений результат: %s\n", resAlice)

	fmt.Println("\n=== 3. Фонова анти-ентропія (Anti-Entropy Sync) ===")
	cluster.AntiEntropySync("Node-EU", "Node-US")
	finalEU, _ := nodeEU.GetLocal("config:theme")
	finalUS, _ := nodeUS.GetLocal("config:theme")
	fmt.Printf("Node-EU фінал: %s | Clock: %s\n", finalEU.Value, finalEU.Clock.String())
	fmt.Printf("Node-US фінал: %s | Clock: %s\n", finalUS.Value, finalUS.Clock.String())
}
