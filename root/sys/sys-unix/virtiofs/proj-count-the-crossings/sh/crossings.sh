#!/bin/bash
# crossings.sh — скільки запитів FUSE коштує одне складання на спільній теці.
# Запускати В ГОСТІ, від root, у теці, змонтованій як virtiofs.
set -eu

EV=/sys/kernel/tracing/events/fuse/fuse_request_send
HIST='hist:keys=opcode:sort=hitcount.descending'
LABEL=${1:?мітка прогону, напр. "auto"}
ROOT=${2:-./lab}
FILES=240 HDRS=160 INCS=4

[ -d "$EV" ] || { echo "нема точки fuse:fuse_request_send: ядро старше за 6.12" >&2; exit 1; }

gen_tree() {                     # те саме дерево на кожному прогоні — до байта
  rm -rf "$ROOT"; mkdir -p "$ROOT/src" "$ROOT/obj"
  i=0; while [ $i -lt $INCS ]; do mkdir -p "$ROOT/inc$i"; i=$((i + 1)); done

  h=0
  while [ $h -lt $HDRS ]; do
    printf 'static inline int h%d(void) { return %d; }\n' "$h" "$h" \
      > "$ROOT/inc$((h % INCS))/h$h.h"
    h=$((h + 1))
  done

  c=0
  while [ $c -lt $FILES ]; do
    { k=0
      while [ $k -lt 4 ]; do
        printf '#include <h%d.h>\n' "$(( (c * 4 + k) % HDRS ))"; k=$((k + 1))
      done
      printf 'int f%d(void) { return h%d(); }\n' "$c" "$(( c * 4 % HDRS ))"
    } > "$ROOT/src/m$c.c"
    c=$((c + 1))
  done

  { echo 'CFLAGS = -Iinc0 -Iinc1 -Iinc2 -Iinc3'
    echo 'OBJS = $(patsubst src/%.c,obj/%.o,$(wildcard src/*.c))'
    echo 'all: $(OBJS)'
    echo 'obj/%.o: src/%.c'
    printf '\t$(CC) $(CFLAGS) -c $< -o $@\n'    # рецепт починається з табуляції
  } > "$ROOT/Makefile"
}

run() {
  sync; echo 3 > /proc/sys/vm/drop_caches      # холодний старт: геть кеш сторінок і дентрі
  echo "!$HIST" > "$EV/trigger" 2>/dev/null || true
  echo "$HIST"  > "$EV/trigger"

  t0=$(date +%s%N)
  ( cd "$ROOT" && find . -type f > /dev/null && make -s -j"$(nproc)" > /dev/null )
  t1=$(date +%s%N)

  awk -v label="$1" -v ms=$(( (t1 - t0) / 1000000 )) '
    BEGIN {
      n = split("1 LOOKUP 3 GETATTR 4 SETATTR 14 OPEN 15 READ 16 WRITE 18 RELEASE " \
                "22 GETXATTR 25 FLUSH 27 OPENDIR 28 READDIR 29 RELEASEDIR " \
                "34 ACCESS 35 CREATE 44 READDIRPLUS", a, " ")
      for (i = 1; i < n; i += 2) name[a[i]] = a[i + 1]
    }
    /hitcount:/ {
      op = $0; sub(/.*opcode: */, "", op); sub(/ *}.*/, "", op)
      hc = $0; sub(/.*hitcount: */, "", hc); sub(/[^0-9].*/, "", hc)
      key = (op in name) ? name[op] : ("op" op)
      cnt[key] += hc; total += hc
    }
    END {
      printf "%-8s %6d мс  усього %6d", label, ms, total
      split("LOOKUP GETATTR OPEN READ", show, " ")
      for (i = 1; i <= 4; i++) printf "  %s %d", show[i], cnt[show[i]] + 0
      printf "\n"
    }' "$EV/hist"

  echo "!$HIST" > "$EV/trigger"
}

gen_tree
run "$LABEL"
