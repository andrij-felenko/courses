package topology

import (
	"errors"
	"time"
)

type LocalityTier uint8

const (
	TierSameHost LocalityTier = iota
	TierSameRack
	TierSameZone
	TierSameRegion
	TierCrossRegion
)

type NodeCoordinates struct {
	Region      string
	Zone        string
	Rack        string
	HostAddress string
	GossipPort  uint16
}

type PeerEndpoint struct {
	NodeID      string
	Coords      NodeCoordinates
	Tier        LocalityTier
	EwmaRTT     time.Duration
	IsSeedNode  bool
	IsSuspended bool
}

type RouterConfig struct {
	WeightSameRack    float64
	WeightSameZone    float64
	WeightCrossRegion float64
	Fanout            int
	MaxWANEgressBurst int
	ProbeInterval     time.Duration
	RTTTimeout        time.Duration
}

type RouterMetrics struct {
	TotalRounds            uint64
	IntraRackDispatches    uint64
	IntraZoneDispatches    uint64
	CrossRegionDispatches  uint64
	DegradedTierFallbacks  uint64
	DroppedWANBursts       uint64
}

var (
	ErrEmptyPeerPool          = errors.New("peer pool is empty")
	ErrNoReachablePeersInTier = errors.New("no reachable peers found in requested tier")
	ErrPeerNotFound           = errors.New("peer not found")
	ErrInvalidConfig          = errors.New("invalid configuration: weights must sum to 1.0")
)

type TopologyRouter interface {
	SetLocalCoordinates(coords NodeCoordinates) error
	UpsertPeer(peer PeerEndpoint) error
	RemovePeer(nodeID string) error
	ReportRTT(nodeID string, rtt time.Duration)
	SelectGossipTargets() ([]PeerEndpoint, error)
	SelectIndirectProxy(suspectNodeID string, excluded []string) (PeerEndpoint, error)
	GetPeerCount(tier LocalityTier) int
	GetMetrics() RouterMetrics
}
