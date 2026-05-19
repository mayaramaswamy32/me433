#include <stdio.h>
#include "pico/stdlib.h"



#define clock_time_us 50
#define PIN_DOUT 14
#define PIN_PD_SCK 15

void init_hx711(){
    gpio_init(PIN_DOUT);
    gpio_set_dir(PIN_DOUT, GPIO_IN);
    gpio_pull_up(PIN_DOUT);
    
    gpio_init(PIN_PD_SCK);
    gpio_set_dir(PIN_PD_SCK, GPIO_OUT);
    gpio_put(PIN_PD_SCK, 0);
}

int hx711_read_raw(void){
    while (gpio_get(PIN_DOUT)){
        tight_loop_contents();

    }

    unsigned int raw = 0;
    for (int i =0; i < 24; ++i){
        gpio_put(PIN_PD_SCK, 1);
        sleep_us(clock_time_us);
        raw = (raw << 1) | (gpio_get(PIN_DOUT) ? 1 : 0);
        gpio_put(PIN_PD_SCK, 0);
        sleep_us(clock_time_us);
    }

    // 25th pulse to set gain = 128 for next reading
    gpio_put(PIN_PD_SCK, 1);
    sleep_us(clock_time_us);
    gpio_put(PIN_PD_SCK,0);
    sleep_us(clock_time_us);

    // sign-extend 24-bit two's complement to 32-bit signed int

    if (raw & 0x800000){
        raw |= 0xFF000000;
    }
    return (int)raw;



}
int main()
{
    stdio_init_all();

    init_hx711();

    int i = 0;
    uint64_t last_t = 0;

    while (true) {
        char m[100];
        int v[1000];
        int raw_v[1000]; // plots raw vals
        int num = 0;
        uint64_t t[1000];
        scanf("%d", &num);
        float avg = 828000;
        for (i=0; i<num; i++){
            int val = hx711_read_raw();
            avg = val*0.1f+avg*0.9f;
            raw_v[i] = val; // raw val
            v[i] = (int)avg; // filtered val
            t[i] = to_ms_since_boot(get_absolute_time());
        }
        for (i=0; i<num; i++){
            printf("%llu %d %d\n", t[i], raw_v[i], v[i]); // time, raw, filtered
        }
    }
}
