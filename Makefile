.PHONY: setup pipeline dashboard

setup:
	pip install -r requirements.txt

pipeline: setup
	python load_data.py

dashboard:
	python dashboard.py