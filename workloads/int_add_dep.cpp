#include <stdint.h>

#include <cstdint>

#include "../workload.h"

const char* name = "int_add_dep";

void workload() {
    int64_t count = 0;

    asm volatile(
        "xor %%r12, %%r12\n\t"
        :
        :
        : "r12"
    );

    do {
        asm volatile(
            ".align 64\n\t"

            // Cadeia longa e totalmente dependente
            ".rept 64\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r12, %%r12\n\t"
            ".endr\n\t"
            :
            :
            : "r12"
        );
    } while (alive);

    asm volatile(
        "mov %%r12, %0\n\t"
        : "=r"(count)
        :
        : "r12"
    );

    volatile int64_t avoidOtimization = count;
    (void)avoidOtimization;
}

int main(int argc, char* argv[]) {
    init(argc, argv);
    workload();
    fini(name);

    return 0;
}
