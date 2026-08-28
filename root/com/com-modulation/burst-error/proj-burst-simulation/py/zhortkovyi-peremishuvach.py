def conv_interleave(stream, N, M):
    fifos = [[0] * (j * M) for j in range(N)]      # гілка j: черга на j·M символів
    out = []
    for i, s in enumerate(stream):
        j = i % N
        if j == 0:
            out.append(s)                          # гілка 0 без затримки — наскрізь
        else:
            fifos[j].append(s); out.append(fifos[j].pop(0))
    return out

def conv_deinterleave(stream, N, M):
    fifos = [[0] * ((N - 1 - j) * M) for j in range(N)]   # дзеркальні затримки
    out = []
    for i, s in enumerate(stream):
        j = i % N
        if (N - 1 - j) * M == 0:
            out.append(s)
        else:
            fifos[j].append(s); out.append(fifos[j].pop(0))
    return out
