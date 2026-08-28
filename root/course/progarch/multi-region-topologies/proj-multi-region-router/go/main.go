package main

import (
	"fmt"
	"sync"
)

type Region string

const (
	RegionFrankfurtPrimary Region = "eu-central-1 (Primary)"
	RegionVirginiaReplica  Region = "us-east-1 (Replica)"
	RegionTokyoReplica     Region = "ap-northeast-1 (Replica)"
)

type Lsn uint64

type HttpRequest struct {
	Path         string
	IsWrite      bool
	ClientRegion Region
	RequiredLSN  Lsn // RAW token
}

type HttpResponse struct {
	StatusCode int
	Body       string
	ServedBy   Region
	NewLSN     Lsn
}

type PrimaryDB struct {
	mu  sync.Mutex
	lsn Lsn
}

func NewPrimaryDB(initialLSN Lsn) *PrimaryDB {
	return &PrimaryDB{lsn: initialLSN}
}

func (p *PrimaryDB) ExecuteRead(req HttpRequest) HttpResponse {
	p.mu.Lock()
	defer p.mu.Unlock()
	return HttpResponse{
		StatusCode: 200,
		Body:       `{"status": "ok", "data": "fresh_primary_state"}`,
		ServedBy:   RegionFrankfurtPrimary,
		NewLSN:     p.lsn,
	}
}

func (p *PrimaryDB) ExecuteWrite(req HttpRequest) HttpResponse {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.lsn++
	return HttpResponse{
		StatusCode: 200,
		Body:       fmt.Sprintf(`{"status": "written", "lsn": %d}`, p.lsn),
		ServedBy:   RegionFrankfurtPrimary,
		NewLSN:     p.lsn,
	}
}

type ReadReplica struct {
	mu     sync.RWMutex
	region Region
	lsn    Lsn
}

func NewReadReplica(region Region, initialLSN Lsn) *ReadReplica {
	return &ReadReplica{region: region, lsn: initialLSN}
}

func (r *ReadReplica) UpdateLSN(newLSN Lsn) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.lsn = newLSN
}

func (r *ReadReplica) GetLSN() Lsn {
	r.mu.RLock()
	defer r.mu.RUnlock()
	return r.lsn
}

func (r *ReadReplica) ExecuteRead(req HttpRequest) HttpResponse {
	return HttpResponse{
		StatusCode: 200,
		Body:       `{"status": "ok", "data": "local_replica_state"}`,
		ServedBy:   r.region,
		NewLSN:     r.GetLSN(),
	}
}

type GeoRouter struct {
	primary  *PrimaryDB
	replicas map[Region]*ReadReplica
}

func NewGeoRouter(primary *PrimaryDB) *GeoRouter {
	return &GeoRouter{
		primary:  primary,
		replicas: make(map[Region]*ReadReplica),
	}
}

func (g *GeoRouter) RegisterReplica(region Region, replica *ReadReplica) {
	g.replicas[region] = replica
}

func (g *GeoRouter) RouteRequest(req HttpRequest) HttpResponse {
	if req.IsWrite {
		fmt.Printf("[Router] Write request -> Routing to Primary in %s\n", RegionFrankfurtPrimary)
		return g.primary.ExecuteWrite(req)
	}

	replica, exists := g.replicas[req.ClientRegion]
	if !exists {
		fmt.Printf("[Router] No local replica -> Fallback to Primary\n")
		return g.primary.ExecuteRead(req)
	}

	if req.RequiredLSN > 0 {
		replicaLSN := replica.GetLSN()
		if replicaLSN < req.RequiredLSN {
			fmt.Printf("[Router] RAW Check Failed! Client LSN: %d, Replica LSN: %d (Lag: %d ops) -> Fallback to Primary!\n",
				req.RequiredLSN, replicaLSN, req.RequiredLSN-replicaLSN)
			return g.primary.ExecuteRead(req)
		}
	}

	fmt.Printf("[Router] Local Replica LSN is fresh -> Serving locally in %s\n", req.ClientRegion)
	return replica.ExecuteRead(req)
}

func main() {
	primary := NewPrimaryDB(4000)
	tokyoReplica := NewReadReplica(RegionTokyoReplica, 4000)

	router := NewGeoRouter(primary)
	router.RegisterReplica(RegionTokyoReplica, tokyoReplica)

	fmt.Println("=== Крок 1: Запис у Токіо ===")
	wResp := router.RouteRequest(HttpRequest{
		Path:         "/api/v1/homes/h-101/devices/lamp",
		IsWrite:      true,
		ClientRegion: RegionTokyoReplica,
	})
	token := wResp.NewLSN
	fmt.Printf("Отримано токен X-LSN=%d\n\n", token)

	fmt.Println("=== Крок 2: Читання з відстаючої репліки ===")
	rResp1 := router.RouteRequest(HttpRequest{
		Path:         "/api/v1/homes/h-101/devices",
		IsWrite:      false,
		ClientRegion: RegionTokyoReplica,
		RequiredLSN:  token,
	})
	fmt.Printf("Відповідь оброблено: %s\n\n", rResp1.ServedBy)

	fmt.Println("=== Крок 3: Оновлення репліки ===")
	tokyoReplica.UpdateLSN(token)

	fmt.Println("=== Крок 4: Читання після синхронізації ===")
	rResp2 := router.RouteRequest(HttpRequest{
		Path:         "/api/v1/homes/h-101/devices",
		IsWrite:      false,
		ClientRegion: RegionTokyoReplica,
		RequiredLSN:  token,
	})
	fmt.Printf("Відповідь оброблено: %s\n", rResp2.ServedBy)
}
