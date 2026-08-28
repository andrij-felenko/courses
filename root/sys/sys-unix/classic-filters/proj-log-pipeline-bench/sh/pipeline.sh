#!/usr/bin/env bash
# pipeline.sh: Пошук 5xx помилок, вирізання IP, сортування та топ-10
export LC_ALL=C
cat access.log \
  | grep ' "5[0-9][0-9] ' \
  | cut -d' ' -f1 \
  | sort \
  | uniq -c \
  | sort -nr \
  | head -n 10
