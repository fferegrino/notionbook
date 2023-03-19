fmt:
	$(TOOL_RUN) black .
	$(TOOL_RUN) isort .

lint:
	$(TOOL_RUN) isort . --check-only
	$(TOOL_RUN) black . --check
