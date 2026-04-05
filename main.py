import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Importa as utilidades e classes criadas nas issues anteriores
from image_utils import carregar, salvar, psnr, mostrar_comparativo, desenhar_blocos
from quadtree import QuadTree

def comprimir(entrada, saida, limiar):
    """
    Realiza o fluxo completo de compressão de uma imagem:
    1. Carrega a imagem original do disco.
    2. Insere os blocos na QuadTree usando o limiar informado.
    3. Reconstrói a imagem comprimida.
    4. Salva o resultado reconstruído no caminho especificado.
    5. Retorna um dicionário com estatísticas (PSNR, número de folhas, taxa de compressão).
    """
    print(f"\n[+] Comprimindo '{entrada}' com limiar {limiar}...")
    
    # 1. Carregar
    original = carregar(entrada)
    
    # 2. Estruturar a QuadTree
    qt = QuadTree(limiar=limiar)
    qt.inserir(original)
    
    # 3. Reconstruir a nova imagem processada
    comprimida = qt.reconstruir(original.shape)
    
    # 4. Salvar imagem no disco
    salvar(comprimida, saida)
    
    # 5. Computar Métricas
    psnr_val = psnr(original, comprimida)
    stats = qt.estatistica()
    
    print(f"    -> Concluído! PSNR: {psnr_val:.2f} dB, Folhas: {stats['total_folhas']}")
    
    return {
        "limiar": limiar,
        "psnr": psnr_val,
        "folhas": stats["total_folhas"],
        "taxa_compressao": stats["taxa_compressao"],
        "quadtree": qt,
        "original": original,
        "comprimida": comprimida
    }

def benchmark_limiares(caminho):
    """
    Testa diversos limiares de variância predefinidos na mesma imagem
    e retorna os resultados comparativos de cada execução.
    """
    limiares = [1.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0]
    resultados = []
    
    print(f"=== Iniciando Benchmark de Limiares ===")
    
    for lim in limiares:
        saida_temp = f"temp_limiar_{lim}.png"
        res = comprimir(caminho, saida_temp, limiar=lim)
        resultados.append(res)
        
        # Apaga o arquivo temporário apenas se preferir não manter os arquivos
        if os.path.exists(saida_temp):
             os.remove(saida_temp)
             
    print("\n=== Benchmark Finalizado ===")
    return resultados

def grafico_limiares(resultados):
    """
    Plota dois gráficos combinados em um só (com eixos Y paralelos):
    - PSNR versus Limiar (Métrica de Qualidade)
    - Folhas versus Limiar (Custo de Estrutura / Memória)
    """
    # Extrai os dados do dicionário de resultados
    limiares = [r["limiar"] for r in resultados]
    
    # Caso PSNR seja infinito, substitui por um teto representativo para a visualização
    psnrs = [r["psnr"] if r["psnr"] != float('inf') else 100.0 for r in resultados]
    folhas = [r["folhas"] for r in resultados]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Grafico 1: PSNR (Eixo Y da esquerda)
    cor1 = 'tab:blue'
    ax1.set_xlabel('Limiar de Variância')
    ax1.set_ylabel('PSNR (Qualidade em dB)', color=cor1)
    ax1.plot(limiares, psnrs, marker='o', linestyle='-', color=cor1, label='PSNR')
    ax1.tick_params(axis='y', labelcolor=cor1)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Grafico 2: Quantidade de Folhas (Eixo Y da direita - twinx)
    ax2 = ax1.twinx()
    cor2 = 'tab:red'
    ax2.set_ylabel('Número de Folhas (Tamanho)', color=cor2)
    ax2.plot(limiares, folhas, marker='s', linestyle='--', color=cor2, label='Folhas')
    ax2.tick_params(axis='y', labelcolor=cor2)

    # Título e ajustes finais
    plt.title('Desempenho da Compressão QuadTree: PSNR e Qt. Folhas versus Limiar')
    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    # ==========================================
    # FLUXO DE TESTE DA MAIN ()
    # ==========================================
    pasta_imagens = "images"
    pasta_saida = "saida"
    
    if not os.path.exists(pasta_imagens):
        os.makedirs(pasta_imagens)
        
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)
        
    # Define o caminho da imagem de entrada e da imagem processada de saída
    imagem_teste = os.path.join(pasta_imagens, "imagem_teste.png")
    saida_teste = os.path.join(pasta_saida, "teste_unico.png")
    
    # 1. Pega da pasta 'images'. Se não existir, gera uma gradiente de exemplo lá dentro para o código não quebrar
    if not os.path.exists(imagem_teste):
        print(f"Aviso: Imagem não encontrada. Gerando imagem sintética em '{imagem_teste}'...")
        x = np.linspace(0, 255, 256)
        y = np.linspace(0, 255, 256)
        X, Y = np.meshgrid(x, y)
        gradiente = ((X + Y) / 2).astype(np.uint8)
        Image.fromarray(gradiente, mode='L').save(imagem_teste)
    else:
        print(f"Lendo imagem a partir do diretório: {imagem_teste}")
    
    # 2. Demonstrar uma compressão única utilizando ferramentas visuais (Issue #8)
    res_comum = comprimir(imagem_teste, saida_teste, limiar=15.0)
    
    print("\nAbrindo Comparativo Visual da compressão única...")
    mostrar_comparativo(res_comum['original'], res_comum['comprimida'], res_comum['psnr'], res_comum['limiar'])
    
    print("\nAbrindo Desenho de Blocos (Isso mostrará as partições da QuadTree)...")
    desenhar_blocos(res_comum['original'], res_comum['quadtree'])
    
    # 3. Rodar Benchmark do gráfico completo (Limiares variando)
    print("\nIniciando testes em lote (Benchmark) para montar os gráficos...")
    resultados_lote = benchmark_limiares(imagem_teste)
    
    # 4. Plotar gráfico analítico
    print("Gerando Gráficos Analíticos...")
    grafico_limiares(resultados_lote)
    
    # Limpeza
    if os.path.exists(saida_teste): os.remove(saida_teste)
