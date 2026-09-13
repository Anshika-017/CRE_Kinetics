import type { AutocatalyticResult, DataPoint } from "../types";
import { Eq } from "./Equation";
import { Chart } from "./Chart";

export function AutocatalyticAnalysis({ result, raw }: { result: AutocatalyticResult; raw: DataPoint[] }) {
  return (
    <div className="panel">
      <h2>05 · Autocatalytic Check (A + R → R + R)</h2>
      {!result.applicable ? (
        <div className="warning-box">{result.reason}</div>
      ) : (
        <>
          <Eq tex={result.rate_law_latex!} />
          <Eq tex={result.integrated_equation_latex!} />
          <div className="metric-grid">
            <Metric label="C_A0" value={result.C_A0!.toFixed(3)} />
            <Metric label="C_R0" value={result.C_R0!.toFixed(3)} />
            <Metric label="C_0 = C_A0 + C_R0" value={result.C0!.toFixed(3)} />
            <Metric label="k = slope / C_0" value={result.k != null ? result.k.toExponential(4) : "—"} />
            <Metric label="R²" value={result.r_squared != null ? result.r_squared.toFixed(4) : "—"} />
          </div>

          <Chart
            title="Autocatalytic linear plot"
            xLabel="t"
            yLabel="ln[C_A0(C_0-C_A) / (C_A(C_0-C_A0))]"
            series={[
              { x: result.transformed_points!.x, y: result.transformed_points!.y, name: "Transformed data", mode: "markers", color: "#7dd3fc" },
              ...(result.regression_line
                ? [{ x: result.regression_line.x, y: result.regression_line.y, name: "Regression line", mode: "lines" as const, color: "#a78bfa" }]
                : []),
            ]}
          />

          {result.prediction_curve && (
            <Chart
              title="Experimental vs. autocatalytic model prediction"
              xLabel="t"
              yLabel="C_A"
              series={[
                { x: raw.map((p) => p.time), y: raw.map((p) => p.concentration), name: "Experimental", mode: "markers", color: "#7dd3fc" },
                { x: result.prediction_curve.t, y: result.prediction_curve.C_A_predicted, name: "Autocatalytic model", mode: "lines", color: "#facc15" },
              ]}
            />
          )}
        </>
      )}
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
