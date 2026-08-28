package main

import (
	"bufio"
	"fmt"
	"net"
	"strings"
	"sync"
	"time"
)

// PeerEndpoint містить мережеву адресу виявленого сусіда
type PeerEndpoint struct {
	IP       string
	Port     int
	LastSeen time.Time
}

// PeerBusNode реалізує безброкерний вузол шини
type PeerBusNode struct {
	NodeID        string
	DataPort      int
	DiscoveryPort int
	Subscriptions []string

	peersMu sync.RWMutex
	peers   map[string]PeerEndpoint

	quit chan struct{}
}

func NewPeerBusNode(id string, dataPort, discoveryPort int) *PeerBusNode {
	return &PeerBusNode{
		NodeID:        id,
		DataPort:      dataPort,
		DiscoveryPort: discoveryPort,
		peers:         make(map[string]PeerEndpoint),
		quit:          make(chan struct{}),
	}
}

func (n *PeerBusNode) Subscribe(prefix string) {
	n.Subscriptions = append(n.Subscriptions, prefix)
}

func (n *PeerBusNode) Start() error {
	// 1. TCP Listener для прийому прямих повідомлень
	listener, err := net.Listen("tcp", fmt.Sprintf(":%d", n.DataPort))
	if err != nil {
		return err
	}

	// 2. UDP Сокет для розсилання та прийому маячків виявлення
	discAddr, err := net.ResolveUDPAddr("udp", fmt.Sprintf(":%d", n.DiscoveryPort))
	if err != nil {
		return err
	}
	discConn, err := net.ListenUDP("udp", discAddr)
	if err != nil {
		return err
	}

	go n.beaconLoop()
	go n.discoveryLoop(discConn)
	go n.acceptLoop(listener)

	return nil
}

func (n *PeerBusNode) Publish(topic, payload string) {
	msg := fmt.Sprintf("%s|%s\n", topic, payload)

	n.peersMu.RLock()
	defer n.peersMu.RUnlock()

	for _, peer := range n.peers {
		go func(addr string) {
			conn, err := net.DialTimeout("tcp", addr, 100*time.Millisecond)
			if err != nil {
				return
			}
			defer conn.Close()
			conn.Write([]byte(msg))
		}(fmt.Sprintf("%s:%d", peer.IP, peer.Port))
	}
}

func (n *PeerBusNode) beaconLoop() {
	bcastAddr, _ := net.ResolveUDPAddr("udp", fmt.Sprintf("255.255.255.255:%d", n.DiscoveryPort))
	conn, err := net.DialUDP("udp", nil, bcastAddr)
	if err != nil {
		return
	}
	defer conn.Close()

	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	msg := []byte(fmt.Sprintf("PEER:%s:%d", n.NodeID, n.DataPort))

	for {
		select {
		case <-n.quit:
			return
		case <-ticker.C:
			conn.Write(msg)
		}
	}
}

func (n *PeerBusNode) discoveryLoop(conn *net.UDPConn) {
	defer conn.Close()
	buf := make([]byte, 256)

	for {
		readN, remoteAddr, err := conn.ReadFrom(buf)
		if err != nil {
			return
		}
		raw := string(buf[:readN])
		if strings.HasPrefix(raw, "PEER:") {
			parts := strings.Split(raw, ":")
			if len(parts) == 3 {
				peerID := parts[1]
				var peerPort int
				fmt.Sscanf(parts[2], "%d", &peerPort)

				if peerID != n.NodeID {
					udpAddr := remoteAddr.(*net.UDPAddr)
					n.peersMu.Lock()
					n.peers[peerID] = PeerEndpoint{
						IP:       udpAddr.IP.String(),
						Port:     peerPort,
						LastSeen: time.Now(),
					}
					n.peersMu.Unlock()
				}
			}
		}
	}
}

func (n *PeerBusNode) acceptLoop(listener net.Listener) {
	defer listener.Close()
	for {
		conn, err := listener.Accept()
		if err != nil {
			return
		}
		go n.handleConnection(conn)
	}
}

func (n *PeerBusNode) handleConnection(conn net.Conn) {
	defer conn.Close()
	scanner := bufio.NewScanner(conn)
	if scanner.Scan() {
		line := scanner.Text()
		parts := strings.SplitN(line, "|", 2)
		if len(parts) == 2 {
			topic, payload := parts[0], parts[1]
			for _, sub := range n.Subscriptions {
				if strings.HasPrefix(topic, sub) {
					fmt.Printf("[%s RX] Тема: %s | Дані: %s\n", n.NodeID, topic, payload)
					break
				}
			}
		}
	}
}

func (n *PeerBusNode) Stop() {
	close(n.quit)
}
