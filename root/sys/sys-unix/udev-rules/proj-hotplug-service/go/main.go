// go get golang.org/x/sys/unix
package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"os"
	"os/signal"

	"golang.org/x/sys/unix"
)

func openPort(path string) (*os.File, error) {
	fd, err := unix.Open(path, unix.O_RDWR|unix.O_NOCTTY|unix.O_NONBLOCK, 0)
	if err != nil {
		return nil, fmt.Errorf("open %s: %w", path, err)
	}
	// На Linux швидкість живе в бітах CBAUD усередині c_cflag —
	// полів Ispeed/Ospeed ядро при TCSETS не читає.
	t := unix.Termios{Cflag: unix.CS8 | unix.CREAD | unix.CLOCAL | unix.B115200}
	t.Cc[unix.VMIN], t.Cc[unix.VTIME] = 1, 0
	if err := unix.IoctlSetTermios(fd, unix.TCSETS, &t); err != nil {
		unix.Close(fd)
		return nil, fmt.Errorf("termios: %w", err)
	}
	// Дескриптор лишається неблокувальним — так os.File потрапляє під
	// опитувач середовища виконання, і Close розбудить чужий Read.
	return os.NewFile(uintptr(fd), path), nil
}

func main() {
	port, err := openPort(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Printf("агент %s: почали\n", port.Name())

	sigc := make(chan os.Signal, 1)
	signal.Notify(sigc, unix.SIGTERM, unix.SIGINT)
	go func() {
		<-sigc
		fmt.Println("SIGTERM: закриваємо порт")
		port.Close() // розблокує Read у головній горутині
	}()

	sc := bufio.NewScanner(port)
	for sc.Scan() {
		fmt.Println("верстат:", sc.Text()) // stdout забирає journald
	}

	switch err := sc.Err(); {
	case err == nil, errors.Is(err, io.EOF), errors.Is(err, os.ErrClosed):
		// нас закрили за сигналом або шнур висмикнули
	case errors.Is(err, unix.EIO), errors.Is(err, unix.ENODEV),
		errors.Is(err, unix.ENXIO):
		fmt.Println("пристрій зник") // теж не збій: виходимо нулем
	default:
		fmt.Fprintln(os.Stderr, "читання:", err)
		os.Exit(1)
	}
}
