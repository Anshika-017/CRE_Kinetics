import { useRef, useState } from "react";
import type { DataPoint } from "../types";
import { parseDelimitedText, dataPointsToCsv, downloadTextFile } from "../utils/csv";
import { SAMPLE_DATASETS } from "../utils/sampleData";

export function DataInput({
  points,
  setPoints,
  onSampleLoaded,
}: {
  points: DataPoint[];
  setPoints: (p: DataPoint[]) => void;
  onSampleLoaded: (suggestedCR0?: number) => void;
}) {
  const [pasteText, setPasteText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function updateCell(idx: number, field: "time" | "concentration", value: string) {
    const next = [...points];
    const num = value === "" ? NaN : Number(value);
    next[idx] = { ...next[idx], [field]: num };
    setPoints(next);
  }

  function addRow() {
    setPoints([...points, { time: NaN, concentration: NaN }]);
  }

  function deleteRow(idx: number) {
    setPoints(points.filter((_, i) => i !== idx));
  }

  function clearAll() {
    setPoints([]);
    setError(null);
  }

  function loadSample(key: string) {
    const sample = SAMPLE_DATASETS.find((s) => s.key === key);
    if (!sample) return;
    setPoints(sample.points);
    setError(null);
    onSampleLoaded(sample.suggestedCR0);
  }

  function handlePaste() {
    try {
      const parsed = parseDelimitedText(pasteText);
      setPoints(parsed);
      setError(null);
    } catch (e: any) {
      setError(e.message || "Could not parse pasted data.");
    }
  }

  function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = parseDelimitedText(String(reader.result));
        setPoints(parsed);
        setError(null);
      } catch (err: any) {
        setError(err.message || "Could not parse CSV file.");
      }
    };
    reader.readAsText(file);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  function exportCsv() {
    downloadTextFile("experimental_data.csv", dataPointsToCsv(points));
  }

  return (
    <div className="panel">
      <h2>01 · Your Data</h2>
      <p className="muted">
        Enter time / concentration pairs manually, paste delimited text, upload a CSV, or load a
        sample dataset. Your data is used exactly as entered — nothing is silently modified.
      </p>

      <div className="sample-buttons">
        {SAMPLE_DATASETS.map((s) => (
          <button key={s.key} className="btn-ghost" onClick={() => loadSample(s.key)} title={s.description}>
            {s.label}
          </button>
        ))}
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>t</th>
            <th>C_A</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {points.map((p, i) => (
            <tr key={i}>
              <td>
                <input
                  type="number"
                  value={Number.isNaN(p.time) ? "" : p.time}
                  onChange={(e) => updateCell(i, "time", e.target.value)}
                />
              </td>
              <td>
                <input
                  type="number"
                  value={Number.isNaN(p.concentration) ? "" : p.concentration}
                  onChange={(e) => updateCell(i, "concentration", e.target.value)}
                />
              </td>
              <td>
                <button className="btn-icon" onClick={() => deleteRow(i)} aria-label={`Delete row ${i + 1}`}>
                  ✕
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="row-controls">
        <button className="btn-ghost" onClick={addRow}>
          + Add row
        </button>
        <button className="btn-ghost" onClick={clearAll}>
          Clear data
        </button>
        <button className="btn-ghost" onClick={() => fileInputRef.current?.click()}>
          Upload CSV
        </button>
        <button className="btn-ghost" onClick={exportCsv} disabled={points.length === 0}>
          Download data as CSV
        </button>
        <input ref={fileInputRef} type="file" accept=".csv,.tsv,.txt" hidden onChange={handleFileUpload} />
      </div>

      <details className="paste-area">
        <summary>Paste tab/comma-separated data</summary>
        <textarea
          rows={5}
          placeholder={"t,C_A\n0,10\n20,8\n40,6"}
          value={pasteText}
          onChange={(e) => setPasteText(e.target.value)}
        />
        <button className="btn-ghost" onClick={handlePaste}>
          Load pasted data
        </button>
      </details>

      {error && <div className="warning-box">{error}</div>}
    </div>
  );
}
