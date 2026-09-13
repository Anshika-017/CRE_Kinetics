import type { ValidationResult } from "../types";

export function ValidationPanel({ validation }: { validation: ValidationResult }) {
  return (
    <div className="panel">
      <h2>02 · Data Validation</h2>
      <p className={validation.valid ? "status-ok" : "status-bad"}>
        {validation.valid ? "✓" : "✗"} {validation.n_points} observation(s){" "}
        {validation.valid ? "passed validation." : "failed validation."}
      </p>
      {validation.errors.length > 0 && (
        <div className="error-box">
          <strong>Errors:</strong>
          <ul>
            {validation.errors.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </div>
      )}
      {validation.warnings.length > 0 && (
        <div className="warning-box">
          <strong>Warnings:</strong>
          <ul>
            {validation.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}
      {validation.valid && validation.warnings.length === 0 && (
        <p className="muted">No data-quality concerns detected.</p>
      )}
    </div>
  );
}
