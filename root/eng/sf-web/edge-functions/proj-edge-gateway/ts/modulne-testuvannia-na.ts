import { describe, it, expect, vi } from 'vitest';
import worker from './gateway';

describe('Edge Gateway Suite', () => {
  const env = {
    JWT_SECRET: 'test_secret_key_12345',
    UPSTREAM_ORIGIN: 'https://api.internal.local'
  };

  it('повинен негайно відхиляти запити без заголовка Authorization', async () => {
    const request = new Request('https://api.example.com/v1/orders', {
      method: 'GET'
    });
    const ctx = { waitUntil: vi.fn(), passThroughOnException: vi.fn() };

    const response = await worker.fetch(request, env, ctx as any);

    expect(response.status).toBe(401);
    const body = await response.json();
    expect(body.error).toContain('Missing or malformed Authorization');
  });

  it('повинен успішно пропускати валідний JWT токен та додавати заголовки', async () => {
    // Генерація валідного тестового токена через WebCrypto
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      'raw',
      encoder.encode(env.JWT_SECRET),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign']
    );

    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).replace(/=/g, '');
    const payload = btoa(JSON.stringify({
      sub: 'usr_998877',
      role: 'admin',
      exp: Math.floor(Date.now() / 1000) + 3600
    })).replace(/=/g, '');

    const signatureBuf = await crypto.subtle.sign('HMAC', key, encoder.encode(`${header}.${payload}`));
    const signature = btoa(String.fromCharCode(...new Uint8Array(signatureBuf)))
      .replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');

    const validToken = `${header}.${payload}.${signature}`;

    // Мок для глобального fetch до Origin
    globalThis.fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify({ status: 'ok' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    }));

    const request = new Request('https://api.example.com/v1/orders', {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${validToken}` }
    });
    const ctx = { waitUntil: vi.fn(), passThroughOnException: vi.fn() };

    const response = await worker.fetch(request, env, ctx as any);

    expect(response.status).toBe(200);
    expect(response.headers.get('Strict-Transport-Security')).toBeDefined();
    expect(response.headers.get('X-AB-Variant')).toBeDefined();
  });
});
