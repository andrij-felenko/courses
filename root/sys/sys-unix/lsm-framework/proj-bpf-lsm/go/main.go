// main.go — той самий завантажувач мовою Go, github.com/cilium/ebpf
package main

import (
	"log"
	"os"
	"os/signal"

	"github.com/cilium/ebpf/link"
	"golang.org/x/sys/unix"
)

//go:generate go run github.com/cilium/ebpf/cmd/bpf2go denyNet deny-net.bpf.c

func main() {
	var st unix.Stat_t
	if err := unix.Stat(os.Args[1], &st); err != nil {
		log.Fatalf("тека cgroup: %v", err)
	}

	var objs denyNetObjects
	if err := loadDenyNetObjects(&objs, nil); err != nil {
		log.Fatalf("перевіряльник не пропустив: %v", err)
	}
	defer objs.Close()

	if err := objs.Caged.Put(st.Ino, uint8(1)); err != nil {
		log.Fatalf("мапа: %v", err)
	}

	l, err := link.AttachLSM(link.LSMOptions{Program: objs.DenyNet})
	if err != nil {
		log.Fatalf("не причепилось: %v", err)
	}
	defer l.Close()

	log.Printf("правило діє для cgroup %d", st.Ino)
	sig := make(chan os.Signal, 1)
	signal.Notify(sig, os.Interrupt)
	<-sig
}
