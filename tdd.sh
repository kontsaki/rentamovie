fdfind -E test.db* . | PYTHONPATH=src PYTHONBREAKPOINT=ipdb.set_trace entr -rc pytest -x
