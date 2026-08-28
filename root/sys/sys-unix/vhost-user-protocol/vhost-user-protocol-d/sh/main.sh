# 1. Виділення пулу великих сторінок (1024 сторінки по 2 МБ = 2 ГБ)
echo 1024 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# 2. Запуск сервера SPDK з бекендом vhost-user-blk
spdk_tgt &
rpc.py bdev_nvme_attach_controller -b Nvme0 -t PCIe -a 0000:01:00.0
rpc.py vhost_create_blk_controller --cpumask 0x2 vhost.blk0 Nvme0n1

# 3. Запуск QEMU з підключенням до vhost-user сокета
qemu-system-x86_64 \
    -enable-kvm -m 2048 -smp 2 \
    -object memory-backend-file,id=mem,size=2048M,mem-path=/dev/hugepages,share=on \
    -numa node,memdev=mem \
    -chardev socket,id=spdk_vhost,path=/var/tmp/vhost.blk0 \
    -device vhost-user-blk-pci,chardev=spdk_vhost,id=blk0,num-queues=2
