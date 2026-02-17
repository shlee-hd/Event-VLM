#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/paper"
TEXBIN="$ROOT_DIR/.texlive/TinyTeX/bin/universal-darwin"

if [[ -d "$TEXBIN" ]]; then
  export PATH="$TEXBIN:$PATH"
fi

cd "$PAPER_DIR"

if command -v latexmk >/dev/null 2>&1; then
  echo "[build_paper] using latexmk: $(command -v latexmk)"
  latexmk -pdf -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
else
  echo "[build_paper] latexmk not found, fallback to pdftex+bibtex pipeline"
  pdftex -fmt=pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
  bibtex build/main
  pdftex -fmt=pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
  pdftex -fmt=pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
fi

echo "[build_paper] done -> $PAPER_DIR/build/main.pdf"
