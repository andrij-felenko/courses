package main

import (
	"fmt"
	"math/rand"
)

type NodeLocation struct {
	DCID   int
	RackID int
	NodeID int
}

type SimulationConfig struct {
	Datacenters  int
	RacksPerDC   int
	NodesPerRack int
	Fanout       int
	PRack        float64
	PDC          float64
	PWAN         float64
	LatRackMs    float64
	LatDCMs      float64
	LatWANMs     float64
}

type SimulationResult struct {
	TotalRounds        int
	TotalPhysicalTimeMs float64
	TotalWANPackets    int64
}

func runSimulation(cfg SimulationConfig, hierarchical bool) SimulationResult {
	totalNodes := cfg.Datacenters * cfg.RacksPerDC * cfg.NodesPerRack
	nodes := make([]NodeLocation, totalNodes)
	dcNodes := make([][]int, cfg.Datacenters)
	rackNodes := make([][]int, cfg.Datacenters*cfg.RacksPerDC)

	id := 0
	for d := 0; d < cfg.Datacenters; d++ {
		for r := 0; r < cfg.RacksPerDC; r++ {
			globalRack := d*cfg.RacksPerDC + r
			for n := 0; n < cfg.NodesPerRack; n++ {
				nodes[id] = NodeLocation{DCID: d, RackID: r, NodeID: id}
				dcNodes[d] = append(dcNodes[d], id)
				rackNodes[globalRack] = append(rackNodes[globalRack], id)
				id++
			}
		}
	}

	infected := make([]bool, totalNodes)
	infectionTime := make([]float64, totalNodes)
	infected[0] = true
	infectedCount := 1

	round := 0
	var wanPackets int64

	r := rand.New(rand.NewSource(1337))

	for infectedCount < totalNodes && round < 1000 {
		round++
		type arrival struct {
			target int
			time   float64
		}
		var newlyInfected []arrival

		for srcID := 0; srcID < totalNodes; srcID++ {
			if !infected[srcID] {
				continue
			}

			for f := 0; f < cfg.Fanout; f++ {
				var targetID int
				src := nodes[srcID]

				if !hierarchical {
					pick := r.Intn(totalNodes - 1)
					if pick >= srcID {
						pick++
					}
					targetID = pick
				} else {
					roll := r.Float64()
					globalRack := src.DCID*cfg.RacksPerDC + src.RackID
					if roll < cfg.PRack {
						pool := rackNodes[globalRack]
						targetID = pool[r.Intn(len(pool))]
					} else if roll < cfg.PRack+cfg.PDC {
						pool := dcNodes[src.DCID]
						targetID = pool[r.Intn(len(pool))]
					} else {
						remDC := r.Intn(cfg.Datacenters - 1)
						if remDC >= src.DCID {
							remDC++
						}
						pool := dcNodes[remDC]
						targetID = pool[r.Intn(len(pool))]
					}
				}

				if targetID == srcID {
					continue
				}

				dst := nodes[targetID]
				delay := cfg.LatRackMs
				if src.DCID != dst.DCID {
					wanPackets++
					delay = cfg.LatWANMs
				} else if src.RackID != dst.RackID {
					delay = cfg.LatDCMs
				}

				arrTime := infectionTime[srcID] + delay
				newlyInfected = append(newlyInfected, arrival{target: targetID, time: arrTime})
			}
		}

		for _, arr := range newlyInfected {
			if !infected[arr.target] {
				infected[arr.target] = true
				infectionTime[arr.target] = arr.time
				infectedCount++
			} else if arr.time < infectionTime[arr.target] {
				infectionTime[arr.target] = arr.time
			}
		}
	}

	maxTime := 0.0
	for _, t := range infectionTime {
		if t > maxTime {
			maxTime = t
		}
	}

	return SimulationResult{
		TotalRounds:         round,
		TotalPhysicalTimeMs: maxTime,
		TotalWANPackets:     wanPackets,
	}
}

func main() {
	cfg := SimulationConfig{
		Datacenters:  3,
		RacksPerDC:   4,
		NodesPerRack: 50,
		Fanout:       3,
		PRack:        0.60,
		PDC:          0.35,
		PWAN:         0.05,
		LatRackMs:    0.1,
		LatDCMs:      0.8,
		LatWANMs:     80.0,
	}

	flat := runSimulation(cfg, false)
	hier := runSimulation(cfg, true)

	fmt.Println("===============================================================")
	fmt.Println(" РЕЗУЛЬТАТИ ПОРІВНЯННЯ ТОПОЛОГІЙ GOSSIP (600 ВУЗЛІВ, 3 ДЦ)")
	fmt.Println("===============================================================")
	fmt.Printf("Flat Uniform:   %d раундів, %.2f ms, %d WAN-пакетів\n", flat.TotalRounds, flat.TotalPhysicalTimeMs, flat.TotalWANPackets)
	fmt.Printf("Hierarchical:   %d раундів, %.2f ms, %d WAN-пакетів\n", hier.TotalRounds, hier.TotalPhysicalTimeMs, hier.TotalWANPackets)
	saving := 100.0 * (1.0 - float64(hier.TotalWANPackets)/float64(flat.TotalWANPackets))
	fmt.Printf("Скорочення навантаження на канали WAN: %.2f%%\n", saving)
}
