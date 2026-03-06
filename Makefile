.PHONY: setup pipeline dashboard

setup:
	pip install -r requirements.txt

pipeline: setup
	python load_data.py
	python data_overview.py

dashboard:
	python dashboard.py
