#!/usr/bin/env bash
# "$*" проти "$@": одне слово чи N слів.
set -u

count() {
    printf '%d сл.' "$#"
    if [ "$#" -gt 0 ]; then
        printf ':'
        printf ' [%s]' "$@"
    fi
    printf '\n'
}

set -- 'arg 1' 'arg 2' 'arg 3'
printf 'позиційних параметрів: %d\n' "$#"

printf '%-18s ' '$*'   ; count $*     # поділ на слова руйнує межі
printf '%-18s ' '$@'   ; count $@     # без лапок різниці між ними немає
printf '%-18s ' '"$*"' ; count "$*"   # рівно одне слово
printf '%-18s ' '"$@"' ; count "$@"   # рівно три слова, межі збережено

echo '--- перший символ IFS стає клеєм для "$*" ---'
old_ifs=$IFS
IFS=,
printf '%-18s ' '"$*" при IFS=,' ; count "$*"
printf '%-18s ' '"$@" при IFS=,' ; count "$@"   # на "$@" IFS не впливає
IFS=''
printf '%-18s ' '"$*" при IFS=""' ; count "$*"  # значення злипаються без розділювача
IFS=$old_ifs

echo '--- порожній список параметрів ---'
set --
printf '%-18s ' '"$@"' ; count "$@"   # нуль слів — команда просто не отримає аргументів
printf '%-18s ' '"$*"' ; count "$*"   # одне порожнє слово, і воно потрапить у argv[]

echo '--- делегування аргументів у вкладену команду ---'
set -- 'arg 1' 'arg 2' 'arg 3'
relay_ok()     { count "$@"; }
relay_broken() { count $*; }
printf 'через "$@": ' ; relay_ok "$@"
printf 'через $*  : ' ; relay_broken "$@"
