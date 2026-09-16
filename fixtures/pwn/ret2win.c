#include <stdio.h>
#include <unistd.h>

void win(void) { puts("fixture win"); }
int main(void) {
    char buffer[32];
    return read(0, buffer, 128) < 0;
}
