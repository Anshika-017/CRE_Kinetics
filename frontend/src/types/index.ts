export interface DataPoint {
  time: number;
  concentration: number;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  n_points: number;
}

export interface IntegralModel {
  id: string;
  name: string;
  n: number;
  rate_law_latex: string;
  integrated_equation_latex: string;
  transformation: string;
  slope: number | null;
  intercept: number | null;
  r_squared: number | null;
  rmse_transformed: number | null;
  mae_transformed: number | null;
  n_points_used: number;
  valid: boolean;
  reason: string | null;
  k: number | null;
  original_domain_rmse: number | null;
  original_domain_mae: number | null;
  original_domain_max_error: number | null;
  transformed_points: { x: number[]; y: number[] };
  regression_line: { x: number[]; y: number[] } | null;
  rank?: number;
  status?: string | null;
  warning?: string;
}

export interface IntegralResult {
  method: string;
  C_A0: number;
  n_search_range: { min: number; max: number };
  fractional_grid_tested: number[];
  models: IntegralModel[];
  best_model: IntegralModel;
  explanation: string;
}

export interface DerivativeRow {
  t: number;
  C_A: number;
  C_smooth: number;
  dC_A_dt: number;
  minus_r_A: number;
  ln_C_A: number | null;
  ln_minus_r_A: number | null;
}

export interface DifferentialModel {
  id: string;
  name: string;
  n: number;
  graph: string;
  slope: number | null;
  intercept: number | null;
  k: number | null;
  r_squared: number | null;
  rmse?: number | null;
  rate_law_latex: string;
  equation_latex?: string;
  points?: { x: number[]; y: number[] };
  regression_line?: { x: number[]; y: number[] };
  rank?: number;
  status?: string | null;
}

export interface DifferentialResult {
  method: string;
  valid: boolean;
  reason?: string;
  smoothing?: { strength: number; s_parameter: number; description: string };
  derivative_table?: DerivativeRow[];
  models?: DifferentialModel[];
  best_model?: DifferentialModel | null;
  explanation?: string;
}

export interface AutocatalyticResult {
  method: string;
  applicable: boolean;
  reason?: string;
  C_A0?: number;
  C_R0?: number;
  C0?: number;
  rate_law_latex?: string;
  integrated_equation_latex?: string;
  slope?: number | null;
  intercept?: number | null;
  r_squared?: number | null;
  k?: number | null;
  transformed_points?: { x: number[]; y: number[] };
  regression_line?: { x: number[]; y: number[] };
  prediction_curve?: { t: number[]; C_A_predicted: (number | null)[] };
  original_domain_rmse?: number | null;
  original_domain_mae?: number | null;
}

export interface Comparison {
  integral: { n: number | null; k: number | null; r_squared: number | null; rmse: number | null; rate_law_latex: string | null; quality: string };
  differential: { n: number | null; k: number | null; r_squared: number | null; rate_law_latex: string | null; quality: string | null };
  delta_n: number | null;
  methods_agree: boolean | null;
  reasons: string[];
  final_model_name: string;
  final_n: number | null;
  final_k: number | null;
  conclusion: string;
}

export interface AnalyzeResponse {
  validation: ValidationResult;
  units: { concentration_unit: string; time_unit: string; k_units: string | null };
  integral: IntegralResult;
  differential: DifferentialResult;
  autocatalytic: AutocatalyticResult;
  comparison: Comparison;
  assumptions: string[];
}
