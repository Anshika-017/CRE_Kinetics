import Plot from "react-plotly.js";

interface Series {
  x: number[];
  y: (number | null)[];
  name: string;
  mode?: "markers" | "lines" | "lines+markers";
  color?: string;
}

export function Chart({
  title,
  xLabel,
  yLabel,
  series,
  height = 420,
}: {
  title: string;
  xLabel: string;
  yLabel: string;
  series: Series[];
  height?: number;
}) {
  return (
    <div className="chart-wrap">
      <Plot
        data={series.map((s) => ({
          x: s.x,
          y: s.y,
          type: "scatter",
          mode: s.mode || "markers",
          name: s.name,
          marker: { color: s.color, size: 7 },
          line: { color: s.color, width: 2 },
        }))}
        layout={{
          title: { text: title, font: { color: "#e8edf9", size: 16 } },
          autosize: true,
          height,
          paper_bgcolor: "transparent",
          plot_bgcolor: "rgba(255,255,255,0.02)",
          font: { color: "#c7cfe8" },
          xaxis: { title: { text: xLabel }, gridcolor: "rgba(255,255,255,0.08)", zerolinecolor: "rgba(255,255,255,0.15)" },
          yaxis: { title: { text: yLabel }, gridcolor: "rgba(255,255,255,0.08)", zerolinecolor: "rgba(255,255,255,0.15)" },
          legend: { orientation: "h", y: -0.2 },
          margin: { t: 50, r: 20, l: 60, b: 60 },
        }}
        config={{ responsive: true, displaylogo: false, toImageButtonOptions: { filename: title.replace(/\s+/g, "_") } }}
        style={{ width: "100%" }}
        useResizeHandler
      />
    </div>
  );
}
