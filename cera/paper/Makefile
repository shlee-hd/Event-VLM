SHELL := /bin/bash

LATEXMK ?= latexmk
PDFLATEX ?= pdflatex
BIBTEX ?= bibtex
MAIN := main.tex
DOC := $(basename $(MAIN))
OUTDIR := build

.PHONY: pdf clean bootstrap-style

pdf: bootstrap-style
	@mkdir -p $(OUTDIR)
	@if command -v $(LATEXMK) >/dev/null 2>&1; then \
		$(LATEXMK) -pdf -interaction=nonstopmode -outdir=$(OUTDIR) $(MAIN); \
	elif command -v $(PDFLATEX) >/dev/null 2>&1; then \
		$(PDFLATEX) -interaction=nonstopmode -output-directory=$(OUTDIR) $(MAIN); \
		if command -v $(BIBTEX) >/dev/null 2>&1; then \
			(cd $(OUTDIR) && $(BIBTEX) $(DOC)) || true; \
		fi; \
		$(PDFLATEX) -interaction=nonstopmode -output-directory=$(OUTDIR) $(MAIN); \
		$(PDFLATEX) -interaction=nonstopmode -output-directory=$(OUTDIR) $(MAIN); \
	else \
		echo "Neither latexmk nor pdflatex is available in PATH."; \
		exit 1; \
	fi

bootstrap-style:
	@if [ -f eccv.sty ] && [ -f eccvabbrv.sty ]; then \
		echo "ECCV style files already present in cera/paper."; \
	elif [ -f ../../paper/eccv.sty ] && [ -f ../../paper/eccvabbrv.sty ]; then \
		cp ../../paper/eccv.sty .; \
		cp ../../paper/eccvabbrv.sty .; \
		echo "Copied ECCV style files from ../../paper/."; \
	else \
		echo "Missing ECCV style files. Put eccv.sty and eccvabbrv.sty in cera/paper/."; \
		exit 1; \
	fi

clean:
	@if command -v $(LATEXMK) >/dev/null 2>&1; then \
		$(LATEXMK) -C -outdir=$(OUTDIR) $(MAIN); \
	fi
	rm -rf $(OUTDIR)
