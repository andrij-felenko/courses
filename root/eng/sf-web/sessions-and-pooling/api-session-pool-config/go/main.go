package main

import (
	"net"
	"net/http"
	"time"
)

func createOptimizedClient() *http.Client {
	transport := &http.Transport{
		Proxy: http.ProxyFromEnvironment,
		DialContext: (&net.Dialer{
			Timeout:   5 * time.Second,  // Граничний час на TCP Connect
			KeepAlive: 30 * time.Second, // Інтервал TCP Keep-Alive зондів (L4)
		}).DialContext,
		ForceAttemptHTTP2:     true,
		MaxIdleConns:          100,              // Загальний ліміт сокетів у стані IDLE
		MaxIdleConnsPerHost:   20,               // Вільних сокетів для одного хоста
		MaxConnsPerHost:       50,               // Жорсткий ліміт активних+вільних (0 = безлім)
		IdleConnTimeout:       90 * time.Second, // Час життя неактивного сокета в пулі
		TLSHandshakeTimeout:   5 * time.Second,  // Тайм-аут на TLS
		ResponseHeaderTimeout: 10 * time.Second, // Очікування першого байта заголовків
		DisableKeepAlives:     false,            // false = тримати сокети відкритими
	}

	return &http.Client{
		Transport: transport,
		Timeout:   30 * time.Second, // Загальний тайм-аут на весь життєвий цикл запиту
	}
}
