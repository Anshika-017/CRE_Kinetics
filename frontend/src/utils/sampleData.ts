import type { DataPoint } from "../types";

export interface SampleDataset {
  key: string;
  label: string;
  description: string;
  points: DataPoint[];
  suggestedCR0?: number;
}

export const SAMPLE_DATASETS: SampleDataset[] = [
  {
    key: "zero_order",
    label: "Zero order",
    description: "C_A decreases linearly with time.",
    points: [
      { time: 0, concentration: 10 },
      { time: 20, concentration: 9.4 },
      { time: 40, concentration: 8.8 },
      { time: 60, concentration: 8.2 },
      { time: 80, concentration: 7.6 },
      { time: 100, concentration: 7.0 },
      { time: 150, concentration: 5.5 },
      { time: 200, concentration: 4.0 },
    ],
  },
  {
    key: "first_order",
    label: "First order",
    description: "Classic exponential decay, C_A0 = 10, k ≈ 0.02 /s.",
    points: [
      { time: 0, concentration: 10 },
      { time: 20, concentration: 6.7 },
      { time: 40, concentration: 4.49 },
      { time: 60, concentration: 3.01 },
      { time: 120, concentration: 0.91 },
      { time: 180, concentration: 0.27 },
      { time: 300, concentration: 0.025 },
    ],
  },
  {
    key: "second_order",
    label: "Second order",
    description: "1/C_A grows linearly with time, C_A0 = 10, k = 0.01.",
    points: [
      { time: 0, concentration: 10 },
      { time: 20, concentration: 8.33 },
      { time: 40, concentration: 7.14 },
      { time: 60, concentration: 6.25 },
      { time: 120, concentration: 4.55 },
      { time: 180, concentration: 3.57 },
      { time: 300, concentration: 2.5 },
    ],
  },
  {
    key: "fractional_order",
    label: "Fractional order (n = 1.5)",
    description: "Non-integer reaction order n = 1.5.",
    points: [
      { time: 0, concentration: 10 },
      { time: 20, concentration: 7.62 },
      { time: 40, concentration: 6.24 },
      { time: 60, concentration: 5.32 },
      { time: 100, concentration: 4.18 },
      { time: 150, concentration: 3.34 },
      { time: 250, concentration: 2.35 },
    ],
  },
  {
    key: "autocatalytic",
    label: "Autocatalytic",
    description: "A + R -> R + R, C_A0 = 9.5, C_R0 = 0.5.",
    points: [
      { time: 0, concentration: 9.5 },
      { time: 10, concentration: 9.1 },
      { time: 20, concentration: 8.2 },
      { time: 30, concentration: 6.5 },
      { time: 40, concentration: 4.3 },
      { time: 50, concentration: 2.4 },
      { time: 60, concentration: 1.1 },
      { time: 70, concentration: 0.45 },
    ],
    suggestedCR0: 0.5,
  },
  {
    key: "noisy",
    label: "Noisy first-order",
    description: "First-order data with added experimental noise, including a non-monotonic point.",
    points: [
      { time: 0, concentration: 10.1 },
      { time: 20, concentration: 6.9 },
      { time: 40, concentration: 4.3 },
      { time: 60, concentration: 3.15 },
      { time: 80, concentration: 3.3 },
      { time: 120, concentration: 0.95 },
      { time: 180, concentration: 0.3 },
      { time: 300, concentration: 0.04 },
    ],
  },
];
