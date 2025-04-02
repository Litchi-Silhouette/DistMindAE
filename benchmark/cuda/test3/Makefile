CC=nvcc
CPPFLAGS=-lrt -lpthread
UTILS=../../../source/utils/tcp/tcp.cpp ../../../source/utils/shared_memory/shared_memory.cpp

all: cache.out client.out

%.out: %.cu
	$(CC) -o $@ $< $(UTILS) $(CPPFLAGS)

clean:
	rm *.out