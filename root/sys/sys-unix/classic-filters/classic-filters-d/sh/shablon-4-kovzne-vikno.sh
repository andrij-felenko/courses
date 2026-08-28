# Стеження за кількістю запитів за секунду (RPS)
tail -f /var/log/nginx/access.log \
  | stdbuf -oL cut -d' ' -f4 \
  | tr -d '[' \
  | stdbuf -oL awk '
    {
        sec = $1
        if (sec != current_sec) {
            if (current_sec != "") {
                printf "%s -> %5d RPS\n", current_sec, rps
            }
            current_sec = sec
            rps = 1
        } else {
            rps++
        }
    }
'
