export async function handleBackchannelLogout(
  logoutTokenRaw: string,
  expectedIssuer: string,
  expectedClientId: string,
  jwksManager: JwksManager
): Promise<string> {
  const parts = logoutTokenRaw.split('.');
  if (parts.length !== 3) throw new Error('Некоректний формат Logout Token');

  const header = JSON.parse(Buffer.from(parts[0], 'base64url').toString('utf8'));
  const publicKey = await jwksManager.getKey(header.kid);

  const verify = crypto.createVerify('RSA-SHA256');
  verify.update(`${parts[0]}.${parts[1]}`, 'ascii');
  const isValid = verify.verify(publicKey, Buffer.from(parts[2], 'base64url'));
  if (!isValid) throw new Error('Підпис Logout Token недійсний');

  const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString('utf8'));

  if (payload.iss !== expectedIssuer) throw new Error('Невідповідність iss у Logout Token');
  if (payload.aud !== expectedClientId && !(Array.isArray(payload.aud) && payload.aud.includes(expectedClientId))) {
    throw new Error('Невідповідність aud у Logout Token');
  }
  if (payload.nonce) throw new Error('Logout Token не може містити nonce');
  if (!payload.events || !payload.events['http://schemas.openid.net/event/backchannel-logout']) {
    throw new Error('Відсутній маркер події backchannel-logout');
  }

  const sub = payload.sub || payload.sid;
  if (!sub) throw new Error('Logout Token не містить sub або sid');
  return sub;
}
