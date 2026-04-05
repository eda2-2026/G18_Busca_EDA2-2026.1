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

    def buscar_pixel(self, px: int, py: int) -> NodeQuadTree:
        """
        Busca espacial: dado um pixel (px, py), retorna o nó folha
        da Quadtree que cobre aquela posição.
        """

        if self.raiz is None:
            raise ValueError(
                "A Quadtree está vazia. Insira uma imagem antes de buscar pixels."
            )

        if not (0 <= px < self.raiz.largura and 0 <= py < self.raiz.altura):
            raise ValueError(f"Pixel ({px}, {py}) está fora dos limites da imagem.")

        return self._buscar_pixel_recursivo(self.raiz, px, py)

    def _buscar_pixel_recursivo(
        self, no: NodeQuadTree, px: int, py: int
    ) -> NodeQuadTree:
        """
        Desce pela arvore escolhendo o filho correto com base na posição do pixel (px, py).
        Em cada nó, verifica se é folha. Se for, retorna o nó. Se não for, continua descendo.
        """

        if no.eh_folha:
            return no

        # calcula o centro absoluto do bloco atual
        cx = no.x + no.largura // 2
        cy = no.y + no.altura // 2

        # Decide qual quadrante escolher com base na posição do pixel
        if px < cx and py < cy:
            indice_filho = 0  # Top-Left
        elif px >= cx and py < cy:
            indice_filho = 1  # Top-Right
        elif px < cx and py >= cy:
            indice_filho = 2  # Bottom-Left
        else:
            indice_filho = 3  # Bottom-Right

        filho = no.filhos[indice_filho]

        if filho is None:
            return no  # Se o filho não existe, retorna o nó atual (pode acontecer em blocos menores que min_bloco)

        return self._buscar_pixel_recursivo(filho, px, py)

    def serializar(self) -> bytes:
        """
        Serializa a QuadTree em formato binário compacto usando BFS (percurso em largura).

        Estrutura usada: fila (deque) para percorrer a árvore nível por nível,
        garantindo que a ordem de serialização seja idêntica à de desserialização.

        Formato do arquivo:
        - Cabeçalho (13 bytes):
          * 'QT'     (2 bytes): assinatura do formato
          * versão   (1 byte) : versão do formato
          * largura  (2 bytes, uint16 big-endian)
          * altura   (2 bytes, uint16 big-endian)
          * limiar   (4 bytes, float32 big-endian)
          * min_bloco(1 byte,  uint8)
          * max_nivel(1 byte,  uint8)
        - Total de bits válidos (4 bytes, uint32 big-endian)
        - Fluxo de bits em BFS:
          * 0              = nó interno (4 filhos seguem na fila)
          * 1 + 8 bits cor = folha com cor média

        Returns:
            bytes com a árvore serializada
        """
        import struct
        from collections import deque

        if self.raiz is None:
            raise ValueError("Árvore vazia, nada para serializar.")

        cabecalho = struct.pack(
            ">2sBHHfBB",
            b"QT",
            1,
            self.raiz.largura,
            self.raiz.altura,
            self.limiar,
            self.min_bloco,
            self.max_nivel,
        )

        # BFS para construir o fluxo de bits
        bits = []
        fila = deque([self.raiz])

        while fila:
            no = fila.popleft()
            if no.eh_folha:
                bits.append(1)
                cor = int(no.cor_media)
                for i in range(7, -1, -1):
                    bits.append((cor >> i) & 1)
            else:
                bits.append(0)
                for filho in no.filhos:
                    fila.append(filho)

        num_bits = len(bits)

        # Padding para completar o último byte
        while len(bits) % 8 != 0:
            bits.append(0)

        # Empacotar bits em bytes
        dados = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            dados.append(byte)

        return cabecalho + struct.pack(">I", num_bits) + bytes(dados)

    def salvar_arvore(self, caminho: str) -> None:
        """
        Salva a QuadTree serializada em formato binário no caminho especificado.

        caminho: caminho do arquivo de saída (ex: 'saida/arvore.qtb')
        """
        dados = self.serializar()
        with open(caminho, "wb") as f:
            f.write(dados)

    @classmethod
    def deserializar(cls, dados: bytes) -> "QuadTree":
        """
        Desserializa uma QuadTree a partir de bytes no formato binário compacto.

        Estrutura usada: fila (deque) para reconstruir a árvore nível por nível,
        espelhando exatamente a ordem em que os nós foram serialiados.

        dados: bytes retornados por serializar()
        Returns: instância de QuadTree reconstruída
        """
        import struct
        from collections import deque

        fmt_cab = ">2sBHHfBB"
        tam_cab = struct.calcsize(fmt_cab)

        if len(dados) < tam_cab + 4:
            raise ValueError("Dados insuficientes para desserialização.")

        magic, versao, largura, altura, limiar, min_bloco, max_nivel = struct.unpack(
            fmt_cab, dados[:tam_cab]
        )

        if magic != b"QT":
            raise ValueError(f"Formato inválido: assinatura '{magic}' desconhecida.")

        offset = tam_cab
        num_bits = struct.unpack(">I", dados[offset : offset + 4])[0]
        offset += 4

        # Desempacota bytes em bits e descarta o padding
        bits = []
        for byte in dados[offset:]:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        bits = bits[:num_bits]

        qt = cls(limiar=float(limiar), min_bloco=int(min_bloco), max_nivel=int(max_nivel))

        raiz = NodeQuadTree(x=0, y=0, largura=largura, altura=altura, level=0)
        qt.raiz = raiz

        fila = deque([raiz])
        idx = 0

        while fila and idx < len(bits):
            no = fila.popleft()
            qt.total_nos += 1

            bit = bits[idx]
            idx += 1

            if bit == 1:  # folha
                if idx + 8 > len(bits):
                    raise ValueError("Fluxo de bits corrompido: bits insuficientes para cor.")
                cor = 0
                for _ in range(8):
                    cor = (cor << 1) | bits[idx]
                    idx += 1
                no.cor_media = cor
                no.eh_folha = True
                qt.total_folhas += 1
            else:  # nó interno
                no.eh_folha = False
                mx = no.largura // 2
                my = no.altura // 2
                prox = no.level + 1

                # Mesmas dimensões do _inserir_recursivo
                no.filhos[0] = NodeQuadTree(no.x, no.y, mx, my, prox)  # TL
                no.filhos[1] = NodeQuadTree(no.x + mx, no.y, no.largura - mx, my, prox)  # TR
                no.filhos[2] = NodeQuadTree(no.x, no.y + my, mx, no.altura - my, prox)  # BL
                no.filhos[3] = NodeQuadTree(no.x + mx, no.y + my, no.largura - mx, no.altura - my, prox)  # BR

                for filho in no.filhos:
                    fila.append(filho)

        return qt

    @classmethod
    def carregar_arvore(cls, caminho: str) -> "QuadTree":
        """
        Carrega e desserializa uma QuadTree a partir de um arquivo binário.

        caminho: caminho do arquivo gerado por salvar_arvore()
        Returns: instância de QuadTree reconstruída
        """
        with open(caminho, "rb") as f:
            dados = f.read()
        return cls.deserializar(dados)

    def __repr__(self) -> str:
        return (
            f"Quadtree(limiar={self.limiar}, "
            f"nos={self.total_nos}, "
            f"folhas={self.total_folhas})"
        )
