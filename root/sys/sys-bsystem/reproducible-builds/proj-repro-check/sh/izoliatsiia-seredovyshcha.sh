#!/usr/bin/env bash
# Запуск компіляції всередині стерильної пісочниці Bubblewrap
bwrap \
    --ro-bind /usr /usr \
    --ro-bind /lib /lib \
    --ro-bind /lib64 /lib64 \
    --ro-bind /bin /bin \
    --proc /proc \
    --dev /dev \
    --tmpfs /tmp \
    --bind "$PWD" /build \
    --chdir /build \
    --unshare-all \
    --hostname reproducible \
    --setenv LC_ALL C.UTF-8 \
    --setenv TZ UTC \
    --setenv SOURCE_DATE_EPOCH 1700000000 \
    make clean all
