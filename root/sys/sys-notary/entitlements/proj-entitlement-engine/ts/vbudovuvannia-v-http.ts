import { Request, Response, NextFunction } from "express";
import { EntitlementEngine, FeatureKey } from "./entitlement-engine";

export function requireFeature(engine: EntitlementEngine, feature: FeatureKey) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const tenantId = req.headers["x-tenant-id"] as string;
    if (!tenantId) {
      return res.status(401).json({ error: "Missing tenant identification" });
    }

    const allowed = await engine.checkFeature(tenantId, feature);
    if (!allowed) {
      return res.status(403).json({
        type: "https://api.example.com/errors/feature-gated",
        title: "Feature Gated by Subscription",
        status: 403,
        detail: `The feature '${feature}' is not included in your active subscription tier.`,
        code: "feature_gated",
        feature,
      });
    }

    next();
  };
}
