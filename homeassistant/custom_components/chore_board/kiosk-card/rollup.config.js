import typescript from "@rollup/plugin-typescript";
import { terser } from "rollup-plugin-terser";

export default {
  input: "index.ts",
  output: {
    file: "dist/chore-board-card.js",
    format: "es",
  },
  plugins: [
    typescript({
      tsconfig: "./tsconfig.json",
    }),
    terser(),
  ],
  external: ["lit", "custom-card-helpers"],
};
