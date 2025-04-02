CC=nvcc
CPPFLAGS=-lpthread

all: test.out

%.out: %.cu
	$(CC) -o $@ $< #(CPPFLAGS)

clean:
	rm *.out