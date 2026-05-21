x86_64_asm_boot_files := $(shell find src/boot/*.asm)
x86_64_asm_objs_files := $(patsubst src/boot/%.asm, build/%.o, $(x86_64_asm_boot_files))

x86_64_c_boot_files := $(shell find src/boot/*.asm)
x86_64_c_objs_files := $(patsubst src/boot/%.asm, build/%.o, $(x86_64_asm_boot_files))

$(x86_64_asm_objs_files): build/%.o : src/boot/%.asm
	mkdir -p $(dir $@) && \
	nasm -f elf64 $(patsubst build/%.o, src/boot/%.asm, $@) -o $@

.PHONY: build-x86_64
build-x86_64: $(x86_64_asm_objs_files)
	mkdir -p build/dist/ && .
	ld -m elf_x86_64 -n -o build/dist/kernel.bin -T target/linker.ld $(x86_64_asm_objs_files) && \
	cp build/dist/kernel.bin target/content/boot/kernel.bin && \
	grub-mkrescue /usr/lib/grub/i386-pc -o build/dist/kernel.iso target/content