import os
import subprocess
from pathlib import Path
from PIL import Image

# CONFIGURAÇÕES
SOURCE_DIR = Path("./staging")    # Onde você coloca as imagens brutas
EXPORT_DIR = Path("./images")     # Onde o Git monitora as imagens
QUALITY = 85                      # Equilíbrio ótimo entre compressão e qualidade
MAX_WIDTH = 1920                  # Limite para exibição web fluida

def optimize_images():
    """Redimensiona e comprime imagens antes do envio."""
    if not EXPORT_DIR.exists():
        EXPORT_DIR.mkdir(parents=True)

    for img_path in SOURCE_DIR.glob("*.[jp][pn][g]"): # Captura jpg, jpeg, png
        print(f"[*] Processando: {img_path.name}")
        with Image.open(img_path) as img:
            # Converte para RGB (necessário para salvar JPEG)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Redimensionamento Proporcional
            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / float(img.width)
                new_height = int(float(img.height) * float(ratio))
                img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)
            
            # Salva na pasta de exportação
            img.save(EXPORT_DIR / f"{img_path.stem}.jpg", "JPEG", quality=QUALITY, optimize=True)
        
        # Opcional: Remove da pasta staging após processar
        # os.remove(img_path)

def git_sync():
    """Executa a sincronização com o GitHub images_db."""
    try:
        print("[*] Iniciando Git Push...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "update: nova remessa de obras otimizadas"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[+] Esteira concluída com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Falha no Git: {e}")

if __name__ == "__main__":
    optimize_images()
    git_sync()