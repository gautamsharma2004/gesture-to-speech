#include <Wire.h>
#include <MPU6050.h>
#include <esp_wifi.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
//config=>
const char* SSID = "your SSID";
const char* Password = "your password";
const char* HOST_IP = "machine's IP address";
const int UDP_PORT =  5005;
const int SAMPLE_RATE_HZ = 100;
const int WINDOW_SIZE = 200;
const int BTN = 0;
const int LED = 2;

//globals=>
MPU6050 mpu(0x68);
WiFiUDP udp;

float  ax_buf[WINDOW_SIZE], ay_buf[WINDOW_SIZE], az_buf[WINDOW_SIZE];
float gx_buf[WINDOW_SIZE], gy_buf[WINDOW_SIZE], gz_buf[WINDOW_SIZE];

// setup==>

void setup(){
  Serial.begin(115200);
  Wire.begin(8,9); // 8=sda , 9=scl
  Wire.setClock(400000);

  mpu.initialize();
 // if (!mpu.testConnection()){
   // Serial.println("MPU6050 connection failed");
   // while(1);
  //}
  // calibration offsets=>
mpu.setXAccelOffset(4771);
mpu.setYAccelOffset(5782);
mpu.setZAccelOffset(8451);
mpu.setXGyroOffset(-10);
mpu.setYGyroOffset(31);
mpu.setZGyroOffset(-17);
//Set sensitivity
mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_4); //+-4g
mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_500); // +- 500degree/s
mpu.setDLPFMode(MPU6050_DLPF_BW_42); //LPF
//WiFi=>
WiFi.begin(SSID,Password);
while (WiFi.status() != WL_CONNECTED) {
  delay(500); Serial.print(".");

}
Serial.printf("\nConnected. IP: %s\n", WiFi.localIP().toString().c_str());
udp.begin(UDP_PORT);

pinMode(BTN,INPUT_PULLUP);
pinMode(LED,OUTPUT);
Serial.println("Ready,press button to capture gesture.");
  }

//Capture=>
void captureGesture(){
  int16_t ax,ay,az,gx,gy,gz;
  unsigned long interval_us = 1000000/ SAMPLE_RATE_HZ;
  for (int i = 0; i <WINDOW_SIZE; i++){
    unsigned long t = micros();
    mpu.getMotion6(&ax,&ay,&az,&gx,&gy,&gz);

    //converting to physical units=>
ax_buf[i] = ax/8192.0f; //+-4g range => divisor 8192
ay_buf[i] = ay/8192.0f;
az_buf[i] = az/8192.0f;
gx_buf[i] = gx/65.5f;
gy_buf[i] = gy/65.5f;
gz_buf[i] = gz/65.5f;// +-500 degree/s=> divisor 65.5
// To maintain precise 100Hz timing=>
while(micros() - t< interval_us);
  } 
}

//Send data=>
void sendData() {
  const int CHUNK_SIZE = 25;
  const int NUM_CHUNKS = WINDOW_SIZE / CHUNK_SIZE;  // 8 chunks

  for (int chunk = 0; chunk < NUM_CHUNKS; chunk++) {
    String payload = String(chunk) + "|";
    int start = chunk * CHUNK_SIZE;
    int end   = start + CHUNK_SIZE;

    for (int i = start; i < end; i++) {
      payload += String(ax_buf[i], 3) + "," +
                 String(ay_buf[i], 3) + "," +
                 String(az_buf[i], 3) + "," +
                 String(gx_buf[i], 3) + "," +
                 String(gy_buf[i], 3) + "," +
                 String(gz_buf[i], 3);
      if (i < end - 1) payload += ";";
    }

    udp.beginPacket(HOST_IP, UDP_PORT);
    udp.print(payload);
    udp.endPacket();
    delay(10);
  }
  Serial.println("All chunks sent.");
}

//LOOP=>
void loop(){
  if (digitalRead(BTN)==LOW){
    delay(50); // time for debounce
    if(digitalRead(BTN)==LOW){
      digitalWrite(LED, HIGH);
      Serial.println("Capturing..");
      captureGesture();
      digitalWrite(LED, LOW);
      sendData();
      Serial.println("Done.");
      delay(500);
    }
  }
}
