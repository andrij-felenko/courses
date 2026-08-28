static void sweep(uint64_t t)
{
    for (int i = 0; i < npeers; ) {
        if (peers[i].expires_ms <= t) {
            printf("— зник %s (мовчав %llu с)\n", peers[i].name,
                   (unsigned long long)(peers[i].ttl_ms / 1000u));
            peers[i] = peers[--npeers];
        } else i++;
    }
}
