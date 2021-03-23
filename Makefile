all: valid invalid

valid:
	-python3 main.py "/* a */ 1 /* b */"
	-python3 main.py "3-2"
	-python3 main.py "11+22-33 /* a */"
	-python3 main.py "4/2+3"
	-python3 main.py "3+4/2"
	-python3 main.py "2 + 3 */* a */5"
	-python3 main.py "(3 + 2) /5"
	-python3 main.py "--77"
	-python3 main.py "+--++35"
	-python3 main.py "3 - -2/4"
	-python3 main.py "4/(1+1)*2"

invalid:
	-python3 main.py "3+ /* a */"
	-python3 main.py "/* a */"
	-python3 main.py "3- 3 /* a"
	-python3 main.py "(2*2"
	-python3 main.py "(3-(8)"
	-python3 main.py "3+2)"