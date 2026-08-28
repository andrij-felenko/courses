import { Request, Response, NextFunction } from 'express';

export interface CorsOptions {
  allowedOrigins: string[];
  allowedOriginPatterns?: RegExp[];
  allowedMethods?: string[];
  allowedHeaders?: string[];
  exposedHeaders?: string[];
  allowCredentials?: boolean;
  maxAgeSeconds?: number;
}

export function createCorsMiddleware(options: CorsOptions) {
  const {
    allowedOrigins,
    allowedOriginPatterns = [],
    allowedMethods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders = ['Content-Type', 'Authorization', 'X-Requested-With', 'X-Request-Id'],
    exposedHeaders = ['X-Total-Count', 'X-RateLimit-Remaining'],
    allowCredentials = true,
    maxAgeSeconds = 86400,
  } = options;

  const originSet = new Set(allowedOrigins);

  const isOriginAllowed = (origin: string): boolean => {
    if (originSet.has(origin)) return true;
    return allowedOriginPatterns.some((pattern) => pattern.test(origin));
  };

  return (req: Request, res: Response, next: NextFunction): void => {
    const origin = req.headers.origin;

    // Якщо заголовок Origin відсутній (не браузер) — передаємо керування далі
    if (!origin || typeof origin !== 'string') {
      next();
      return;
    }

    if (isOriginAllowed(origin)) {
      // Суворе встановлення точного Origin замість *
      res.setHeader('Access-Control-Allow-Origin', origin);
      res.setHeader('Vary', 'Origin');

      if (allowCredentials) {
        res.setHeader('Access-Control-Allow-Credentials', 'true');
      }

      if (exposedHeaders.length > 0) {
        res.setHeader('Access-Control-Expose-Headers', exposedHeaders.join(', '));
      }

      // Обробка попереднього запиту Preflight
      if (req.method === 'OPTIONS') {
        res.setHeader('Access-Control-Allow-Methods', allowedMethods.join(', '));
        res.setHeader('Access-Control-Allow-Headers', allowedHeaders.join(', '));
        res.setHeader('Access-Control-Max-Age', maxAgeSeconds.toString());
        res.setHeader('Content-Length', '0');
        res.status(204).end();
        return;
      }
    } else if (req.method === 'OPTIONS') {
      // Відхилення неавторизованого Preflight
      res.status(403).end();
      return;
    }

    next();
  };
}
