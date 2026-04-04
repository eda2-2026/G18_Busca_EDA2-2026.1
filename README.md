# G18_Busca_EDA2-2026.1

---

# Quadtree Image Compressor

Trabalho prático da disciplina de Estruturas de Dados 2 (EDA2 - 2026.1).
Implementacao de compressao de imagens em escala de cinza utilizando a estrutura de dados Quadtree, com busca espacial por pixel integrada para demonstrar eficiencia da arvore.

---

## Descricao

O sistema recebe uma imagem em escala de cinza e a representa como uma Quadtree, onde cada no corresponde a um bloco retangular da imagem. Blocos com baixa variancia de pixels (homogeneos) sao armazenados como folhas, guardando apenas a cor media do bloco. Blocos heterogeneos sao recursivamente divididos em quatro quadrantes ate que o criterio de homogeneidade seja satisfeito ou o tamanho minimo de bloco seja atingido.

A imagem pode ser reconstruida a partir das folhas da arvore, resultando em uma versao comprimida visualmente proxima ao original. Quanto maior o limiar de variancia aceito, maior a compressao e menor a qualidade da imagem resultante.

Alem da compressao, o sistema implementa busca espacial: dado um par de coordenadas (x, y), a arvore localiza em O(profundidade) qual folha cobre aquele pixel, demonstrando o uso da estrutura para busca eficiente.

---

## Instalacao

Requer Python 3.8 ou superior.
```bash
pip install -r requirements.txt
```

Dependencias: `Pillow`, `numpy`, `matplotlib`.

---

## Uso

**Comprimir uma imagem:**
```bash
python main.py imagens/foto.jpg saida/comprimida.png 20
```

O terceiro argumento e o limiar de variancia. Valores recomendados: entre 10 e 50.

**Benchmark de limiares:**
```bash
python main.py --benchmark imagens/foto.jpg
```

Testa limiares de 5 a 100 e plota graficos de PSNR e taxa de compressao.

---

## Parametros

| Parametro | Descricao | Padrao |
|---|---|---|
| `limiar` | Variancia maxima para considerar bloco homogeneo | 20.0 |
| `min_bloco` | Tamanho minimo de bloco em pixels | 2 |
| `max_nivel` | Profundidade maxima da arvore | 8 |

---

## Metricas

A qualidade da compressao e medida pelo **PSNR** (Peak Signal-to-Noise Ratio), expresso em dB. Valores acima de 30 dB indicam boa fidelidade visual em relacao ao original.

| Limiar | Folhas (aprox.) | Taxa de Compressao | PSNR |
|---|---|---|---|
| 5 | alta | ~93% | ~41 dB |
| 20 | media | ~98% | ~34 dB |
| 50 | baixa | ~99.6% | ~27 dB |
| 100 | muito baixa | ~99.9% | ~19 dB |

*Valores variam conforme o conteudo da imagem.*

---

## Testes
```bash
python test_issue1.py
python test_issue4.py
```

---

## Autores

Grupo 18 - EDA2 2026.1
Universidade de Brasilia
