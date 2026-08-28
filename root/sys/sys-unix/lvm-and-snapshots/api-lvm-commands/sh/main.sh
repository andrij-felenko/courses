# три яруси знизу вгору
pvcreate /dev/sdb1 /dev/sdc1
vgcreate vg0 /dev/sdb1 /dev/sdc1              # екстент типово 4 МіБ
lvcreate -n home -L 20g vg0
mkfs.ext4 /dev/vg0/home && mount /dev/vg0/home /home

lvextend -L +10g -r vg0/home                  # том і ФС однією дією
pvs -o +pe_start /dev/sdb1                    # перевірити вирівнювання

# класичний знімок: -L — це запас під зміни, не розмір оригіналу
lvcreate -s -n home-snap -L 5g vg0/home
mount -o ro /dev/vg0/home-snap /mnt/snap      # у /dev/mapper воно ж — vg0-home--snap

# тонкий пул, том у ньому та знімок тому
lvcreate --type thin-pool -L 500g -n pool vg0
lvcreate -T vg0/pool -V 2t -n app
lvcreate -s -n app-snap vg0/app               # без -L
lvchange -K -ay vg0/app-snap                  # -K знімає прапорець «пропустити активацію»

# нагляд і авторозширення
lvchange --monitor y vg0/pool
lvs -o lv_name,lv_attr,lv_size,pool_lv,origin,data_percent,metadata_percent vg0
dmsetup table vg0-pool-tpool
