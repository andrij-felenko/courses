// Go: Налаштування gRPC Сервера з параметрами Keepalive та Graceful GOAWAY
package main

import (
	"fmt"
	"net"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"
)

func NewIngestServer(port int) (*grpc.Server, net.Listener, error) {
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
	if err != nil {
		return nil, nil, err
	}

	// Серверні параметри ротації та збереження з'єднань
	kaParams := keepalive.ServerParameters{
		MaxConnectionAge:      1 * time.Hour,  // Через 1 годину надсилається HTTP/2 GOAWAY
		MaxConnectionAgeGrace: 30 * time.Second, // 30 секунд на завершення поточних RPC
		Time:                  30 * time.Second, // PING інтервал перевірки сокета
		Timeout:               10 * time.Second, // Таймаут очікування PING ACK
	}

	srv := grpc.NewServer(
		grpc.KeepaliveParams(kaParams),
	)

	return srv, lis, nil
}
