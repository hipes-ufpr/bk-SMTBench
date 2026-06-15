#include <stdint.h>

#include <cstdint>

#include "../workload.h"

const char* name = "int_add_ind";

void workload() {
    int64_t count = 0;
    
    asm volatile(
        "xor %%r12, %%r12\n\t"
        "xor %%r13, %%r13\n\t"
        "xor %%r14, %%r14\n\t"
        "xor %%r15, %%r15\n\t"
        "xor %%rbx, %%rbx\n\t"
        "xor %%rbp, %%rbp\n\t"
        "xor %%r8, %%r8\n\t"
        "xor %%r9, %%r9\n\t"
        :
        :
        : "r12", "r13", "r14", "r15", "rbx", "rbp", "r8", "r9"
    );

    do {
        asm volatile(
            ".align 64\n\t"

            ".rept 64\n\t"
            "add %%r12, %%r12\n\t"
            "add %%r13, %%r13\n\t"
            "add %%r14, %%r14\n\t"
            "add %%r15, %%r15\n\t"
            "add %%rbx, %%rbx\n\t"
            "add %%rbp, %%rbp\n\t"
            "add %%r8, %%r8\n\t"
            "add %%r9, %%r9\n\t"
            ".endr\n\t"
            :
            :
            : "r12", "r13", "r14", "r15", "rbx", "rbp", "r8", "r9"
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
