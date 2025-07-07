// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

@2
M=0 // R2 = 0 

@1
D=M
@R1
M=D // Store R1 in R1 variable (RAM[17])

(LOOP)
  @R1
  D=M
  @END
  D;JEQ // Exit if R1 == 0

  @0
  D=M
  @2
  M=M+D // R2 += R0

  @R1
  M=M-1 // R1--

  @LOOP
  0;JMP

(END)
  @END
  0;JMP // Inf loop to halt
