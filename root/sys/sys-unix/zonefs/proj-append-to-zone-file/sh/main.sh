sudo modprobe null_blk nr_devices=0        # модуль без готових пристроїв
D=/sys/kernel/config/nullb/zdev
sudo mkdir $D
echo 4096 | sudo tee $D/blocksize     >/dev/null   # логічний блок 4 КіБ
echo 1    | sudo tee $D/memory_backed >/dev/null   # дані справді зберігаються
echo 1    | sudo tee $D/zoned         >/dev/null
echo 512  | sudo tee $D/size          >/dev/null   # увесь пристрій, МіБ
echo 64   | sudo tee $D/zone_size     >/dev/null   # зона, МіБ → усього 8 зон
echo 2    | sudo tee $D/zone_nr_conv  >/dev/null   # перші дві зони — звичайні
echo 1    | sudo tee $D/power         >/dev/null   # вмикаємо → /dev/nullb0
