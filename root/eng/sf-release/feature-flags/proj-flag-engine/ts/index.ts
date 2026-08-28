// TypeScript / Node.js реалізація In-Memory рушія
import * as crypto from "crypto";

export interface EvaluationContext {
  targetingKey: string;
  attributes?: Record<string, string | number | boolean>;
}

export interface TargetingRule {
  attributeName: string;
  expectedValue: string | number | boolean;
  enabledValue: boolean;
}

export interface FlagDefinition {
  key: string;
  defaultValue: boolean;
  rolloutPercentage: number; // 0 - 100
  whitelistUsers: string[];
  rules: TargetingRule[];
}

export interface EvaluationResult {
  value: boolean;
  reason: "OVERRIDE" | "RULE_MATCH" | "PERCENTAGE_ROLLOUT" | "DEFAULT" | "FLAG_NOT_FOUND";
}

export class FlagEngine {
  private ruleset: Map<string, FlagDefinition> = new Map();

  // Неблокуюче обчислення прапорця в пам'яті
  public evaluate(flagKey: string, ctx: EvaluationContext): EvaluationResult {
    const flag = this.ruleset.get(flagKey);
    if (!flag) {
      return { value: false, reason: "FLAG_NOT_FOUND" };
    }

    // 1. Індивідуальний Whitelist
    if (flag.whitelistUsers.includes(ctx.targetingKey)) {
      return { value: true, reason: "OVERRIDE" };
    }

    // 2. Правила атрибутів
    if (ctx.attributes) {
      for (const rule of flag.rules) {
        const actualValue = ctx.attributes[rule.attributeName];
        if (actualValue !== undefined && actualValue === rule.expectedValue) {
          return { value: rule.enabledValue, reason: "RULE_MATCH" };
        }
      }
    }

    // 3. Відсоткове розважування через хеш
    if (flag.rolloutPercentage > 0 && ctx.targetingKey) {
      const hashInput = `${flagKey}:${ctx.targetingKey}`;
      const hashBuffer = crypto.createHash("md5").update(hashInput).digest();
      const hashInt = hashBuffer.readUInt32BE(0);
      const bucket = hashInt % 100;

      if (bucket < flag.rolloutPercentage) {
        return { value: true, reason: "PERCENTAGE_ROLLOUT" };
      }
    }

    // 4. Дефолтне значення
    return { value: flag.defaultValue, reason: "DEFAULT" };
  }

  // Атомарна підміна карти правил
  public updateRules(newFlags: FlagDefinition[]): void {
    const nextMap = new Map<string, FlagDefinition>();
    for (const f of newFlags) {
      nextMap.set(f.key, f);
    }
    this.ruleset = nextMap; // Атомарна заміна посилання на мапу у V8
  }
}
