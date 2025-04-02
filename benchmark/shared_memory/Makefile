CC=g++
CPPFLAGS=-lrt -lpthread
UTILS=../../source/utils/tcp/tcp.cpp ../../source/utils/shared_memory/shared_memory.cpp

all: writer.out reader.out create.out

%.out: %.cpp
	$(CC) -o $@ $< $(UTILS) $(CPPFLAGS)

clean:
	rm *.out