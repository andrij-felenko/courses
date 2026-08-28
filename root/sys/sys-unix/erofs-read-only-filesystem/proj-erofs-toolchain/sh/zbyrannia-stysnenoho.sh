# 1. Базове збирання з алгоритмом LZ4HC (оптимальний баланс швидкості декомпресії)
mkfs.erofs -z lz4hc,12 sys_image.erofs ./target_rootfs/

# 2. Збирання з максимальним стисненням Zstd та упаковкою хвостів файлів (ztailpacking)
mkfs.erofs -z zstd,9 -E ztailpacking sys_image_zstd.erofs ./target_rootfs/

# 3. Формування образу для контейнерного середовища з дедуплікацією (chunk-based)
mkfs.erofs --chunksize=65536 container_layer.erofs ./container_root/

# 4. Збирання з автоматичною індексацією та дедуплікацією атрибутів безпеки SELinux
mkfs.erofs -z lz4hc,9 --file-contexts=/etc/selinux/targeted/contexts/files/file_contexts android_sys.erofs ./android_sys/
