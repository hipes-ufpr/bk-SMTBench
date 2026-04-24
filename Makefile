SRC_DIR := workloads
BIN_DIR := bin

CXX := g++
CXXFLAGS := -O1 -fomit-frame-pointer -Wall -std=c++20

SRCS := $(wildcard $(SRC_DIR)/*.cpp)
BINS := $(patsubst $(SRC_DIR)/%.cpp, $(BIN_DIR)/%.out, $(SRCS))

all: $(BINS)

$(BIN_DIR)/%.out: $(SRC_DIR)/%.cpp | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) -o $@ $<

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

clean:
	rm -rf $(BIN_DIR)

.PHONY: all clean
