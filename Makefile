BIB_FILES := $(wildcard bib/*.bib)
URL_FILES := $(wildcard urls/*.txt)
MARKDOWN_FILES := $(wildcard transcriptions/*.md)

ANC_BIBLATEX_FILES := \
	dancebooks-biblatex.sty

ANC_MARKDOWN_FILES := \
	transcriptions/_markdown2.py \
	transcriptions/_reset.css \
	transcriptions/_style.css
	
ANC_WIKI_FILES := \
	transcriptions/_generate_wiki.py

HTML_FILES := $(MARKDOWN_FILES:.md=.html)

PDFLATEX := pdflatex --shell-escape --max-print-line=250
LUALATEX := lualatex --shell-escape --max-print-line=250
XELATEX  := xelatex  --shell-escape --max-print-line=250
LATEX := $(LUALATEX)

BIBER := biber --listsep=\| --namesep=\| --validate_datamodel

# PDF files related targets

default: test-biblatex.pdf

# LaTeX \filecontents isn't tread-safe
# LuaLaTeX requires to much memory
#
# Disabling parallel compilation
test-biblatex-detailed.pdf: test-biblatex.pdf

%.pdf: JOBNAME = $(@:.pdf=)

%.pdf: %.tex $(BIB_FILES) $(ANC_BIBLATEX_FILES)
	@rm -f $(JOBNAME).bbl biblatex-dm.cfg
	@$(LATEX) $< &>/dev/null
	@$(BIBER) --onlylog $(JOBNAME)
	@$(LATEX) $< &>/dev/null
	@(grep -iE "Datamodel" $(JOBNAME).blg || true) | cut -d ' ' -f 5- | sort | tee $(JOBNAME).validation.log
	@echo "Build completed"

# Target which doesn't hide LaTeX output - useful for debugging stuff
debug: test-biblatex.tex $(BIB_FILES) $(ANC_BIBLATEX_FILES)
	@rm -f ${@:.pdf=.bbl} biblatex-dm.cfg
	@$(LATEX) $<
	@$(BIBER) $(<:.tex=)
	@$(LATEX) $<
	@echo "Build completed"	
	
# Target which doesn't hide LaTeX output - useful for debugging stuff
debug-detailed: test-biblatex-detailed.tex $(BIB_FILES) $(ANC_BIBLATEX_FILES)
	@rm -f ${@:.pdf=.bbl} biblatex-dm.cfg
	@$(LATEX) $<
	@$(BIBER) $(<:.tex=)
	@$(LATEX) $<
	@echo "Build completed"


upload-pdfs.mk: test-biblatex.pdf test-biblatex-detailed.pdf
	@chmod 644 $^
	@scp -p $^ georg@iley.ru:/home/georg/leftparagraphs/static/files/
	@touch $@

clean-pdfs:
	@rm -f *.aux *.bbl *.bcf *.blg *.cfg *.log *.nav *.out *.snm *.swp *.toc *.run.xml *.vrb
	@echo "Clean pdfs completed"

purge-pdfs: clean-pdfs
	@rm -f *.pdf all.mk upload-pdfs.mk
	@echo "Purge pdfs completed"
	
# Transcriptions related targets

%.html: %.md $(ANC_MARKDOWN_FILES)
	@echo "Compiling \"$<\""
	@./transcriptions/_markdown2.py --input "$<" --output "$@"

transcriptions.mk: $(HTML_FILES)
	@echo "Compiling transcriptions completed"
	@touch $@

update-wiki.mk: $(MARKDOWN_FILES) $(ANC_WIKI_FILES)
	@echo "Updating wiki"
	@./transcriptions/_generate_wiki.py $(MARKDOWN_FILES)
	@cd wiki && (git commit -am "Updated wiki" || true) && git push origin master
	@touch $@
	
purge-transcriptions: clean
	@rm -f transcriptions/*.html transriptions.mk
	@echo "Cleaning transcriptions completed"
	
# www-related targets

test-www:
	@cd www && nosetests tests

translations-update-www:
	@cd www && \
	pybabel -q extract -F babel.cfg -o messages.pot . && \
	pybabel -q update -i messages.pot -d translations

translations-compile-www:
	@cd www && \
	pybabel -q compile -d translations

# Ancillary targets

all.mk: test-biblatex.pdf test-biblatex-detailed.pdf $(HTML_FILES)
	@echo "Build all completed"
	@touch $@

upload-urls.mk:	$(URL_FILES)
	@chmod 644 $^
	@scp -p $^ georg@server.goldenforests.ru:/home/georg/urls/
	@touch $@
	
entry-count: $(BIB_FILES)
	@cat $^ | grep -c "@"
	
clean: clean-pdfs
	@true
	
rebuild: purge-pdfs purge-transcriptions all.mk
	@echo "Rebuild completed"
