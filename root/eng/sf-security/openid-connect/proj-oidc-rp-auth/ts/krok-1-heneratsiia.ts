import crypto from 'crypto';

function b64urlEncode(buffer: Buffer): string {
  return buffer.toString('base64url');
}

export function generatePkcePair(): { codeVerifier: string; codeChallenge: string } {
  const verifierBytes = crypto.randomBytes(32);
  const codeVerifier = b64urlEncode(verifierBytes);
  
  const hash = crypto.createHash('sha256').update(codeVerifier, 'ascii').digest();
  const codeChallenge = b64urlEncode(hash);
  
  return { codeVerifier, codeChallenge };
}

export function createAuthorizationUrl(
  authorizationEndpoint: string,
  clientId: string,
  redirectUri: string,
  scope: string = 'openid profile email'
) {
  const state = b64urlEncode(crypto.randomBytes(24));
  const nonce = b64urlEncode(crypto.randomBytes(24));
  const { codeVerifier, codeChallenge } = generatePkcePair();

  const url = new URL(authorizationEndpoint);
  url.searchParams.set('client_id', clientId);
  url.searchParams.set('response_type', 'code');
  url.searchParams.set('scope', scope);
  url.searchParams.set('redirect_uri', redirectUri);
  url.searchParams.set('state', state);
  url.searchParams.set('nonce', nonce);
  url.searchParams.set('code_challenge', codeChallenge);
  url.searchParams.set('code_challenge_method', 'S256');
  url.searchParams.set('response_mode', 'query');

  return {
    authUrl: url.toString(),
    state,
    nonce,
    codeVerifier,
  };
}
