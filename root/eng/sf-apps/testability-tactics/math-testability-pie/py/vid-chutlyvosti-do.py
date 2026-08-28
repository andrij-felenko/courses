import math
def tests_needed(t, C=0.90):
    return math.ceil(math.log(1 - C) / math.log(1 - t))

for t in (0.5, 0.22, 0.1, 0.05, 0.01, 0.001):
    print(t, tests_needed(t), round(2.3026 / t, 1))   # точне n і наближення 2.3/t
# 0.5    4      4.6
# 0.22   10     10.5
# 0.1    22     23.0
# 0.05   45     46.1
# 0.01   230    230.3
# 0.001  2302   2302.6
