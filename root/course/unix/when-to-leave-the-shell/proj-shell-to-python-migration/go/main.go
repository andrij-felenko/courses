package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"sync"
	"syscall"
	"time"
)

// NodeMetric структура метрик окремого вузла
type NodeMetric struct {
	Node         string  `json:"node"`
	CPUUsage     float64 `json:"cpu_usage"`
	MemoryFreeMB float64 `json:"memory_free_mb"`
	Status       string  `json:"status"`
	Error        string  `json:"error,omitempty"`
}

// ClusterReport структура фінального звіту
type ClusterReport struct {
	Timestamp          string       `json:"timestamp"`
	NodesPolled        int          `json:"nodes_polled"`
	NodesSuccessful    int          `json:"nodes_successful"`
	AverageCPUUsage    float64      `json:"average_cpu_usage"`
	TotalMemoryFreeMB  float64      `json:"total_memory_free_mb"`
	Nodes              []NodeMetric `json:"nodes"`
}

func fetchMetrics(ctx context.Context, client *http.Client, node string) NodeMetric {
	url := fmt.Sprintf("http://%s:9100/metrics.json", node)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return NodeMetric{Node: node, Status: "ERROR", Error: err.Error()}
	}

	resp, err := client.Do(req)
	if err != nil {
		return NodeMetric{Node: node, Status: "ERROR", Error: err.Error()}
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return NodeMetric{Node: node, Status: "ERROR", Error: fmt.Sprintf("HTTP %d", resp.StatusCode)}
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return NodeMetric{Node: node, Status: "ERROR", Error: err.Error()}
	}

	var raw struct {
		CPUUsage     float64 `json:"cpu_usage"`
		MemoryFreeMB float64 `json:"memory_free_mb"`
		Status       string  `json:"status"`
	}
	if err := json.Unmarshal(body, &raw); err != nil {
		return NodeMetric{Node: node, Status: "ERROR", Error: err.Error()}
	}

	return NodeMetric{
		Node:         node,
		CPUUsage:     raw.CPUUsage,
		MemoryFreeMB: raw.MemoryFreeMB,
		Status:       raw.Status,
	}
}

func atomicWriteJSON(path string, report ClusterReport) error {
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}

	tmpFile, err := os.CreateTemp(dir, "report-*.tmp")
	if err != nil {
		return err
	}
	tmpName := tmpFile.Name()
	defer os.Remove(tmpName)

	encoder := json.NewEncoder(tmpFile)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(report); err != nil {
		tmpFile.Close()
		return err
	}

	if err := tmpFile.Sync(); err != nil {
		tmpFile.Close()
		return err
	}
	tmpFile.Close()

	return os.Rename(tmpName, path)
}

func main() {
	configPath := flag.String("config", "/etc/cluster/nodes.conf", "Шлях до списку вузлів")
	outPath := flag.String("out", "/var/log/cluster_reports/report.json", "Шлях до результуючого файлу")
	workers := flag.Int("workers", 64, "Кількість паралельних горутин")
	flag.Parse()

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	content, err := os.ReadFile(*configPath)
	if err != nil {
		log.Fatalf("Помилка читання конфігурації: %v", err)
	}

	var nodes []string
	for _, line := range strings.Split(string(content), "\n") {
		line = strings.TrimSpace(line)
		if line != "" && !strings.HasPrefix(line, "#") {
			parts := strings.Fields(line)
			if len(parts) > 0 {
				nodes = append(nodes, parts[0])
			}
		}
	}

	httpClient := &http.Client{
		Timeout: 2 * time.Second,
		Transport: &http.Transport{
			MaxIdleConns:        *workers,
			MaxIdleConnsPerHost: 4,
			IdleConnTimeout:     30 * time.Second,
		},
	}

	nodeChan := make(chan string, len(nodes))
	for _, n := range nodes {
		nodeChan <- n
	}
	close(nodeChan)

	resultChan := make(chan NodeMetric, len(nodes))
	var wg sync.WaitGroup

	for i := 0; i < *workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for node := range nodeChan {
				select {
				case <-ctx.Done():
					return
				default:
					resultChan <- fetchMetrics(ctx, httpClient, node)
				}
			}
		}()
	}

	wg.Wait()
	close(resultChan)

	var report ClusterReport
	report.Timestamp = time.Now().UTC().Format(time.RFC3339)
	report.NodesPolled = len(nodes)

	var totalCPU, totalMem float64
	for m := range resultChan {
		report.Nodes = append(report.Nodes, m)
		if m.Status == "OK" {
			totalCPU += m.CPUUsage
			totalMem += m.MemoryFreeMB
			report.NodesSuccessful++
		}
	}

	if report.NodesSuccessful > 0 {
		report.AverageCPUUsage = totalCPU / float64(report.NodesSuccessful)
		report.TotalMemoryFreeMB = totalMem
	}

	if err := atomicWriteJSON(*outPath, report); err != nil {
		log.Fatalf("Не вдалося зберегти звіт: %v", err)
	}
	log.Printf("Збір завершено. Опитано: %d, успішно: %d. Звіт: %s", report.NodesPolled, report.NodesSuccessful, *outPath)
}
