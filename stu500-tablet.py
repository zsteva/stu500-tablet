#!/usr/bin/env python3

# zsteva@gmail.com
# 2024-05-05

import os
import sys
import hid
from evdev import UInput, AbsInfo, ecodes
import logging

def initLoggerStderr():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

tablet_vendor_id = 1386
tablet_product_id = 161

WIDTH=10040+1
HEIGHT=7621+1

WIDTH_INCH=4.0157
HEIGHT_INCH=2.9921

HEIGHT_DPI=int(WIDTH / WIDTH_INCH)
WIDTH_DPI=int(HEIGHT / HEIGHT_INCH)

cap = {
    ecodes.EV_KEY: [ecodes.BTN_TOUCH, ecodes.BTN_STYLUS],
    ecodes.EV_ABS: [
        (ecodes.ABS_PRESSURE, AbsInfo(value=0, min=0, max=255, flat=0, fuzz=0, resolution=0)),
        (ecodes.ABS_X, AbsInfo(value=0, min=0, max=WIDTH, flat=0, fuzz=0, resolution=WIDTH_DPI)),
        (ecodes.ABS_Y, AbsInfo(value=0, min=0, max=HEIGHT, flat=0, fuzz=0, resolution=HEIGHT_DPI))
    ]
}

def main():
    logger = logging.getLogger()

    if not os.path.exists("/sys/module/uinput"):
        logger.info("Load module uinput")
        ret = os.system("modprobe uinput")
        if ret != 0:
            logger.error("failed to modprobe uinput %d" % (ret))
            exit(21)

    tablet = hid.device()

    try:
        tablet.open(tablet_vendor_id, tablet_product_id)
    except Exception as e:
        logger.error("failed to open device %04x:%04x" % (tablet_vendor_id, tablet_product_id))
        logger.exception(e)
        exit(22)

    ui = UInput(cap, name='tablet-device')

    logger.info("main loop...")

    prev_button = 0;
    while True:
        try:
            buf = tablet.read(7)
        except:
            logger.error("disconnect?")
            break

        x = (buf[3] << 8) | buf[4]
        y = (buf[5] << 8) | buf[6]
        pres = buf[2]
        #logger.debug("x: ", x, "y:", y, "pres:", pres, buf)
        button = 1 if buf[1] > 128 else 0

        ui.write(ecodes.EV_ABS, ecodes.ABS_X, x)
        ui.write(ecodes.EV_ABS, ecodes.ABS_Y, y)

        if button or prev_button:
            ui.write(ecodes.EV_ABS, ecodes.ABS_PRESSURE, pres)
            
        if prev_button != button:
            ui.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, button)
            prev_button = button

        ui.syn()

    logger.info('exit...')
    exit(0)


if __name__ == '__main__':
    initLoggerStderr()

    logger = logging.getLogger()
    try:
        main()
    except Exception as e:
        logger.exception(e)

