# logcomp-compilador-2021
Repositorio dedicado a matéria de Lógica da Computação.


## EBNF

```
EXPRESSION = TERM, {("+" | "-"), TERM} ;
TERM = FACTOR, {("*", "/"), FACTOR} ;
FACTOR = ("+", "-"), FACTOR | "(", EXPRESSION, ")" | NUMBER ;
NUMBER = DIGIT, {DIGIT} ;
DIGIT = 0 | 1 | ... | 9 ;
```

## Diagrama

![Diagrama](Diagrama.png)
