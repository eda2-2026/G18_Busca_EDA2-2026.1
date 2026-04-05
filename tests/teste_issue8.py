import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from image_utils import mostrar_comparativo, desenhar_blocos
from quadtree import QuadTree

def teste_mostrar_comparativo_blocos():
    print("Iniciando Testes da Issue #8 (Visualizações Matplotlib)...")
    
    # Cria uma imagem de teste 64x64 com padrões simples
    pixels = np.zeros((64, 64), dtype=np.uint8)
    pixels[0:32, 0:32] = 200     # Quadrante superior esquerdo claro
    pixels[32:64, 32:64] = 100   # Quadrante inferior direito médio
    # O restante fica 0 (preto)
    
    # Cria e processa uma quadtree para ter os blocos e a imagem comprimida
    qt = QuadTree(limiar=10.0)
    qt.inserir(pixels)
    comprimida = qt.reconstruir(pixels.shape)
    
    # ── Teste Mostrar Comparativo ──────────────────────────────
    print("Testando 'mostrar_comparativo'...")
    try:
        # Como o teste é automatizado, idealmente a janela abre e espera fechar.
        # Estamos executando a função para garantir que não há erros de sintaxe ou execução.
        # Em um uso interativo ela mostraria o plot. Aqui vamos apenas chamá-la.
        mostrar_comparativo(pixels, comprimida, 35.5, qt.limiar)
        print("Mostrar Comparativo OK (A janela foi gerada, feche-a para continuar)")
    except Exception as e:
        print(f"Erro em mostrar_comparativo: {e}")
        assert False
        
    # ── Teste Desenhar Blocos ──────────────────────────────────
    print("Testando 'desenhar_blocos'...")
    try:
        desenhar_blocos(pixels, qt)
        print("Desenhar Blocos OK (A janela foi gerada, feche-a para continuar)")
    except Exception as e:
        print(f"Erro em desenhar_blocos: {e}")
        assert False

    print("\n Issue #8 concluída com sucesso!")

if __name__ == "__main__":
    teste_mostrar_comparativo_blocos()
