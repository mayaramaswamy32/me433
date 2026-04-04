#include <stdio.h> // set pico_enable_stdio_usb to 1 in CMakeLists.txt 
#include "pico/stdlib.h" // CMakeLists.txt must have pico_stdlib in target_link_libraries
#include "hardware/pwm.h" // CMakeLists.txt must have hardware_pwm in target_link_libraries
#include "hardware/adc.h" // CMakeLists.txt must have hardware_adc in target_link_libraries

#define PWMPIN 16

//* HELPER FUNC PROTOTYPES

void setServo(float angle);

bool timer_interrupt_function(__unused struct repeating_timer *t) {
    // read the adc
    uint16_t result1 = adc_read();
    // print the voltage
    // printf("%f\r\n",(float)result1/4095*3.3);
    return true;
}

int main()
{
    stdio_init_all();

    // turn on a timer interrupt
    struct repeating_timer timer;
    // -100 means call the function every 100ms
    // +100 would mean call the function 100ms after the function has ended
    add_repeating_timer_ms(-100, timer_interrupt_function, NULL, &timer);

    // turn on the pwm, in this example to 10kHz with a resolution of 1500
    gpio_set_function(PWMPIN, GPIO_FUNC_PWM); // Set the Pin to be PWM
    uint slice_num = pwm_gpio_to_slice_num(PWMPIN); // Get PWM slice number
    // the clock frequency is 150MHz divided by a float from 1 to 255
    float div = 50; // must be between 1-255
    pwm_set_clkdiv(slice_num, div); // sets the clock speed
    uint16_t wrap = 60000; // when to rollover, must be less than 65535
    pwm_set_wrap(slice_num, wrap); 
    pwm_set_enabled(slice_num, true); // turn on the PWM

    pwm_set_gpio_level(PWMPIN, 0); // set the duty cycle to 50%

    // turn on the adc
    adc_init();
    adc_gpio_init(26); // pin GP26 is pin ADC0
    adc_select_input(0); // sample from ADC0

    while (true) {
        // loop through the servo angkes
        int i = 0;
        for (i=10; i<170; i++){ // start at 10º and go to 170, counting up
            setServo(i);
            printf("Angle: %dº \n",i); // do nothing here, the interrupt does the work
            sleep_ms(15);
        }
        for (i=170; i>10; i--){  // start at 170, and go back to 10º, counting down
            setServo(i);
            printf("Angle: %dº \n",i); // do nothing here, the interrupt does the work
            sleep_ms(15);
        }
    }
}

void setServo(float angle){
    // controlling a duty cycle
    // 1. takes number from 0 to wrap number
    // 2. take the input angle and normalize it (divide by 180)
    // 3. turn it into a percent duty cycle; the min = 5%, max = 10% duty cycke
    // 3. Turn percent duty cycle into wrap number, so multiply by 60000
    pwm_set_gpio_level(PWMPIN, (int)((0.05 + (angle/180.0)*0.05)*60000));
}
