// echod.go — та сама служба ідіоматичним Go.
//   go build -o echod echod.go
package main

import (
	"io"
	"log"
	"net"
	"os"
	"strconv"
)

const listenFDsStart = 3

// Слухач, переданий менеджером, або nil, якщо нам нічого не передавали.
func inherited() net.Listener {
	if os.Getenv("LISTEN_PID") != strconv.Itoa(os.Getpid()) {
		return nil // змінні дісталися нам у спадок від предка
	}
	n, err := strconv.Atoi(os.Getenv("LISTEN_FDS"))
	if err != nil || n != 1 {
		return nil
	}
	os.Unsetenv("LISTEN_PID") // далі, до власних нащадків, вони не поїдуть
	os.Unsetenv("LISTEN_FDS")
	os.Unsetenv("LISTEN_FDNAMES")

	f := os.NewFile(listenFDsStart, "listen-fd") // уже прив'язаний і слухає
	defer f.Close()                              // FileListener узяв собі копію

	l, err := net.FileListener(f)
	if err != nil {
		log.Fatalf("переданий дескриптор не є слухачем: %v", err)
	}
	return l
}

func main() {
	l := inherited()
	if l == nil { // запустили руками — сокет робимо самі
		var err error
		if l, err = net.Listen("tcp", "127.0.0.1:9000"); err != nil {
			log.Fatal(err)
		}
	}

	for {
		c, err := l.Accept()
		if err != nil {
			log.Fatal(err)
		}
		go func() { // кожне з'єднання — своя горутина
			defer c.Close()
			io.Copy(c, c)
		}()
	}
}
