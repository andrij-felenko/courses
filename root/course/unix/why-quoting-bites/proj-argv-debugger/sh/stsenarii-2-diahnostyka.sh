#!/usr/bin/env bash

forward_star_unquoted() { ./argv-dump $*; }
forward_star_quoted()   { ./argv-dump "$*"; }
forward_at_unquoted()   { ./argv-dump $@; }
forward_at_quoted()     { ./argv-dump "$@"; }

echo "=== ТЕСТ 1: forward_star_unquoted ==="
forward_star_unquoted "alpha beta" "gamma"

echo "=== ТЕСТ 2: forward_star_quoted ==="
forward_star_quoted "alpha beta" "gamma"

echo "=== ТЕСТ 3: forward_at_unquoted ==="
forward_at_unquoted "alpha beta" "gamma"

echo "=== ТЕСТ 4: forward_at_quoted ==="
forward_at_quoted "alpha beta" "gamma"
