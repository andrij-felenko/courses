// web/routes.ts — лише переклад HTTP ↔ виклик сценарію
import { Router } from "express";
import { PlaceOrder, OutOfStock, UnknownProduct } from "../application/placeOrder";

export function makeRoutes(place: PlaceOrder): Router {
  const r = Router();
  r.post("/orders", (req, res) => {
    try {
      const result = place.run(req.body.items, req.body.promo);
      res.status(201).json(result);
    } catch (e) {
      if (e instanceof UnknownProduct)
        return res.status(404).json({ error: `немає товару ${e.message}` });
      if (e instanceof OutOfStock)
        return res.status(409).json({ error: `замало ${e.message}` });
      throw e;
    }
  });
  return r;
}
