package pipeline

import (
	"context"
	"math"
	"runtime/metrics"
	"sync/atomic"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// Command — та сама команда пристрою, що й на ендпоінті: обмежена множина імен.
type Command struct {
	Name string // "heat" | "set_target" | "reboot" — саме це піде в мітку
	Arg  int
}

// Job — команда плюс МОНОТОННИЙ штамп постановки в чергу.
type Job struct {
	Cmd      Command
	enqueued time.Time // час у системі рахуємо ВІД цієї миті, не від пробудження робітника
}

// ── Прилади конкурентності. Мітки — ЛИШЕ обмежені (тип команди), нічого більше. ──
var (
	queueDepth = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "dh_pipeline_queue_depth",
		Help: "Задачі, що чекають у буфері перед пулом просто зараз (насиченість).",
	})
	poolBusy = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "dh_pipeline_pool_busy",
		Help: "Робітники, зайняті обробкою просто зараз.",
	})
	poolSize = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "dh_pipeline_pool_size",
		Help: "Усього робітників у пулі (стеля на L).",
	})
	inflight = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "dh_pipeline_inflight",
		Help: "Задачі в системі: у черзі плюс в обробці — це L.",
	})
	// W: від ENQUEUE до завершення (черга + обслуга), а не сама обслуга.
	sojourn = promauto.NewHistogramVec(prometheus.HistogramOpts{
		Name:    "dh_pipeline_sojourn_seconds",
		Help:    "Час у системі від постановки в чергу до завершення.",
		Buckets: []float64{0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5},
	}, []string{"command"})
	// Суперництво самого рантайму — не наш код, а планувальник і замки.
	schedLatencyP99 = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "dh_pipeline_sched_latency_p99_seconds",
		Help: "p99 лагу планувальника: скільки горутина була готова, поки її пустили на ядро.",
	})
	mutexWaitTotal = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "dh_pipeline_mutex_wait_seconds_total",
		Help: "Сумарний час, який горутини провели, чекаючи на замках.",
	})
	// Сторож: наскільки виміряне L розходиться з передбаченим λ·W.
	llResidual = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "dh_pipeline_littles_residual",
		Help: "|L − λ·W| / L: розбіжність приладів проти закону Літтла.",
	})
)
