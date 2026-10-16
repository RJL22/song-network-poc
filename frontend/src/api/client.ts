const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

let onUnauthorized: (() => void) | null = null;
export function setUnauthorized(fn : () => void) {onUnauthorized = fn;}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function apiFetch<T>(path: string, options: RequestInit = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers, credentials: "include" });

  if (response.status === 401) {
    if (onUnauthorized) onUnauthorized();
    throw new ApiError(401, "Unauthorized");
  }

  if (!response.ok) {
    let detail = `API error: ${response.status}`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") {
        detail = body.detail;
      }
      // else: leave the generic message — see note below on 422s
    } catch {
      // response wasn't JSON (or was empty) — fall back to the generic message
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
