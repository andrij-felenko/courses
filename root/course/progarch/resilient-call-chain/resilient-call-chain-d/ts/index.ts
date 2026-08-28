// A викликає B, передаючи залишок спільного дедлайну, а не свіжий таймаут.
async function handle(req: Req, deadline: number): Promise<Resp> {
  // deadline — абсолютна мить (monotonic), поставлена на шлюзі.
  if (deadline - now() < MIN_WORK_NEEDED) {
    throw new NoTimeLeft();            // приречена робота — не беремося
  }
  const local = doOwnWork(req);        // трохи часу з'їли тут
  const left = deadline - now();
  return callB(local, AbortSignal.timeout(left)); // B дістає залишок
}
