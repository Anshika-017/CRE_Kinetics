import type { DifferentialResult } from "../types";
import { Eq } from "./Equation";
import { Chart } from "./Chart";
import { downloadTextFile } from "../utils/csv";
import Papa from "papaparse";

export function DifferentialAnalysis({ differential }: { differential: DifferentialResult }) {
  if (!differential.valid) {
    return (
      <div className="panel">
        <h2>04 · Differential Method of Analysis</h2>
        <div className="warning-box">{differential.reason}</div>
      </div>
    );
  }

  const best = differential.best_model;
  const table = differential.derivative_table || [];

  function exportTable() {
    downloadTextFile("differential_derivative_table.csv", Papa.unparse(table));
  }

  return (
    <div className="panel">
      <h2>04 · Differential Method of Analysis</h2>
      <p className="muted">{differential.explanation}</p>
      <p className="muted">
        {differential.smoothing?.description} (smoothing strength ={" "}
        {differential.smoothing?.strength.toFixed(2)}). Raw data are used for the integral method above; this
        smoothed representation is used only to estimate dC_A/dt.
      </p>

      <Chart
        title="Raw data vs. smoothed C_A(t)"
        xLabel="t"
        yLabel="C_A"
        series={[
          { x: table.map((r) => r.t), y: table.map((r) => r.C_A), name: "Experimental data", mode: "markers", color: "#7dd3fc" },
          { x: table.map((r) => r.t), y: table.map((r) => r.C_smooth), name: "Smoothed curve", mode: "lines", color: "#facc15" },
        ]}
      />

      {best && (
        <>
          <h3>Rate law regression: ln(-r_A) vs ln(C_A)</h3>
          <Eq tex={best.equation_latex || "\\ln(-r_A) = \\ln k + n\\ln C_A"} />
          <div className="metric-grid">
            <Metric label="n (slope)" value={best.n != null ? best.n.toFixed(3) : "—"} />
            <Metric label="k = exp(intercept)" value={best.k != null ? best.k.toExponential(4) : "—"} />
            <Metric label="R²" value={best.r_squared != null ? best.r_squared.toFixed(4) : "—"} />
          </div>
          {best.points && (
            <Chart
              title="ln(-r_A) vs ln(C_A)"
              xLabel="ln(C_A)"
              yLabel="ln(-r_A)"
              series={[
                { x: best.points.x, y: best.points.y, name: "Differential data points", mode: "markers", color: "#7dd3fc" },
                ...(best.regression_line
                  ? [{ x: best.regression_line.x, y: best.regression_line.y, name: "Regression line", mode: "lines" as const, color: "#a78bfa" }]
                  : []),
              ]}
            />
          )}
        </>
      )}

      <h3>Differential model comparison</h3>
      <div className="table-scroll">
        <table className="results-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Model</th>
              <th>n</th>
              <th>Graph</th>
              <th>Slope</th>
              <th>k</th>
              <th>R²</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {(differential.models || []).map((m) => (
              <tr key={m.id} className={m.status === "BEST" ? "row-best" : ""}>
                <td>{m.rank}</td>
                <td>{m.name}</td>
                <td>{m.n.toFixed(3)}</td>
                <td>{m.graph}</td>
                <td>{m.slope != null ? m.slope.toExponential(3) : "—"}</td>
                <td>{m.k != null ? m.k.toExponential(3) : "—"}</td>
                <td>{m.r_squared != null ? m.r_squared.toFixed(4) : "—"}</td>
                <td>{m.status === "BEST" ? "BEST" : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3>Derivative data table</h3>
      <button className="btn-ghost" onClick={exportTable}>
        Download derivative table (CSV)
      </button>
      <div className="table-scroll">
        <table className="results-table small">
          <thead>
            <tr>
              <th>t</th>
              <th>C_A</th>
              <th>C_smooth</th>
              <th>dC_A/dt</th>
              <th>-r_A</th>
              <th>ln(C_A)</th>
              <th>ln(-r_A)</th>
            </tr>
          </thead>
          <tbody>
            {table.map((r, i) => (
              <tr key={i}>
                <td>{r.t.toFixed(2)}</td>
                <td>{r.C_A.toFixed(3)}</td>
                <td>{r.C_smooth.toFixed(3)}</td>
                <td>{r.dC_A_dt.toExponential(3)}</td>
                <td>{r.minus_r_A.toExponential(3)}</td>
                <td>{r.ln_C_A != null ? r.ln_C_A.toFixed(3) : "—"}</td>
                <td>{r.ln_minus_r_A != null ? r.ln_minus_r_A.toFixed(3) : "—"}</td>
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
