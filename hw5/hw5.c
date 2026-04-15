#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "hardware/adc.h"
#include "ssd1306.h"
#include "font.h"

// I2C defines
// This example will use I2C0 on GPIO8 (SDA) and GPIO9 (SCL) running at 400KHz.
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define I2C_PORT_OLED i2c0
#define I2C_SDA_OLED 8
#define I2C_SCL_OLED 9
#define I2C_PORT_IMU i2c1
#define I2C_SDA_IMU 14
#define I2C_SCL_IMU 15
#define LED 18 

// mpu6050 address, and who am i reg
#define MPU6050_ADDR 0x68
#define WHO_AM_I 0x75 

// config registers
#define CONFIG 0x1A
#define GYRO_CONFIG 0x1B
#define ACCEL_CONFIG 0x1C
#define PWR_MGMT_1 0x6B
#define PWR_MGMT_2 0x6C

// sensor data registers:
#define ACCEL_XOUT_H 0x3B
#define ACCEL_XOUT_L 0x3C
#define ACCEL_YOUT_H 0x3D
#define ACCEL_YOUT_L 0x3E
#define ACCEL_ZOUT_H 0x3F
#define ACCEL_ZOUT_L 0x40
#define TEMP_OUT_H   0x41
#define TEMP_OUT_L   0x42
#define GYRO_XOUT_H  0x43
#define GYRO_XOUT_L  0x44
#define GYRO_YOUT_H  0x45
#define GYRO_YOUT_L  0x46
#define GYRO_ZOUT_H  0x47
#define GYRO_ZOUT_L  0x48
#define WHO_AM_I     0x75


// read from imu
void mpu6050_read(uint8_t reg, uint8_t *buf, uint8_t len);

// write to imu
void mpu6050_write(uint8_t reg, uint8_t data){
    uint8_t buf[2] = {reg, data};
    i2c_write_blocking(I2C_PORT_IMU, MPU6050_ADDR, buf, 2, false);
}

// initialize imu
void mpu6050_init(){
    mpu6050_write(PWR_MGMT_1, 0x00); // wakes up chip
    mpu6050_write(ACCEL_CONFIG, 0x00); // configures acceleration sensitivity to +/- 2g
    mpu6050_write(GYRO_CONFIG, 0x18); // configures gyro sensitivity to +/- 2000 dps
}

// burst read all 14 bytes of data
void mpu6050_read_all(int16_t *ax, int16_t *ay, int16_t *az, int16_t *temp, int16_t *gx, int16_t *gy, int16_t *gz);

// drawline function
void drawLine(int x0, int y0, int x1, int y1);
// from OLED hw
void drawChar(uint16_t x, uint16_t y, char letter);
void drawMessage(uint16_t x, uint16_t y, char*m);
void heartbeat();

int main()
{

    stdio_init_all();
    // while (!stdio_usb_connected()){
    //     tight_loop_contents();
    // }
    
    // oled init
    i2c_init(I2C_PORT_OLED, 1700*1000);
    
    gpio_set_function(I2C_SDA_OLED, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL_OLED, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA_OLED);
    gpio_pull_up(I2C_SCL_OLED);

    // imu init
    i2c_init(I2C_PORT_IMU, 400*1000);
    gpio_set_function(I2C_SDA_IMU, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL_IMU, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA_IMU);
    gpio_pull_up(I2C_SCL_IMU);

    //heartbeat
    gpio_init(LED);
    gpio_set_dir(LED, 1);

    // check who_am_i reg
    uint8_t who_am_i;
    mpu6050_read(WHO_AM_I, &who_am_i, 1);
    if (who_am_i!= 0x68&& who_am_i!= 0x98) {
        // if we dont get a good response, i'll blink my led forever
        while(1) {
            gpio_put(LED, 1); sleep_ms(200);
            gpio_put(LED, 0); sleep_ms(200);
        }
    }

    mpu6050_init(); // init imu after who_am_i passes

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
        // heartbeat();
        int16_t ax, ay, az, temp, gx, gy, gz; // store read imu values here
        mpu6050_read_all(&ax, &ay, &az, &temp, &gx, &gy, &gz);
        printf("ax:%6d ay:%6d az:%6d temp:%6d gx:%6d gy:%6d gz:%6d\n", ax, ay, az, temp, gx, gy, gz);

        //convert to float g units
        float fx = ax*0.000061f;
        float fy = ay*0.000061f;

        // the OLED center is (64,16) and its a 128x32 display
        // so to scale: 1g = a 20 pxl long line
        int cx = 64, cy = 16;
        int scale = 20;

        int ex = cx + (int)(fx * scale);
        int ey = cy + (int)(fy * scale);

        ssd1306_clear();
        drawLine(cx, cy, ex, ey); // these will draw my lines
        ssd1306_update();

        // absolute_time_t t1, t2;
        // t1 = get_absolute_time();
        // ssd1306_clear();
        // uint16_t raw = adc_read();
        // float voltage = raw * 3.3f/ 4095.0f; // compute voltage
        // char message[30];
        // sprintf(message, "Hello 1234567890123456789");
        // drawMessage(0, 0, message);
        // sprintf(message, "Row 2 1234567890123456789");
        // drawMessage(0, 8, message);
        // sprintf(message, "ADC0 = %.2f V", voltage);
        // drawMessage(0, 16, message);
        // ssd1306_update();
        // t2 = get_absolute_time();
        // uint64_t ta;
        // ta = to_us_since_boot(t2) - to_us_since_boot(t1);
        // char speed[30];
        // sprintf(speed, "FPS = %6.3f ", 1.0/(ta/1000000.0));
        // drawMessage(0,24,speed);
        // ssd1306_update();
        // sleep_ms(1000);
        gpio_put(LED, 1); // ill just turn it on to save time
    }
}

void mpu6050_read(uint8_t reg, uint8_t *buf, uint8_t len){
    i2c_write_blocking(I2C_PORT_IMU, MPU6050_ADDR, &reg, 1, true);
    i2c_read_blocking(I2C_PORT_IMU, MPU6050_ADDR, buf, len, false);
}

void mpu6050_read_all(int16_t *ax, int16_t *ay, int16_t *az, int16_t *temp, int16_t *gx, int16_t *gy, int16_t *gz){
    uint8_t buf[14];
    //! EXPLAIN
    mpu6050_read(ACCEL_XOUT_H, buf, 14);
    *ax = (int16_t)(buf[0]<< 8|buf[1]);
    *ay = (int16_t)(buf[2]<< 8|buf[3]);
    *az = (int16_t)(buf[4]<< 8|buf[5]);
    *temp = (int16_t)(buf[6]<<8| buf[7]);
    *gx = (int16_t)(buf[8]<< 8|buf[9]);
    *gy = (int16_t)(buf[10]<< 8|buf[11]);
    *gz = (int16_t)(buf[12]<< 8|buf[13]);
}


void drawLine(int x0, int y0, int x1, int y1) {
    //! the bresenham implementation
    int dx = abs(x1-x0), sx = x0<x1 ? 1 : -1; // looked up ?, this is the ternary operator, it means: if true -> 1, else, -> -1
    int dy = -abs(y1-y0), sy = y0<y1 ? 1 : -1;
    int err = dx+dy;
    while (1) {
        ssd1306_drawPixel(x0, y0, 1);
        if (x0==x1 && y0==y1) break;
        int e2 = 2*err;
        if (e2 >= dy) { err += dy; x0 += sx; }
        if (e2 <= dx) { err += dx; y0 += sy; }
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