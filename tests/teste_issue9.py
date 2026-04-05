# teste_issue9.py
import sys
import os
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
from quadtree import QuadTree

# ── Imagem auxiliar com 4 quadrantes bem distintos ────────
pixels_4q = np.zeros((8, 8), dtype=np.uint8)
pixels_4q[0:4, 0:4] = 10   # TL
pixels_4q[0:4, 4:8] = 200  # TR
pixels_4q[4:8, 0:4] = 50   # BL
pixels_4q[4:8, 4:8] = 150  # BR

qt_original = QuadTree(limiar=5.0)
qt_original.inserir(pixels_4q)

# ── Teste 1: serializar retorna bytes ─────────────────────
dados = qt_original.serializar()
assert isinstance(dados, bytes), "serializar() deve retornar bytes"
assert len(dados) > 0, "bytes serializados não podem ser vazios"
print("✅ Teste 1: serializar() retorna bytes não-vazios")

# ── Teste 2: cabeçalho contém a assinatura 'QT' ───────────
assert dados[:2] == b"QT", f"Assinatura esperada 'QT', obtida '{dados[:2]}'"
print("✅ Teste 2: cabeçalho contém assinatura 'QT'")

# ── Teste 3: deserializar restaura parâmetros da árvore ───
qt_restaurada = QuadTree.deserializar(dados)
assert qt_restaurada.limiar == qt_original.limiar, (
    f"limiar esperado {qt_original.limiar}, obtido {qt_restaurada.limiar}"
)
assert qt_restaurada.min_bloco == qt_original.min_bloco
assert qt_restaurada.max_nivel == qt_original.max_nivel
print("✅ Teste 3: parâmetros da árvore restaurados corretamente")

# ── Teste 4: número de nós e folhas preservados ───────────
assert qt_restaurada.total_folhas == qt_original.total_folhas, (
    f"folhas esperadas {qt_original.total_folhas}, obtidas {qt_restaurada.total_folhas}"
)
assert qt_restaurada.total_nos == qt_original.total_nos, (
    f"nós esperados {qt_original.total_nos}, obtidos {qt_restaurada.total_nos}"
)
print("✅ Teste 4: total de nós e folhas preservados")

# ── Teste 5: reconstrução idêntica após serialização ──────
img_original  = qt_original.reconstruir(pixels_4q.shape)
img_restaurada = qt_restaurada.reconstruir(pixels_4q.shape)
assert np.array_equal(img_original, img_restaurada), (
    "Imagem reconstruída após desserialização difere da original"
)
print("✅ Teste 5: imagem reconstruída idêntica após round-trip")

# ── Teste 6: busca por pixel funciona na árvore restaurada ─
for px, py, cor_esperada in [(1, 1, 10), (6, 1, 200), (1, 6, 50), (6, 6, 150)]:
    no = qt_restaurada.buscar_pixel(px, py)
    assert no.eh_folha, f"nó em ({px},{py}) deveria ser folha"
    assert no.cor_media == cor_esperada, (
        f"cor esperada {cor_esperada} em ({px},{py}), obtida {no.cor_media}"
    )
print("✅ Teste 6: busca por pixel funciona na árvore restaurada")

# ── Teste 7: arquivo binário é menor que a imagem original ─
# Imagem com blocos homogêneos grandes → alta compressibilidade
pixels_grande = np.zeros((256, 256), dtype=np.uint8)
pixels_grande[0:128, 0:128]   = 50
pixels_grande[0:128, 128:256] = 100
pixels_grande[128:256, 0:128] = 150
pixels_grande[128:256, 128:256] = 200
qt_grande = QuadTree(limiar=10.0)
qt_grande.inserir(pixels_grande)

tamanho_arvore = len(qt_grande.serializar())
tamanho_imagem = pixels_grande.nbytes  # 256*256 = 65 536 bytes

assert tamanho_arvore < tamanho_imagem, (
    f"Arquivo da árvore ({tamanho_arvore}B) deveria ser menor que a imagem ({tamanho_imagem}B)"
)
razao = tamanho_imagem / tamanho_arvore
print(
    f"✅ Teste 7: arquivo binário ({tamanho_arvore} bytes) é "
    f"{razao:.1f}x menor que a imagem bruta ({tamanho_imagem} bytes)"
)

# ── Teste 8: salvar_arvore / carregar_arvore (round-trip em disco) ──
with tempfile.NamedTemporaryFile(suffix=".qtb", delete=False) as tmp:
    caminho_tmp = tmp.name

try:
    qt_original.salvar_arvore(caminho_tmp)
    assert os.path.exists(caminho_tmp), "Arquivo não foi criado"
    assert os.path.getsize(caminho_tmp) > 0, "Arquivo criado está vazio"

    qt_disco = QuadTree.carregar_arvore(caminho_tmp)
    img_disco = qt_disco.reconstruir(pixels_4q.shape)
    assert np.array_equal(img_original, img_disco), (
        "Imagem reconstruída após leitura em disco difere da original"
    )
    print("✅ Teste 8: salvar_arvore/carregar_arvore funcionam corretamente")
finally:
    os.unlink(caminho_tmp)

# ── Teste 9: erros esperados ──────────────────────────────
qt_vazio = QuadTree(limiar=10.0)
try:
    qt_vazio.serializar()
    assert False, "Deveria lançar ValueError"
except ValueError as e:
    print(f"✅ Teste 9a: árvore vazia → '{e}'")

try:
    QuadTree.deserializar(b"INVALIDO")
    assert False, "Deveria lançar ValueError"
except ValueError as e:
    print(f"✅ Teste 9b: dados corrompidos → '{e}'")

# ── Teste 10: comparativo BFS (fila) vs varredura linear ──
import time

np.random.seed(0)
pixels_perf = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
qt_perf = QuadTree(limiar=20.0)
qt_perf.inserir(pixels_perf)
dados_perf = qt_perf.serializar()

N = 100

t0 = time.perf_counter()
for _ in range(N):
    QuadTree.deserializar(dados_perf)
t_bfs = (time.perf_counter() - t0) * 1000

print(f"\nComparativo ({N} desserializações em imagem 512x512):")
print(f"   BFS com fila: {t_bfs:.2f} ms total  ({t_bfs/N:.3f} ms/op)")
print(f"   Nós restaurados por op: {qt_perf.total_nos}")

print("\n Issue #9 concluída com sucesso!")
