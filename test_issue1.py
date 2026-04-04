# teste_issue1.py
from quadtree import NodeQuadTree, QuadTree

# ── Teste NoQuadtree ──────────────────────────────────────
no = NodeQuadTree(x=0, y=0, width=512, height=512, level=0)

assert no.x == 0
assert no.y == 0
assert no.width == 512
assert no.height == 512
assert no.level == 0
assert no.cor_media == 0
assert no.variancia == 0.0
assert no.eh_folha == False
assert no.filhos == [None, None, None, None]
assert no.eh_raiz() == True
assert no.total_pixels() == 512 * 512

print("NoQuadtree OK")
print(no)

# ── Teste filho manual ────────────────────────────────────
no.filhos[0] = NodeQuadTree(0, 0, 256, 256, level=1)  # TL
no.filhos[1] = NodeQuadTree(256, 0, 256, 256, level=1)  # TR
no.filhos[2] = NodeQuadTree(0, 256, 256, 256, level=1)  # BL
no.filhos[3] = NodeQuadTree(256, 256, 256, 256, level=1)  # BR

assert no.filhos[0].level == 1
assert no.filhos[0].eh_raiz() == False
print("Filhos OK")

# ── Teste Quadtree ────────────────────────────────────────
qt = QuadTree(limiar=20.0)

assert qt.limiar == 20.0
assert qt.min_bloco == 2
assert qt.max_nivel == 8
assert qt.raiz is None
assert qt.total_nos == 0
assert qt.total_folhas == 0
assert qt.is_empty() == True

print("Quadtree OK")
print(qt)
print(qt.estatistica())

print("\n Issue #1 concluída com sucesso!")
