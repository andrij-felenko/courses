// controller.go — Go-реалізація контролера заморозки релізів
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"time"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

const (
	sloTarget      = 0.999
	windowSeconds  = 30 * 24 * 3600
	configMapName  = "dh-release-policy"
	namespace      = "dh-system"
)

type PromResponse struct {
	Data struct {
		Result []struct {
			Value []interface{} `json:"value"`
		} `json:"result"`
	} `json:"data"`
}

func queryPrometheus(promURL, query string) (float64, error) {
	u := fmt.Sprintf("%s/api/v1/query?query=%s", promURL, url.QueryEscape(query))
	resp, err := http.Get(u)
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()

	var pr PromResponse
	if err := json.NewDecoder(resp.Body).Decode(&pr); err != nil {
		return 0, err
	}
	if len(pr.Data.Result) == 0 || len(pr.Data.Result[0].Value) < 2 {
		return 0, nil
	}
	strVal, ok := pr.Data.Result[0].Value[1].(string)
	if !ok {
		return 0, fmt.Errorf("invalid value format")
	}
	return strconv.ParseFloat(strVal, 64)
}

func main() {
	promURL := os.Getenv("PROMETHEUS_URL")
	if promURL == "" {
		promURL = "http://prometheus-k8s.monitoring:9090"
	}

	config, err := rest.InClusterConfig()
	if err != nil {
		config, err = clientcmd.BuildConfigFromFlags("", os.Getenv("KUBECONFIG"))
		if err != nil {
			log.Fatalf("Error loading kubeconfig: %v", err)
		}
	}
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		log.Fatalf("Error creating k8s client: %v", err)
	}

	for {
		qTotal := fmt.Sprintf(`sum(increase(dh_http_server_request_duration_seconds_count{job="dh-lock-service"}[%ds]))`, windowSeconds)
		qErrors := fmt.Sprintf(`sum(increase(dh_http_server_request_duration_seconds_count{job="dh-lock-service", http_status_code!="200"}[%ds]))`, windowSeconds)

		total, err := queryPrometheus(promURL, qTotal)
		if err != nil {
			log.Printf("Error querying total: %v", err)
			time.Sleep(60 * time.Second)
			continue
		}
		if total == 0 {
			time.Sleep(60 * time.Second)
			continue
		}

		errors, err := queryPrometheus(promURL, qErrors)
		if err != nil {
			log.Printf("Error querying errors: %v", err)
			time.Sleep(60 * time.Second)
			continue
		}

		allowedErrors := total * (1.0 - sloTarget)
		remainingBudget := ((allowedErrors - errors) / allowedErrors) * 100.0
		freeze := remainingBudget <= 0.0

		log.Printf("SLI Checked | Remaining Budget: %.2f%% | Freeze Needed: %v", remainingBudget, freeze)

		ctx := context.Background()
		cm, err := clientset.CoreV1().ConfigMaps(namespace).Get(ctx, configMapName, metav1.GetOptions{})
		if err == nil {
			currentVal := cm.Data["RELEASE_FREEZE_ENABLED"]
			newVal := "false"
			if freeze {
				newVal = "true"
			}
			if currentVal != newVal {
				cm.Data["RELEASE_FREEZE_ENABLED"] = newVal
				_, err = clientset.CoreV1().ConfigMaps(namespace).Update(ctx, cm, metav1.UpdateOptions{})
				if err != nil {
					log.Printf("Error updating ConfigMap: %v", err)
				} else {
					log.Printf("ConfigMap updated: RELEASE_FREEZE_ENABLED = %s", newVal)
				}
			}
		}
		time.Sleep(60 * time.Second)
	}
}
