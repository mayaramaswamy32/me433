#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"

#define UART_ID uart0
#define BAUD_RATE 115200
#define UART_TX_PIN 0  // GP0
#define UART_RX_PIN 1  // GP1

int main() {
    stdio_init_all();  // sets up USB

    // Set up UART0 for STM32 communication
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);

    while (true) {
        // Read from STM32, send to computer
        if (uart_is_readable(UART_ID)) {
            char c = uart_getc(UART_ID);
            putchar(c);
            stdio_flush();
        }

        // Read from computer, send to STM32
        int c = getchar_timeout_us(0);
        if (c != PICO_ERROR_TIMEOUT) {
            uart_putc(UART_ID, (char)c);
        }
    }
}