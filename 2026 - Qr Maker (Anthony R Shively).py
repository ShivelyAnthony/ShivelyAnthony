#2026 Anthony R Shively (Mercer Ohio 1997)
import segno
import os
import glob
import time
location_png = '*.png'
location_jpg = '*.jpg'
photo = glob.glob(location_png) + glob.glob(location_jpg)
for line in photo:
    print(line)
    new = line
    if '.jpg' in new:
        new = new.replace('.jpg', '_qrcode.png')
    elif '.JPG' in new:
        new = new.replace('.JPG', '_qrcode.png')
    elif '.png' in new:
        new = new.replace('.png', '_qrcode.png')
    elif 'PNG' in new:
        new = new.replace('.PNG', '_qrcode.png')
    if os.path.exists(new) == False:
        #Segno must convert JPG to PNG
        source = input('Source:')
        if source == '':
            pass
        else:
            qrcode = segno.make_qr(source)
            qrcode.save(new, scale=10,)
#input('Exit')