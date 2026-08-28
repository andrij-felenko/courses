package main

import (
	"context"
	"errors"
	"fmt"
	"math/rand"
	"sync"
	"time"
)

type BranchResponse struct {
	BranchID  string
	Data      string
	Latency   time.Duration
	WasHedged bool
}

type AggregationStatus string

const (
	StatusSuccess         AggregationStatus = "SUCCESS"
	StatusDegradedPartial AggregationStatus = "DEGRADED_PARTIAL"
	StatusCriticalFailure AggregationStatus = "TIMEOUT_CRITICAL_FAILURE"
)

type GatherResult struct {
	Status         AggregationStatus
	Responses      []BranchResponse
	FailedBranches []string
	TotalDuration  time.Duration
}

type ShardTask struct {
	BranchID   string
	PrimaryURL string
	BackupURL  string
	IsCritical bool
}

func executeSingleRPC(ctx context.Context, branchID, endpoint string, isHedged bool) (BranchResponse, error) {
	start := time.Now()
	// Симуляція мережевої затримки 10..120 мс
	delay := time.Duration(10+rand.Intn(110)) * time.Millisecond

	select {
	case <-time.After(delay):
		return BranchResponse{
			BranchID:  branchID,
			Data:      fmt.Sprintf("Payload from %s", endpoint),
			Latency:   time.Since(start),
			WasHedged: isHedged,
		}, nil
	case <-ctx.Done():
		return BranchResponse{}, ctx.Err()
	}
}

func executeBranchWithHedging(ctx context.Context, task ShardTask, hedgeDelay time.Duration) (BranchResponse, error) {
	branchCtx, cancelBranch := context.WithCancel(ctx)
	defer cancelBranch()

	resultCh := make(chan BranchResponse, 2)
	errCh := make(chan error, 2)

	// Первинний виклик
	go func() {
		res, err := executeSingleRPC(branchCtx, task.BranchID, task.PrimaryURL, false)
		if err == nil {
			select {
			case resultCh <- res:
				cancelBranch()
			case <-branchCtx.Done():
			}
		} else {
			errCh <- err
		}
	}()

	// Таймер геджування
	hedgeTimer := time.NewTimer(hedgeDelay)
	defer hedgeTimer.Stop()

	var hedgeStarted bool

	for {
		select {
		case res := <-resultCh:
			return res, nil
		case <-hedgeTimer.C:
			if !hedgeStarted {
				hedgeStarted = true
				go func() {
					res, err := executeSingleRPC(branchCtx, task.BranchID, task.BackupURL, true)
					if err == nil {
						select {
						case resultCh <- res:
							cancelBranch()
						case <-branchCtx.Done():
						}
					} else {
						errCh <- err
					}
				}()
			}
		case <-ctx.Done():
			return BranchResponse{}, ctx.Err()
		}
	}
}

func ScatterGatherExecute(tasks []ShardTask, hedgeDelay, globalDeadline time.Duration) GatherResult {
	start := time.Now()
	ctx, cancel := context.WithTimeout(context.Background(), globalDeadline)
	defer cancel()

	type branchOutcome struct {
		task ShardTask
		res  BranchResponse
		err  error
	}

	outcomes := make(chan branchOutcome, len(tasks))
	var wg sync.WaitGroup

	for _, t := range tasks {
		wg.Add(1)
		go func(task ShardTask) {
			defer wg.Done()
			res, err := executeBranchWithHedging(ctx, task, hedgeDelay)
			outcomes <- branchOutcome{task: task, res: res, err: err}
		}(t)
	}

	go func() {
		wg.Wait()
		close(outcomes)
	}()

	var result GatherResult
	hasCriticalFailure := false

	for out := range outcomes {
		if out.err == nil {
			result.Responses = append(result.Responses, out.res)
		} else {
			result.FailedBranches = append(result.FailedBranches, out.task.BranchID)
			if out.task.IsCritical {
				hasCriticalFailure = true
			}
		}
	}

	result.TotalDuration = time.Since(start)

	if hasCriticalFailure {
		result.Status = StatusCriticalFailure
	} else if len(result.FailedBranches) > 0 {
		result.Status = StatusDegradedPartial
	} else {
		result.Status = StatusSuccess
	}

	return result
}
