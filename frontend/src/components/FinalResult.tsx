import type { AnalyzeResponse } from "../types";
import { Eq } from "./Equation";
import { downloadTextFile } from "../utils/csv";

export function FinalResult({ result }: { result: AnalyzeResponse }) {
  const c = result.comparison;

  function exportFullReport() {
    const lines: string[] = [];
    lines.push("REACTION KINETICS — FINAL ANALYSIS REPORT");
    lines.push("");
    lines.push(c.conclusion);
    lines.push("");
    lines.push(`Integral method: n = ${c.integral.n}, k = ${c.integral.k}, R2 = ${c.integral.r_squared}`);
    lines.push(`Differential method: n = ${c.differential.n}, k = ${c.differential.k}, R2 = ${c.differential.r_squared}`);
    lines.push(`Methods agree: ${c.methods_agree}`);
    lines.push("");
    lines.push("Reasons:");
    c.reasons.forEach((r) => lines.push(`- ${r}`));
    lines.push("");
    lines.push("Assumptions:");
    result.assumptions.forEach((a) => lines.push(`- ${a}`));
    downloadTextFile("kinetic_analysis_report.txt", lines.join("\n"), "text/plain");
  }

  return (
    <div className="panel final-panel">
      <h2>06 · Final Kinetic Model</h2>
      <Eq tex={"-r_A = kC_A^n"} />
      <div className="metric-grid">
        <Metric label="Reaction order n" value={c.final_n != null ? c.final_n.toFixed(3) : "—"} />
        <Metric
          label="Rate constant k"
          value={c.final_k != null ? `${c.final_k.toExponential(4)} ${result.units.k_units ?? ""}` : "—"}
        />
        <Metric label="Integral R²" value={c.integral.r_squared != null ? c.integral.r_squared.toFixed(4) : "—"} />
        <Metric label="Differential R²" value={c.differential.r_squared != null ? c.differential.r_squared.toFixed(4) : "—"} />
      </div>

      <h3>Integral vs. Differential comparison</h3>
      <table className="results-table">
        <thead>
          <tr>
            <th></th>
            <th>Integral Method</th>
            <th>Differential Method</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Reaction order n</td>
            <td>{c.integral.n?.toFixed(3) ?? "—"}</td>
            <td>{c.differential.n?.toFixed(3) ?? "—"}</td>
          </tr>
          <tr>
            <td>Rate constant k</td>
            <td>{c.integral.k != null ? c.integral.k.toExponential(3) : "—"}</td>
            <td>{c.differential.k != null ? c.differential.k.toExponential(3) : "—"}</td>
          </tr>
          <tr>
            <td>R²</td>
            <td>{c.integral.r_squared?.toFixed(4) ?? "—"}</td>
            <td>{c.differential.r_squared?.toFixed(4) ?? "—"}</td>
          </tr>
          <tr>
            <td>Fit quality</td>
            <td>{c.integral.quality}</td>
            <td>{c.differential.quality ?? "—"}</td>
          </tr>
        </tbody>
      </table>

      <div className={c.methods_agree ? "status-ok" : "warning-box"}>
        {c.methods_agree
          ? "Integral and differential methods agree on reaction order."
          : "Integral and differential methods do not agree strongly — see explanation below."}
      </div>

      <h3>Why this model?</h3>
      <ul className="reasons-list">
        {c.reasons.map((r, i) => (
          <li key={i}>{r}</li>
        ))}
      </ul>

      <h3>Assumptions used in this analysis</h3>
      <ul className="assumptions-list">
        {result.assumptions.map((a, i) => (
          <li key={i}>{a}</li>
        ))}
      </ul>
      <p className="muted">
        Note: the reaction order reported here is an empirical fit to the supplied concentration-time data.
        It does not by itself establish a reaction mechanism.
      </p>

      <button className="btn-primary" onClick={exportFullReport}>
        Download full report (.txt)
      </button>
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
