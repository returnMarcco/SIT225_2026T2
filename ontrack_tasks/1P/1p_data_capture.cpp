// Python will handle the timestamping of each reading to save a bunch
// of convoluted WIFI setup + NTP comms.
const int pirPin = 27;
int previousState = LOW;

void setup() {
  pinMode(pirPin, INPUT);
  Serial.begin(115200);
}

void loop() {
  int currentState = digitalRead(pirPin);

  // Once HIGH, pin can remain HIGH for several seconds, leading to duplicate readings. Only capture the first HIGH reading for each `LOW > HIGH` input change.
  if (currentState == HIGH && previousState == LOW) { 
    Serial.println(1);
  }

  previousState = currentState;

  // Poll the sensor every 100ms. This delay should be enough to limit iterations without missing input change. Might not work in a serious pest infestation.
  delay(500);
}