# Makefile for managing a Python project with a virtual environment

DB_NAME = "tickets.db"
CSV_DIR = "csv_data/"

TEST_DB_NAME = "test_tickets.db"
TEST_CSV_DIR = "test_csv_data/"

# Define the name of your virtual environment
VENV_NAME = venv

# Define the path to the Python executable within the virtual environment
VENV_PYTHON = $(VENV_NAME)/bin/python

MODULE_DIR = main

CSV_MODULE = csv_writer
DB_MODULE = db

export PYTHONPATH := $(MODULE_DIR):$(PYTHONPATH)

# Create and activate the virtual environment
setup:
	python3 -m venv $(VENV_NAME)
	. $(VENV_NAME)/bin/activate

# Install project dependencies using pip
install:
	$(VENV_PYTHON) -m pip install -r requirements.txt

# Run your Python script using the virtual environment
run:
	$(VENV_PYTHON) main/handler.py

runTest:
	$(VENV_PYTHON) tests/tests.py

# Remove the virtual environment and other generated files
clean:
	rm -rf $(VENV_NAME)

clearScrapes:
	rm -f scrapes/*

clearDB:
	$(VENV_PYTHON) -c "from $(DB_MODULE) import clearDB; clearDB('$(DB_NAME)')"

clearCSV:
	$(VENV_PYTHON) -c "from $(CSV_MODULE) import clearCSVs; clearCSVs('$(CSV_DIR)')"

clearRealData: clearDB clearCSV

clearTestDB:
	$(VENV_PYTHON) -c "from $(DB_MODULE) import clearDB; clearDB('$(TEST_DB_NAME)')"

clearTestCSV:
	$(VENV_PYTHON) -c "from $(CSV_MODULE) import clearCSVs; clearCSVs('$(TEST_CSV_DIR)')"

clearTestData: clearTestDB clearTestCSV

clearAll: clearRealData clearTestData


.PHONY: debug

debug:
	. $(VENV_NAME)/bin/activate
	$(VENV_PYTHON) -m pdb tests/tests.py
