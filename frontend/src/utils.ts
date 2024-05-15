export async function sendRequest(
  method: string,
  path: string,
  body?: any
): Promise<any> {
  const res = await fetch(`/api${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  return await res.json();
}