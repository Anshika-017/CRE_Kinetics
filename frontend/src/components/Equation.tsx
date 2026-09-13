import { BlockMath, InlineMath } from "react-katex";
import "katex/dist/katex.min.css";

export function Eq({ tex, block = true }: { tex: string; block?: boolean }) {
  if (!tex) return null;
  return block ? (
    <div className="eq-block">
      <BlockMath math={tex} />
    </div>
  ) : (
    <InlineMath math={tex} />
  );
}
