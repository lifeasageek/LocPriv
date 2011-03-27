all:
	rm -rf myemd emd.so emd.o example1.o
	gcc emd.c example1.c -o myemd
	gcc -c -fPIC emd.c -o emd.o
	gcc -c -fPIC example1.c -o example1.o
	gcc -shared -Wl,-soname,emd.so -o emd.so emd.o example1.o
