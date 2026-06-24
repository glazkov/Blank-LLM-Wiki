PYTHON ?= python3
PUBLIC_DOCS_DIR ?= public-docs
PUBLIC_DOCS_PYTHON ?= $(PYTHON)

.PHONY: lint lint-struct lint-semantic status test public-docs-install public-docs-validate public-docs-source public-docs-build public-docs-serve public-docs-zip

lint: lint-struct lint-semantic

lint-struct:
	"$(PYTHON)" tools/lint_wiki.py

lint-semantic:
	"$(PYTHON)" tools/check_orphans.py
	"$(PYTHON)" tools/check_stale.py

status:
	@echo "== wiki files =="
	@find wiki -type f | sort
	@echo ""
	@echo "== project intake =="
	@cat wiki/operations/project-intake.md
	@echo ""
	@echo "== project status =="
	@cat wiki/operations/project-status.md
	@echo ""
	@echo "== next steps =="
	@cat wiki/operations/next-steps.md
	@echo ""
	@echo "== structural lint =="
	@"$(PYTHON)" tools/lint_wiki.py || true
	@echo ""
	@echo "== semantic lint =="
	@"$(PYTHON)" tools/check_orphans.py || true
	@"$(PYTHON)" tools/check_stale.py || true

test:
	"$(PYTHON)" -m unittest discover -s tests -v

public-docs-install:
	"$(PUBLIC_DOCS_PYTHON)" -m pip install -r $(PUBLIC_DOCS_DIR)/requirements.txt

public-docs-validate:
	"$(PUBLIC_DOCS_PYTHON)" $(PUBLIC_DOCS_DIR)/tools/validate_public_docs.py

public-docs-source: public-docs-validate
	"$(PUBLIC_DOCS_PYTHON)" $(PUBLIC_DOCS_DIR)/tools/build_public_docs.py

public-docs-build: public-docs-source
	cd $(PUBLIC_DOCS_DIR) && "$(PUBLIC_DOCS_PYTHON)" -m mkdocs build --strict

public-docs-serve: public-docs-source
	cd $(PUBLIC_DOCS_DIR) && "$(PUBLIC_DOCS_PYTHON)" -m mkdocs serve

public-docs-zip: public-docs-build
	@mkdir -p outputs
	cd $(PUBLIC_DOCS_DIR)/build/site && COPYFILE_DISABLE=1 zip -r ../../../outputs/public-docs-site.zip . -x '*.DS_Store' '._*' '__MACOSX/*'
