.PHONY: lint lint-struct lint-semantic status test

lint: lint-struct lint-semantic

lint-struct:
	python3 tools/lint_wiki.py

lint-semantic:
	python3 tools/check_orphans.py
	python3 tools/check_stale.py

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
	@python3 tools/lint_wiki.py || true
	@echo ""
	@echo "== semantic lint =="
	@python3 tools/check_orphans.py || true
	@python3 tools/check_stale.py || true

test:
	python3 -m unittest discover -s tests -v
