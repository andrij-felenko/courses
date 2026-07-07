#!/bin/bash

# Process files 381-390 from codefiles.txt
files=(
  "book/electronics/analog/current-source/math-output-resistance.md"
  "book/electronics/analog/current-source/proj-jfet-current-source.md"
  "book/electronics/analog/dac-weighted-resistors/dac-weighted-resistors.md"
  "book/electronics/analog/dac-weighted-resistors/hist-dac-origins.md"
  "book/electronics/analog/darlington-pair/comp-darlington-array.md"
  "book/electronics/analog/darlington-pair/darlington-pair.md"
  "book/electronics/analog/darlington-pair/hist-darlington-sziklai.md"
  "book/electronics/analog/dds-synthesis/dds-synthesis.md"
  "book/electronics/analog/dds-synthesis/hist-dds-origins.md"
  "book/electronics/analog/dds-synthesis/math-phase-truncation.md"
)

for f in "${files[@]}"; do
  full_path="E:\develop\courses\$f"
  echo "File: $f"
  grep -n '^```' "$full_path" 2>/dev/null | head -3
  echo ""
done
