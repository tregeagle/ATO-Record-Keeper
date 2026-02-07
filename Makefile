.PHONY: help reports clean index all

# Report output directory
REPORTS_DIR := output
HTML_DIR := $(REPORTS_DIR)/html
MARKDOWN_DIR := $(REPORTS_DIR)/markdown

# Tax years are dynamically detected from trade directories
# This supports any year: trades/1066/, trades/2999/, trades/2025/, etc.
# Python script discovers all year directories and generates reports for each
TAX_YEARS := $(shell python3 -c "import os; dirs = [d for d in os.listdir('input') if d[0].isdigit()]; print(' '.join(sorted(dirs)))" 2>/dev/null || echo "")

# Python scripts
FIFO_CALC := scripts/fifo_calculator.py

help:
	@echo "=== ATO Tax Reporting - Makefile ==="
	@echo ""
	@echo "Targets:"
	@echo "  make reports      - Generate all tax reports (markdown + HTML)"
	@echo "  make index        - Generate HTML index page"
	@echo "  make all          - Generate reports and index"
	@echo "  make clean        - Remove all generated reports"
	@echo ""
	@echo "Report formats:"
	@echo "  Markdown: $(MARKDOWN_DIR)/cgt-YEAR.md"
	@echo "  HTML:     $(HTML_DIR)/cgt-YEAR.html"
	@echo ""

# Create directories
$(REPORTS_DIR):
	mkdir -p $(REPORTS_DIR)

$(MARKDOWN_DIR): | $(REPORTS_DIR)
	mkdir -p $(MARKDOWN_DIR)

$(HTML_DIR): | $(REPORTS_DIR)
	mkdir -p $(HTML_DIR)

# Generate markdown reports for each tax year
$(MARKDOWN_DIR)/cgt-%.md: | $(MARKDOWN_DIR)
	@echo "Generating capital gains report for $*..."
	@python $(FIFO_CALC) --year $* > $@
	@echo "✓ Created $@"

# Convert markdown to HTML (with raw_html to preserve <details> tags)
$(HTML_DIR)/cgt-%.html: $(MARKDOWN_DIR)/cgt-%.md | $(HTML_DIR)
	@echo "Converting $< to HTML..."
	@pandoc -f markdown+raw_html -t html5 --standalone \
		--css style.css \
		--metadata title="Capital Gains Report - Tax Year $*" \
		-o $@ $<
	@echo "✓ Created $@"

# Generate all markdown reports
markdown: $(addprefix $(MARKDOWN_DIR)/cgt-,$(addsuffix .md,$(TAX_YEARS)))
	@echo ""
	@echo "✓ All markdown reports generated"

# Generate all HTML reports
html: $(addprefix $(HTML_DIR)/cgt-,$(addsuffix .html,$(TAX_YEARS)))
	@echo ""
	@echo "✓ All HTML reports generated"

# Generate reports
reports: markdown html

# Generate CSS stylesheet
$(HTML_DIR)/style.css: | $(HTML_DIR)
	@echo "Generating CSS stylesheet..."
	@echo '/* ATO Tax Reports Stylesheet */' > $@
	@echo '' >> $@
	@echo 'body {' >> $@
	@echo '  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;' >> $@
	@echo '  line-height: 1.6;' >> $@
	@echo '  color: #333;' >> $@
	@echo '  background: #f5f5f5;' >> $@
	@echo '  padding: 2rem;' >> $@
	@echo '}' >> $@
	@echo '' >> $@
	@echo 'main, article {' >> $@
	@echo '  background: white;' >> $@
	@echo '  padding: 2rem;' >> $@
	@echo '  border-radius: 8px;' >> $@
	@echo '  box-shadow: 0 2px 4px rgba(0,0,0,0.1);' >> $@
	@echo '  max-width: 1000px;' >> $@
	@echo '  margin: 0 auto;' >> $@
	@echo '}' >> $@
	@echo '' >> $@
	@echo 'h1, h2, h3 { color: #2c3e50; margin-top: 1.5rem; }' >> $@
	@echo 'h1 { border-bottom: 2px solid #3498db; padding-bottom: 0.5rem; }' >> $@
	@echo '' >> $@
	@echo 'table {' >> $@
	@echo '  width: 100%;' >> $@
	@echo '  border-collapse: collapse;' >> $@
	@echo '  margin: 1rem 0;' >> $@
	@echo '}' >> $@
	@echo '' >> $@
	@echo 'th, td {' >> $@
	@echo '  padding: 0.75rem;' >> $@
	@echo '  text-align: left;' >> $@
	@echo '  border-bottom: 1px solid #ddd;' >> $@
	@echo '}' >> $@
	@echo '' >> $@
	@echo 'th {' >> $@
	@echo '  background: #3498db;' >> $@
	@echo '  color: white;' >> $@
	@echo '  font-weight: 600;' >> $@
	@echo '}' >> $@
	@echo '' >> $@
	@echo 'tr:hover { background: #f9f9f9; }' >> $@
	@echo '' >> $@
	@echo 'code, pre {' >> $@
	@echo '  background: #f4f4f4;' >> $@
	@echo '  font-family: "Courier New", monospace;' >> $@
	@echo '  border-radius: 4px;' >> $@
	@echo '}' >> $@
	@echo '' >> $@
	@echo 'pre { padding: 1rem; overflow-x: auto; }' >> $@
	@echo '.nav { margin: 2rem 0; padding: 1rem; background: #ecf0f1; border-radius: 4px; }' >> $@
	@echo '.nav a { margin-right: 1rem; color: #3498db; text-decoration: none; }' >> $@
	@echo '.nav a:hover { text-decoration: underline; }' >> $@
	@echo '' >> $@
	@echo '/* Print styles */' >> $@
	@echo '@media print {' >> $@
	@echo '  body { background: white; }' >> $@
	@echo '  main { box-shadow: none; padding: 0; }' >> $@
	@echo '  .nav { display: none; }' >> $@
	@echo '}' >> $@
	@echo "✓ Created $@"

# Generate index pages with CGT indicators and holdings values
index: reports $(HTML_DIR)/style.css
	@echo "Generating index pages with holdings values..."
	@python3 scripts/generate_index.py \
		--trades-path input \
		--reports-path $(REPORTS_DIR) \
		--markdown-dir $(MARKDOWN_DIR) \
		--html-dir $(HTML_DIR)

# Generate all reports and index
all: reports index
	@echo ""
	@echo "=========================================="
	@echo "✓ All reports generated successfully!"
	@echo "=========================================="
	@echo ""
	@echo "Output location: $(HTML_DIR)/"
	@echo "  • index.html         - Report index"
	@echo "  • cgt-YEAR.html      - Tax year reports"
	@echo "  • style.css          - Stylesheet"
	@echo ""
	@echo "Markdown source: $(MARKDOWN_DIR)/"
	@echo ""
	@echo "Open in browser: file://$(shell pwd)/$(HTML_DIR)/index.html"
	@echo ""

# Clean generated files
clean:
	@echo "Cleaning generated reports..."
	@rm -rf $(REPORTS_DIR)
	@echo "✓ Removed $(REPORTS_DIR)/"
	@echo ""

# Display report structure
status:
	@echo "=== Report Status ==="
	@echo ""
	@echo "Markdown Reports:"
	@ls -lh $(MARKDOWN_DIR)/*.md 2>/dev/null || echo "  (none generated yet)"
	@echo ""
	@echo "HTML Reports:"
	@ls -lh $(HTML_DIR)/*.html 2>/dev/null || echo "  (none generated yet)"
	@echo ""
