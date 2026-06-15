#include <stdint.h>

#include "../workload.h"

const char* name = "int_div_ind";

void workload() {
    uint64_t count = 0;

    asm volatile("mov $0x1, %%rbx" : : : "rbx");

    do {
        asm volatile(
            ".align 64\n\t"
            
            // Cria uma variável inicial
            ".set valor_rax, 12345\n\t"

            // Repete o bloco
            ".rept 32\n\t"
                "mov $valor_rax, %%rax\n\t"
                "mov $0, %%rdx\n\t"
                "idiv %%rbx\n\t"
                
                // Incrementa a variável para a próxima repetição
                ".set valor_rax, valor_rax + 1\n\t"
            ".endr\n\t"
            :
            :
            : "rax", "rdx", "rbx"
        );
    } while (alive);
    asm volatile("mov %%rbx, %0" : "=r"(count) : : ); 

    volatile int64_t avoidOtimization = count;
    (void)avoidOtimization;
}

int main(int argc, char* argv[]) {
    init(argc, argv);
    workload();
    fini(name);

    return 0;
}
