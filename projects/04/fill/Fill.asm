// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.
(LOOP)
  @KBD
  D=M
  @FILL_BLACK
  D;JNE    // If key is pressed, go fill black

  @FILL_WHITE
  0;JMP    // If no key, go fill white

// Fill screen black
(FILL_BLACK)
  @SCREEN
  D=A
  @PTR
  M=D

  @8192
  D=A
  @COUNT
  M=D

(BLACK_LOOP)
  @COUNT
  D=M
  @LOOP
  D;JEQ

  @PTR
  A=M
  M=-1

  @PTR
  M=M+1
  @COUNT
  M=M-1
  @BLACK_LOOP
  0;JMP

// Fill screen white
(FILL_WHITE)
  @SCREEN
  D=A
  @PTR
  M=D

  @8192
  D=A
  @COUNT
  M=D

(WHITE_LOOP)
  @COUNT
  D=M
  @LOOP
  D;JEQ

  @PTR
  A=M
  M=0

  @PTR
  M=M+1
  @COUNT
  M=M-1
  @WHITE_LOOP
  0;JMP









