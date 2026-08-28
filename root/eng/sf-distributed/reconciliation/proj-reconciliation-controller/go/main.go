package main

import (
	"context"
	"fmt"
	"math"
	"math/rand"
	"sync"
	"time"
)

// NodeSpec описує бажаний стан пулу вузлів
type NodeSpec struct {
	TargetReplicas int
	InstanceType   string
}

// NodeStatus описує фактичний спостережуваний стан
type NodeStatus struct {
	AvailableReplicas int
	Phase             string
	ActiveInstanceIDs []string
}

// ManagedCluster — корінь агрегату кластера
type ManagedCluster struct {
	Key               string
	ResourceVersion   uint64
	DeletionTimestamp bool
	Finalizers        []string
	Spec              NodeSpec
	Status            NodeStatus
}

// ReconcileResult керує наступним кроком планування
type ReconcileResult struct {
	Requeue      bool
	RequeueAfter time.Duration
}

// RateLimitingWorkQueue реалізує коалесценцію подій та експоненційний бекоф
type RateLimitingWorkQueue struct {
	mu             sync.Mutex
	cond           *sync.Cond
	queue          []string
	queuedSet      map[string]struct{}
	dirtySet       map[string]struct{}
	processingSet  map[string]struct{}
	failureCounts  map[string]int
	shutdown       bool
}

func NewWorkQueue() *RateLimitingWorkQueue {
	q := &RateLimitingWorkQueue{
		queuedSet:     make(map[string]struct{}),
		dirtySet:      make(map[string]struct{}),
		processingSet: make(map[string]struct{}),
		failureCounts: make(map[string]int),
	}
	q.cond = sync.NewCond(&q.mu)
	return q
}

func (q *RateLimitingWorkQueue) Add(key string) {
	q.mu.Lock()
	defer q.mu.Unlock()
	q.dirtySet[key] = struct{}{}
	if _, processing := q.processingSet[key]; !processing {
		if _, queued := q.queuedSet[key]; !queued {
			q.queue = append(q.queue, key)
			q.queuedSet[key] = struct{}{}
			q.cond.Signal()
		}
	}
}

func (q *RateLimitingWorkQueue) Get() (string, bool) {
	q.mu.Lock()
	defer q.mu.Unlock()
	for len(q.queue) == 0 && !q.shutdown {
		q.cond.Wait()
	}
	if q.shutdown && len(q.queue) == 0 {
		return "", false
	}
	key := q.queue[0]
	q.queue = q.queue[1:]
	delete(q.queuedSet, key)
	delete(q.dirtySet, key)
	q.processingSet[key] = struct{}{}
	return key, true
}

func (q *RateLimitingWorkQueue) Done(key string, success bool) {
	q.mu.Lock()
	defer q.mu.Unlock()
	delete(q.processingSet, key)

	if !success {
		q.failureCounts[key]++
		attempts := q.failureCounts[key]
		backoff := time.Duration(math.Min(5000, float64(100*(1<<min(attempts, 6)))) * float64(time.Millisecond))
		time.AfterFunc(backoff+time.Duration(rand.Intn(50))*time.Millisecond, func() {
			q.Add(key)
		})
	} else {
		delete(q.failureCounts, key)
	}

	if _, dirty := q.dirtySet[key]; dirty {
		if _, queued := q.queuedSet[key]; !queued {
			q.queue = append(q.queue, key)
			q.queuedSet[key] = struct{}{}
			q.cond.Signal()
		}
	}
}

// ClusterReconciler реалізує бізнес-логіку узгодження
type ClusterReconciler struct {
	mu       sync.Mutex
	store    map[string]ManagedCluster
	cloudVMs map[string][]string
}

func (r *ClusterReconciler) Reconcile(ctx context.Context, key string) ReconcileResult {
	r.mu.Lock()
	cluster, exists := r.store[key]
	r.mu.Unlock()

	if !exists {
		return ReconcileResult{Requeue: false}
	}

	finalizer := "infra.example.com/cleanup-vms"

	// Обробка безпечного каскадного видалення
	if cluster.DeletionTimestamp {
		for i, f := range cluster.Finalizers {
			if f == finalizer {
				// Очищення фізичних VM
				r.mu.Lock()
				r.cloudVMs[key] = nil
				cluster.Finalizers = append(cluster.Finalizers[:i], cluster.Finalizers[i+1:]...)
				cluster.ResourceVersion++
				r.store[key] = cluster
				r.mu.Unlock()
				return ReconcileResult{Requeue: false}
			}
		}
		return ReconcileResult{Requeue: false}
	}

	// Читання стану фізичного світу
	r.mu.Lock()
	vms := append([]string{}, r.cloudVMs[key]...)
	r.mu.Unlock()

	// Diff
	delta := cluster.Spec.TargetReplicas - len(vms)

	// Act
	if delta > 0 {
		for i := 0; i < delta; i++ {
			vmID := fmt.Sprintf("vm-%d", rand.Intn(10000))
			vms = append(vms, vmID)
		}
	} else if delta < 0 {
		vms = vms[:cluster.Spec.TargetReplicas]
	}

	// Збереження фізичного стану та оновлення статусу через CAS
	r.mu.Lock()
	defer r.mu.Unlock()
	current := r.store[key]
	if current.ResourceVersion != cluster.ResourceVersion {
		return ReconcileResult{Requeue: true, RequeueAfter: 100 * time.Millisecond}
	}

	r.cloudVMs[key] = vms
	current.Status.AvailableReplicas = len(vms)
	current.Status.ActiveInstanceIDs = vms
	current.Status.Phase = "Ready"
	current.ResourceVersion++
	r.store[key] = current

	return ReconcileResult{Requeue: false}
}
