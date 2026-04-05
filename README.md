# G18_Busca_EDA2-2026.1

---

# Quadtree Image Compressor

Trabalho prático da disciplina de Estruturas de Dados 2 (EDA2 - 2026.1).
Implementação de compressão de imagens em escala de cinza utilizando a estrutura de dados Quadtree, com busca espacial por pixel integrada para demonstrar eficiência da árvore.

---

## Descrição

O sistema recebe uma imagem em escala de cinza e a representa como uma Quadtree, onde cada nó corresponde a um bloco retangular da imagem. Blocos com baixa variância de pixels (homogêneos) são armazenados como folhas, guardando apenas a cor média do bloco. Blocos heterogêneos são recursivamente divididos em quatro quadrantes até que o critério de homogeneidade seja satisfeito ou o tamanho mínimo de bloco seja atingido.

A imagem pode ser reconstruída a partir das folhas da árvore, resultando em uma versão comprimida visualmente próxima ao original. Quanto maior o limiar de variância aceito, maior a compressão e menor a qualidade da imagem resultante.

Além da compressão, o sistema implementa busca espacial: dado um par de coordenadas (x, y), a árvore localiza em O(profundidade) qual folha cobre aquele pixel, demonstrando o uso da estrutura para busca eficiente.

---

## Instalação

Requer Python 3.8 ou superior.
```bash
pip install -r requirements.txt
```

Dependências: `Pillow`, `numpy`, `matplotlib`.

---

## Uso

**Importante:** Para utilizar o sistema, é **obrigatório** colocar uma imagem na pasta `images/`. A imagem deve ser preferencialmente em **preto e branco** (escala de cinza), embora o sistema a converta automaticamente. Você deve referenciar o nome exato do seu arquivo de imagem no código do arquivo `main.py` (alterando o da variável `imagem_teste`).

O resultado da execução (a versão comprimida) ficará automaticamente salvo na pasta `saida/`.

**Comprimir uma imagem (via script automático):**
```bash
python main.py
```

Rodar o arquivo `main.py` testará os limiares em Benchmark de 5 a 500 automaticamente e plotará os gráficos de PSNR e taxa de compressão usando os arquivos definidos.

---

## Parâmetros

| Parâmetro | Descrição | Padrão |
|---|---|---|
| `limiar` | Variância máxima para considerar bloco homogêneo | 20.0 |
| `min_bloco` | Tamanho mínimo de bloco em pixels | 2 |
| `max_nivel` | Profundidade máxima da árvore | 8 |

---

## Métricas

A qualidade da compressão é medida pelo **PSNR** (Peak Signal-to-Noise Ratio), expresso em dB. Valores acima de 30 dB indicam boa fidelidade visual em relação ao original.

| Limiar | Folhas (aprox.) | Taxa de Compressão | PSNR |
|---|---|---|---|
| 5 | alta | ~93% | ~41 dB |
| 20 | média | ~98% | ~34 dB |
| 50 | baixa | ~99.6% | ~27 dB |
| 100 | muito baixa | ~99.9% | ~19 dB |

*Valores variam conforme o conteúdo da imagem.*

---

## Serialização Binária da Árvore (Issue #9)

O projeto implementa serialização e desserialização compacta da QuadTree em formato binário próprio, permitindo salvar e restaurar a estrutura completa da árvore sem precisar reprocessar a imagem original.

### Como funciona

A serialização percorre a árvore em **BFS (largura)** usando uma **fila** (`deque`), nível por nível. Para cada nó visitado, escreve:

- `0` — nó interno (os 4 filhos serão visitados em seguida na fila)
- `1` seguido de 8 bits — folha com sua cor média

A desserialização usa a mesma fila BFS para reconstruir os nós exatamente na mesma ordem, sem necessidade de marcadores de fim ou separadores.

### Formato do arquivo `.qtb`

```text
Cabeçalho (13 bytes):
  'QT'        2 bytes   assinatura do formato
  versão      1 byte    uint8
  largura     2 bytes   uint16 big-endian
  altura      2 bytes   uint16 big-endian
  limiar      4 bytes   float32 big-endian
  min_bloco   1 byte    uint8
  max_nivel   1 byte    uint8

Total de bits válidos  4 bytes  uint32 big-endian
Fluxo de bits BFS      ceil(bits/8) bytes
```

### Por que a fila (BFS) é essencial aqui

A BFS garante que serializar e desserializar percorram os nós **na mesma ordem**, sem precisar armazenar ponteiros ou índices de posição no arquivo. Se a serialização usasse DFS (pilha/recursão), a desserialização precisaria de delimitadores para saber onde cada subárvore termina — tornando o formato mais complexo e maior. Com BFS:

1. O produtor enfileira a raiz, processa, enfileira os filhos → escreve bits em ordem.
2. O consumidor replica exatamente esse comportamento: lê um bit, sabe se criará filhos ou não, enfileira na mesma ordem.

A correspondência 1-para-1 entre a fila do produtor e a fila do consumidor é o que torna o formato autocontido e sem overhead de metadados por nó.

### Compressão real

Para imagens com regiões homogêneas, o arquivo `.qtb` pode ser drasticamente menor que a imagem bruta:

| Imagem | Pixels (bruto) | Arquivo `.qtb` | Redução |
|--------|---------------|---------------|---------|
| 256x256 com 4 blocos uniformes | 65 536 bytes | ~22 bytes | ~2979x |
| 512x512 fotografia (limiar 20) | 262 144 bytes | variável | depende do conteúdo |

A compressão é maximizada quando os blocos da imagem são grandes e homogêneos, pois toda uma região é representada por 9 bits (1 flag + 8 bits de cor) em vez de `largura × altura × 8` bits.

---

## Testes
```bash
python tests/teste_issue1.py
python tests/teste_issue2.py
python tests/teste_issue3.py
python tests/teste_issue4.py
python tests/teste_issue5.py
python tests/teste_issue6.py
python tests/teste_issue7.py
python tests/teste_issue8.py
python tests/teste_issue9.py
```

---

## Autores

Grupo 18 - EDA2 2026.1
Universidade de Brasília
