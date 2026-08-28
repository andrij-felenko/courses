# господар, по одному разу на кожен режим із never / auto / always
virtiofsd --socket-path=/run/vfs.sock --shared-dir=/srv/lab --cache="$MODE" &

qemu-system-x86_64 -m 4G \
  -object memory-backend-memfd,id=mem,size=4G,share=on -numa node,memdev=mem \
  -chardev socket,id=vfs0,path=/run/vfs.sock \
  -device vhost-user-fs-pci,chardev=vfs0,tag=lab \
  …                                    # решта машини: ядро, диск, консоль

# гість
mount -t virtiofs lab /mnt/lab && /mnt/lab/crossings.sh "$MODE"
