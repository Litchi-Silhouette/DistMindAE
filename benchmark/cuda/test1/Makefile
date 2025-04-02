CC=nvcc
UTILS=../../source/utils/tcp/tcp.cpp

all: first.out second.out

%.out: %.cu
	$(CC) -o $@ $< $(UTILS)

clean:
	rm *.out