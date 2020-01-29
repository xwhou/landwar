SHELL := /bin/bash

INC=-I./hashdict/ -I./queue/ -I./general_array/ -I./
CC=gcc -std=c11 -O3 -g -Wall 
CCO=gcc -std=c11 -O3 -g -Wall -fPIC 
CCSO=gcc -std=c11 -fPIC -shared -O3 -Wall

#CUDAINC=-I /usr/local/cuda-9.1/include/
#CUDALIB=-L/usr/local/cuda-9.1/lib64 -lcudart
#NVCCO=nvcc -O3 -g  --compiler-options "-Wall -fPIC" -gencode arch=compute_61,code=sm_61 

#utilities.so:  feature.o strategy.o judge.o map.o operator.o  hex.o  weapen.o common.o hashdict.o  queue.o ga.o utilities.o  strategy_cu.o feature_cu.o map_cu.o judge_cu.o weapen_cu.o cuda_final.o
utilities.so:  feature.o strategy.o judge.o map.o operator.o  hex.o  weapen.o common.o hashdict.o  queue.o ga.o utilities.o  
	$(CCSO) *.o -o utilities.so 

utilities.o:utilities.c utilities.h
	$(CCO) -c utilities.c -o utilities.o $(INC)
strategy.o: strategy.c strategy.h 
	$(CCO) -c strategy.c -o strategy.o $(INC)
feature.o: feature.c feature.h 
	$(CCO) -c feature.c -o feature.o $(INC)
judge.o: judge.c judge.h 
	$(CCO) -c judge.c -o judge.o $(INC)
operator.o:operator.c operator.h weapen.h
	$(CCO) -c operator.c -o operator.o 
weapen.o:weapen.c weapen.h ./hashdict/hashdict.h 
	$(CCO) -c weapen.c  -o weapen.o $(INC)
map.o:map.c map.h 
	$(CCO) -c map.c -o map.o $(INC)
hex.o:hex.c hex.h
	$(CCO) -c hex.c -o hex.o $(INC)
common.o:common.c common.h
	$(CCO) -c common.c -o common.o
hashdict.o:./hashdict/hashdict.c ./hashdict/hashdict.h
	$(CCO) -c ./hashdict/hashdict.c -o hashdict.o $(INC)
queue.o:./queue/queue.c ./queue/queue.h 
	$(CCO) -c ./queue/queue.c -o queue.o  $(INC)
ga.o:./general_array/general_array.c ./general_array/general_array.h
	$(CCO) -c ./general_array/general_array.c -o ga.o  $(INC)

# cuda-c 
#map_cu.o:map.cu map_cu.h hex.h hex.c
#	$(NVCCO) --device-c map.cu -o map_cu.o $(CUDAINC) $(INC)
#weapen_cu.o:weapen.cu weapen_cu.h map_cu.h
#	$(NVCCO) --device-c weapen.cu -o weapen_cu.o $(CUDAINC) $(INC)
#judge_cu.o:judge.cu judge_cu.h map_cu.h
#	$(NVCCO) --device-c judge.cu -o judge_cu.o $(CUDAINC) $(INC)
#feature_cu.o: feature.cu feature_cu.h map_cu.h judge_cu.h weapen_cu.h
#	$(NVCCO) --device-c feature.cu -o feature_cu.o $(INC) $(CUDAINC)
#strategy_cu.o: strategy.cu strategy_cu.h feature_cu.h map_cu.h judge_cu.h weapen_cu.h 
#	$(NVCCO) --device-c strategy.cu -o strategy_cu.o $(INC) $(CUDAINC)
#cuda_final.o: feature_cu.o  map_cu.o judge_cu.o weapen_cu.o
#	$(NVCCO) --device-link strategy_cu.o feature_cu.o map_cu.o judge_cu.o  weapen_cu.o -o cuda_final.o $(CUDAINC)
clean:
	rm *.o
copy: 	
	cp utilities.so utilities1.so
	cp utilities.so utilities2.so
	cp utilities.so utilities3.so
	cp utilities.so utilities4.so
	cp utilities.so utilities5.so
	cp utilities.so utilities6.so
	cp utilities.so utilities7.so
	cp utilities.so utilities8.so
	cp utilities.so gytd.so
