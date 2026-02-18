import os
import shutil
import subprocess
import uuid
from pathlib import Path
from PIL import Image

# DETERMINAÇÃO DO CONTEXTO
BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "staging"
EXPORT_DIR = BASE_DIR / "images"

# CONFIGURAÇÕES DE CONSERVAÇÃO
QUALITY = 95 # Aumentado de 85 para 95 (Conservação de Alta Fidelidade)
MAX_WIDTH = 1920

# VETORES DE CLASSIFICAÇÃO
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
RAW_EXTS = {".gif", ".mp4", ".webm", ".mp3", ".wav", ".ogg"}

def generate_token():
    """Gera um hash hexadecimal único de 12 caracteres."""
    return uuid.uuid4().hex[:12].upper()

def process_assets():
    """Roteia, processa e tokeniza assets com suporte universal de formatos."""
    if not EXPORT_DIR.exists():
        EXPORT_DIR.mkdir(parents=True)

    # Captura todos os arquivos na staging (ignora pastas e arquivos ocultos)
    files_found = [f for f in SOURCE_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]

    if not files_found:
        print(f"[*] Entropia Zero: Nenhum asset na fila de ingestão ({SOURCE_DIR}).")
        return False

    processed_any = False

    for file_path in files_found:
        ext = file_path.suffix.lower()
        token = generate_token()
        
        # FLUXO 1: OTIMIZAÇÃO DE IMAGEM
        if ext in IMAGE_EXTS:
            output_path = EXPORT_DIR / f"{token}.jpg"
            try:
                with Image.open(file_path) as img:
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    if img.width > MAX_WIDTH:
                        ratio = MAX_WIDTH / float(img.width)
                        new_height = int(float(img.height) * float(ratio))
                        img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)
                    
                    img.save(output_path, "JPEG", quality=QUALITY, optimize=True)
                    print(f"[+] Imagem Processada: {token} -> {output_path.name}")
                    processed_any = True
                    file_path.unlink() # Esvazia o staging
            except Exception as e:
                print(f"[!] Erro Crítico na Imagem {file_path.name}: {e}")

        # FLUXO 2: BYPASS DE MÍDIA BRUTA (Vídeos, GIFs, Áudios)
        elif ext in RAW_EXTS:
            # Mantém a extensão original para que o Worker consiga identificar a tag correta
            output_path = EXPORT_DIR / f"{token}{ext}"
            try:
                shutil.copy2(file_path, output_path)
                print(f"[+] Mídia Copiada (Bypass): {token} -> {output_path.name}")
                processed_any = True
                file_path.unlink() # Esvazia o staging
            except Exception as e:
                print(f"[!] Erro Crítico na Mídia {file_path.name}: {e}")
        
        # FLUXO 3: REJEIÇÃO
        else:
            print(f"[-] Formato Não Suportado Ignorado: {file_path.name}")

    return processed_any

def git_sync():
    """Sincroniza o estado local com a nuvem."""
    os.chdir(BASE_DIR)
    try:
        status_proc = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        
        if not status_proc.stdout.strip():
            print("[*] Estado Constante: Nada para sincronizar.")
            return

        print("[*] Propagando dados para a Nuvem...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "sys-auto: ingestão de novos assets tokenizados"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[V] Sincronização Absoluta Concluída.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Falha na Sincronização Git: {e}")

if __name__ == "__main__":
    if process_assets():
        git_sync()