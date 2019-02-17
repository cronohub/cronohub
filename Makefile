VENV = venv
VIRTUALENV = virtualenv
BIN = $(VENV)/bin
PYTHON = $(BIN)/python

INSTALL = $(BIN)/pip install


all: build

$(PYTHON):
	$(VIRTUALENV) $(VTENV_OPTS) $(VENV)

build: $(PYTHON)
	$(PYTHON) setup.py develop

clean:
	rm -rf build && rm -rf dist && rm -rf cronohub.egg-info

test_dependencies:
	$(INSTALL) -r test-requirements.txt

test:
	$(BIN)/tox

dist:
	$(INSTALL) wheel
	$(PYTHON) setup.py sdist bdist_wheel

.PHONY: init test build dist