# Створення групи портів цілі TPG 1 для бекенду iblock
mkdir -p /sys/kernel/config/target/core/iblock_0/lun_0/alua/tpg_1

# Встановлення типу доступу: Active/Optimized (значення 0)
echo 0 > /sys/kernel/config/target/core/iblock_0/lun_0/alua/tpg_1/alua_access_state

# Встановлення біта Preferred
echo 1 > /sys/kernel/config/target/core/iblock_0/lun_0/alua/tpg_1/alua_pref

# Встановлення штучної затримки для стану Non-Optimized (у мілісекундах)
echo 100 > /sys/kernel/config/target/core/iblock_0/lun_0/alua/tpg_1/nonop_delay_msecs

# Встановлення затримки переходу стану Transitioning (у мілісекундах)
echo 500 > /sys/kernel/config/target/core/iblock_0/lun_0/alua/tpg_1/trans_delay_msecs
