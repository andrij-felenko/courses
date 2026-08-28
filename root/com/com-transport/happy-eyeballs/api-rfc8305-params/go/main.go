package main

import (
	"context"
	"net"
	"net/http"
	"time"
)

func createHappyEyeballsClient() *http.Client {
	dialer := &net.Dialer{
		Timeout:       10 * time.Second, /* Загальний ліміт часу на підключення */
		KeepAlive:     30 * time.Second,
		FallbackDelay: 250 * time.Millisecond, /* Інтервал старту паралельної goroutine */
	}

	transport := &http.Transport{
		DialContext:           dialer.DialContext,
		ForceAttemptHTTP2:     true,
		MaxIdleConns:          100,
		IdleConnTimeout:       90 * time.Second,
		TLSHandshakeTimeout:   10 * time.Second,
		ExpectContinueTimeout: 1 * time.Second,
	}

	return &http.Client{
		Transport: transport,
		Timeout:   15 * time.Second,
	}
}
