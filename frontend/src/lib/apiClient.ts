import { API_BASE_URL } from "@/config/env";

export class ApiError extends Error {
  constructor(message: string, public readonly status?: number) {
    super(message);
    this.name = "ApiError";
  }
}

export async function postJson<TResponse, TBody>(
  path: string,
  body: TBody
): Promise<TResponse> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
  } catch {
    throw new ApiError(
      `Cannot reach the Orion API at ${API_BASE_URL}. Check that FastAPI is running.`
    );
  }

  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) message = payload.detail;
    } catch {
      // Keep the status-based message when the response body is not JSON.
    }
    throw new ApiError(message, response.status);
  }

  return (await response.json()) as TResponse;
}