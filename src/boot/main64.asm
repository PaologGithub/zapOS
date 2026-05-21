; https://github.com/davidcallanan/os-series/blob/ep2/src/impl/x86_64/boot/main64.asm

global long_mode_start
extern kmain

section .text
bits 64
long_mode_start:
    ; load null into all data segment registers
    mov ax, 0
    mov ss, ax
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax

	call kmain
    hlt