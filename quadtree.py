from __future__ import annotations
from typing import Optional
import numpy as np


class NodeQuadTree:
    """
    Representa um bloco retangular da imagem dentro da Quadtree.
    Cada nó cobre uma região definida por (x, y, largura, altura).
    """

    def __init__(self, x: int, y: int, width: int, height: int, level: int = 0):

        self.x = x
        self.y = y
        self.width = width
        self.height = height

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
        return self.width * self.height

    def __repr__(self) -> str:
        tipo = "FOLHA" if self.eh_folha else "NODE"
        return (
            f"[{tipo}] pos=({self.x}, {self.y}) "
            f"tam={self.width}x{self.height} "
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
