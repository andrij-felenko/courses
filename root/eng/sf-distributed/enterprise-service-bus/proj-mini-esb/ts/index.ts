interface NormalizedMessage {
  messageId: string;
  correlationId: string;
  headers: Map<string, string>;
  payload: string;
}

interface Exchange {
  request: NormalizedMessage;
  response?: NormalizedMessage;
  targetEndpoint?: string;
  faultReason?: string;
  isFault: boolean;
}

type StageResult = 'CONTINUE' | 'FILTERED' | 'FAULT';

interface PipelineStage {
  name: string;
  process(exchange: Exchange): Promise<StageResult>;
}

class AuthValidatorStage implements PipelineStage {
  name = 'AuthValidator';
  async process(exchange: Exchange): Promise<StageResult> {
    const token = exchange.request.headers.get('X-Auth-Token');
    if (token !== 'secret-token-123') {
      exchange.faultReason = 'AUTH_REJECTED: Invalid or missing token';
      exchange.isFault = true;
      return 'FAULT';
    }
    return 'CONTINUE';
  }
}

class ContentBasedRouterStage implements PipelineStage {
  name = 'ContentBasedRouter';
  async process(exchange: Exchange): Promise<StageResult> {
    const type = exchange.request.headers.get('X-Message-Type');
    if (type === 'ORDER_PAYMENT') {
      exchange.targetEndpoint = 'billing.service.v1';
    } else if (type === 'INVENTORY_SYNC') {
      exchange.targetEndpoint = 'warehouse.service.v2';
    } else {
      exchange.faultReason = 'ROUTING_FAILED: Unknown message type';
      exchange.isFault = true;
      return 'FAULT';
    }
    return 'CONTINUE';
  }
}

class JsonTransformerStage implements PipelineStage {
  name = 'JsonTransformer';
  async process(exchange: Exchange): Promise<StageResult> {
    exchange.response = {
      ...exchange.request,
      headers: new Map(exchange.request.headers),
      payload: JSON.stringify({
        target: exchange.targetEndpoint,
        id: exchange.request.messageId,
        data: exchange.request.payload
      })
    };
    exchange.response.headers.set('Content-Type', 'application/json');
    return 'CONTINUE';
  }
}

class BusPipeline {
  private stages: PipelineStage[] = [];

  addStage(stage: PipelineStage): this {
    this.stages.push(stage);
    return this;
  }

  async dispatch(exchange: Exchange): Promise<void> {
    console.log(`[BUS-TS] Обробка ID=${exchange.request.messageId}`);
    for (const stage of this.stages) {
      const result = await stage.process(exchange);
      if (result === 'FAULT') {
        console.log(`[BUS-TS] Збій на '${stage.name}': ${exchange.faultReason} -> DLQ`);
        return;
      }
      if (result === 'FILTERED') {
        console.log(`[BUS-TS] Відфільтровано на '${stage.name}'`);
        return;
      }
    }
    console.log(`[BUS-TS] Доставлено до '${exchange.targetEndpoint}': ${exchange.response?.payload}`);
  }
}
