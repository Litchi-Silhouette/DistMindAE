CC=g++
UTILS=../../source/utils/tcp/tcp.cpp

all: client.out server.out

%.out: %.cpp
	$(CC) -o $@ $< $(UTILS)

clean:
	rm *.out