# Prepare
mkdir build
mkdir build/output
mkdir build/kernel

# Assembly
nasm -f elf64 src/boot/header.asm -o build/output/header.o
nasm -f elf64 src/boot/main.asm -o build/output/main.o
nasm -f elf64 src/boot/main64.asm -o build/output/main64.o

# C
gcc -m64 -ffreestanding -c src/kernel/c_helpers/vga_helper.c -o build/output/vga_helper.o
gcc -m64 -ffreestanding -c src/kernel/c_helpers/str_helper.c -o build/output/str_helper.o

# Zap
zapc -nostdlib --allow-unsafe -c src/kernel/main.zp
mv a.out build/output/krnl.o

# Linker
ld -m elf_x86_64 -n -o build/kernel/kernel.bin -T target/linker.ld build/output/*.o

# ISO
cp build/kernel/kernel.bin target/content/boot/kernel.bin
grub-mkrescue /usr/lib/grub/i386-pc -o build/kernel/kernel.iso target/content