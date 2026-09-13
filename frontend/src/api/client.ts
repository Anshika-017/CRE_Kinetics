import type { AnalyzeResponse, DataPoint } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface AnalyzeOptions {
  concentrationUnit: string;
  timeUnit: string;
  smoothingStrength: number;
  nSearchMin: number;
  nSearchMax: number;
  autocatalyticCR0: number | null;
}

export interface AnalyzeApiResult {
  ok: boolean;
  result?: AnalyzeResponse;
  validation?: { errors: string[]; warnings: string[]; valid: boolean; n_points: number };
  message?: string;
}

export async function analyzeData(data: DataPoint[], opts: AnalyzeOptions): Promise<AnalyzeApiResult> {
  try {
    const resp = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        data,
        concentration_unit: opts.concentrationUnit,
        time_unit: opts.timeUnit,
        smoothing_strength: opts.smoothingStrength,
        n_search_min: opts.nSearchMin,
        n_search_max: opts.nSearchMax,
        autocatalytic_C_R0: opts.autocatalyticCR0,
      }),
    });

    if (resp.status === 422) {
      const body = await resp.json();
      return { ok: false, validation: body?.detail?.validation, message: "Data validation failed." };
    }
    if (!resp.ok) {
      return { ok: false, message: `Server error (${resp.status}). Is the backend running at ${API_BASE_URL}?` };
    }
    const result = (await resp.json()) as AnalyzeResponse;
    return { ok: true, result };
  } catch (err) {
    return {
      ok: false,
      message: `Could not reach backend at ${API_BASE_URL}. Check VITE_API_BASE_URL and that the server is running.`,
    };
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const resp = await fetch(`${API_BASE_URL}/api/health`);
    return resp.ok;
  } catch {
    return false;
  }
}
