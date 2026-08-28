export async function fetchUserInfo(
  userinfoEndpoint: string,
  accessToken: string
): Promise<Record<string, any>> {
  const res = await fetch(userinfoEndpoint, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      Accept: 'application/json',
      'User-Agent': 'OIDC-RelyingParty-Engine/1.0',
    },
  });

  if (!res.ok) {
    throw new Error(`Помилка отримання UserInfo: HTTP ${res.status}`);
  }

  return res.json();
}
