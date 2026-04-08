#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

// I2C defines
// This example will use I2C0 on GPIO8 (SDA) and GPIO9 (SCL) running at 400KHz.
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define I2C_PORT i2c0
#define I2C_SDA 8
#define I2C_SCL 9
#define LED 15
#define CHIP_ADDRESS 0x20
#define IODIR 0x00
#define OLAT 0x0A
#define GPIO_REG 0x09

// function prototypes
void setPin(unsigned char reg, unsigned char value);
unsigned char readPin(unsigned char reg);
void heartbeat();


int main()
{
    stdio_init_all();
    while (!stdio_usb_connected()) {
    tight_loop_contents();
    }

    // I2C Initialisation. Using it at 400Khz.
    i2c_init(I2C_PORT, 400*1000);
    
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA);
    gpio_pull_up(I2C_SCL);
    // For more examples of I2C use see https://github.com/raspberrypi/pico-examples/tree/master/i2c


    // set gpio pin for led to test
    gpio_init(LED);
    gpio_set_dir(LED, 1);

    // onitial configutaton
    setPin(IODIR, 0b01111111); //set gp7 as output, gp0 as inpit

    while (true) {

        // heartbeat
        heartbeat();
        //! ============================test led blink
        // setPin(CHIP_ADDRESS, OLAT, 0b10000000); // turn on gp7

        // sleep_ms(500); // small delay bw on and off

        // setPin(CHIP_ADDRESS, OLAT, 0b00000000); // turn off gp7
        //! ============================end of test led blink


        // button logic
        uint8_t gpio_val = readPin(GPIO_REG);

        if (gpio_val & 0x01){
            // button NOT pressed
            setPin(OLAT, 0b00000000); // LED of
        }
        else {
            // button pressed
            setPin(OLAT, 0b10000000); // LED on GP7
        }
        sleep_ms(100); // delay for chip tpo be ok
    }
}

void setPin(unsigned char reg, unsigned char value){
    uint8_t buf[2];
    buf[0] = reg; // writes to this register
    buf[1] = value; // writes this value
    int result = i2c_write_blocking(I2C_PORT, CHIP_ADDRESS, buf, 2, false);
    // printf("I2C write result: %d\n", result);
}

unsigned char readPin(unsigned char reg){
    // read back IODIR to verify
    uint8_t val;
    int write_result = i2c_write_blocking(I2C_PORT, CHIP_ADDRESS, &reg, 1, true); //tells chip which register we want
    int read_result  = i2c_read_blocking(I2C_PORT, CHIP_ADDRESS, &val, 1, false); // we read the value from that register

    //printf("I2C write (set reg) result: %d\n", write_result);
    printf("I2C read result: %d, value: %d\n", read_result, val);

    return val;
}

void heartbeat(){
            gpio_put(LED, 1);
        sleep_ms(500);
        gpio_put(LED, 0);
        sleep_ms(500);
}