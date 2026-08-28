# cd /sys/kernel/debug/block/nvme0n1/rqos/wbt
# grep . enabled min_lat_nsec curr_win_nsec wb_normal wb_background
enabled:1
min_lat_nsec:2000000
curr_win_nsec:100000000
wb_normal:8
wb_background:4
# cat inflight
0: inflight 0
1: inflight 0
2: inflight 0
