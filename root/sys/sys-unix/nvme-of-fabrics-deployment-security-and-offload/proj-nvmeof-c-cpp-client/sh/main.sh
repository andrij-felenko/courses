# Створення тестової підсистеми у ConfigFS
sudo mkdir /sys/kernel/config/nvmet/subsystems/nqn.2024-08.com.example:nvme.target1
echo 1 | sudo tee /sys/kernel/config/nvmet/subsystems/nqn.2024-08.com.example:nvme.target1/attr_allow_any_host

# Створення логічного порту TCP
sudo mkdir /sys/kernel/config/nvmet/ports/1
echo "tcp" | sudo tee /sys/kernel/config/nvmet/ports/1/addr_trtype
echo "127.0.0.1" | sudo tee /sys/kernel/config/nvmet/ports/1/addr_traddr
echo "4420" | sudo tee /sys/kernel/config/nvmet/ports/1/addr_trsvcid
echo "ipv4" | sudo tee /sys/kernel/config/nvmet/ports/1/addr_adrfam

# Зв'язування порту з підсистемою
sudo ln -s /sys/kernel/config/nvmet/subsystems/nqn.2024-08.com.example:nvme.target1 \
    /sys/kernel/config/nvmet/ports/1/subsystems/
