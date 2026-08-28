virsh migrate --live \
  --p2p \
  --postcopy \
  --auto-converge \
  --auto-converge-initial 20 \
  --auto-converge-increment 10 \
  --persistent \
  --undefinesource \
  --bandwidth 10000 \
  --parallel \
  --parallel-connections 8 \
  --verbose \
  production-db-vm qemu+tcp://node2.datacenter.lan/system
