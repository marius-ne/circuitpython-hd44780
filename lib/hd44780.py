import board
import busio
import time

class HD44780(object):
  ADDRESS = 0x27
  CLEARDISPLAY = 0x01
  RETURNHOME = 0x02
  ENTRYMODESET = 0x04
  DISPLAYCONTROL = 0x08
  FUNCTIONSET = 0x20
  ENTRYLEFT = 0x02
  DISPLAYON = 0x04
  F_4BITMODE = 0x00
  F_2LINE = 0x08
  F_5x8DOTS = 0x00
  EN = 0b00000100 # Enable bit
  RS = 0b00000001 # Register select bit
  LINE = [0x80,0xC0,0x94,0xD4]
  
  def __init__(self,i2c=None,address=ADDRESS,trans_map={}):
    if i2c is None:
      i2c = busio.I2C(board.SCL,board.SDA)
    self.i2c = i2c
    self.address = address
    self.trans_map = trans_map

    self._write(0x03)
    self._write(0x03)
    self._write(0x03)
    self._write(0x02)

    self._write(HD44780.FUNCTIONSET |
                HD44780.F_2LINE | HD44780.F_5x8DOTS | HD44780.F_4BITMODE)
    self._write(HD44780.DISPLAYCONTROL | HD44780.DISPLAYON)
    self._write(HD44780.CLEARDISPLAY)
    self._write(HD44780.ENTRYMODESET | HD44780.ENTRYLEFT)
    time.sleep(0.2)

  def write(self,string,line):
    self._write(HD44780.LINE[line-1])
    for char in string:
      if char in self.trans_map:
        self._write(self.trans_map[char],HD44780.RS)
      else:
        self._write(ord(char),HD44780.RS)

  def clear(self):
    self._write(HD44780.CLEARDISPLAY)
    self._write(HD44780.RETURNHOME)

  def _write(self, cmd, mode=0):
    self._write_four_bits(mode | (cmd & 0xF0))
    self._write_four_bits(mode | ((cmd << 4) & 0xF0))

  def _write_four_bits(self, data):
    self._write_to_i2c(data | HD44780.BACKLIGHT)
    self._strobe(data)

  def _strobe(self, data):
    self._write_to_i2c(data | HD44780.EN | HD44780.BACKLIGHT)
    time.sleep(.0005)
    self._write_to_i2c(((data & ~HD44780.EN) | HD44780.BACKLIGHT))
    time.sleep(.0001)

  def _write_to_i2c(self,data):
    self.i2c.writeto(self.address,bytes([data]))
    time.sleep(0.0001)