#include <stdint.h>

#include "../workload.h"

const char* name = "fp_mul_ind";

void workload() {
    double count = 0.00, in = 1.00;

    asm volatile(
        "movsd %[val], %%xmm0\n\t" // Acumulador 0
        "movsd %[val], %%xmm1\n\t" // Acumulador 1
        "movsd %[val], %%xmm2\n\t" // Acumulador 2
        "movsd %[val], %%xmm3\n\t" // Acumulador 3
        "movsd %[val], %%xmm4\n\t" // Acumulador 4
        "movsd %[val], %%xmm5\n\t" // Acumulador 5
        "movsd %[val], %%xmm6\n\t" // Acumulador 6
        "movsd %[val], %%xmm7\n\t" // Acumulador 7
        
        "movsd %[val], %%xmm8\n\t" // Multiplicador fixo (sempre 1.0)
        :
        : [val] "m"(in)
        : "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7", "xmm8"
    );

    do {
        asm volatile(
            ".align 64\n\t" // Alinhamento
            
            ".rept 64\n\t" 
                "mulsd %%xmm8, %%xmm0\n\t" // %xmm0 = %xmm0 * 1.0
                "mulsd %%xmm8, %%xmm1\n\t"
                "mulsd %%xmm8, %%xmm2\n\t"
                "mulsd %%xmm8, %%xmm3\n\t"
                "mulsd %%xmm8, %%xmm4\n\t"
                "mulsd %%xmm8, %%xmm5\n\t"
                "mulsd %%xmm8, %%xmm6\n\t"
                "mulsd %%xmm8, %%xmm7\n\t"
            ".endr\n\t"
            :
            :
            : "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"
        );
    } while (alive);

    asm volatile(
        "movsd %%xmm0, %[out]\n\t"
        : [out] "=m"(count)
        :
        : "xmm0"
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
