cd /tmp/build-workspace

# Генерація нативного DEB-пакунка
fpm -s dir -t deb \
    -n netbridge \
    -v 1.0.0 \
    --iteration 1 \
    --architecture x86_64 \
    --maintainer "DevOps Team <admin@example.com>" \
    --description "NetBridge High Performance Network Service" \
    --after-install - << 'EOF'
#!/bin/sh
systemctl daemon-reload
echo "[netbridge] Пакунок успішно встановлено в /opt/netbridge"
EOF \
    -C /tmp/build-workspace/stage \
    .
