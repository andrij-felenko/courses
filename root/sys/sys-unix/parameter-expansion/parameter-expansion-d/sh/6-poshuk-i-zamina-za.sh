DATA="root:x:0:0:root:/root:/bin/bash"

# 1. Заміна першого входження:
echo "${DATA/:/,}"
# Вивід: "root,x:0:0:root:/root:/bin/bash"

# 2. Глобальна заміна всіх входжень (подвійний слеш //):
echo "${DATA//:/,}"
# Вивід: "root,x,0,0,root,/root,/bin/bash"

# 3. Видалення входжень (replacement опущено):
echo "${DATA//:}"
# Вивід: "rootx00root/root/bin/bash"
