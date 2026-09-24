/* Educational x86-64 cache timing baseline. Accesses only this process's own buffer.
 * It is not a vulnerability checker or a cross-boundary attack. */
#if !defined(__x86_64__) && !defined(_M_X64)
#error "This example requires x86-64 with CLFLUSH and RDTSCP."
#endif

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <x86intrin.h>

enum { SAMPLES = 1001 };
static unsigned char buffer[4096] __attribute__((aligned(64)));

static int compare_u64(const void *a, const void *b) {
    uint64_t x = *(const uint64_t *)a;
    uint64_t y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}

static uint64_t timed_read(volatile unsigned char *p) {
    unsigned aux;
    _mm_lfence();
    uint64_t start = __rdtscp(&aux);
    (void)*p;
    _mm_lfence();
    uint64_t end = __rdtscp(&aux);
    return end - start;
}

int main(void) {
    uint64_t hit[SAMPLES], miss[SAMPLES];
    volatile unsigned char *p = &buffer[0];
    *p = 7;
    for (int i = 0; i < SAMPLES; ++i) {
        (void)*p;
        hit[i] = timed_read(p);
        _mm_clflush((const void *)p);
        _mm_mfence();
        miss[i] = timed_read(p);
    }
    qsort(hit, SAMPLES, sizeof hit[0], compare_u64);
    qsort(miss, SAMPLES, sizeof miss[0], compare_u64);
    printf("samples=%d, own buffer only\n", SAMPLES);
    printf("cached median=%llu cycles\n", (unsigned long long)hit[SAMPLES / 2]);
    printf("flushed median=%llu cycles\n", (unsigned long long)miss[SAMPLES / 2]);
    puts("These medians are observations, not a CPU vulnerability verdict.");
    return 0;
}
