import sys

numbers = [str(x) for x in range(10)]
operators = ['+', '-']

def clean_numbers(sentence, numbers, clean):
    temp = [sentence]
    for number in clean:
        temp = number.join(temp).split(number)
    sentence = temp
    temp = []
    for i, number in enumerate(sentence):
        if i == 0 and number == '':
            continue
        for char in number.strip():
            if char not in numbers:
                print('Found invalid character')
                exit(1)
        temp.append(int(number))
    return temp

def clean_operators(sentence, operators, clean):
    temp = [sentence]
    for operator in clean:
        temp = operator.join(temp).split(operator)
    sentence = temp
    temp = []
    for operator in sentence:
        if operator.strip() in operators:
            temp.append(operator.strip())
        elif operator.strip() != '':
            print('Encountered double operators')
            exit(1)
    return temp

sentence = sys.argv[1].strip()

if len(sentence) == 0:
    print("Invalid size")
    exit(1)

if sentence[-1] in operators:
    print('Last char is operator')
    exit(1)

operators_in_sentence = clean_operators(sentence, operators, numbers)
numbers_in_sentence = clean_numbers(sentence, numbers, operators)

if sentence[0] not in operators:
    operators_in_sentence = ['+'] + operators_in_sentence
else:
    print("Invalid first char")
    exit(1)

total = 0

for operator, number in zip(operators_in_sentence, numbers_in_sentence):
    if operator == '+':
        total += number
    elif operator == '-':
        total -= number

print(total)
