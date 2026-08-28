# fdinfo дескриптора inotify має рядок на кожне стеження — рахуємо їх
# по всіх дескрипторах одного процесу
cat /proc/$(pgrep -x watchtree | head -1)/fdinfo/* 2>/dev/null | grep -c '^inotify'

# те саме по всій системі
cat /proc/[0-9]*/fdinfo/* 2>/dev/null | grep -c '^inotify'

# скільки насправді зайнято в ядрі: <active_objs> <num_objs> <objsize>
sudo grep -E '^(inotify_inode_mark|ext4_inode_cache) ' /proc/slabinfo

# чинна межа
cat /proc/sys/fs/inotify/max_user_watches
