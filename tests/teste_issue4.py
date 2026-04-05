# test_issue4.py
import numpy as np
from quadtree import QuadTree, NodeQuadTree

# ── Teste 1: imagem totalmente uniforme ──────────────────
# Variância = 0 → a raiz já deve virar folha
pixels_uniforme = np.full((8, 8), fill_value=128, dtype=np.uint8)
qt = QuadTree(limiar=10.0)
qt.inserir(pixels_uniforme)

assert qt.raiz is not None
assert qt.raiz.eh_folha == True  # bloco uniforme → folha imediata
assert qt.total_nos == 1
assert qt.total_folhas == 1
assert qt.raiz.cor_media == 128
assert qt.raiz.variancia == 0.0
print("✅ Teste 1 passou: imagem uniforme vira folha na raiz")

# ── Teste 2: imagem com variação total ───────────────────
# Metade escura, metade clara → raiz deve dividir
pixels_variado = np.zeros((8, 8), dtype=np.uint8)
pixels_variado[:, 4:] = 255  # lado direito branco
qt2 = QuadTree(limiar=10.0)
qt2.inserir(pixels_variado)

assert qt2.raiz.eh_folha == False  # deve ter dividido
assert qt2.total_nos > 1
assert qt2.total_folhas > 0
print(
    f"✅ Teste 2 passou: imagem variada dividiu → {qt2.total_nos} nós, {qt2.total_folhas} folhas"
)

# ── Teste 3: limiar alto → menos divisões ────────────────
qt_alto = QuadTree(limiar=1000.0)  # aceita qualquer variância
qt_baixo = QuadTree(limiar=1.0)  # exige blocos muito uniformes

qt_alto.inserir(pixels_variado)
qt_baixo.inserir(pixels_variado)

assert qt_alto.total_folhas <= qt_baixo.total_folhas
print(
    f"✅ Teste 3 passou: limiar alto={qt_alto.total_folhas} folhas | baixo={qt_baixo.total_folhas} folhas"
)

# ── Teste 4: estatísticas coerentes ──────────────────────
stats = qt2.estatistica()
assert stats["total_nos"] == qt2.total_nos
assert stats["total_folhas"] == qt2.total_folhas
assert stats["nos_internos"] == qt2.total_nos - qt2.total_folhas
assert 0.0 <= stats["taxa_compressao"] <= 100.0
print(f"✅ Teste 4 passou: estatísticas → {stats}")

# ── Teste 5: imagem real 64x64 ───────────────────────────
np.random.seed(42)
pixels_real = np.random.randint(0, 256, (64, 64), dtype=np.uint8)
qt_real = QuadTree(limiar=20.0)
qt_real.inserir(pixels_real)

assert qt_real.raiz is not None
assert qt_real.total_folhas > 0
assert qt_real.total_nos >= qt_real.total_folhas
print(
    f"✅ Teste 5 passou: 64x64 aleatório → {qt_real.total_nos} nós, "
    f"{qt_real.total_folhas} folhas, "
    f"compressão={qt_real.estatistica()['taxa_compressao']:.1f}%"
)

print("\n🎉 Issue #4 concluída com sucesso!")
