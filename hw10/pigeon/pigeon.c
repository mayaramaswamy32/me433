#include <stdio.h> // set pico_enable_stdio_usb to 1 in CMakeLists.txt 
#include "pico/stdlib.h" // CMakeLists.txt must have pico_stdlib in target_link_libraries
// my imu includes
#include "mpu6050.h"
#include "hardware/gpio.h"
#define PWMPIN 16


int main()
{
    stdio_init_all();
    // imu init
    mpu6050_init();

    while (true) {
        //read from imu
        int16_t ax, ay, az, temp, gx, gy, gz;
        int8_t deltax, deltay;
        mpu6050_read_all(&ax, &ay, &az, &temp, &gx, &gy, &gz);
        // ax and ay = raw counts, +/2 g = 16384 counts
        // map to 4 speed levels: 0,1,3,5
        // x axis corresponds to mouse x
        int ax_abs = ax < 0 ? -ax:ax; // ternaery operator! I used this for last hw too.
        int8_t speedx;
        if(ax_abs < 1000){
          speedx = 0;}
        else if(ax_abs < 4000){
          speedx = 1;}
        else if (ax_abs < 10000){
          speedx = 3;}
        else {
          speedx = 5;}
        deltax = ax > 0 ? speedx:-speedx; // again used the ternary operator

        // Y axis -> mouse Y
        int ay_abs = ay < 0 ? -ay : ay; // ternary operatir for y
        int8_t speedy;
        if (ay_abs < 1000){
          speedy = 0;}
        else if (ay_abs < 4000){
          speedy = 1;}
        else if (ay_abs < 10000){
          speedy = 3;}
        else{
          speedy = 5;}
        deltay = ay > 0 ? speedy: -speedy;
        // printf("ax:%6d  ay:%6d  az:%6d  | gx:%6d  gy:%6d  gz:%6d\n",
        // ax, ay, az, gx, gy, gz);
        printf("(%6d,%6d)\r\n",
        deltax, deltay);
        sleep_ms(1000/30);  
      }
    
}