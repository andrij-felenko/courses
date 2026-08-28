package main

import (
	"errors"
	"fmt"
	"sync"
)

type ActionType string

const (
	ActionNoop    ActionType = "NOOP"
	ActionCreate  ActionType = "CREATE"
	ActionUpdate  ActionType = "UPDATE"
	ActionReplace ActionType = "REPLACE"
	ActionDestroy ActionType = "DESTROY"
)

type Resource struct {
	Type          string
	Name          string
	Props         map[string]string
	Deps          []string
	ImmutableKeys []string
}

func (r Resource) URN() string {
	return fmt.Sprintf("%s.%s", r.Type, r.Name)
}

type ResourceState struct {
	URN        string
	PhysicalID string
	Props      map[string]string
}

type PlanItem struct {
	URN        string
	Action     ActionType
	OldProps   map[string]string
	NewProps   map[string]string
	PhysicalID string
}

type MockCloudProvider struct {
	mu        sync.Mutex
	resources map[string]map[string]string
	counter   int
}

func NewMockCloudProvider() *MockCloudProvider {
	return &MockCloudProvider{
		resources: make(map[string]map[string]string),
		counter:   1000,
	}
}

func (p *MockCloudProvider) Create(rType string, props map[string]string) string {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.counter++
	id := fmt.Sprintf("%s-%d", rType, p.counter)
	cp := make(map[string]string)
	for k, v := range props {
		cp[k] = v
	}
	p.resources[id] = cp
	return id
}

func (p *MockCloudProvider) Update(id string, props map[string]string) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	if _, ok := p.resources[id]; !ok {
		return errors.New("ресурс не знайдено")
	}
	for k, v := range props {
		p.resources[id][k] = v
	}
	return nil
}

func (p *MockCloudProvider) Delete(id string) {
	p.mu.Lock()
	defer p.mu.Unlock()
	delete(p.resources, id)
}

func (p *MockCloudProvider) Read(id string) (map[string]string, bool) {
	p.mu.Lock()
	defer p.mu.Unlock()
	val, ok := p.resources[id]
	if !ok {
		return nil, false
	}
	cp := make(map[string]string)
	for k, v := range val {
		cp[k] = v
	}
	return cp, true
}

type StateStore struct {
	mu        sync.Mutex
	locked    bool
	resources map[string]ResourceState
}

func NewStateStore() *StateStore {
	return &StateStore{
		resources: make(map[string]ResourceState),
	}
}

func (s *StateStore) AcquireLock() bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.locked {
		return false
	}
	s.locked = true
	return true
}

func (s *StateStore) ReleaseLock() {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.locked = false
}

type IaCEngine struct {
	provider *MockCloudProvider
	state    *StateStore
}

func NewIaCEngine(provider *MockCloudProvider, state *StateStore) *IaCEngine {
	return &IaCEngine{provider: provider, state: state}
}

func (e *IaCEngine) BuildDAGAndSort(desired map[string]Resource) ([]string, error) {
	inDegree := make(map[string]int)
	adj := make(map[string][]string)

	for urn := range desired {
		inDegree[urn] = 0
		adj[urn] = []string{}
	}

	for urn, res := range desired {
		for _, dep := range res.Deps {
			if _, ok := desired[dep]; !ok {
				return nil, fmt.Errorf("невідома залежність %s у %s", dep, urn)
			}
			adj[dep] = append(adj[dep], urn)
			inDegree[urn]++
		}
	}

	queue := make([]string, 0)
	for urn, deg := range inDegree {
		if deg == 0 {
			queue = append(queue, urn)
		}
	}

	order := make([]string, 0, len(desired))
	for len(queue) > 0 {
		node := queue[0]
		queue = queue[1:]
		order = append(order, node)

		for _, neighbor := range adj[node] {
			inDegree[neighbor]--
			if inDegree[neighbor] == 0 {
				queue = append(queue, neighbor)
			}
		}
	}

	if len(order) != len(desired) {
		return nil, errors.New("виявлено циклічну залежність в графі")
	}

	return order, nil
}
