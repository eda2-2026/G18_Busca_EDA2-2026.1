# test_issue5.py
import numpy as np
from quadtree import QuadTree

# ── Teste 1: imagem uniforme ──────────────────────────────
# Folha única com cor 128 → reconstrução idêntica ao original
pixels = np.full((8, 8), fill_value=128, dtype=np.uint8)
qt = QuadTree(limiar=10.0)
qt.inserir(pixels)
reconstruida = qt.reconstruir(pixels.shape)

assert reconstruida.shape == pixels.shape
assert reconstruida.dtype == np.uint8
assert np.all(reconstruida == 128)
print("✅ Teste 1: imagem uniforme reconstruída corretamente")

# ── Teste 2: imagem com dois blocos distintos ─────────────
# Metade esquerda = 0, metade direita = 255
# Após reconstrução cada bloco deve ter sua cor média
pixels2 = np.zeros((8, 8), dtype=np.uint8)
pixels2[:, 4:] = 255
qt2 = QuadTree(limiar=10.0)
qt2.inserir(pixels2)
rec2 = qt2.reconstruir(pixels2.shape)

assert rec2.shape == (8, 8)
# lado esquerdo deve ser escuro, lado direito claro
assert np.mean(rec2[:, :4]) < 50
assert np.mean(rec2[:, 4:]) > 200
print("✅ Teste 2: dois blocos distintos reconstruídos corretamente")

# ── Teste 3: a reconstrução não modifica o array original ─
pixels3 = np.random.randint(0, 256, (16, 16), dtype=np.uint8)
copia = pixels3.copy()
qt3 = QuadTree(limiar=20.0)
qt3.inserir(pixels3)
qt3.reconstruir(pixels3.shape)

assert np.array_equal(
    pixels3, copia
), "inserir/reconstruir não deve alterar o array original"
print("✅ Teste 3: array original não foi modificado")

# ── Teste 4: limiar alto → menos folhas → imagem mais borrada
pixels4 = np.random.randint(0, 256, (64, 64), dtype=np.uint8)

qt_preciso = QuadTree(limiar=5.0)
qt_borrado = QuadTree(limiar=200.0)

qt_preciso.inserir(pixels4)
qt_borrado.inserir(pixels4)

rec_preciso = qt_preciso.reconstruir(pixels4.shape)
rec_borrado = qt_borrado.reconstruir(pixels4.shape)

# Limiar baixo = mais folhas = mais fiel ao original
from image_utils import psnr

psnr_preciso = psnr(pixels4, rec_preciso)
psnr_borrado = psnr(pixels4, rec_borrado)

assert psnr_preciso >= psnr_borrado, "limiar baixo deve gerar PSNR maior"
print(f"✅ Teste 4: PSNR preciso={psnr_preciso:.1f}dB | borrado={psnr_borrado:.1f}dB")

# ── Teste 5: erro ao reconstruir sem inserir ──────────────
qt_vazio = QuadTree(limiar=10.0)
try:
    qt_vazio.reconstruir((8, 8))
    assert False, "Deveria ter lançado ValueError"
except ValueError as e:
    print(f"✅ Teste 5: erro capturado corretamente → '{e}'")

print("\n🎉 Issue #5 concluída com sucesso!")
