type Account = { id: string; userId: string; balance: number; frozen: boolean };
type WithdrawReq = { amount: number };
type Effect =
  | { kind: "debit";  accountId: string; amount: number }
  | { kind: "notify"; userId: string; message: string };

function decideWithdraw(acc: Account, req: WithdrawReq): Effect[] {
  if (acc.frozen)                                       // заморожено — тільки сповістити
    return [{ kind: "notify", userId: acc.userId, message: "Рахунок заморожено" }];
  if (req.amount > acc.balance)                         // не вистачає — тільки сповістити
    return [{ kind: "notify", userId: acc.userId, message: "Недостатньо коштів" }];
  return [{ kind: "debit", accountId: acc.id, amount: req.amount },
          { kind: "notify", userId: acc.userId, message: `Видано ${req.amount}` }];
}
