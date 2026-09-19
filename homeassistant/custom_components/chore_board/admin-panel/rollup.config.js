import typescript from "@rollup/plugin-typescript";
import { terser } from "rollup-plugin-terser";

export default {
  input: "chore-board-admin.ts",
  output: {
    file: "dist/chore-board-admin.js",
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
