package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

type CanaryController struct {
	PrometheusURL   string
	GatewayAdminURL string
	Client          *http.Client
}

type PromResponse struct {
	Status string `json:"status"`
	Data   struct {
		Result []struct {
			Value []interface{} `json:"value"`
		} `json:"result"`
	} `json:"data"`
}

func NewCanaryController(promURL, gatewayURL string) *CanaryController {
	return &CanaryController{
		PrometheusURL:   promURL,
		GatewayAdminURL: gatewayURL,
		Client:          &http.Client{Timeout: 5 * time.Second},
	}
}

func (c *CanaryController) QueryScalarMetric(promql string) float64 {
	reqURL := fmt.Sprintf("%s/api/v1/query?query=%s", c.PrometheusURL, promql)
	resp, err := c.Client.Get(reqURL)
	if err != nil {
		fmt.Fprintf(os.Stderr, "[WARN] Помилка запиту Prometheus: %v\n", err)
		return 0.0
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var pResp PromResponse
	if err := json.Unmarshal(body, &pResp); err != nil {
		return 0.0
	}

	if len(pResp.Data.Result) == 0 || len(pResp.Data.Result[0].Value) < 2 {
		return 0.0
	}

	valStr, ok := pResp.Data.Result[0].Value[1].(string)
	if !ok {
		return 0.0
	}

	var val float64
	fmt.Sscanf(valStr, "%f", &val)
	return val
}

func (c *CanaryController) SetCanaryWeight(weight int) error {
	payload := map[string]interface{}{
		"routes": []map[string]interface{}{
			{"cluster": "dh-backend-baseline", "weight": 100 - weight},
			{"cluster": "dh-backend-canary", "weight": weight},
		},
	}
	data, _ := json.Marshal(payload)
	resp, err := c.Client.Post(c.GatewayAdminURL+"/v1/routes/weight", "application/json", bytes.NewBuffer(data))
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	fmt.Printf("[ROUTER] Встановлено вагу: База=%d%%, Канарка=%d%%\n", 100-weight, weight)
	return nil
}

func (c *CanaryController) EvaluateHealth() float64 {
	time.Sleep(5 * time.Minute)

	errBase := c.QueryScalarMetric("sum(rate(http_requests_total{version=\"v1.4\",status=~\"5..\"}[5m])) / (sum(rate(http_requests_total{version=\"v1.4\"}[5m])) + 0.001)")
	errCanary := c.QueryScalarMetric("sum(rate(http_requests_total{version=\"v1.5\",status=~\"5..\"}[5m])) / (sum(rate(http_requests_total{version=\"v1.5\"}[5m])) + 0.001)")

	p95Base := c.QueryScalarMetric("histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{version=\"v1.4\"}[5m])) by (le))")
	p95Canary := c.QueryScalarMetric("histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{version=\"v1.5\"}[5m])) by (le))")

	score := 100.0
	if errCanary-errBase > 0.005 {
		score -= 50.0
	}
	if p95Base > 0 && (p95Canary/p95Base) > 1.20 {
		score -= 30.0
	}
	return score
}

func (c *CanaryController) ExecuteRollout() bool {
	steps := []int{1, 10, 50, 100}
	for _, w := range steps {
		if err := c.SetCanaryWeight(w); err != nil {
			c.Rollback()
			return false
		}
		if w == 100 {
			return true
		}
		score := c.EvaluateHealth()
		if score < 75.0 {
			c.Rollback()
			return false
		}
	}
	return true
}

func (c *CanaryController) Rollback() {
	_ = c.SetCanaryWeight(0)
	fmt.Println("[ROLLBACK] Аварійне зняття трафіку завершено.")
}
