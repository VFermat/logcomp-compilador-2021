# logcomp-compilador-2021
Repositorio dedicado a matéria de Lógica da Computação.

## Roteiro 0

Entrega do Roteiro 0 (*Tag v0.1*) - Calculadora

Para rodar o código, digite o comando
```shell
python3 main.py "expressão"
```

Em caso de erro, o programa printará uma mensagem explicando o motivo, e exitará com erro.

### Questionário

**1 - Explique como foi feito para reconhecer múltiplos dígitos e realizar múltiplas operações.**

```
Utilizei uma estratégia de separar os números dos operadores. Realize splits para cada dígito possível para separar os operadores e splits para cada operador possível para separar os digitos. Com isso foi possível obter strings separadas para cada uma delas.

Tendo as strings separadas, podemos checar se existem erros em alguns lugares. Para os dígitos, podemos checar se existem números separados por espaços (o que causaria erro). Caso não, podemos realizar um cast dos digitos para int, transformando assim em número.

Feito isso, como o split mantém as operações e os números alinhados, podemos realizar as operações em ordem, acumulando o resultado em uma variável.
```

**2 - Pense na estrutura de alguma linguagem procedural (C por exemplo), indique com detalhes como você expandiria o seu programa para compilar um programa nessa linguagem.**

```
Acredito que adotaria um programa similar, quebrando a estrutura nos `operadores` desejados. Porém, criaria uma estrutura de progama mais robusta, que não dependesse dos operadores estarem na sequência (como feita na calculadora com os operadores). 

Utilizaria os comandos da linguagem como sendo os operadores que separarão o código. E ao invés de fazer o cast para um diferente tipo de variável (como feito com os números), faria a transformação para o procedimento que a sequência de palavras indicasse.
```