#include <stdio.h>
#include <string.h>

static unsigned char expected[] = {0x26, 0x27, 0x2e, 0x36, 0x23};

int main(int argc, char **argv) {
    if (argc != 2 || strlen(argv[1]) != sizeof(expected)) return 1;
    for (size_t i = 0; i < sizeof(expected); i++) {
        if (((unsigned char)argv[1][i] ^ 0x42) != expected[i]) return 1;
    }
    puts("fixture accepted");
    return 0;
}
