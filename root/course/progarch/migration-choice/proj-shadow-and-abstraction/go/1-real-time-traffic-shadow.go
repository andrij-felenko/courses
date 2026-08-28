package shadow

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"log/slog"
	"net/http"
	"reflect"
	"time"
)

type DiffResult struct {
	Match        bool          `json:"match"`
	LatencyLegacy time.Duration `json:"latency_legacy_ms"`
	LatencyShadow time.Duration `json:"latency_shadow_ms"`
	MismatchPath string        `json:"mismatch_path,omitempty"`
}

type ShadowRouter struct {
	LegacyURL string
	ShadowURL string
	Client    *http.Client
	Logger    *slog.Logger
}

func NewShadowRouter(legacyURL, shadowURL string, logger *slog.Logger) *ShadowRouter {
	return &ShadowRouter{
		LegacyURL: legacyURL,
		ShadowURL: shadowURL,
		Client: &http.Client{
			Timeout: 2 * time.Second,
		},
		Logger: logger,
	}
}

func (sr *ShadowRouter) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	bodyBytes, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "bad request body", http.StatusBadRequest)
		return
	}
	r.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))

	// 1. Синхронний виклик до Legacy
	startLegacy := time.Now()
	legacyReq, _ := http.NewRequestWithContext(r.Context(), r.Method, sr.LegacyURL+r.URL.Path, bytes.NewBuffer(bodyBytes))
	copyHeaders(r.Header, legacyReq.Header)

	legacyResp, err := sr.Client.Do(legacyReq)
	latencyLegacy := time.Since(startLegacy)

	if err != nil {
		http.Error(w, "legacy upstream failure", http.StatusBadGateway)
		return
	}
	defer legacyResp.Body.Close()

	legacyBody, _ := io.ReadAll(legacyResp.Body)

	// 2. Асинхронний тіньовий виклик (Dark Launch)
	go func(reqBody []byte, headers http.Header, path string) {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel()

		shadowReq, _ := http.NewRequestWithContext(ctx, r.Method, sr.ShadowURL+path, bytes.NewBuffer(reqBody))
		copyHeaders(headers, shadowReq.Header)
		shadowReq.Header.Set("X-Dark-Launch-Shadow", "true")

		startShadow := time.Now()
		shadowResp, err := sr.Client.Do(shadowReq)
		latencyShadow := time.Since(startShadow)

		if err != nil {
			sr.Logger.Warn("shadow service unavailable", "error", err)
			return
		}
		defer shadowResp.Body.Close()

		shadowBody, _ := io.ReadAll(shadowResp.Body)

		// 3. Порівняння відповідей (Diff Engine)
		diff := comparePayloads(legacyBody, shadowBody, latencyLegacy, latencyShadow)
		if !diff.Match {
			sr.Logger.Error("shadow payload mismatch",
				"path", path,
				"mismatch", diff.MismatchPath,
				"latency_legacy_ms", diff.LatencyLegacy.Milliseconds(),
				"latency_shadow_ms", diff.LatencyShadow.Milliseconds(),
			)
		}
	}(bodyBytes, r.Header.Clone(), r.URL.Path)

	// 4. Повернення відповіді споживачеві від Legacy
	copyHeaders(legacyResp.Header, w.Header())
	w.WriteHeader(legacyResp.StatusCode)
	w.Write(legacyBody)
}

func comparePayloads(legacy, shadow []byte, tLeg, tShd time.Duration) DiffResult {
	var mapLegacy, mapShadow map[string]any
	if err := json.Unmarshal(legacy, &mapLegacy); err != nil {
		return DiffResult{Match: bytes.Equal(legacy, shadow), LatencyLegacy: tLeg, LatencyShadow: tShd}
	}
	if err := json.Unmarshal(shadow, &mapShadow); err != nil {
		return DiffResult{Match: false, LatencyLegacy: tLeg, LatencyShadow: tShd, MismatchPath: "shadow_json_parse_error"}
	}

	// Ігноруємо сольові/волатильні поля (наприклад, timestamp, request_id)
	delete(mapLegacy, "timestamp")
	delete(mapLegacy, "server_id")
	delete(mapShadow, "timestamp")
	delete(mapShadow, "server_id")

	match := reflect.DeepEqual(mapLegacy, mapShadow)
	path := ""
	if !match {
		path = "json_structure_or_values_differ"
	}
	return DiffResult{Match: match, LatencyLegacy: tLeg, LatencyShadow: tShd, MismatchPath: path}
}

func copyHeaders(src, dst http.Header) {
	for k, vv := range src {
		for _, v := range vv {
			dst.Add(k, v)
		}
	}
}
