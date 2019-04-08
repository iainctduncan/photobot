# Makefile for FLIRA65-Capture 

# ICTD trying changing 0.4 to 0.6.1 for aravis
CC = gcc
#FLAGS = --std=c99 -I./contrib/include/ -I./contrib/include/aravis-0.6/ $(shell pkg-config --cflags gobject-2.0) $(shell pkg-config --cflags libpng12) -g
FLAGS = --std=c99 -I/usr/local/include/ -I/usr/local/include/aravis-0.4/ $(shell pkg-config --cflags gobject-2.0) $(shell pkg-config --cflags libpng16) -g
#LIB = -L./contrib/lib -laravis-0.4 $(shell pkg-config --libs gobject-2.0) $(shell pkg-config --libs libpng12) -lrt
LIB = -L/usr/local/lib -laravis-0.4 $(shell pkg-config --libs gobject-2.0) $(shell pkg-config --libs libpng16) -lrt
PREPROCESSOR_FLAGS = 
OBJ = FLIRA65-Capture.o savebuffer.o
BIN = FLIRA65-Capture

$(BIN) : $(OBJ)
	$(CC) -o $(BIN) $(OBJ) $(LIB)

%.o : %.c
	$(CC) $(FLAGS) $(PREPROCESSOR_FLAGS) -o $@ -c $<


clean :
	$(RM) $(OBJ)

