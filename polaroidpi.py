#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function
from gpiozero import LED, Button
from picamera import PiCamera
from datetime import datetime
from subprocess import check_call
from signal import pause
from PIL import Image
from Adafruit_Thermal import *
import os

# Tanımlamalar
button = Button("GPIO2", hold_time=3)

ledR = LED("GPIO17")
ledG = LED("GPIO27")
ledB = LED("GPIO22")


printer = Adafruit_Thermal("/dev/serial0", 9600, timeout=5)


# Fonksiyonları burada belirleyelim!
def shutdownPi():
    # Raspberry Pi yi kapatır. Fişi çekmeyi unutmayın!
    print("Sistem kapanıyor...")
    check_call(['sudo', 'poweroff'])

def takePic(image_name):
    #Fotoğraf çeker ve yazıcıya gönderir.
    try:
        ledB.on() # mavi ledi yakalım
        with PiCamera() as camera:
            print("Fotoğraf çekimi başlıyor")
            camera.rotation = 90
            camera.capture('./images/%s' % image_name, resize=(384, 512))
            print("Fotoğraf çekimi bitti")
    except:
        ledB.off()
        print("Fotoğraf çekilemedi!")


def printPic(img):
    try:
        # Printer header
        ledR.blink()
        print("Yazdırma işlemi başlıyor...")
        header = Image.open("./src/printer_header.png")
        header = header.convert('1')
        printer.printImage(header, LaaT=True)
        printer.feed(1)
        printer.printImage(img, LaaT=True)
        printer.feed(1)
        simdi = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        printer.justify('c')
        printer.println(simdi)
        printer.feed(2)
        printer.setDefault()
        print("Yazdırma işlemi sona erdi")
        ledR.off()
    except:
        print("Printer yazmada sorun yaşadı!")
        ledR.off()




# Açık olan (tabi açıksa) ledi söndürelim
ledR.off()
ledG.off()
ledB.off()


def takeNPrint():
    # Fotoğraf çekelim ve yazdıralım
    if ledG.value == 1:
        ledG.off()
        stamp = datetime.now().strftime("%d%m%Y%H%M%S")
        image_name = "img_%s.png" % stamp
        takePic(image_name)

        if ledB.value == 1:
            # fotoğraf çekilmiş hadi devam edelim
            # önce ledi kapatalım
            ledB.off()

            # fotoğrafı yazıcıya gönderelim
            with Image.open("./images/%s" % image_name) as img:
                img = img.convert('1')
                img.save("./images/gray_image.png")
                printPic(img)

            print("Fotoğraf siliniyor")
            try:
                os.remove("./images/%s" % image_name)
                print("Fotoğraf silindi")
            except:
                print("Fotoğraf sişlinemedi. Senin canın sağolsun")

            ledG.on()




print("Sistem başladı...")
ledG.on()

# Buton davranışlarını belirleyelim!
button.when_held = shutdownPi
button.when_released = takeNPrint
# Programı burada durdur!
pause()