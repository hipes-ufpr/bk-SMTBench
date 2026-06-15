#include <stdint.h>

#include "../workload.h"

const char* name = "int_div_dep";

void workload() {
  uint64_t count = 0;

    asm volatile("mov $0x0, %%rax" : : : "rax");
    asm volatile("mov $0x0, %%rdx" : : : "rdx");
    asm volatile("mov $0x1, %%rbx" : : : "rbx");

    do {
      asm volatile(
        ".align 64\n\t"

        ".rept 64\n\t"
        "idiv %%rbx\n\t"
        "idiv %%rbx\n\t"
        "idiv %%rbx\n\t"
        "idiv %%rbx\n\t"
        "idiv %%rbx\n\t"
        "idiv %%rbx\n\t"
        "idiv %%rbx\n\t"
        ".endr\n\t"
        :
        :
        : "rax", "rdx", "rbx"
      );
    } while (alive);
    asm volatile("mov %%rbx, %0" : "=r"(count) : : "rbx");

    volatile int64_t avoidOtimization = count;
    (void)avoidOtimization;
}

int main(int argc, char* argv[]) {
    init(argc, argv);
    workload();
    fini(name);

    return 0;
}
