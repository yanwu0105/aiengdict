.PHONY: help open-venv test clean run dev

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

open-venv: ## Setup development environment
	source .venv/bin/activate

test: ## Run tests
	uv run python scripts/run_tests.py

test-clean: ## Run tests without warnings
	uv run pytest tests/ --disable-warnings -q

test-verbose: ## Run tests with full output
	uv run pytest tests/ -v

clean: ## Clean cache and temporary files
	uv run pyclean -v .
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	@echo "Cache and temporary files cleaned"

git-commit:
	make clean
	git add .
	uv run pre-commit run --all-files
	uv run cz commit
	git push

run: ## Run the main application
	uv run python main.py

dev: ## Run in development mode with auto-reload
	uv run python main.py

view-db: ## View database contents
	uv run python scripts/view_database.py

clear-db: ## Clear database contents (with confirmation)
	uv run python scripts/clear_database.py

clear-db-force: ## Force clear database contents (no confirmation)
	uv run python scripts/clear_database.py --force

migrate-db: ## Migrate database to latest schema
	uv run python scripts/migrate_database.py
