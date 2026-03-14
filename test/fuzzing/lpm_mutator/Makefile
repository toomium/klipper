TARGET=mutator
PROTO_DIR=protobuf
FACTORY_DIR=factory
PB_SRC_DIR = $(PROTO_DIR)/genfiles

PROTO_SRC = $(wildcard $(PROTO_DIR)/*.proto)
PB_SRC = $(patsubst $(PROTO_DIR)/%.proto,$(PB_SRC_DIR)/%.pb.cc,$(PROTO_SRC))
PB_OBJS = $(PB_SRC:.cc=.o)
FACTORY_SRC = $(FACTORY_DIR)/_mutator_factory.cc
FACTORY_OBJ = $(FACTORY_SRC:.cc=.o)

OBJ = $(TARGET).o $(FACTORY_OBJ) $(PB_OBJS)

CXXFLAGS= -std=c++17 -fPIC -Wall -Wno-unused-parameter
#-std=c++17 -I$(PB_SRC_DIR)
LDFLAGS = -shared -Wall -O3

LPM_DIR=/usr/local/include/libprotobuf-mutator
# libprotobuf-mutator
PROTOBUF_DIR=/usr/local/include/google/protobuf

LPM_LIB=/usr/local/lib/libprotobuf-mutator.a
# $(LPM_DIR)/build/src/libprotobuf-mutator.a
PROTOBUF_LIB=/usr/local/lib/libprotobuf.a

#libprotobuf-mutator/build/external.protobuf
PROTOC = protoc
PROTOC_FLAGS = --cpp_out=$(PB_SRC_DIR) -I$(PROTO_DIR)

INC=-I$(LPM_DIR) -I$(PB_SRC_DIR) -I$(FACTORY_DIR) -I.
#INC=-I/usr/local/include -I$(PB_SRC_DIR) -I$(FACTORY_DIR) -I.
LIBS = -lprotobuf-mutator -lprotobuf #$(LPM_LIB) $(PROTOBUF_LIB) 
#-lprotobuf

all: proto gen_factory compile_factories $(TARGET).so

proto: $(PB_SRC)

gen_factory: $(FACTORY_SRC)

# $(TARGET).so: $(OBJ)
# 	$(CXX) -shared -o $@ $(OBJ) $(LIBS)

$(TARGET).so: $(OBJ)
	$(CXX) -shared -o $@ $^ $(shell find $(FACTORY_DIR) -name "factory_*.o") $(LIBS)

%.o: %.cc
	$(CXX) $(CXXFLAGS) -c -o $@ $< $(INC)

# compile .proto to .pb.cc and .pb.h
$(PB_SRC_DIR)/%.pb.cc $(PB_SRC_DIR)/%.pb.h: $(PROTO_DIR)/%.proto | $(PB_SRC_DIR)
	$(PROTOC) $(PROTOC_FLAGS) $<

# genfiles dir
$(PB_SRC_DIR):
	mkdir -p $(PB_SRC_DIR)

# factory dir
$(FACTORY_DIR):
	mkdir -p $(FACTORY_DIR)

compile_factories: factory
	$(MAKE) $(shell find $(FACTORY_DIR) -name "factory_*.cc" | sed 's/\.cc/\.o/')

# generate mutator factories
$(FACTORY_SRC): $(PROTO_SRC) | $(FACTORY_DIR)
	python3 generateMutators.py -i $(PROTO_DIR) -o $(FACTORY_DIR)

.PHONY: all clean proto factory post_process

clean:
	rm -f *.so *.o
	rm -f $(OBJ) $(PB_SRC) $(PB_SRC:.cc=.h)
	rm -rf $(PB_SRC_DIR)
	rm -rf $(FACTORY_DIR)
	rm -f jumbo_protos.cc
