// Концерн — обгортка. Справа не знає, що її логують.
function logged<A extends unknown[], R>(name: string, fn: (...a: A) => R) {
  return (...args: A): R => {
    log.info(`${name}: in`);
    try {
      const r = fn(...args);
      log.info(`${name}: ok`);
      return r;
    } catch (e) {
      log.error(`${name}: err`, e);
      throw e;
    }
  };
}

const placeOrder = logged("placeOrder", (order: Order): Receipt =>
  doPlace(order));                    // лише справа, нічого зайвого
