#include <stdio.h>
#include "pico/stdlib.h"

// add hardware spi
#include "hardware/spi.h"
// add include math
#include "math.h"


// pound defines
#define PIN_CS 5
#define SPI_PORT spi0


// function prototypes:
void writeDAC(int channel, float v);

static inline void cs_select(uint cs_pin) {
    asm volatile("nop \n nop \n nop"); // FIXME
    gpio_put(cs_pin, 0);
    asm volatile("nop \n nop \n nop"); // FIXME
}

static inline void cs_deselect(uint cs_pin) {
    asm volatile("nop \n nop \n nop"); // FIXME
    gpio_put(cs_pin, 1);
    asm volatile("nop \n nop \n nop"); // FIXME
}

int main()
{
    stdio_init_all();

    spi_init(spi_default, 1000 * 1000); // the baud, or bits per second
    gpio_set_function(PICO_DEFAULT_SPI_RX_PIN, GPIO_FUNC_SPI);
    gpio_set_function(PICO_DEFAULT_SPI_SCK_PIN, GPIO_FUNC_SPI);
    gpio_set_function(PICO_DEFAULT_SPI_TX_PIN, GPIO_FUNC_SPI);


    // initialize CS pin
    gpio_init(PIN_CS);
    gpio_set_dir(PIN_CS, GPIO_OUT);
    gpio_put(PIN_CS, 1);
    float t = 0;
    while (true) {
        t = t+0.001;
        float voltage = ((sin(2*M_PI*2*t) + 1) / 2.0) * 3.3;

        // t is in seconds, fmod will give me position within 1-second period
        float tri_pos = fmod(t, 1.0);  // 0.0 to 1.0
        float tri_voltage;
        if (tri_pos < 0.5)
            tri_voltage = tri_pos * 2.0 * 3.3; // ramp up
        else
            tri_voltage = (1.0 - tri_pos) * 2.0 * 3.3; // ramp down
        // call writeDAC for sine wave
        writeDAC(0, voltage); // channel 0
        // call writeDAC for triangle wave
        writeDAC(1, tri_voltage); // channel 1
        //if (t > 1000.0f) t = 0; // to cap the time?
        sleep_ms(1);
    }
}

void writeDAC(int channel, float v){
    uint8_t data[2];

    data[0] = 0b01110000;
    data[0] = data[0] | ((channel&0b1)<<7); // put the channel bit in
    uint16_t myV = (uint16_t)((v/3.3) * 1023); // 0b11111111
    data[0] = data[0] | ((myV>>6)&0b00001111);

    data[1] = (myV<<2) & 0xFF; // 0b11111100

    cs_select(PIN_CS);
    spi_write_blocking(SPI_PORT, data, 2); // where data is a uint8_t array with length len
    cs_deselect(PIN_CS);
}

