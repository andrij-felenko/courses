package main

import (
	"fmt"
	"math/rand"
	"time"
)

type Endpoint struct {
	ID         string
	Datacenter string
	Rack       string
}

type LocalityAwarePeerSelector struct {
	self     Endpoint
	pRack    float64
	pDC      float64
	pRemote  float64
	rnd      *rand.Rand
	sameRack []Endpoint
	sameDC   []Endpoint
	remoteDC []Endpoint
}

func NewLocalityAwarePeerSelector(self Endpoint, pRack, pDC, pRemote float64) *LocalityAwarePeerSelector {
	return &LocalityAwarePeerSelector{
		self:    self,
		pRack:   pRack,
		pDC:     pDC,
		pRemote: pRemote,
		rnd:     rand.New(rand.NewSource(time.Now().UnixNano())),
	}
}

func (s *LocalityAwarePeerSelector) UpdatePeerList(peers []Endpoint) {
	s.sameRack = nil
	s.sameDC = nil
	s.remoteDC = nil

	for _, peer := range peers {
		if peer.ID == s.self.ID {
			continue
		}
		if peer.Datacenter != s.self.Datacenter {
			s.remoteDC = append(s.remoteDC, peer)
		} else if peer.Rack != s.self.Rack {
			s.sameDC = append(s.sameDC, peer)
		} else {
			s.sameRack = append(s.sameRack, peer)
		}
	}
}

func (s *LocalityAwarePeerSelector) SelectTargets(fanout int) []Endpoint {
	selected := make([]Endpoint, 0, fanout)

	for i := 0; i < fanout; i++ {
		roll := s.rnd.Float64()

		switch {
		case roll < s.pRack && len(s.sameRack) > 0:
			selected = append(selected, s.sameRack[s.rnd.Intn(len(s.sameRack))])
		case roll < (s.pRack+s.pDC) && len(s.sameDC) > 0:
			selected = append(selected, s.sameDC[s.rnd.Intn(len(s.sameDC))])
		case len(s.remoteDC) > 0:
			selected = append(selected, s.remoteDC[s.rnd.Intn(len(s.remoteDC))])
		case len(s.sameDC) > 0:
			selected = append(selected, s.sameDC[s.rnd.Intn(len(s.sameDC))])
		case len(s.sameRack) > 0:
			selected = append(selected, s.sameRack[s.rnd.Intn(len(s.sameRack))])
		}
	}
	return selected
}

func main() {
	local := Endpoint{ID: "node-1", Datacenter: "us-east-1", Rack: "rack-A"}
	selector := NewLocalityAwarePeerSelector(local, 0.60, 0.35, 0.05)

	cluster := []Endpoint{
		{ID: "node-1", Datacenter: "us-east-1", Rack: "rack-A"},
		{ID: "node-2", Datacenter: "us-east-1", Rack: "rack-A"},
		{ID: "node-3", Datacenter: "us-east-1", Rack: "rack-B"},
		{ID: "node-4", Datacenter: "eu-central-1", Rack: "rack-C"},
	}

	selector.UpdatePeerList(cluster)
	targets := selector.SelectTargets(2)

	for _, t := range targets {
		fmt.Printf("Обрано партнера для пліток: %s (%s / %s)\n", t.ID, t.Datacenter, t.Rack)
	}
}
