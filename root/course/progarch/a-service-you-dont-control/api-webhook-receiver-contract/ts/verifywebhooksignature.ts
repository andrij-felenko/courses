import crypto from 'node:crypto';

export interface WebhookValidationResult {
  isValid: boolean;
  error?: string;
}

export function verifyWebhookSignature(
  rawBody: Buffer,
  signatureHeader: string,
  secret: string,
  toleranceSeconds: number = 300
): WebhookValidationResult {
  const parts = signatureHeader.split(',');
  let timestamp: number | null = null;
  const signatures: string[] = [];

  for (const part of parts) {
    const [key, value] = part.split('=');
    if (key === 't' && value) {
      timestamp = parseInt(value, 10);
    } else if (key === 'v1' && value) {
      signatures.push(value);
    }
  }

  if (!timestamp || isNaN(timestamp) || signatures.length === 0) {
    return { isValid: false, error: 'MISSING_SIGNATURE_OR_TIMESTAMP' };
  }

  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - timestamp) > toleranceSeconds) {
    return { isValid: false, error: 'TIMESTAMP_OUT_OF_TOLERANCE' };
  }

  const signedPayload = Buffer.concat([
    Buffer.from(`${timestamp}.`, 'utf8'),
    rawBody
  ]);

  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(signedPayload)
    .digest('hex');

  const expectedBuffer = Buffer.from(expectedSignature, 'utf8');

  for (const sig of signatures) {
    const clientBuffer = Buffer.from(sig, 'utf8');
    if (
      clientBuffer.length === expectedBuffer.length &&
      crypto.timingSafeEqual(clientBuffer, expectedBuffer)
    ) {
      return { isValid: true };
    }
  }

  return { isValid: false, error: 'INVALID_SIGNATURE' };
}
