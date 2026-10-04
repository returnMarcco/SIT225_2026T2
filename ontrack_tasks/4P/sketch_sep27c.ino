#include "esp_camera.h"

// --------------------------------------------------
// PIR
// --------------------------------------------------

#define PIR_PIN 14

int previousPirState = LOW;


// --------------------------------------------------
// Freenove ESP32-S3 WROOM camera pins
// --------------------------------------------------

#define PWDN_GPIO_NUM   -1
#define RESET_GPIO_NUM  -1

#define XCLK_GPIO_NUM   15
#define SIOD_GPIO_NUM   4
#define SIOC_GPIO_NUM   5

#define Y9_GPIO_NUM     16
#define Y8_GPIO_NUM     17
#define Y7_GPIO_NUM     18
#define Y6_GPIO_NUM     12
#define Y5_GPIO_NUM     10
#define Y4_GPIO_NUM     8
#define Y3_GPIO_NUM     9
#define Y2_GPIO_NUM     11

#define VSYNC_GPIO_NUM  6
#define HREF_GPIO_NUM   7
#define PCLK_GPIO_NUM   13


// --------------------------------------------------
// Initialise camera
// --------------------------------------------------

bool initialiseCamera() {

  camera_config_t config;

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;

  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;

  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;

  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;

  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 10000000;

  // We want JPEG because it is already compressed.
  config.pixel_format = PIXFORMAT_JPEG;

  // QVGA = 320 x 240.
  // Good starting size for storing as Base64.
  config.frame_size = FRAMESIZE_QVGA;

  // Lower number = higher quality / larger file
  config.jpeg_quality = 12;

  config.fb_count = 1;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;

  if (psramFound()) {
    config.fb_location = CAMERA_FB_IN_PSRAM;
  } else {
    config.fb_location = CAMERA_FB_IN_DRAM;
  }

  esp_err_t result = esp_camera_init(&config);

  if (result != ESP_OK) {
    Serial.print("CAMERA_ERROR:");
    Serial.println(result);
    return false;
  }

  return true;
}


// --------------------------------------------------
// Capture + send image
// --------------------------------------------------

void captureAndSendImage() {

  camera_fb_t *frameBuffer = esp_camera_fb_get();

  if (!frameBuffer) {
    Serial.println("CAPTURE_ERROR");
    return;
  }

  /*
     Header tells Python:

     1 = movement detected
     frameBuffer->len = exact number of JPEG bytes

     Example:

     EVENT:1:17248
  */

  Serial.print("EVENT:1:");
  Serial.println(frameBuffer->len);

  // Send the raw JPEG bytes
  Serial.write(frameBuffer->buf, frameBuffer->len);

  // Make sure everything is sent
  Serial.flush();

  // Release the camera buffer
  esp_camera_fb_return(frameBuffer);
}


// --------------------------------------------------
// Setup
// --------------------------------------------------

void setup() {

  Serial.begin(115200);

  pinMode(PIR_PIN, INPUT);

  delay(1500);

  if (!initialiseCamera()) {
    Serial.println("Camera failed to initialise.");

    while (true) {
      delay(1000);
    }
  }

  Serial.println("READY");
}


// --------------------------------------------------
// Loop
// --------------------------------------------------

void loop() {

  int currentPirState = digitalRead(PIR_PIN);

  // Only capture the LOW -> HIGH transition
  if (
    currentPirState == HIGH &&
    previousPirState == LOW
  ) {

    captureAndSendImage();
  }

  previousPirState = currentPirState;

  delay(50);
}