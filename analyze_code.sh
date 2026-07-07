#!/bin/bash

# Files to analyze (from lines 481-490)
files=(
  "book/electronics/analog/class-d-amplifier/class-d-amplifier.md"
  "book/electronics/analog/class-d-amplifier/hist-class-d.md"
  "book/electronics/analog/cmrr/cmrr.md"
  "book/electronics/analog/cmrr/hist-long-tailed-pair.md"
  "book/electronics/analog/colpitts-oscillator/colpitts-oscillator.md"
  "book/electronics/analog/colpitts-oscillator/hist-colpitts-hartley.md"
  "book/electronics/analog/colpitts-oscillator/math-startup-condition.md"
  "book/electronics/analog/common-mode-noise/common-mode-noise.md"
  "book/electronics/analog/common-mode-noise/comp-common-mode-choke.md"
  "book/electronics/analog/common-mode-noise/math-mode-conversion.md"
)

for file in "${files[@]}"; do
  echo "=== $file ==="
  rg -n '```' "$file" | head -20
  echo ""
done
