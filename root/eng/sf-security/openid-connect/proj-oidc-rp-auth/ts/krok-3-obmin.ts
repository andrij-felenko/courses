export async function exchangeCodeForTokens(
  tokenEndpoint: string,
  clientId: string,
  clientSecret: string | null,
  code: string,
  codeVerifier: string,
  redirectUri: string
): Promise<{ id_token: string; access_token: string; refresh_token?: string; expires_in: number }> {
  const body = new URLSearchParams();
  body.set('grant_type', 'authorization_code');
  body.set('code', code);
  body.set('redirect_uri', redirectUri);
  body.set('client_id', clientId);
  body.set('code_verifier', codeVerifier);
  if (clientSecret) {
    body.set('client_secret', clientSecret);
  }

  const res = await fetch(tokenEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Accept: 'application/json',
      'User-Agent': 'OIDC-RelyingParty-Engine/1.0',
    },
    body: body.toString(),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Помилка обміну коду на токени: HTTP ${res.status} - ${errText}`);
  }

  return res.json();
}
