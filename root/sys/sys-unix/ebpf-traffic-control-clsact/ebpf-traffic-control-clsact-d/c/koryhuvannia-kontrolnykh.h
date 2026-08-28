// Оновлення IP (L3) контрольної суми при зміні IP-адреси
__be32 old_ip = ip->saddr;
__be32 new_ip = bpf_htonl(0x0A000001);

ip->saddr = new_ip;

bpf_l3_csum_replace(skb, offsetof(struct iphdr, check), old_ip, new_ip, sizeof(new_ip));

// Оновлення TCP (L4) контрольної суми
bpf_l4_csum_replace(skb, offsetof(struct tcphdr, check) + ETH_HLEN + sizeof(struct iphdr),
                    old_ip, new_ip, sizeof(new_ip) | BPF_F_PSEUDO_HDR);
