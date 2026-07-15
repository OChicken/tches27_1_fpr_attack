VPATH  += ../Falcon-impl-20211101/
CFLAGS += -I../Falcon-impl-20211101/ -Wall -Wextra -O2

CC = gcc

OBJ = codec.o common.o falcon.o fft.o fpr.o rng.o shake.o sign.o vrfy.o
SRC = codec.c common.c falcon.c fft.c fpr.c rng.c shake.c sign.c vrfy.c

all: calc_FG gen_rand_key gen_rand_key.so

calc_FG: calc_FG.o $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^

gen_rand_key: gen_rand_key.o $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^

# Shared library for use from Python (ctypes). gen_rand_key.c includes
# keygen.c inline, so keygen.c is not listed in SRC (avoids duplicate symbols).
gen_rand_key.so: gen_rand_key.c $(SRC)
	$(CC) $(CFLAGS) -fPIC -shared -o $@ $^

clean:
	-rm -f *.o calc_FG gen_rand_key gen_rand_key.so
