# Makefile for managing a Python project with a virtual environment

# Define the name of your virtual environment
VENV_NAME = venv

# Define the path to the Python executable within the virtual environment
VENV_PYTHON = $(VENV_NAME)/bin/python

# Create and activate the virtual environment
setup:
	python3 -m venv $(VENV_NAME)
	. $(VENV_NAME)/bin/activate

# Install project dependencies using pip
install:
	$(VENV_PYTHON) -m pip install -r requirements.txt

# Run your Python script using the virtual environment
run:
	$(VENV_PYTHON) scraper.py

# Remove the virtual environment and other generated files
clean:
	rm -rf $(VENV_NAME)


