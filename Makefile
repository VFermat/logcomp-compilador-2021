all: valid invalid

valid:
	-python3 main.py "1"
	-python3 main.py "1+1"
	-python3 main.py "1+1-1"
	-python3 main.py "1-1"
	-python3 main.py "1-2"
	-python3 main.py "1  -2"
	-python3 main.py "1-   2"
	-python3 main.py "1   -   2"
	-python3 main.py "1   -   2+1"

invalid:
	-python3 main.py "1+"
	-python3 main.py "+34"
	-python3 main.py "19 1283"
	-python3 main.py "15++"
	-python3 main.py "!"