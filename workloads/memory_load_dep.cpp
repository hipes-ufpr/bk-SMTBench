#include <stdint.h>
#include <cstdlib>

#include "../workload.h"

const char* name = "memory_load_dep";

// You can check L3 cache size in
// /sys/devices/system/cpu/cpu0/cache/index3/size

#define KB_SIZE 67108864

typedef struct list_s {
    struct list_s *next;
    uint64_t v;
} list_t;

size_t length;
list_t *base;

void workload() {

    uint64_t j = 0;
    uint64_t value = 0;
    list_t *ptr_this;

    do {
        ptr_this = base;
        for (j = 0; j <= length - 32; j += 32) {
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;

            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;

            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;

            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;
            ptr_this = ptr_this->next;

            value = ptr_this->v;
        }
    } while (alive);

    volatile int64_t avoidOtimization = value;
    (void)avoidOtimization;
}

int main(int argc, char* argv[]) {

    length = KB_SIZE / sizeof(list_t);
    base = (list_t*) aligned_alloc(64, length * sizeof(list_t));

    for (size_t i = 0; i < length - 1; i++) {
        base[i].next = &base[i + 1];
        base[i].v = i;
    }
    base[length - 1].next = &base[0];
    base[length - 1].v = length - 1;

    init(argc, argv);
    workload();
    fini(name);

    return 0;
}
