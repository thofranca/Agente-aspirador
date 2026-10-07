# Trabalho 1: Agente Aspirador Inteligente

Repositório destinado ao desenvolvimento do Trabalho 1 da disciplina de Inteligência Artificial da UFSM. 
O projeto consiste na implementação de um simulador de agente autônomo (um robô aspirador) que tem como objetivo limpar um ambiente representado em matriz retangular, gerenciando restrições como limite de bateria e alcance de visão.

## Sobre a Implementação

O programa lê a configuração inicial do mapa a partir de um arquivo de texto. Este arquivo define as características do mapa, a localização da base de recarga, a posição inicial do robô, o campo de visão, o custo energético de movimentação e aspiração, a probabilidade de sujeira nas células, o seed utilizado para gerar a sujeira e o número máximo de passos que o robô pode dar.

Os arquivos fornecidos para teste estão disponível com nome de input1.txt, input2.txt, input3.txt e input4.txt. 

Esses arquivos representam a evolução de complexidade no sistema do agente, sendo input1 o que apresenta mais simplicidade de aplicação e input4 o que apresenta maior quantidade de restrições.  

## Funcionalidades e Estratégias

O robô adapta o seu comportamento principal com base no campo de visão (`sight_range`):

### 1. Agente com Visão (`sight_range > 0`)
O robô é capaz de enxergar as células ao seu redor. Ao iniciar, a interface permite escolher entre duas abordagens:
- **Ordem de descoberta**: O robô vai até as sujeiras na exata ordem em que as identificou no mapa.
- **Sujeira mais próxima**: Utiliza o algoritmo BFS (Busca em Largura) para calcular dinamicamente a rota para a sujeira mais próxima de sua localização atual.

### 2. Agente Cego (`sight_range == 0`)
O robô não possui informações prévias do mapa, sendo obrigado a realizar uma varredura às cegas. As opções de estratégia são:
- **Cima-Baixo**: Percorre o ambiente verticalmente, coluna por coluna.
- **Esquerda-Direita**: Percorre o ambiente horizontalmente, linha por linha.

### Gerenciamento de Bateria
Para que haja consumo, é necessário passar os parâmetros `CHARGE-PER-MOVEMENT` e `CHARGE-PER-VACUUM`. Durante a execução, o agente calcula continuamente se a energia atual é suficiente para realizar a limpeza e voltar para a estação de recarga. Caso atinja o limite de segurança, ele interrompe a exploração e retorna à base.

## Como Executar

Foi desenvolvido com auxílio de I.A. uma interface feita em Pygame para agregar ao entendimento e funcionamento do programa. Isso não exclui sua ativação unicamente por meio de linha de comando e mantém atualizações síncronas e constantes de estado no terminal. 

**Pré-requisitos:**
É necessário ter o Python 3 e a biblioteca Pygame instalados.
```bash
pip install pygame
```

**Rodando o simulador:**
Execute o arquivo `main.py` passando o arquivo de configuração desejado como argumento.
```bash
python src/main.py src/input1.txt
```

Ao final da execução, o programa exibe um relatório com as métricas geradas.