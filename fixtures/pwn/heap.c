#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
    char *value = malloc(16);
    if (!value) return 1;
    if (argc == 2) strcpy(value, argv[1]);
    puts(value);
    free(value);
    return 0;
}
