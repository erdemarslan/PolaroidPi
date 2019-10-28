#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function
import gpiozero
from picamera import PiCamera
from datetime import datetime
from signal import pause
from PIL import Image
from Adafruit_Thermal import *
import os

# Tanımlamalar
button = gpiozero.Button("GPIO17")
led = gpiozero.LED("GPIO2")

printer = Adafruit_Thermal("/dev/serial0", 9600, timeout=5)

# Açık olan (tabi açıksa) ledi söndürelim
led.off()

# Resim Çekmece - Çekilemezse ledi söndürür! O da hata döndürür!
def captureImage(image_name):
    try:
        with PiCamera() as camera:
            camera.resolution = (800, 600)
            camera.rotation = 90
            camera.capture('./images/%s' % image_name, resize = (384, 512))
    except:
        led.off()
        
def printAll(img):
    try:
        # Printer header
        header = Image.open("./src/printer_header.png")
        printer.printImage(header, LaaT=True)
        printer.feed(1)
        printer.printImage(img, LaaT=True)
        printer.feed(1)
        simdi = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        printer.justify('c')
        printer.println(simdi)
        printer.feed(2)
        printer.setDefault()
        
    except:
        print("Printer yazmada sorun yaşadı!")

print("Sistem açıldı!")

while True:
    # LED sönükken düğmeye basılırsa... (çalışmaya uygunken)
    if led.value == 0 and button.is_pressed:
        # Ledi yakalım
        led.on()
        # Resmin ismini belirleyelim!
        stamp = datetime.now().strftime("%d%m%Y%H%M%S")
        image_name = "img_%s.png" % stamp
        # resmi çek...
        captureImage(image_name)
        # resim başarılı bir biçimde çekilirse led yanık kalacak. yazdırmaya çalışalım
        if led.value == 1:
            # Devam edelim foto çekilmiş!
            led.blink()
            # haydi print edelim
            with Image.open("./images/%s" % image_name).convert('LA') as img:
                printAll(img)
            
            # hadi resmi silelim! Hafızayı doldurmasın!
            try:
                os.remove("./images/%s" % image_name)
                print("Resim silindi!")
            except:
                print("Resim silinemedi!")
            
            led.off()
            print("Fotoğraf çekildi ve basıldı!")
            
        else:
            print("Fotoğraf çekilemedi!")
        