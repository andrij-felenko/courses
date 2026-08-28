import { EventEmitter } from 'events';

enum PriorityClass {
  P0_Critical = 0,
  P1_High = 1,
  P2_Medium = 2,
  P3_Low = 3,
  P4_Background = 4,
}

enum BrownoutLevel {
  L0_Normal = 0,
  L1_Shed_P4 = 1,
  L2_Shed_P3 = 2,
  L3_Shed_P2 = 3,
  L4_Shed_P1 = 4,
}

interface RequestContext {
  requestId: string;
  tenantId: string;
  priority: PriorityClass;
  payload: string;
}

interface PipelineError {
  status: number;
  code: string;
  message: string;
  retryAfterMs: number;
}

class ResiliencePipelineTS {
  private brownoutLevel: BrownoutLevel = BrownoutLevel.L0_Normal;
  private inFlight = 0;
  private readonly maxConcurrency = 100;
  private isCircuitOpen = false;

  public setBrownoutLevel(level: BrownoutLevel): void {
    this.brownoutLevel = level;
  }

  private shouldShed(priority: PriorityClass): boolean {
    switch (this.brownoutLevel) {
      case BrownoutLevel.L1_Shed_P4: return priority >= PriorityClass.P4_Background;
      case BrownoutLevel.L2_Shed_P3: return priority >= PriorityClass.P3_Low;
      case BrownoutLevel.L3_Shed_P2: return priority >= PriorityClass.P2_Medium;
      case BrownoutLevel.L4_Shed_P1: return priority >= PriorityClass.P1_High;
      default: return false;
    }
  }

  public async execute(
    ctx: RequestContext,
    primaryHandler: (c: RequestContext) => Promise<string>,
    fallbackHandler: (c: RequestContext, reason: string) => Promise<string>
  ): Promise<string> {
    // 1. Priority Load Shedding
    if (this.shouldShed(ctx.priority)) {
      throw {
        status: 503,
        code: 'LOAD_SHEDDED',
        message: 'Request shedded due to Brownout level',
        retryAfterMs: 5000,
      } as PipelineError;
    }

    // 2. Concurrency Control
    if (this.inFlight >= this.maxConcurrency) {
      throw {
        status: 429,
        code: 'CONCURRENCY_EXCEEDED',
        message: 'Too many active requests',
        retryAfterMs: 2000,
      } as PipelineError;
    }

    // 3. Circuit Breaker Check
    if (this.isCircuitOpen) {
      return fallbackHandler(ctx, 'Circuit Breaker is OPEN');
    }

    this.inFlight++;
    try {
      const result = await primaryHandler(ctx);
      return result;
    } catch (err: any) {
      // Direct poison messages or service failures to Fallback / DLQ
      return fallbackHandler(ctx, `Primary failure: ${err.message}`);
    } finally {
      this.inFlight--;
    }
  }
}
