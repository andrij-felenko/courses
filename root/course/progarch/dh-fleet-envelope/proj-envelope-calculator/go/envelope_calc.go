// envelope_calc.go - Go implementation of DH Capacity Calculator
package main

import (
	"fmt"
)

type FleetConfig struct {
	FleetSize          uint64
	TelemetryIntervalS float64
	PayloadBytes       uint32
	PeakMultiplier     float64
	ReconnectWindowS   float64
	ReconnectFraction  float64
	TLSResumptionRate  float64
}

type CapacityReport struct {
	MsgRateSteady    float64
	MsgRatePeak      float64
	RAMSocketsGB     float64
	NetBandwidthMbps float64
	CPUCryptoCores   float64
	CPUParseCores    float64
	IOPSRaw          uint32
	IOPSBatched      uint32
	StorageGBPerDay  float64
}

func CalculateCapacity(cfg FleetConfig) CapacityReport {
	steadyRate := float64(cfg.FleetSize) / cfg.TelemetryIntervalS
	peakRate := steadyRate * cfg.PeakMultiplier

	bytesPerSession := 48.0 * 1024.0
	ramSocketsGB := (float64(cfg.FleetSize) * bytesPerSession) / (1024.0 * 1024.0 * 1024.0)

	frameBytes := float64(cfg.PayloadBytes) + 107.0
	netBandwidthMbps := (peakRate * frameBytes * 8.0) / 1000000.0

	reconnectEvents := float64(cfg.FleetSize) * cfg.ReconnectFraction
	handshakesPerSec := reconnectEvents / cfg.ReconnectWindowS

	fullHandshakeMS := 0.60
	resumeHandshakeMS := 0.05

	avgHandshakeMS := (handshakesPerSec * (1.0 - cfg.TLSResumptionRate) * fullHandshakeMS) +
		(handshakesPerSec * cfg.TLSResumptionRate * resumeHandshakeMS)
	cpuCryptoCores := avgHandshakeMS / 1000.0

	cpuParseCores := peakRate * 0.000005

	return CapacityReport{
		MsgRateSteady:    steadyRate,
		MsgRatePeak:      peakRate,
		RAMSocketsGB:     ramSocketsGB,
		NetBandwidthMbps: netBandwidthMbps,
		CPUCryptoCores:   cpuCryptoCores,
		CPUParseCores:    cpuParseCores,
		IOPSRaw:          uint32(peakRate),
		IOPSBatched:      10,
		StorageGBPerDay:  (steadyRate * 86400.0 * float64(cfg.PayloadBytes)) / (1024.0 * 1024.0 * 1024.0),
	}
}

func main() {
	cfg := FleetConfig{
		FleetSize:          200000,
		TelemetryIntervalS: 30.0,
		PayloadBytes:       500,
		PeakMultiplier:     3.0,
		ReconnectWindowS:   60.0,
		ReconnectFraction:  0.50,
		TLSResumptionRate:  0.80,
	}

	rep := CalculateCapacity(cfg)
	fmt.Println("=== DH Fleet Capacity Report (200k devices) ===")
	fmt.Printf("Steady Msg Rate:   %.1f msg/s\n", rep.MsgRateSteady)
	fmt.Printf("Peak Msg Rate:     %.1f msg/s\n", rep.MsgRatePeak)
	fmt.Printf("RAM Sockets State: %.2f GB\n", rep.RAMSocketsGB)
	fmt.Printf("Peak Bandwidth:    %.2f Mbps\n", rep.NetBandwidthMbps)
	fmt.Printf("TLS Crypto Cores:  %.2f cores\n", rep.CPUCryptoCores)
	fmt.Printf("Event Parse Cores: %.2f cores\n", rep.CPUParseCores)
	fmt.Printf("Raw Disk IOPS:     %d IOPS\n", rep.IOPSRaw)
	fmt.Printf("Batched Disk IOPS: %d IOPS\n", rep.IOPSBatched)
	fmt.Printf("Storage Growth:    %.2f GB/day\n", rep.StorageGBPerDay)
}
