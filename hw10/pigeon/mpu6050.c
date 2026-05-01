#include "mpu6050.h"
#include "pico/stdlib.h"

void mpu6050_write(uint8_t reg, uint8_t data) {
    uint8_t buf[2] = {reg, data};
    i2c_write_blocking(I2C_PORT_IMU, MPU6050_ADDR, buf, 2, false);
}

void mpu6050_read(uint8_t reg, uint8_t *buf, uint8_t len) {
    i2c_write_blocking(I2C_PORT_IMU, MPU6050_ADDR, &reg, 1, true);
    i2c_read_blocking(I2C_PORT_IMU, MPU6050_ADDR, buf, len, false);
}

int mpu6050_init(void) {
    // sets up i2c bus for imu
    i2c_init(I2C_PORT_IMU, 400 * 1000);
    gpio_set_function(I2C_SDA_IMU, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL_IMU, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA_IMU);
    gpio_pull_up(I2C_SCL_IMU);

    // my who_am_i test to make sure communication's okay
    uint8_t who;
    mpu6050_read(WHO_AM_I, &who, 1);
    if (who != 0x68 && who != 0x98) {
        return 0; // failed
    }

    // wakes up chip and sets up acceleration and gyro
    mpu6050_write(PWR_MGMT_1,  0x00);
    mpu6050_write(ACCEL_CONFIG, 0x00);
    mpu6050_write(GYRO_CONFIG,  0x18);
    return 1; // success
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