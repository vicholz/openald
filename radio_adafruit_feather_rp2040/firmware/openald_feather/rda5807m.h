// Minimal RDA5807M driver for OpenALD Feather RP2040 v1.0 (no external library).
// Register map from the RDA5807M datasheet (rev 1.1/1.8). Random-access I2C address 0x11:
// write [reg] [hi] [lo]; read = write [reg], then 2 bytes. Not hardware-tested.
#pragma once
#include <Arduino.h>
#include <Wire.h>

namespace rda {

const uint8_t ADDR_RANDOM = 0x11;

// REG 0x02
const uint16_t R02_DHIZ = 1u << 15, R02_DMUTE = 1u << 14, R02_MONO = 1u << 13, R02_BASS = 1u << 12,
               R02_SEEKUP = 1u << 9, R02_SEEK = 1u << 8, R02_SKMODE = 1u << 7, R02_NEW_METHOD = 1u << 2,
               R02_SOFT_RESET = 1u << 1, R02_ENABLE = 1u << 0;
// REG 0x03
const uint16_t R03_TUNE = 1u << 4;     // band 00 = 87-108 MHz, space 00 = 100 kHz
// REG 0x04
const uint16_t R04_DE_50US = 1u << 11, R04_SOFTMUTE_EN = 1u << 9;
// REG 0x05: INT_MODE=1, SEEKTH=8, LNA_PORT_SEL=10 (LNAP), volume in bits 3:0
const uint16_t R05_BASE = 0x8880;
// REG 0x0A
const uint16_t R0A_STC = 1u << 14, R0A_SF = 1u << 13, R0A_ST = 1u << 10;

const uint16_t BAND_LO_10K = 8700, BAND_HI_10K = 10800;   // 87.00 - 108.00 MHz, in 10 kHz units

class Radio {
 public:
  bool begin(bool deemph50us) {
    de50_ = deemph50us;
    Wire.beginTransmission(ADDR_RANDOM);
    if (Wire.endTransmission() != 0) return false;             // no ACK: module missing, unpowered or no pull-ups
    write(0x02, R02_DHIZ | R02_SOFT_RESET | R02_ENABLE);
    delay(20);
    r02_ = R02_DHIZ | R02_DMUTE | R02_NEW_METHOD | R02_ENABLE;
    write(0x02, r02_);
    write(0x04, R04_SOFTMUTE_EN | (de50_ ? R04_DE_50US : 0));
    delay(600);                                                  // crystal / PLL settle after enable (datasheet: ~0.5 s)
    return true;
  }
  void setVolume(uint8_t v) {                                    // 0 = muted, 1..15
    if (v > 15) v = 15;
    write(0x05, R05_BASE | v);
    uint16_t want = v ? (r02_ | R02_DMUTE) : (r02_ & ~R02_DMUTE);
    if (want != r02_) { if (seeking_) stopSeek(); r02_ = (want & ~(R02_SEEK | R02_SEEKUP)); write(0x02, r02_); }
  }
  void tune(uint16_t f10k) {                                     // frequency in 10 kHz units, e.g. 9910 = 99.1 MHz
    f10k = constrain(f10k, BAND_LO_10K, BAND_HI_10K);
    stopSeek();
    uint16_t chan = (f10k - BAND_LO_10K) / 10;                   // 100 kHz spacing
    write(0x03, (chan << 6) | R03_TUNE);
  }
  void startSeek(bool up) {
    r02_ |= R02_SEEK | (up ? R02_SEEKUP : 0);
    if (!up) r02_ &= ~R02_SEEKUP;
    r02_ &= ~R02_SKMODE;                                         // wrap at the band edge
    write(0x02, r02_);
    seeking_ = true;
  }
  // Poll while seeking. Returns true once the seek has finished (or was never running).
  bool seekDone() {
    if (!seeking_) return true;
    if (!(read(0x0A) & R0A_STC)) return false;
    stopSeek();
    return true;
  }
  void stopSeek() {
    if (!seeking_ && !(r02_ & R02_SEEK)) return;
    r02_ &= ~(R02_SEEK | R02_SEEKUP);
    write(0x02, r02_);
    seeking_ = false;
  }
  bool seeking() const { return seeking_; }
  uint16_t frequency() {                                         // current channel (also valid after a seek)
    uint16_t chan = read(0x0A) & 0x03FF;
    return BAND_LO_10K + chan * 10;
  }
  uint8_t rssi() { return read(0x0B) >> 9; }
  bool stereo() { return read(0x0A) & R0A_ST; }
  void powerDown() {                                             // ENABLE = 0: ~5 uA, audio off
    seeking_ = false;
    r02_ &= ~(R02_ENABLE | R02_SEEK | R02_SEEKUP | R02_DMUTE);
    write(0x02, r02_);
  }

  void write(uint8_t reg, uint16_t v) {
    Wire.beginTransmission(ADDR_RANDOM);
    Wire.write(reg); Wire.write(v >> 8); Wire.write(v & 0xFF);
    Wire.endTransmission();
  }
  uint16_t read(uint8_t reg) {
    Wire.beginTransmission(ADDR_RANDOM);
    Wire.write(reg);
    Wire.endTransmission(false);
    if (Wire.requestFrom(ADDR_RANDOM, (uint8_t)2) != 2) return 0;
    uint16_t hi = Wire.read(), lo = Wire.read();
    return (hi << 8) | lo;
  }

 private:
  uint16_t r02_ = 0;
  bool seeking_ = false, de50_ = false;
};

}  // namespace rda
