$ cat /sys/kernel/mm/transparent_hugepage/enabled
always [madvise] never

$ ./budinfo --need 2097152 | grep Normal -A1
Node 0, zone Normal    вільно     674.1 МіБ   найбільший блок: порядок 7 = 512.0 КіБ
    під 2.0 МіБ треба порядок 9 → таких блоків ще дістану: 0

$ echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag > /dev/null
$ ./thpprobe --count 128
велика сторінка 2097152 Б = порядок 9; прошу 128 штук (256.0 МіБ)
дано великих сторінок: 0 з 128   (відмов: 128, інших помилок: 0)
затримка на шматок, мкс: медіана 1.8, 90% 2.4, найгірша 11.9
приріст: thp_fault_alloc +0, thp_fault_fallback +128, compact_stall +0, compact_success +0
