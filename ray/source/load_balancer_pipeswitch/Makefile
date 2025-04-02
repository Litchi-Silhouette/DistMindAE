CC=g++
CPPFLAGS=-lpthread
DEPS=*.cpp

all: load_balancer.out

%.out: $(DEPS)
	$(CC) -o $@ $(DEPS) $(CPPFLAGS)

clean:
	rm *.out