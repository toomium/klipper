#include <string.h>
#include <stdint.h>


#include <stdio.h>
#include "command.h" 
#include "sched.h"

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // Hex dump
    fprintf(stderr, "[HARNESS] got %zu bytes\n", size);
    

    fprintf(stderr, "[HARNESS] data: ");
    for (size_t i = 0; i < size && i < 32; i++) {
        fprintf(stderr, "%02x ", data[i]);
    }
    fprintf(stderr, "\n");
    fflush(stderr);

    uint8_t fuzz_buf[256];
    
    if (size > 256) {
        size = 256;
    }

    memcpy(fuzz_buf, data, size);


    int ret = set_fuzzing_jmp();
    //command_dispatch(fuzz_buf, (uint_fast8_t)size);
    if (!ret) {
        // Starte die Klipper-Logik
        command_dispatch(fuzz_buf, (uint_fast8_t)size);
    }

    return 0;
}