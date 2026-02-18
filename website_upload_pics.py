import os
import subprocess
from pathlib import Path
from PIL import Image

# DETERMINAÇÃO DO CONTEXTO (Garante que o script ache as pastas de qualquer lugar)
BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "staging"
EXPORT_DIR = BASE_DIR / "images"

# CONFIGURAÇÕES
QUALITY = 85
MAX_WIDTH = 1920

def optimize_images():
    """Redimensiona e comprime imagens com suporte a múltiplas extensões."""
    if not EXPORT_DIR.exists():
        EXPORT_DIR.mkdir(parents=True)

    # Captura jpg, jpeg, png (ignorando maiúsculas/minúsculas)
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG")
    files_found = []
    for ext in extensions:
        files_found.extend(SOURCE_DIR.glob(ext))

    if not files_found:
        print(f"[!] Aviso: Nenhuma imagem encontrada em {SOURCE_DIR}")
        return False

    for img_path in files_found:
        print(f"[*] Processando: {img_path.name}")
        try:
            with Image.open(img_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                if img.width > MAX_WIDTH:
                    ratio = MAX_WIDTH / float(img.width)
                    new_height = int(float(img.height) * float(ratio))
                    img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)
                
                output_path = EXPORT_DIR / f"{img_path.stem}.jpg"
                img.save(output_path, "JPEG", quality=QUALITY, optimize=True)
                print(f"[V] Salvo em: {output_path}")
        except Exception as e:
            print(f"[!] Erro ao processar {img_path.name}: {e}")
    return True

def git_sync():
    """Sincroniza com o GitHub."""
    os.chdir(BASE_DIR) # Garante que estamos dentro do repo para o Git funcionar
    try:
        status_proc = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        
        if not status_proc.stdout.strip():
            print("[*] Entropia Zero: Nada para subir.")
            return

        print("[*] Propagando alterações para o GitHub...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "update: novas obras otimizadas"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[+] Sincronização concluída.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Falha no Git: {e}")

if __name__ == "__main__":
    if optimize_images():
        git_sync()