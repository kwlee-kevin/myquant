export type QueryPrimitive = string | number | boolean;

export function buildQuery(
  params: Record<string, QueryPrimitive | QueryPrimitive[] | undefined | null>
): string {
  const search = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    if (Array.isArray(value)) {
      value.forEach((item) => {
        if (item !== undefined && item !== null && item !== "") {
          search.append(key, String(item));
        }
      });
      return;
    }
    search.append(key, String(value));
  });

  const query = search.toString();
  return query ? `?${query}` : "";
}

export async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });

  if (!response.ok) {
    const error = new Error(`HTTP ${response.status}`) as Error & { status?: number };
    error.status = response.status;
    throw error;
  }

  return (await response.json()) as T;
}
