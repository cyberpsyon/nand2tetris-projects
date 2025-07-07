@0
D=M
@2
M=D

@1
D=M
@i
M=D

(LOOP)
@i
D=M
@END
D;JEQ

@2
M=M+1

@i
M=M-1

@LOOP
0;JMP

(END)
@END
0;JMP
