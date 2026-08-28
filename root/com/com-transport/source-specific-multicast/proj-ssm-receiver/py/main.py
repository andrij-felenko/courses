from scapy.all import IP, IPOption_RouterAlert, send
from scapy.contrib.igmpv3 import IGMPv3, IGMPv3mr, IGMPv3gr

# Створення IGMPv3 Membership Report з кількома записами Group Record
pkt = IP(dst="224.0.0.22", ttl=1, options=[IPOption_RouterAlert()]) / \
      IGMPv3() / \
      IGMPv3mr(records=[
          # Запис 1: Режим INCLUDE для двох джерел
          IGMPv3gr(rtype=1, maddr="232.1.1.1", srcaddrs=["198.51.100.1", "198.51.100.2"]),
          # Запис 2: Зміна режиму на EXCLUDE з одним виключенням
          IGMPv3gr(rtype=4, maddr="232.2.2.2", srcaddrs=["198.51.100.99"])
      ])

send(pkt, iface="eth0", verbose=True)
