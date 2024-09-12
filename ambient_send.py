# SoratobuMacaroniPenguin
# for Micropython-1.23.0 later
# upload iot server https://ambient.
# used library
#     ambient github
#     max31865 bithub

import password_file
import time
import machine
from machine import Pin , SoftSPI
import max31865 as adafruit_max31865 
MISO = 14
MOSI = 5
SCK = 4
CS = 0

import ambient
import urequests as requests
CHANNEL_ID = password_file.CHANNEL_ID
WRITE_KEY = password_file.WRITE_KEY

import urequests

import network
SSID = password_file.SSID
KEY = password_file.KEY

spi = SoftSPI(baudrate=200000, polarity=1, phase=0, sck=Pin(SCK), mosi=Pin(MOSI), miso=Pin(MISO))
cs = CS
sensor = adafruit_max31865.Max31865(spi, cs , rtd_nominal=100, ref_resistor=430.0, wires=3,misoPin=MISO,mosiPin=MOSI,sckPin=SCK)

max_board_switch = Pin(12 , Pin.OUT)
sta_if = network.WLAN(network.STA_IF)
    

def do_connect():
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect( SSID , KEY )
        while not sta_if.isconnected():
            time.sleep(1)
    print('network config:', sta_if.ifconfig())

def max31865_measurement():
    temp = sensor.temperature
    print("Temperature: {0:0.3f}C".format(temp))
    return temp


def main():
    do_connect()
    am = ambient.Ambient( CHANNEL_ID , WRITE_KEY)
    # デバイスを起こすための RTC.ALARM0 を設定
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

    # ディープスリープから起こされたかをチェック
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        print('woke from a deep sleep')

    # 10秒後に RTC.ALARM0 を発火して、デバイスを起こすよう設定
    rtc.alarm(rtc.ALARM0, 53000)

    #while True:
    max_board_switch.value(1) #max boead on
    time.sleep(1)
    temp =max31865_measurement()
    try:
        r = am.send({'d1': "{:.1f}".format(temp)})
        print(r.status_code)
    except requests.exceptions.RequestException as e:
        print('request failed: ', e)
    #sleep準備
    max_board_switch.value(0) #max board off
    sta_if.active(False) #wifi off
    time.sleep(5)
    # ディープスリープに入る
    print("go sleep")
    machine.deepsleep()
#        time.sleep(30)


if __name__ == "__main__":
    main()
