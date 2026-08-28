import crypto from 'node:crypto';

// Одноразове підписування рядка чи бінарного буфера
function signPayload(secretKey, payloadString) {
    const hmac = crypto.createHmac('sha256', secretKey);
    hmac.update(payloadString, 'utf8');
    return hmac.digest('hex');
}

// Захищена верифікація з обов'язковою попередньою перевіркою довжини буферів
function verifyPayload(secretKey, payloadString, expectedHexSignature) {
    const computedSignature = crypto.createHmac('sha256', secretKey)
                                    .update(payloadString, 'utf8')
                                    .digest();
    const expectedSignature = Buffer.from(expectedHexSignature, 'hex');

    // Перевірка рівності довжин перед викликом timingSafeEqual:
    // timingSafeEqual викидає виняток RangeError, якщо довжини буферів не збігаються!
    if (computedSignature.length !== expectedSignature.length) {
        return false;
    }

    return crypto.timingSafeEqual(computedSignature, expectedSignature);
}
