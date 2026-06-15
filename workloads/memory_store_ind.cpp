#include <stdint.h>
#include <cstdlib>

#include "../workload.h"

const char* name = "memory_store_ind";

// You can check L3 cache size in
// /sys/devices/system/cpu/cpu0/cache/index3/size

#define KB_SIZE 67108864

size_t length;
uint64_t *arr;

void workload() {
    uint64_t j = 0;
    do{
        for (j = 0; j <= length - 32; j += 32) {
            arr[j + 0] = 1;
            arr[j + 1] = 1;
            arr[j + 2] = 1;
            arr[j + 3] = 1;
            arr[j + 4] = 1;
            arr[j + 5] = 1;
            arr[j + 6] = 1;
            arr[j + 7] = 1;

            arr[j + 8] = 1;
            arr[j + 9] = 1;
            arr[j + 10] = 1;
            arr[j + 11] = 1;
            arr[j + 12] = 1;
            arr[j + 13] = 1;
            arr[j + 14] = 1;
            arr[j + 15] = 1;

            arr[j + 16] = 1;
            arr[j + 17] = 1;
            arr[j + 18] = 1;
            arr[j + 19] = 1;
            arr[j + 20] = 1;
            arr[j + 21] = 1;
            arr[j + 22] = 1;
            arr[j + 23] = 1;

            arr[j + 24] = 1;
            arr[j + 25] = 1;
            arr[j + 26] = 1;
            arr[j + 27] = 1;
            arr[j + 28] = 1;
            arr[j + 29] = 1;
            arr[j + 30] = 1;
            arr[j + 31] = 1;
        }
    } while (alive);

    volatile uint64_t *avoidOtimization = arr;
    (void)avoidOtimization;
}

int main(int argc, char* argv[]) {

    length = KB_SIZE / sizeof(uint64_t);
    arr = (uint64_t*) aligned_alloc(64, length * sizeof(uint64_t));

    for (size_t i = 0; i < length; i++)
        arr[i] = i;

    init(argc, argv);
    workload();
    fini(name);

    return 0;
}
