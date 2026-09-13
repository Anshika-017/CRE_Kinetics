import type { DataPoint, IntegralResult } from "../types";
import { Eq } from "./Equation";
import { Chart } from "./Chart";
import { downloadTextFile } from "../utils/csv";
import Papa from "papaparse";

export function IntegralAnalysis({ integral, raw }: { integral: IntegralResult; raw: DataPoint[] }) {
  const best = integral.best_model;

  function exportModelTable() {
    const rows = integral.models.map((m) => ({
      rank: m.rank,
      model: m.name,
      n: m.n,
      transformation: m.transformation,
      r_squared: m.r_squared,
      rmse_transformed: m.rmse_transformed,
      k: m.k,
      status: m.status || "",
    }));
    downloadTextFile("integral_model_comparison.csv", Papa.unparse(rows));
  }

  return (
    <div className="panel">
      <h2>03 · Integral Method of Analysis</h2>
      <p className="muted">{integral.explanation}</p>
      <Eq tex={"-r_A = -\\frac{dC_A}{dt} = kC_A^n"} />

      <h3>Best-fit model: {best.name}</h3>
      <Eq tex={best.rate_law_latex} />
      <Eq tex={best.integrated_equation_latex} />
      <p className="muted">Linear form: {best.transformation}</p>

      <div className="metric-grid">
        <Metric label="Reaction order n" value={best.n.toFixed(3)} />
        <Metric label="Rate constant k" value={best.k != null ? best.k.toExponential(4) : "—"} />
        <Metric label="R² (transformed)" value={best.r_squared != null ? best.r_squared.toFixed(4) : "—"} />
        <Metric label="Slope" value={best.slope != null ? best.slope.toExponential(4) : "—"} />
        <Metric label="Intercept" value={best.intercept != null ? best.intercept.toExponential(4) : "—"} />
        <Metric
          label="Original-domain RMSE"
          value={best.original_domain_rmse != null ? best.original_domain_rmse.toFixed(4) : "—"}
        />
      </div>

      {best.warning && <div className="warning-box">{best.warning}</div>}

      <Chart
        title={`${best.name}: ${best.transformation}`}
        xLabel="t"
        yLabel="transformed C_A"
        series={[
          { x: best.transformed_points.x, y: best.transformed_points.y, name: "Experimental (transformed)", mode: "markers", color: "#7dd3fc" },
          ...(best.regression_line
            ? [{ x: best.regression_line.x, y: best.regression_line.y, name: "Regression line", mode: "lines" as const, color: "#a78bfa" }]
            : []),
        ]}
      />

      <h3>Original-domain validation: experimental vs. predicted C_A(t)</h3>
      <Chart
        title="Experimental data vs. reconstructed model curve"
        xLabel={`t`}
        yLabel="C_A"
        series={[
          { x: raw.map((p) => p.time), y: raw.map((p) => p.concentration), name: "Experimental", mode: "markers", color: "#7dd3fc" },
          {
            x: [...raw].sort((a, b) => a.time - b.time).map((p) => p.time),
            y: predictCurve(best, raw),
            name: "Selected kinetic model",
            mode: "lines",
            color: "#facc15",
          },
        ]}
      />

      <details className="calc-trace">
        <summary>How did we get this result? (calculation trace)</summary>
        <ol>
          <li>
            Assume <Eq tex={best.rate_law_latex} block={false} /> and write the batch-reactor mass balance for
            constant volume: <Eq tex={"-\\frac{dC_A}{dt} = kC_A^n"} block={false} />.
          </li>
          <li>
            Integrate to obtain <Eq tex={best.integrated_equation_latex} block={false} />, which is linear when
            plotting {best.transformation}.
          </li>
          <li>
            Ordinary least-squares regression on the raw experimental points gives slope ={" "}
            {best.slope?.toExponential(4)} and intercept = {best.intercept?.toExponential(4)}, with R² ={" "}
            {best.r_squared?.toFixed(4)}.
          </li>
          <li>
            The rate constant is recovered from the slope/intercept relationship for this model, giving k ={" "}
            {best.k != null ? best.k.toExponential(4) : "undefined"}.
          </li>
        </ol>
      </details>

      <h3>Candidate model comparison</h3>
      <button className="btn-ghost" onClick={exportModelTable}>
        Download comparison table (CSV)
      </button>
      <div className="table-scroll">
        <table className="results-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Model</th>
              <th>n</th>
              <th>Transformation</th>
              <th>R²</th>
              <th>RMSE</th>
              <th>k</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {integral.models.map((m) => (
              <tr key={m.id} className={m.status === "BEST" ? "row-best" : ""}>
                <td>{m.rank}</td>
                <td>{m.name}</td>
                <td>{m.n.toFixed(3)}</td>
                <td>{m.transformation}</td>
                <td>{m.r_squared != null ? m.r_squared.toFixed(4) : "—"}</td>
                <td>{m.rmse_transformed != null ? m.rmse_transformed.toExponential(2) : "—"}</td>
                <td>{m.k != null ? m.k.toExponential(3) : "—"}</td>
                <td>{m.status === "BEST" ? "BEST" : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  );
}

function predictCurve(best: IntegralResult["best_model"], raw: DataPoint[]): (number | null)[] {
  // Reconstruct C_A(t) client-side for display consistency using the same
  // closed-form relationships the backend used (mirrors backend/app/kinetics/models.py).
  const sorted = [...raw].sort((a, b) => a.time - b.time);
  const C0 = best.n === 0 || true ? sorted[0].concentration : sorted[0].concentration; // C_A0 from first sorted point
  const k = best.k ?? 0;
  const n = best.n;
  return sorted.map((p) => {
    const t = p.time;
    if (Math.abs(n) < 1e-9) {
      const c = C0 - k * t;
      return c >= 0 ? c : null;
    }
    if (Math.abs(n - 1) < 1e-9) {
      return C0 * Math.exp(-k * t);
    }
    const oneMinusN = 1 - n;
    const base = Math.pow(C0, oneMinusN) - oneMinusN * k * t;
    if (base < 0) return null;
    return Math.pow(base, 1 / oneMinusN);
  });
}
