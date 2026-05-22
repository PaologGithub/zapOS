# Imports
from pathlib import Path
import os
import json
import hashlib
import shutil

# Functions
def get_files_tree(dir: Path, search_pattern: str) -> list[Path]:
    files = []
    
    for root, _, filenames in os.walk(dir):
        for file in filenames:
            if search_pattern in file:
                path = Path(root) / file
                files.append(path)
    
    return files

def get_file_sha(path: Path) -> str:
    sha = hashlib.sha256()

    with open(path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)

    return sha.hexdigest()

# Paths
source_path  = Path("src")
build_path   = Path("build")
output_path  = build_path / "output"
kernel_path  = build_path / "kernel"

asm_out_path = output_path / "asm"
c_out_path   = output_path / "c"
zap_out_path = output_path / "zap"

shas_path    = build_path / "cached_shas.json"

# Loads cached shas
cached_shas: dict[str, str] = {}

if shas_path.exists():
    with open(shas_path, "r") as f:
        cached_shas = json.load(f)

# Prepare building
for path in [build_path, output_path, kernel_path, asm_out_path, c_out_path, zap_out_path]:
    path.mkdir(parents=True, exist_ok=True)

# Assembly
for asm_file in get_files_tree(source_path, ".asm"):
    filename = os.path.splitext(os.path.basename(asm_file.name))[0]

    # sha
    file_sha = get_file_sha(asm_file)
    file = str(asm_file)

    cached_sha = cached_shas.get(file)
    if cached_sha == file_sha and f"{filename}.o" in os.listdir(asm_out_path):
        continue

    print(f"Building {filename}.asm")

    os.system(f"nasm -f elf64 {file} -o {str(asm_out_path / (filename + ".o"))}")

    cached_shas[file] = file_sha

# C
for c_file in get_files_tree(source_path, ".c"):
    filename = os.path.splitext(os.path.basename(c_file.name))[0]

    # sha
    file_sha = get_file_sha(c_file)
    file = str(c_file)

    cached_sha = cached_shas.get(file)
    if cached_sha == file_sha and f"{filename}.o" in os.listdir(c_out_path):
        continue

    print(f"Building {filename}.c")

    os.system(f"gcc -m64 -ffreestanding -c {file} -o {str(c_out_path / (filename + ".o"))}")

    cached_shas[file] = file_sha

# Zap
# We only need to compile main.zp for now, but I keep this
#  for loop just in case
for zap_file in [source_path / "kernel" / "main.zp"]:
    filename = os.path.splitext(os.path.basename(zap_file.name))[0]

    # sha
    file_sha = get_file_sha(zap_file)
    file = str(zap_file)

    cached_sha = cached_shas.get(file)
    if cached_sha == file_sha and f"{filename}.o" in os.listdir(zap_out_path):
        continue

    print(f"Building {filename}.zp")

    os.system(f"zapc -nostdlib --allow-unsafe -c {file}")
    os.replace("a.out", str(zap_out_path / (filename + ".o")))

    cached_shas[file] = file_sha

# Linker
command = "ld -m elf_x86_64 -n -o build/kernel/kernel.bin -T target/linker.ld "
for o_file in get_files_tree(output_path, ".o"):
    command += (str(o_file) + " ")
os.system(command)

# ISO
shutil.copy(str(kernel_path / "kernel.bin"), "target/content/boot/kernel.bin")
os.system("grub-mkrescue /usr/lib/grub/i386-pc -o build/kernel/kernel.iso target/content")

# Save cached sha
with open(shas_path, "w", encoding="utf-8") as f:
    json.dump(cached_shas, f, indent=4)