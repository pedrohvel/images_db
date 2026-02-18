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
    """Executa a sincronização condicional baseada na detecção de mudanças."""
    try:
        # Captura o estado atual do repositório (vetor de mudanças)
        status_proc = subprocess.run(
            ["git", "status", "--porcelain"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        # Se o stdout estiver vazio, não há o que processar
        if not status_proc.stdout.strip():
            print("[*] Entropia Zero: Repositório já está em estado de equilíbrio (Clean).")
            return

        print("[*] Mudanças detectadas. Iniciando propagação...")
        subprocess.run(["git", "add", "."], check=True)
        
        # O commit agora só ocorre se houver arquivos no index
        subprocess.run(["git", "commit", "-m", "update: obras otimizadas via pipeline"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[+] Sincronização concluída com sucesso.")
        
    except subprocess.CalledProcessError as e:
        print(f"[!] Erro crítico na execução do Git: {e}")

if __name__ == "__main__":
    optimize_images()
    git_sync()