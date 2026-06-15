#include <stdint.h>
#include <cstdlib>

#include "../workload.h"

const char* name = "memory_load_ind";

// You can check L3 cache size in
// /sys/devices/system/cpu/cpu0/cache/index3/size

#define KB_SIZE 67108864

size_t length;
uint64_t *vec;

void workload() {
    uint64_t j = 0;

    uint64_t c0 = 0, c1 = 0, c2 = 0, c3 = 0;
    uint64_t c4 = 0, c5 = 0, c6 = 0, c7 = 0;

    do {
        for (j = 0; j <= length - 32; j += 32) {
            c0 += vec[j + 0];
            c1 += vec[j + 1];
            c2 += vec[j + 2];
            c3 += vec[j + 3];
            c4 += vec[j + 4];
            c5 += vec[j + 5];
            c6 += vec[j + 6];
            c7 += vec[j + 7];

            c0 += vec[j + 8];
            c1 += vec[j + 9];
            c2 += vec[j + 10];
            c3 += vec[j + 11];
            c4 += vec[j + 12];
            c5 += vec[j + 13];
            c6 += vec[j + 14];
            c7 += vec[j + 15];

            c0 += vec[j + 16];
            c1 += vec[j + 17];
            c2 += vec[j + 18];
            c3 += vec[j + 19];
            c4 += vec[j + 20];
            c5 += vec[j + 21];
            c6 += vec[j + 22];
            c7 += vec[j + 23];

            c0 += vec[j + 24];
            c1 += vec[j + 25];
            c2 += vec[j + 26];
            c3 += vec[j + 27];
            c4 += vec[j + 28];
            c5 += vec[j + 29];
            c6 += vec[j + 30];
            c7 += vec[j + 31];
        }

    } while (alive);

    volatile int64_t avoidOtimization = c0 + c1 + c2 + c3 + c4 + c5 + c6 + c7;
    (void)avoidOtimization;
}

int main(int argc, char* argv[]) {
    length = KB_SIZE / sizeof(uint64_t);
    vec = (uint64_t *) aligned_alloc(64, length * sizeof(uint64_t));

    for (size_t i = 0; i < length; i++)
        vec[i] = i;
    init(argc, argv);
    workload();
    fini(name);

    return 0;
}
