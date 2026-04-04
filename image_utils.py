from PIL import Image
import numpy as np

def carregar(caminho):
    """
    Carrega uma imagem a partir do caminho, converte para escala de cinza
    e retorna como um array NumPy 2D (uint8).
    """
    # Abre a imagem e converte para 'L' (escala de cinza, 8-bit pixels)
    img = Image.open(caminho).convert('L')
    
    # Converte a imagem do Pillow para um array NumPy
    pixels = np.array(img, dtype=np.uint8)
    
    return pixels

def salvar(pixels, caminho):
    """
    Recebe um array NumPy 2D correspondente a uma imagem em escala de cinza
    e a salva no caminho especificado.
    """
    # Se garantir que está no tipo correto 
    if pixels.dtype != np.uint8:
        pixels = pixels.astype(np.uint8)
        
    # Cria uma imagem a partir do array e salva
    img = Image.fromarray(pixels, mode='L')
    img.save(caminho)
