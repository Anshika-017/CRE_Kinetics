import { useState } from "react";
import type { AnalyzeResponse, DataPoint } from "./types";
import { analyzeData } from "./api/client";
import { DataInput } from "./components/DataInput";
import { ValidationPanel } from "./components/ValidationPanel";
import { IntegralAnalysis } from "./components/IntegralAnalysis";
import { DifferentialAnalysis } from "./components/DifferentialAnalysis";
import { AutocatalyticAnalysis } from "./components/AutocatalyticAnalysis";
import { FinalResult } from "./components/FinalResult";

const LOADING_STEPS = [
  "Validating experimental data…",
  "Testing integral transformations…",
  "Smoothing curve and estimating dC_A/dt…",
  "Fitting differential rate law…",
  "Comparing kinetic models…",
  "Building final kinetic model…",
];

export default function App() {
  const [points, setPoints] = useState<DataPoint[]>([]);
  const [concentrationUnit, setConcentrationUnit] = useState("mol/L");
  const [timeUnit, setTimeUnit] = useState("s");
  const [smoothing, setSmoothing] = useState(0.3);
  const [cr0, setCr0] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[] | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [rawUsed, setRawUsed] = useState<DataPoint[]>([]);

  async function handleAnalyze() {
    setError(null);
    setValidationErrors(null);
    setResult(null);

    const cleanPoints = points.filter((p) => !Number.isNaN(p.time) && !Number.isNaN(p.concentration));
    if (cleanPoints.length < 3) {
      setError("Enter at least 3 valid (t, C_A) rows before analyzing.");
      return;
    }

    setLoading(true);
    let step = 0;
    const interval = setInterval(() => {
      step = Math.min(step + 1, LOADING_STEPS.length - 1);
      setLoadingStep(step);
    }, 350);

    const resp = await analyzeData(cleanPoints, {
      concentrationUnit,
      timeUnit,
      smoothingStrength: smoothing,
      nSearchMin: -2,
      nSearchMax: 5,
      autocatalyticCR0: cr0 === "" ? null : Number(cr0),
    });

    clearInterval(interval);
    setLoading(false);
    setLoadingStep(0);

    if (!resp.ok || !resp.result) {
      if (resp.validation) {
        setValidationErrors(resp.validation.errors);
      }
      setError(resp.message || "Analysis failed.");
      return;
    }
    setRawUsed(cleanPoints);
    setResult(resp.result);
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div className="hero-eyebrow">CHEMICAL REACTION ENGINEERING</div>
        <h1>REACTION KINETICS</h1>
        <p className="hero-sub">
          Decode concentration–time data into a transparent rate law — integral and differential
          methods, side by side, with every equation and regression visible.
        </p>
      </header>

      <main className="content">
        <DataInput
          points={points}
          setPoints={setPoints}
          onSampleLoaded={(suggestedCR0) => {
            if (suggestedCR0 != null) setCr0(String(suggestedCR0));
          }}
        />

        <div className="panel">
          <h2>Settings</h2>
          <div className="settings-grid">
            <label>
              Concentration unit
              <input value={concentrationUnit} onChange={(e) => setConcentrationUnit(e.target.value)} />
            </label>
            <label>
              Time unit
              <input value={timeUnit} onChange={(e) => setTimeUnit(e.target.value)} />
            </label>
            <label>
              Smoothing strength ({smoothing.toFixed(2)})
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={smoothing}
                onChange={(e) => setSmoothing(Number(e.target.value))}
              />
            </label>
            <label>
              Autocatalytic C_R0 (optional)
              <input
                type="number"
                placeholder="leave blank to skip"
                value={cr0}
                onChange={(e) => setCr0(e.target.value)}
              />
            </label>
          </div>
          <button className="btn-primary" onClick={handleAnalyze} disabled={loading}>
            {loading ? "Analyzing…" : "Analyze"}
          </button>
          {loading && <div className="loading-step">{LOADING_STEPS[loadingStep]}</div>}
          {error && <div className="warning-box">{error}</div>}
          {validationErrors && (
            <div className="error-box">
              <strong>Fix these before analyzing:</strong>
              <ul>
                {validationErrors.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {result && (
          <>
            <ValidationPanel validation={result.validation} />
            <IntegralAnalysis integral={result.integral} raw={rawUsed} />
            <DifferentialAnalysis differential={result.differential} />
            <AutocatalyticAnalysis result={result.autocatalytic} raw={rawUsed} />
            <FinalResult result={result} />
          </>
        )}
      </main>

      <footer className="footer">
        <p>
          This tool performs transparent numerical regression (OLS, spline smoothing) — no machine
          learning is used to determine reaction kinetics.
        </p>
      </footer>
    </div>
  );
}
