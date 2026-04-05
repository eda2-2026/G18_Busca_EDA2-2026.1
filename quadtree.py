from __future__ import annotations
from typing import Optional
import numpy as np
from image_utils import cor_media, variancia


class NodeQuadTree:
    """
    Representa um bloco retangular da imagem dentro da Quadtree.
    Cada nó cobre uma região definida por (x, y, largura, altura).
    """

    def __init__(self, x: int, y: int, largura: int, altura: int, level: int = 0):

        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura

        # Determina a profundidade da arvore
        self.level = level

        # Dados calculados sobre os pixels do bloco
        self.cor_media: int = 0
        self.variancia: float = 0.0

        # Status do no
        self.eh_folha: bool = False

        self.filhos: list[Optional[NodeQuadTree]] = [None, None, None, None]

    def eh_raiz(self) -> bool:
        return self.level == 0

    def total_pixels(self) -> int:
        return self.largura * self.altura

    def __repr__(self) -> str:
        tipo = "FOLHA" if self.eh_folha else "NODE"
        return (
            f"[{tipo}] pos=({self.x}, {self.y}) "
            f"tam={self.largura}x{self.altura} "
            f"nivel={self.level} "
            f"cor={self.cor_media} var={self.variancia:.1f}"
        )


class QuadTree:
    """
    Árvore quaternária para compressão de imagens em escala de cinza.
    Cada nó representa um bloco da imagem.
    Blocos homogêneos (variância < limiar) viram folhas.
    """

    def __init__(self, limiar: float, min_bloco: int = 2, max_nivel: int = 8):
        self.limiar = limiar
        self.min_bloco = min_bloco
        self.max_nivel = max_nivel

        # Raiz da arvore, criada quando chamar inserir()
        self.raiz: Optional[NodeQuadTree] = None

        # Estatistica
        self.total_nos: int = 0
        self.total_folhas: int = 0

    def is_empty(self) -> bool:
        return self.raiz is None

    def inserir(self, pixels: np.ndarray):
        """
        Ponto de Entrada publica da insercao
        Recebe o array 2d de pixels e controi a arvore binaria

        pixels: np.array de shape (altura, largura), dtype=uint8
        """
        altura, largura = pixels.shape

        # Cria o node da raiz cobrindo a imagem inteira
        self.raiz = NodeQuadTree(x=0, y=0, largura=largura, altura=altura, level=0)
        self._inserir_recursivo(self.raiz, pixels)

    def _inserir_recursivo(self, no: NodeQuadTree, pixels: np.ndarray):
        """
        Algoritmo Principal da Quadtree

        1. Calcula a cor media e variancia do bloco
        2. Verifica se deve virar folha
        3. Se nao for folha: divide em 4 filhos e repete
        """

        self.total_nos += 1

        # 1.
        no.cor_media = cor_media(pixels, no.x, no.y, no.largura, no.altura)
        no.variancia = variancia(pixels, no.x, no.y, no.largura, no.altura)

        # 2.
        # Checa se e homogenea o suficiente
        bloco_homogeneo = no.variancia <= self.limiar

        # Checa se o bloco chegou no tamanho minimo
        bloco_minimo = no.level >= self.max_nivel

        # Checa se atingiu a profundidade maxima da arvore
        profundidade_maxima = no.level >= self.max_nivel

        if bloco_homogeneo or bloco_minimo or profundidade_maxima:
            no.eh_folha = True
            self.total_folhas += 1
            return

        mx = no.largura // 2
        my = no.altura // 2

        proximo_nivel = no.level + 1

        # filho[0] — Top-Left (TL)
        no.filhos[0] = NodeQuadTree(
            x=no.x, y=no.y, largura=mx, altura=my, level=proximo_nivel
        )
        # filho[1] — Top-Right (TR)
        no.filhos[1] = NodeQuadTree(
            x=no.x + mx, y=no.y, largura=no.largura - mx, altura=my, level=proximo_nivel
        )
        # filho[2] — Bottom-Left (BL)
        no.filhos[2] = NodeQuadTree(
            x=no.x, y=no.y + my, largura=mx, altura=no.altura - my, level=proximo_nivel
        )
        # filho[3] — Bottom-Right (BR)
        no.filhos[3] = NodeQuadTree(
            x=no.x + mx,
            y=no.y + my,
            largura=no.largura - mx,
            altura=no.altura - my,
            level=proximo_nivel,
        )

        # Recursao nos 4 filhos
        for filho in no.filhos:
            assert filho is not None
            self._inserir_recursivo(filho, pixels)

    def reconstruir(self, shape: tuple) -> np.ndarray:
        """
        Reconstrói a imagem a partir da Quadtree, preenchendo cada folha com sua cor média.
        Cada folha representa um bloco homogêneo da imagem original, e a cor média é usada para preencher esse bloco na imagem reconstruída.

        shape: tupla (altura, largura) da imagem original
        Retorna um array 2D de pixels reconstruídos a partir da Quadtree.
        """

        if self.raiz is None:
            raise ValueError(
                "A Quadtree está vazia. Insira uma imagem antes de reconstruir."
            )

        # cria array zerada com o mesmo formato da imagem original
        imagem = np.zeros(shape, dtype=np.uint8)

        self._reconstruir_recursivo(self.raiz, imagem)
        return imagem

    def _reconstruir_recursivo(self, no: NodeQuadTree, imagem: np.ndarray):
        """
        DFS na arvore:
            - se folha: preenche o bloco correspondente na imagem com a cor média
            - se nó interno: continua recursão nos filhos
        """

        if no.eh_folha:
            imagem[no.y : no.y + no.altura, no.x : no.x + no.largura] = no.cor_media
            return

        # No interno: continua recursão nos filhos
        for filho in no.filhos:
            if filho is not None:
                self._reconstruir_recursivo(filho, imagem)

    def taxa_de_compressao(self, total_pixels: int) -> float:
        """
        Percentual de reducao de dados
        Compara folhas vs pixeis totais
        """
        if total_pixels == 0:
            return 0.0
        return (1.0 - self.total_folhas / total_pixels) * 100.0

    def estatistica(self) -> dict:
        # Retorna um dicionario com as metricas da arvore
        total_pixels = 0
        if self.raiz:
            total_pixels = self.raiz.total_pixels()
        return {
            "total_nos": self.total_nos,
            "total_folhas": self.total_folhas,
            "nos_internos": self.total_nos - self.total_folhas,
            "taxa_compressao": self.taxa_de_compressao(total_pixels),
            "limiar_usado": self.limiar,
        }

    def __repr__(self) -> str:
        return (
            f"Quadtree(limiar={self.limiar}, "
            f"nos={self.total_nos}, "
            f"folhas={self.total_folhas})"
        )
