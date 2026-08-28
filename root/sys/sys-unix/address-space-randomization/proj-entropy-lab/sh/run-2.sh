# 1) типовий
sh run.sh 500 ./probe > plain.txt

# 2) рандомізації немає зовсім: прапорець особистості
setarch --addr-no-randomize sh run.sh 500 ./probe > off.txt

# 3) рівень 1: усе рухається, крім купи  (глобально, потрібен root)
old=$(cat /proc/sys/kernel/randomize_va_space)
printf '1\n' | sudo tee /proc/sys/kernel/randomize_va_space > /dev/null
sh run.sh 500 ./probe > va1.txt
printf '%s\n' "$old" | sudo tee /proc/sys/kernel/randomize_va_space > /dev/null

for f in plain off va1; do printf '\n== %s\n' "$f"; ./bits < "$f.txt"; done
