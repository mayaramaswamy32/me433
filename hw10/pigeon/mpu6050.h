// mpu6050.h file using my imu code from last hw 5

#ifndef MPU6050_H
#define MPU6050_H

#include "hardware/i2c.h"
#include <stdint.h>

//i2c ports
#define I2C_PORT_IMU  i2c1
#define I2C_SDA_IMU   14
#define I2C_SCL_IMU   15

//imu address
#define MPU6050_ADDR  0x68

//registers from git
#define WHO_AM_I      0x75
#define CONFIG        0x1A
#define GYRO_CONFIG   0x1B
#define ACCEL_CONFIG  0x1C
#define PWR_MGMT_1    0x6B
#define PWR_MGMT_2    0x6C
#define ACCEL_XOUT_H  0x3B
#define ACCEL_XOUT_L  0x3C
#define ACCEL_YOUT_H  0x3D
#define ACCEL_YOUT_L  0x3E
#define ACCEL_ZOUT_H  0x3F
#define ACCEL_ZOUT_L  0x40
#define TEMP_OUT_H    0x41
#define TEMP_OUT_L    0x42
#define GYRO_XOUT_H   0x43
#define GYRO_XOUT_L   0x44
#define GYRO_YOUT_H   0x45
#define GYRO_YOUT_L   0x46
#define GYRO_ZOUT_H   0x47
#define GYRO_ZOUT_L   0x48

// Initialize I2C and wake up the MPU6050.
// Returns 1 on success (who_am_i passed), 0 on failure.
int  mpu6050_init(void);

// Write one byte to a register.
void mpu6050_write(uint8_t reg, uint8_t data);

// Read len bytes starting at reg into buf.
void mpu6050_read(uint8_t reg, uint8_t *buf, uint8_t len);

// Burst-read all 14 sensor bytes in one I2C transaction.
// Outputs raw int16 counts for accel (ax,ay,az), temp, gyro (gx,gy,gz).
void mpu6050_read_all(int16_t *ax, int16_t *ay, int16_t *az,
                       int16_t *temp,
                       int16_t *gx, int16_t *gy, int16_t *gz);

#endif