#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "hardware/adc.h"
#include "ssd1306.h"
#include "font.h"

// I2C defines
// This example will use I2C0 on GPIO8 (SDA) and GPIO9 (SCL) running at 400KHz.
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define I2C_PORT i2c0
#define I2C_SDA 8
#define I2C_SCL 9
#define LED 15

void drawChar(uint16_t x, uint16_t y, char letter);
void drawMessage(uint16_t x, uint16_t y, char*m);
void heartbeat();

int main()
{
    stdio_init_all();

    // I2C Initialisation. Using it at 400Khz.
    i2c_init(I2C_PORT, 1700*1000);
    
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA);
    gpio_pull_up(I2C_SCL);

    //heartbeat
    gpio_init(LED);
    gpio_set_dir(LED, 1);

    // initialize adc
    adc_init();
    adc_gpio_init(26);
    adc_select_input(0);


    ssd1306_setup();
    ssd1306_clear();
    ssd1306_update();


    // For more examples of I2C use see https://github.com/raspberrypi/pico-examples/tree/master/i2c

    while (true) {
        //! speck test: turns on/off one spec

        /*
        ssd1306_drawPixel(10, 20, 1);
        ssd1306_update();
        sleep_ms(1000);
        ssd1306_drawPixel(10, 20, 0);
        ssd1306_update();
        sleep_ms(1000);
        */
       heartbeat();
        absolute_time_t t1, t2;
        t1 = get_absolute_time();
        ssd1306_clear();
        uint16_t raw = adc_read();
        float voltage = raw * 3.3f/ 4095.0f; // compute voltage
        char message[30];
        sprintf(message, "Hello 1234567890123456789");
        drawMessage(0, 0, message);
        sprintf(message, "Row 2 1234567890123456789");
        drawMessage(0, 8, message);
        sprintf(message, "ADC0 = %.2f V", voltage);
        drawMessage(0, 16, message);
        ssd1306_update();
        t2 = get_absolute_time();
        uint64_t ta;
        ta = to_us_since_boot(t2) - to_us_since_boot(t1);
        char speed[30];
        sprintf(speed, "FPS = %6.3f ", 1.0/(ta/1000000.0));
        drawMessage(0,24,speed);
        ssd1306_update();
        sleep_ms(1000);
    }
}
void drawChar(uint16_t x, uint16_t y, char letter){
    int i;
    for(i=0;i<5;i++){
        unsigned char colm = ASCII[letter-0x20][i];
        int j;
        for (j=0;j<8;j++){
            uint8_t bit = (colm >> j) & 0x1;
            ssd1306_drawPixel(x+i,y+j,bit);
        }
    }

}
void drawMessage(uint16_t x, uint16_t y, char*m){
    int k=0;
    while(m[k]!='\0'){ 
    drawChar(x+k*6,y,m[k]);
    k++;
    }
}

void heartbeat(){
    gpio_put(LED, 1);
    sleep_ms(500);
    gpio_put(LED, 0);
    sleep_ms(500);
}