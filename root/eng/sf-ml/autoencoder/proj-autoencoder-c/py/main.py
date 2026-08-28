import torch, torch.nn as nn

X = torch.eye(8)                                  # 8 one-hot шаблонів
net = nn.Sequential(nn.Linear(8, 3), nn.Sigmoid(),   # кодер
                    nn.Linear(3, 8), nn.Sigmoid())   # декодер
opt = torch.optim.SGD(net.parameters(), lr=1.0)

for epoch in range(6000):
    loss = 0.5 * ((net(X) - X) ** 2).sum(1).mean()
    opt.zero_grad(); loss.backward(); opt.step()      # увесь зворотний хід — тут
