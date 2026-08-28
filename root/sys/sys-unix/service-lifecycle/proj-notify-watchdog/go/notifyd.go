// notifyd.go — та сама служба ідіоматичним Go: без залежностей, той самий протокол.
package main

import (
	"fmt"
	"net"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"
)

// notify — увесь протокол: датаграма з рядками КЛЮЧ=значення.
// Позначку «@» для абстрактного імені стандартна бібліотека розуміє сама,
// тож замінювати її на нульовий байт вручну не треба — і НЕ МОЖНА.
func notify(msg string) {
	path := os.Getenv("NOTIFY_SOCKET")
	if path == "" {
		return // запустили не менеджером
	}
	conn, err := net.DialUnix("unixgram", nil, &net.UnixAddr{Name: path, Net: "unixgram"})
	if err != nil {
		return
	}
	defer conn.Close()
	conn.Write([]byte(msg))
}

// Половина сторожового терміну; 0 — сторожа немає.
func pingPeriod() time.Duration {
	if owner := os.Getenv("WATCHDOG_PID"); owner != "" && owner != strconv.Itoa(os.Getpid()) {
		return 0 // змінна дісталася в спадок від предка
	}
	usec, err := strconv.ParseInt(os.Getenv("WATCHDOG_USEC"), 10, 64)
	if err != nil || usec <= 0 {
		return 0
	}
	return time.Duration(usec) * time.Microsecond / 2
}

func serve(c net.Conn) {
	defer c.Close()
	c.SetDeadline(time.Now().Add(2 * time.Second))
	buf := make([]byte, 256)
	// Запис у закрите з'єднання поверне помилку: середовище виконання Go
	// саме ігнорує SIGPIPE для всього, крім стандартного виводу й помилок.
	if n, err := c.Read(buf); err == nil {
		c.Write(buf[:n])
	}
}

func main() {
	ln, err := net.Listen("tcp", "127.0.0.1:9100")
	if err != nil {
		fmt.Fprintln(os.Stderr, "listen:", err)
		os.Exit(1) // READY=1 не було — менеджер бачить невдалий старт
	}
	notify("READY=1\nSTATUS=слухаю 127.0.0.1:9100\n")

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM, syscall.SIGINT)

	// Accept блокує, тому живе в окремій горутині — але вона лише ПРИНОСИТЬ
	// з'єднання; сама робота лишається в головному циклі, нижче.
	conns := make(chan net.Conn)
	go func() {
		defer close(conns)
		for {
			c, err := ln.Accept()
			if err != nil {
				return
			}
			conns <- c
		}
	}()

	var ping <-chan time.Time // nil-канал у select блокує назавжди
	if p := pingPeriod(); p > 0 {
		t := time.NewTicker(p)
		defer t.Stop()
		ping = t.C
	}

	served := 0
	for {
		select {
		case c, ok := <-conns:
			if !ok {
				return
			}
			serve(c) // робота — в ЦЬОМУ ж циклі
			served++
		case <-ping:
			notify(fmt.Sprintf("WATCHDOG=1\nSTATUS=обслужено з'єднань: %d\n", served))
		case <-stop:
			notify("STOPPING=1\nSTATUS=закриваю сокет\n")
			ln.Close()
			return // код виходу 0
		}
	}
}
