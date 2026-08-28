package main

import (
	"net"
	"os"
	"strconv"
)

const listenFDsStart = 3

// Повертає слухача, переданого менеджером, або nil, якщо не передавали.
func inheritedListener() net.Listener {
	if os.Getenv("LISTEN_PID") != strconv.Itoa(os.Getpid()) {
		return nil // змінна дісталася нам у спадок від предка
	}
	if n, err := strconv.Atoi(os.Getenv("LISTEN_FDS")); err != nil || n != 1 {
		return nil
	}

	f := os.NewFile(listenFDsStart, "listen-fd") // сокет уже прив'язаний і слухає
	l, err := net.FileListener(f)
	if err != nil {
		return nil
	}
	return l
}

func main() {
	l := inheritedListener()
	if l == nil {
		l, _ = net.Listen("tcp", ":8080") // запустили руками — робимо сокет самі
	}
	serveForever(l)
}
