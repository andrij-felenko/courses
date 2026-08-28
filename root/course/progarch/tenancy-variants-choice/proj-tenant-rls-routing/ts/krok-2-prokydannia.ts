import { AsyncLocalStorage } from 'node:async_hooks';
import { Pool, PoolClient } from 'pg';

const tenantStorage = new AsyncLocalStorage<string>();

export class TenantContext {
  static run<T>(tenantId: string, store: () => Promise<T>): Promise<T> {
    if (!tenantId) {
      throw new Error('Security violation: tenantId is required');
    }
    return tenantStorage.run(tenantId, store);
  }

  static current(): string {
    const tenantId = tenantStorage.getStore();
    if (!tenantId) {
      throw new Error('Security violation: no tenant context bound to current async execution');
    }
    return tenantId;
  }
}

export async function withTenantClient<T>(
  pool: Pool,
  action: (client: PoolClient) => Promise<T>
): Promise<T> {
  const tenantId = TenantContext.current();
  const client = await pool.connect();

  try {
    await client.query('BEGIN');
    // set_config z is_local = true ізолює параметр у межах цієї транзакції
    await client.query('SELECT set_config($1, $2, true)', ['app.current_tenant', tenantId]);

    const result = await action(client);

    await client.query('COMMIT');
    return result;
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    // При поверненні до пулу підключення гарантовано чисте за рахунок ROLLBACK/COMMIT
    client.release();
  }
}
