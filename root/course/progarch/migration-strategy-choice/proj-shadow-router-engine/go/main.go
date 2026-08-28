// go
package main

import (
	"fmt"
	"log"
	"sync/atomic"
	"time"
)

type Request struct {
	RequestID string
	Payload   string
	UserID    int
}

type Response struct {
	StatusCode int
	Data       string
	LatencyMS  float64
}

type ServiceFunc func(req Request) (Response, error)

type ShadowRouter struct {
	primary           ServiceFunc
	shadow            ServiceFunc
	enableParallelRun bool
	totalProcessed    uint64
	diffCount         uint64
}

func NewShadowRouter(primary, shadow ServiceFunc, enableParallelRun bool) *ShadowRouter {
	return &ShadowRouter{
		primary:           primary,
		shadow:            shadow,
		enableParallelRun: enableParallelRun,
	}
}

func (r *ShadowRouter) Dispatch(req Request) (Response, error) {
	// 1. Первинне виконання для клієнта
	resp, err := r.primary(req)
	if err != nil {
		return resp, err
	}

	// 2. Асинхронне тіньове дублювання
	go func(primaryResp Response) {
		atomic.AddUint64(&r.totalProcessed, 1)

		shadowResp, err := r.shadow(req)
		if err != nil || shadowResp.StatusCode != primaryResp.StatusCode || shadowResp.Data != primaryResp.Data {
			if r.enableParallelRun {
				atomic.AddUint64(&r.diffCount, 1)
				log.Printf("[RECONCILER ALERT] ID %s: Primary='%s', Shadow='%s', Err=%v",
					req.RequestID, primaryResp.Data, shadowResp.Data, err)
			}
		}
	}(resp)

	return resp, nil
}
