export async function sendRequest(
  method: string,
  path: string,
  body?: any
): Promise<any> {
  const token = localStorage.getItem('token');
  const headers: any = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`/api${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  return await res.json();
}