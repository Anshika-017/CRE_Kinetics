import Papa from "papaparse";
import type { DataPoint } from "../types";

/** Parse pasted or uploaded CSV/TSV text into DataPoint[]. Throws on structural errors. */
export function parseDelimitedText(text: string): DataPoint[] {
  const parsed = Papa.parse<string[]>(text.trim(), {
    skipEmptyLines: true,
    delimitersToGuess: [",", "\t", ";", " "],
  });

  if (parsed.errors.length > 0) {
    throw new Error(`CSV parse error: ${parsed.errors[0].message}`);
  }

  const rows = parsed.data;
  if (rows.length === 0) {
    throw new Error("No data rows found.");
  }

  // Detect and skip a header row (e.g. "t, C_A" / "time, concentration").
  let startIdx = 0;
  const first = rows[0].map((c) => String(c).trim().toLowerCase());
  if (first.length >= 2 && isNaN(Number(first[0])) ) {
    startIdx = 1;
  }

  const points: DataPoint[] = [];
  for (let i = startIdx; i < rows.length; i++) {
    const row = rows[i];
    if (row.length < 2) continue;
    const time = Number(String(row[0]).trim());
    const concentration = Number(String(row[1]).trim());
    if (Number.isNaN(time) || Number.isNaN(concentration)) {
      throw new Error(
        `Row ${i + 1}: non-numeric value ("${row[0]}", "${row[1]}"). Fix the file and re-upload.`
      );
    }
    points.push({ time, concentration });
  }

  if (points.length === 0) {
    throw new Error("No valid numeric rows found in the file.");
  }
  return points;
}

export function dataPointsToCsv(points: DataPoint[]): string {
  const rows = [["time", "concentration"], ...points.map((p) => [String(p.time), String(p.concentration)])];
  return Papa.unparse(rows);
}

export function downloadTextFile(filename: string, content: string, mime = "text/csv") {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
