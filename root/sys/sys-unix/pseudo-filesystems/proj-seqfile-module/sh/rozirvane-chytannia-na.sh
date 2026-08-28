# термінал 1: читач, що робить паузу між read()
$ ./reader-slow
row    0  generation 1
row    1  generation 1
…
row  177  generation 1
row  178  generation 2      ← межа порції
row  179  generation 2
…
row  199  generation 2

# термінал 2, у паузі між першим і другим read()
$ echo bump > /proc/heartbeat
