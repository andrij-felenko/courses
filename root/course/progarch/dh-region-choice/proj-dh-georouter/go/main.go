package georouter

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

var (
	ErrRegionStale  = errors.New("fencing epoch is stale for target region")
	ErrHomeNotFound = errors.New("home_id not registered in global directory")
)

type RegionTarget struct {
	PrimaryRegion  string
	FailoverRegion string
	FencingEpoch   uint64
	IsReadOnly     bool
}

type GlobalDirectoryClient interface {
	LookupHomeRegion(ctx context.Context, homeID string) (*RegionTarget, error)
}

type GeoRouter struct {
	dirClient GlobalDirectoryClient
	cache     sync.Map
	ttl       time.Duration
	hits      uint64
	misses    uint64
}

type cacheEntry struct {
	target    *RegionTarget
	createdAt time.Time
}

func NewGeoRouter(client GlobalDirectoryClient, cacheTTL time.Duration) *GeoRouter {
	return &GeoRouter{
		dirClient: client,
		ttl:       cacheTTL,
	}
}

func (gr *GeoRouter) ResolveRegion(ctx context.Context, homeID string, clientEpoch uint64) (string, error) {
	if val, ok := gr.cache.Load(homeID); ok {
		entry := val.(*cacheEntry)
		if time.Since(entry.createdAt) < gr.ttl {
			atomic.AddUint64(&gr.hits, 1)
			return gr.validateAndRoute(entry.target, clientEpoch)
		}
	}

	atomic.AddUint64(&gr.misses, 1)

	target, err := gr.dirClient.LookupHomeRegion(ctx, homeID)
	if err != nil {
		return "", fmt.Errorf("global directory lookup failed: %w", err)
	}

	gr.cache.Store(homeID, &cacheEntry{
		target:    target,
		createdAt: time.Now(),
	})

	return gr.validateAndRoute(target, clientEpoch)
}

func (gr *GeoRouter) validateAndRoute(target *RegionTarget, clientEpoch uint64) (string, error) {
	if clientEpoch < target.FencingEpoch {
		return "", ErrRegionStale
	}
	return target.PrimaryRegion, nil
}
