package main

import (
	"fmt"
	"math"
)

func calculateHTTPReplicas(currentReplicas int, currentMetric, targetMetric, tolerance float64, minRep, maxRep int) int {
	ratio := currentMetric / targetMetric
	if math.Abs(ratio-1.0) <= tolerance {
		return currentReplicas
	}
	desired := int(math.Ceil(float64(currentReplicas) * ratio))
	if desired < minRep {
		return minRep
	}
	if desired > maxRep {
		return maxRep
	}
	return desired
}

func calculateQueueWorkers(queueLag int64, arrivalRateRPS, taskDurationSec, targetDrainTimeSec float64, maxWorkers int) int {
	if queueLag <= 0 && arrivalRateRPS <= 0.0 {
		return 0
	}
	totalTasks := float64(queueLag) + arrivalRateRPS*targetDrainTimeSec
	tasksPerWorker := targetDrainTimeSec / taskDurationSec
	desired := int(math.Ceil(totalTasks / tasksPerWorker))
	if desired > maxWorkers {
		return maxWorkers
	}
	return desired
}

func main() {
	httpPool := calculateHTTPReplicas(8, 88.0, 65.0, 0.10, 4, 20)
	workerPool := calculateQueueWorkers(45000, 250.0, 0.12, 60.0, 200)

	fmt.Printf("HTTP API target replicas: %d (очікується 11)\n", httpPool)
	fmt.Printf("Queue Workers target pool: %d (очікується 120)\n", workerPool)
}
