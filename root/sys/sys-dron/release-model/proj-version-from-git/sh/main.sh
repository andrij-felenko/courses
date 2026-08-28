#!/bin/sh
# Рядок версії і числовий код магазину — з історії репозиторію.
set -eu

TAG_GLOB=${TAG_GLOB:-'v[0-9]*'}   # теги СВОЄЇ лінії, і тільки вони

# 1. Опис відносно найближчого тега.
#    --tags   рахувати й легкі теги, не лише анотовані
#    --match  не хапати теги чужого призначення (latest, стара пакувальна лінія…)
#    --long   друкувати «тег-N-gхеш» навіть тоді, коли стоїмо просто на тезі
#    --dirty  дописати «-dirty», якщо у відстежуваних файлах є незакомічені правки
#    --always НЕ додаємо навмисно: він підміняє відмову хешем, і збірка без тегів
#             мовчки поїде далі з версією 0.0.0
desc=$(git describe --tags --long --dirty --match "$TAG_GLOB" 2>/dev/null) || desc=''

if [ -z "$desc" ]; then
    echo "версію не обчислити: немає .git або в клоні немає тегів" >&2
    exit 1
fi

# 2. Розбір «<тег>-<комітів>-g<хеш>[-dirty]».
#    Ім'я тега саме може містити дефіси (v5.1.0-rc1), тож відкушуємо з кінця.
dirty=''
case $desc in
    *-dirty) dirty='-dirty'; desc=${desc%-dirty} ;;
esac
hash=${desc##*-g}      # усе після останнього «-g»
rest=${desc%-g*}       # «<тег>-<комітів>»
count=${rest##*-}      # число після останнього дефіса
tag=${rest%-*}         # що лишилось — ім'я тега

# 3. Три числа з імені тега. Знімаємо буквений префікс лінії
#    (v — стабільна, d — основа щоденних) і хвіст на кшталт «-rc1».
case $tag in
    [vd][0-9]*.[0-9]*.[0-9]*) ;;
    *) echo "тег «$tag» не схожий на X.Y.Z — уточніть TAG_GLOB" >&2; exit 1 ;;
esac
num=${tag#[vd]}
major=${num%%.*};  num=${num#*.}
minor=${num%%.*};  num=${num#*.}
patch=${num%%[!0-9]*}

version="$major.$minor.$patch"
version_str="$tag-$count-g$hash$dirty"

# 4. Числовий код: BB M I PP DDD. Ширина полів фіксована, і вихід за неї
#    не «переповнюється» — він мовчки зсуває сусідні розряди, тож ловимо тут.
if [ "$major" -gt 9 ] || [ "$minor" -gt 9 ] || [ "$patch" -gt 99 ]; then
    echo "версія $version не влазить у формат BBMIPPDDD" >&2
    exit 1
fi
if [ "$count" -gt 999 ]; then
    echo "після $tag уже $count комітів — лічильник уперся у стелю" >&2
    count=999
fi

# 64-бітні пакунки мусять мати БІЛЬШИЙ код: пристрій, якому підходять обидва,
# бере той, у якого код вищий.
case ${ABI:-arm64-v8a} in
    arm64-v8a|x86_64) bitness=66 ;;
    armeabi-v7a|x86)  bitness=34 ;;
    *) echo "невідоме ABI: ${ABI-}" >&2; exit 1 ;;
esac

version_code=$(printf '%s%d%d%02d%03d' \
                      "$bitness" "$major" "$minor" "$patch" "$count")

printf 'version=%s\nversion_str=%s\nversion_code=%s\n' \
       "$version" "$version_str" "$version_code"
