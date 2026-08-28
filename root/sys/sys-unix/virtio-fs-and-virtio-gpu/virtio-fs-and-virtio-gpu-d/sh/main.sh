# 1. Запуск демона virtiofsd на хості
virtiofsd --socket-path=/tmp/vfs.sock \
          --shared-dir=/home/user/project \
          --sandbox=namespace

# 2. Запуск QEMU: пам'ять ВМ обов'язково спільна (share=on),
#    інакше демон не зможе звертатися до неї напряму
qemu-system-x86_64 \
    -enable-kvm -m 4G \
    -object memory-backend-file,id=mem,size=4G,mem-path=/dev/shm,share=on \
    -numa node,memdev=mem \
    -chardev socket,id=char0,path=/tmp/vfs.sock \
    -device vhost-user-fs-pci,queue-size=1024,chardev=char0,tag=my_shared_dir
