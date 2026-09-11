package boundarybench

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"sync"
)

// UnixSocketTransport реалізує локальний міжпроцесний зв'язок (IPC)
// через Unix Domain Socket із передачею length-prefixed JSON.
type UnixSocketTransport struct {
	listener net.Listener
	sockPath string
	conn     net.Conn
	mu       sync.Mutex
	quit     chan struct{}
}

// NewUnixSocketTransport запускає локальний сокет-сервер та створює клієнтське з'єднання.
func NewUnixSocketTransport() (*UnixSocketTransport, error) {
	tmpDir, err := os.MkdirTemp("", "uds_bench_*")
	if err != nil {
		return nil, err
	}
	sockPath := filepath.Join(tmpDir, "server.sock")

	_ = os.Remove(sockPath)

	listener, err := net.Listen("unix", sockPath)
	if err != nil {
		listener, err = net.Listen("tcp", "127.0.0.1:0")
		if err != nil {
			return nil, err
		}
	}

	transport := &UnixSocketTransport{
		listener: listener,
		sockPath: sockPath,
		quit:     make(chan struct{}),
	}

	go func() {
		for {
			conn, err := listener.Accept()
			if err != nil {
				return
			}
			go transport.handleConnection(conn)
		}
	}()

	clientConn, err := net.Dial(listener.Addr().Network(), listener.Addr().String())
	if err != nil {
		_ = listener.Close()
		return nil, err
	}
	transport.conn = clientConn

	return transport, nil
}

func (ust *UnixSocketTransport) handleConnection(conn net.Conn) {
	defer conn.Close()
	var lenBuf [4]byte
	for {
		if _, err := io.ReadFull(conn, lenBuf[:]); err != nil {
			return
		}
		msgLen := binary.BigEndian.Uint32(lenBuf[:])
		payload := make([]byte, msgLen)
		if _, err := io.ReadFull(conn, payload); err != nil {
			return
		}

		var order Order
		_ = json.Unmarshal(payload, &order)
		resp, _ := ValidateOrder(&order)
		respBytes, _ := json.Marshal(resp)

		binary.BigEndian.PutUint32(lenBuf[:], uint32(len(respBytes)))
		if _, err := conn.Write(lenBuf[:]); err != nil {
			return
		}
		if _, err := conn.Write(respBytes); err != nil {
			return
		}
	}
}

// Validate передає замовлення через сокет і повертає відповідь.
func (ust *UnixSocketTransport) Validate(order *Order) (ValidationResponse, error) {
	ust.mu.Lock()
	defer ust.mu.Unlock()

	data, err := json.Marshal(order)
	if err != nil {
		return ValidationResponse{}, err
	}

	var lenBuf [4]byte
	binary.BigEndian.PutUint32(lenBuf[:], uint32(len(data)))
	if _, err := ust.conn.Write(lenBuf[:]); err != nil {
		return ValidationResponse{}, err
	}
	if _, err := ust.conn.Write(data); err != nil {
		return ValidationResponse{}, err
	}

	if _, err := io.ReadFull(ust.conn, lenBuf[:]); err != nil {
		return ValidationResponse{}, err
	}
	respLen := binary.BigEndian.Uint32(lenBuf[:])
	respBuf := make([]byte, respLen)
	if _, err := io.ReadFull(ust.conn, respBuf); err != nil {
		return ValidationResponse{}, err
	}

	var resp ValidationResponse
	if err := json.Unmarshal(respBuf, &resp); err != nil {
		return ValidationResponse{}, err
	}

	return resp, nil
}

// Close закриває з'єднання, зупиняє слухач та видаляє файл сокета.
func (ust *UnixSocketTransport) Close() error {
	ust.mu.Lock()
	defer ust.mu.Unlock()

	if ust.conn != nil {
		_ = ust.conn.Close()
	}
	err := ust.listener.Close()
	if ust.sockPath != "" {
		_ = os.Remove(ust.sockPath)
		_ = os.Remove(filepath.Dir(ust.sockPath))
	}
	return err
}

// HTTPJSONTransport реалізує мережеву взаємодію через класичний REST/HTTP-1.1
// стек із серіалізацією структури в JSON.
type HTTPJSONTransport struct {
	server *httptest.Server
	client *http.Client
}

// NewHTTPJSONTransport запускає локальний HTTP-сервер на базі httptest.
func NewHTTPJSONTransport() *HTTPJSONTransport {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var order Order
		if err := json.NewDecoder(r.Body).Decode(&order); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		resp, _ := ValidateOrder(&order)
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(resp)
	})

	server := httptest.NewServer(handler)
	client := server.Client()

	return &HTTPJSONTransport{
		server: server,
		client: client,
	}
}

// Validate виконує POST-запит із JSON-тілом до HTTP-сервера.
func (hjt *HTTPJSONTransport) Validate(order *Order) (ValidationResponse, error) {
	body, err := json.Marshal(order)
	if err != nil {
		return ValidationResponse{}, err
	}

	resp, err := hjt.client.Post(hjt.server.URL, "application/json", bytes.NewReader(body))
	if err != nil {
		return ValidationResponse{}, err
	}
	defer resp.Body.Close()

	var valResp ValidationResponse
	if err := json.NewDecoder(resp.Body).Decode(&valResp); err != nil {
		return ValidationResponse{}, err
	}

	return valResp, nil
}

// Close вивільняє ресурси HTTP-сервера та закриває пул з'єднань клієнта.
func (hjt *HTTPJSONTransport) Close() {
	hjt.server.Close()
	hjt.client.CloseIdleConnections()
}

// --- Реалізація Protobuf-серіалізації та gRPC фреймінгу ---

func appendVarint(buf []byte, v uint64) []byte {
	for v >= 0x80 {
		buf = append(buf, byte(v)|0x80)
		v >>= 7
	}
	return append(buf, byte(v))
}

func readVarint(buf []byte) (uint64, int, error) {
	var v uint64
	var shift uint
	for i, b := range buf {
		v |= uint64(b&0x7f) << shift
		if b < 0x80 {
			return v, i + 1, nil
		}
		shift += 7
		if shift >= 64 {
			return 0, 0, errors.New("переповнення varint")
		}
	}
	return 0, 0, io.ErrUnexpectedEOF
}

func encodeProtobufItem(item OrderItem) []byte {
	var buf []byte
	if item.SKU != "" {
		buf = append(buf, 0x0A)
		buf = appendVarint(buf, uint64(len(item.SKU)))
		buf = append(buf, item.SKU...)
	}
	if item.Quantity != 0 {
		buf = append(buf, 0x10)
		buf = appendVarint(buf, uint64(item.Quantity))
	}
	if item.Price != 0 {
		buf = append(buf, 0x18)
		buf = appendVarint(buf, uint64(item.Price))
	}
	return buf
}

func decodeProtobufItem(data []byte) (OrderItem, error) {
	var item OrderItem
	offset := 0
	for offset < len(data) {
		tag, n, err := readVarint(data[offset:])
		if err != nil {
			return item, err
		}
		offset += n
		fieldNum := tag >> 3
		wireType := tag & 0x07

		switch wireType {
		case 0:
			val, n, err := readVarint(data[offset:])
			if err != nil {
				return item, err
			}
			offset += n
			switch fieldNum {
			case 2:
				item.Quantity = int(val)
			case 3:
				item.Price = int64(val)
			}
		case 2:
			l, n, err := readVarint(data[offset:])
			if err != nil {
				return item, err
			}
			offset += n
			if offset+int(l) > len(data) {
				return item, io.ErrUnexpectedEOF
			}
			if fieldNum == 1 {
				item.SKU = string(data[offset : offset+int(l)])
			}
			offset += int(l)
		default:
			return item, fmt.Errorf("невідомий wire type: %d", wireType)
		}
	}
	return item, nil
}

func encodeProtobufOrder(order *Order) []byte {
	var buf []byte
	if order.ID != "" {
		buf = append(buf, 0x0A)
		buf = appendVarint(buf, uint64(len(order.ID)))
		buf = append(buf, order.ID...)
	}
	if order.CustomerID != "" {
		buf = append(buf, 0x12)
		buf = appendVarint(buf, uint64(len(order.CustomerID)))
		buf = append(buf, order.CustomerID...)
	}
	for _, it := range order.Items {
		itemBytes := encodeProtobufItem(it)
		buf = append(buf, 0x1A)
		buf = appendVarint(buf, uint64(len(itemBytes)))
		buf = append(buf, itemBytes...)
	}
	if order.Total != 0 {
		buf = append(buf, 0x20)
		buf = appendVarint(buf, uint64(order.Total))
	}
	return buf
}

func decodeProtobufOrder(data []byte) (*Order, error) {
	var ord Order
	offset := 0
	for offset < len(data) {
		tag, n, err := readVarint(data[offset:])
		if err != nil {
			return nil, err
		}
		offset += n
		fieldNum := tag >> 3
		wireType := tag & 0x07

		switch wireType {
		case 0:
			val, n, err := readVarint(data[offset:])
			if err != nil {
				return nil, err
			}
			offset += n
			if fieldNum == 4 {
				ord.Total = int64(val)
			}
		case 2:
			l, n, err := readVarint(data[offset:])
			if err != nil {
				return nil, err
			}
			offset += n
			if offset+int(l) > len(data) {
				return nil, io.ErrUnexpectedEOF
			}
			bytesVal := data[offset : offset+int(l)]
			offset += int(l)

			switch fieldNum {
			case 1:
				ord.ID = string(bytesVal)
			case 2:
				ord.CustomerID = string(bytesVal)
			case 3:
				item, err := decodeProtobufItem(bytesVal)
				if err != nil {
					return nil, err
				}
				ord.Items = append(ord.Items, item)
			}
		default:
			return nil, fmt.Errorf("невідомий wire type: %d", wireType)
		}
	}
	return &ord, nil
}

func encodeProtobufResponse(resp ValidationResponse) []byte {
	var buf []byte
	buf = append(buf, 0x08)
	if resp.Valid {
		buf = append(buf, 1)
	} else {
		buf = append(buf, 0)
	}
	if resp.Error != "" {
		buf = append(buf, 0x12)
		buf = appendVarint(buf, uint64(len(resp.Error)))
		buf = append(buf, resp.Error...)
	}
	return buf
}

func decodeProtobufResponse(data []byte) (ValidationResponse, error) {
	var resp ValidationResponse
	offset := 0
	for offset < len(data) {
		tag, n, err := readVarint(data[offset:])
		if err != nil {
			return resp, err
		}
		offset += n
		fieldNum := tag >> 3
		wireType := tag & 0x07

		switch wireType {
		case 0:
			val, n, err := readVarint(data[offset:])
			if err != nil {
				return resp, err
			}
			offset += n
			if fieldNum == 1 {
				resp.Valid = (val != 0)
			}
		case 2:
			l, n, err := readVarint(data[offset:])
			if err != nil {
				return resp, err
			}
			offset += n
			if offset+int(l) > len(data) {
				return resp, io.ErrUnexpectedEOF
			}
			if fieldNum == 2 {
				resp.Error = string(data[offset : offset+int(l)])
			}
			offset += int(l)
		default:
			return resp, fmt.Errorf("невідомий wire type: %d", wireType)
		}
	}
	return resp, nil
}

func writeGRPCFrame(w io.Writer, payload []byte) error {
	var header [5]byte
	header[0] = 0
	binary.BigEndian.PutUint32(header[1:5], uint32(len(payload)))
	if _, err := w.Write(header[:]); err != nil {
		return err
	}
	_, err := w.Write(payload)
	return err
}

func readGRPCFrame(r io.Reader) ([]byte, error) {
	var header [5]byte
	if _, err := io.ReadFull(r, header[:]); err != nil {
		return nil, err
	}
	length := binary.BigEndian.Uint32(header[1:5])
	payload := make([]byte, length)
	if _, err := io.ReadFull(r, payload); err != nil {
		return nil, err
	}
	return payload, nil
}

// GRPCTransport реалізує клієнт-серверний зв'язок за протоколом gRPC/Protobuf
// із двійковою серіалізацією та стандартизованим 5-байтовим префіксом кадру.
type GRPCTransport struct {
	listener net.Listener
	conn     net.Conn
	mu       sync.Mutex
}

// NewGRPCTransport запускає локальний TCP RPC-сервер та підключає клієнта.
func NewGRPCTransport() (*GRPCTransport, error) {
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		return nil, err
	}

	gt := &GRPCTransport{
		listener: listener,
	}

	go func() {
		for {
			c, err := listener.Accept()
			if err != nil {
				return
			}
			go gt.handleConnection(c)
		}
	}()

	clientConn, err := net.Dial("tcp", listener.Addr().String())
	if err != nil {
		_ = listener.Close()
		return nil, err
	}
	gt.conn = clientConn

	return gt, nil
}

func (gt *GRPCTransport) handleConnection(conn net.Conn) {
	defer conn.Close()
	for {
		payload, err := readGRPCFrame(conn)
		if err != nil {
			return
		}

		order, err := decodeProtobufOrder(payload)
		if err != nil {
			return
		}

		resp, _ := ValidateOrder(order)
		respPayload := encodeProtobufResponse(resp)

		if err := writeGRPCFrame(conn, respPayload); err != nil {
			return
		}
	}
}

// Validate передає замовлення у форматі Protobuf через gRPC фреймінг.
func (gt *GRPCTransport) Validate(order *Order) (ValidationResponse, error) {
	gt.mu.Lock()
	defer gt.mu.Unlock()

	payload := encodeProtobufOrder(order)
	if err := writeGRPCFrame(gt.conn, payload); err != nil {
		return ValidationResponse{}, err
	}

	respPayload, err := readGRPCFrame(gt.conn)
	if err != nil {
		return ValidationResponse{}, err
	}

	return decodeProtobufResponse(respPayload)
}

// Close закриває з'єднання та зупиняє gRPC TCP-сервер.
func (gt *GRPCTransport) Close() error {
	gt.mu.Lock()
	defer gt.mu.Unlock()

	if gt.conn != nil {
		_ = gt.conn.Close()
	}
	return gt.listener.Close()
}
