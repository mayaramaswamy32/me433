#include <stdio.h>
#include "pico/stdlib.h"

// add hardware spi
#include "hardware/spi.h"
// add include math
#include "math.h"


// pound defines
#define SPI_PORT spi0
#define PIN_MISO 16
#define PIN_CS_DAC 5
#define PIN_CS_RAM 20 // choose a different pin for this
#define PIN_SCK 18
#define PIN_MOSI 19


// function prototypes:
void update_dac_from_ram(int);
void spi_ram_init();
void spi_ram_write(uint16_t, uint8_t*, int);
void spi_ram_read(uint16_t, uint8_t*, int);
void ram_write_sine();


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
    // initialize CS pin
    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_CS_DAC, GPIO_FUNC_SIO);
    gpio_set_function(PIN_CS_RAM, GPIO_FUNC_SIO);
    gpio_set_function(PIN_SCK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);

    // set directorn
    gpio_set_dir(PIN_CS_DAC, GPIO_OUT);
    gpio_put(PIN_CS_DAC, 1);

    gpio_set_dir(PIN_CS_RAM, GPIO_OUT);
    gpio_put(PIN_CS_RAM, 1);

    // init ram chip
    spi_ram_init();
    ram_write_sine();

    int i=0;
    while (true) {
        update_dac_from_ram((uint16_t)(i*2));
        i = (i+1)% 1024;
        sleep_ms(1);
        // for (i=0; i<1024*2;i+=2){
        //     update_dac_from_ram(i);
        //     sleep_ms(1);
        // }
    }
}

void spi_ram_init(){
    uint8_t data[2];
    int len = 2;
    data[0] = 0b00000001;
    data[1] = 0b01000000; // sequential mode
    cs_select(PIN_CS_RAM);
    spi_write_blocking(SPI_PORT, data, len);
    cs_deselect(PIN_CS_RAM);
}

void update_dac_from_ram(int i){
    uint8_t data[2];
    spi_ram_read(i, data, 2);

    cs_select(PIN_CS_DAC);
    spi_write_blocking(SPI_PORT, data, 2);
    cs_deselect(PIN_CS_DAC);
}

void ram_write_sine(){
    int i;
    for (i=0; i<1024; i++){
        float voltage = (sinf(2.0f*M_PI*i/1024.0)+1.0)/2.0f*3.3f;// what is that for?
        uint16_t v = (uint16_t)(voltage/3.3f *1023);

        uint8_t buf[2];
        buf[0] = 0b01110000 | (v>>6);
        buf[1] = (v << 2) & 0xFF;

        spi_ram_write((uint16_t)(i*2), buf, 2);

    }
}

void spi_ram_write(uint16_t addr, uint8_t * data, int len){
    uint8_t packet[5];
    packet[0] = 0b00000010; // instruction, write
    packet[1] = addr>>8; // addr
    packet[2] = addr&0xFF;
    packet[3] = data[0];
    packet[4] = data[1];

    cs_select(PIN_CS_RAM);
    spi_write_blocking(SPI_PORT, packet, 5); // where data is a uint8_t array
    cs_deselect(PIN_CS_RAM);

}

void spi_ram_read(uint16_t addr, uint8_t *data, int len){
    uint8_t packet[5];
    packet[0] = 0b00000011; // instructions, read
    packet[1] = addr>>8;
    packet[2] = addr&0xFF; // addr
    packet[3] = 0;
    packet[4] = 0;
    uint8_t dst[5];
    cs_select(PIN_CS_RAM);
    spi_write_read_blocking(SPI_PORT, packet, dst, 5);
    cs_deselect(PIN_CS_RAM);
    data[0] = dst[3];
    data[1] = dst[4];

}
