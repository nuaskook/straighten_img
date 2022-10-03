# -*- coding: utf-8 -*-
"""Straighten Picture - NTK.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19XrTA8gO0WP_hwalGfUF3QZOGVog6oft

#Straighten Picture 🎯 


การทำภาพตรงมีขั้นตอนดังนี้


1.  การปรับภาพ
ด้วยแปลงภาพให้เป็นสีเทา
เบลอภาพด้วยเทคนิค GaussianBlur
ปรับความสว่างภาพ
2. การหาขอบภาพ
หาขอบภาพด้วย Canny Edged
contour ภาพ
หามุมของขอบภาพ
จากนั้นทำการ warp image
3. ปรับรูปภาพให้ดีขึ้น
โดยการลบเงาภาพ



## การใช้งาน




1. upload รูปภาพ จากนั้น run ทุก cell
2. แสดงผลลัพธ์
"""

pip install imshowtools

#@title Import module
import os
import numpy as np
import cv2
from google.colab.patches import cv2_imshow # for image display
from skimage. filters import threshold_local
from google.colab import files
from IPython.display import HTML
from PIL import Image
from imshowtools import imshow

"""<h1>การอัพโหลดรูปภาพ<h1>"""

#@markdown <h3> เลือกรูปภาพ Upload Image </h3>
#@markdown <h5>📤 upload your image</h5>
display(HTML('<h3 style="color:Tomato;padding:5px;border:2px solid powderblue;Width:15%;">Select your image 🚀</h3>'))
directory = os.getcwd()
uploaded = files.upload()
preupload = [os.path.join(directory, f) for f in uploaded.keys()]
image = preupload[0]
img = cv2.imread(image)

"""<h1>ปรับภาพ 📈<h1>

---


"""

#@markdown <h3> แปลงภาพให้เป็นสีเทา</h3>
Grayimg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #convert to gray color

#@markdown <h3> เบลอภาพเพื่อลด noise</h3>
#@markdown <h5>เทคนิค GuassianBlur</h5>
#Blurring using the Gaussian function where pixels closer to the pixels color gets a higher weight
Blur = cv2.GaussianBlur(Grayimg,(13,13),2) #blur pic

#@markdown <h3> ปรับความสว่างภาพ</h3>
#@markdown <h5>ด้วยปรับ alpha และ beta ของรูปภาพ โดย alpha คือการปรับ contrast และ beta คือการปรับความสว่าง</h5>
alpha = 1.2 # Contrast control (1.0-3.0)
beta = 10 # Brightness control (0-100)
con = cv2.convertScaleAbs(Blur, alpha=alpha, beta=beta)

imshow(img,Grayimg,Blur,con,mode='BGR',size=(15,15),rows=2,padding=0)

"""<h1>การหาขอบภาพ 📐 <h1>

---

# <h3>Morphological Transformations<h3>
1.    เทคนิค Erosion คือการลบเส้นขอบ ลด noises 
2.   เทคนิค Dilation คือการเพิ่มความหนาของเส้น เหมาะสำหรับการเพิ่มจุดที่เสียหายไป

<center>
<img src="https://drive.google.com/uc?export=view&id=1WBsIKiQ180gIgGiAHrRfa_Ll3IIwr1ZX" width="500"/>
</center>



*  ข้อมูลเพิ่มเติมดูได้ที่ [Morphological OpenCV](https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html)
"""

#@markdown <h3> 📑การหาขอบภาพ📑</h3>
#@markdown <h5>หาขอบภาพด้วย Canny Edged โดยมีการเสริมเทคนิค Morphology 1.dilate 2.erosion และ threshold_otsu คือการปรับ threshold ลดสีของ background  ซึ่งจะทำให้สามารถหาเอกสารได้แม่นยำมากยิ่งขึ้น</h5>
def remove_noise_and_smooth(file_name):
  kernel = np.ones((5,5))
  ret, th = cv2.threshold(file_name,
    0,  # threshold value, ignored when using cv2.THRESH_OTSU
    255,  # maximum value assigned to pixel values exceeding the threshold
    cv2.THRESH_BINARY + cv2.THRESH_OTSU)
  dilation = cv2.dilate(th,kernel,iterations = 3) # increases the white region in the image
  erosion = cv2.erode(dilation, kernel, iterations=2) #erodes away the boundaries
  imshow(th,dilation,erosion,size=(15,15),padding=0)
  return erosion
#Finding Intensity Gradient of the Image
edged = cv2.Canny(remove_noise_and_smooth(con), 300, 200)

#@markdown <h3> 📑Contour ภาพ  📑</h3>
#@markdown <h5> เทคนิค Find & DrawContours โดย Find จะจับขอบรูปร่างของภาพและ Draw คือทำการวาดลงไป โดยกำหนดให้เส้นขอบนี้มีสีชมพู</h5>
contours, _ = cv2.findContours(edged,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
Contourry = img.copy()
Contourry = cv2.drawContours(Contourry,contours,-1,(255,50,255),5)

#@markdown <h3> 📑 หามุมขอบภาพ 📑</h3> <h5>โดยการกำหนด Area ที่มีขอบภาพ 4 ด้าน ซึ่งหากพื้นที่นั้นมากกว่า 3000 ให้ทำการจุดขอบภาพนั้น ซึ่งกำหนดให้จุดมีสีชมพู<h5>
Pop = img.copy()
MaxArea = 0
biggest = []
for i in contours:
  area = cv2.contourArea(i)
  if area > 3000:
    peri = cv2.arcLength(i,True)
    edge = cv2.approxPolyDP(i,0.02*peri,True)
    if area > MaxArea and len(edge)==4:
      biggest = edge
      MaxArea = area
if len(biggest) == 4:
  Pop = cv2.drawContours(Pop,biggest,-1,(255,0,255),20)

#@markdown <h3> 📑 ลากเส้นขอบ 📑</h3> <h5>ทำการเชื่อมเส้นจากจุดที่กำหนดจากภาพก่อนหน้า โดยกำหนดให้เส้นมี 4 สี คือ 1.สีฟ้าคือเส้นตำแหน่งด้านบน 2.สีส้มคือ เส้นตำแหน่งด้านล่าง 3.สีเขียว-เส้นด้านซ้าย และ 4.สีชมพูคือตำแหน่งด้านขวา ซึ่งภาพที่ได้อาจจะมีการพลิกหรือสลับได้ หากสีของเส้นดังกล่าว อยู่ไม่ถูกตำแหน่งด้านของภาพ<h5>
w,h = img.shape[1::-1]
def drawRec(BiggestNew,mainframe):
  cv2.line (mainframe,(BiggestNew[0][0][0],BiggestNew[0][0][1]),(BiggestNew[1][0][0],BiggestNew[1][0][1]),(255,20,147),5)
  cv2.line (mainframe,(BiggestNew[0][0][0],BiggestNew[0][0][1]),(BiggestNew[2][0][0],BiggestNew[2][0][1]),(124,252,0),5)
  cv2.line (mainframe,(BiggestNew[3][0][0],BiggestNew[3][0][1]),(BiggestNew[2][0][0],BiggestNew[2][0][1]),(100,149,237),5)
  cv2.line (mainframe,(BiggestNew[3][0][0],BiggestNew[3][0][1]),(BiggestNew[1][0][0],BiggestNew[1][0][1]),(218,112,214),5)
imgwarp = img.copy()
Cornerf = img.copy()
if len(biggest) != 0:
  biggest = biggest.reshape((4,2))
  BiggestNew = np.zeros((4,1,2),dtype=np.int32)
  add = biggest.sum(1)
  BiggestNew[0]=biggest[np.argmin(add)]
  BiggestNew[3]=biggest[np.argmax(add)]
  dif = np.diff(biggest,axis=1)
  BiggestNew[1]=biggest[np.argmin(dif)]
  BiggestNew[2]=biggest[np.argmax(dif)]
  drawRec(BiggestNew,Cornerf)
  Cornerf = cv2.drawContours(Cornerf,BiggestNew,-1,(255,0,255),15)
  pts1 = np.float32(BiggestNew)
  pts2 = np.float32([[0,0],[w,0],[0,h],[w,h]])
  matrix = cv2.getPerspectiveTransform(pts1,pts2)
  imgwarp = cv2.warpPerspective(img,matrix,(w,h))

#REMOVE 20 PIXELS FORM EACH SIDE
imgwarp = imgwarp[20:imgwarp.shape[0]-20,20:imgwarp.shape[1]-20]
imgwarp= cv2.resize(imgwarp,(w,h))

imshow(edged,Contourry,Pop,Cornerf,mode='BGR',size=(15,15),rows=2,padding=0)

"""<h1>Enhancement<h1>

---



"""

#@markdown <h3> 📑 การลบเงาภาพ 📑</h3>
#@markdown <h5>ด้วยการแบ่งภาพเป็น 3 สี RGB ใช้เทคนิค dilate เพิ่มความหนาของรายละเอียดบนภาพแล้วปรับให้เบลอด้วย median blur จากนั้นทำการ normalize ภาพ</h5>
rgb_planes = cv2.split(imgwarp)
result_norm_planes = []
for plane in rgb_planes:
    dilated_img = cv2.dilate(plane, np.ones((5,5), np.uint8))
    bg_img = cv2.medianBlur(dilated_img, 13)
    diff_img = 255 - cv2.absdiff(plane, bg_img)
    norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    result_norm_planes.append(norm_img)
    
result_norm = cv2.merge(result_norm_planes)

#@markdown <h5> ใช้เทคนิค threshold local </h5>
grayscaled = cv2.cvtColor(result_norm,cv2.COLOR_BGR2GRAY)
T = threshold_local(grayscaled,11,offset=10,method="gaussian")
warp = (grayscaled>T).astype("uint8")*255

#@markdown <h5> ใช้เทคนิค Adaptive threshold จากนั้นเปลี่ยนสีกระดาษในภาพต้นฉบับ ให้เป็นสีขาว (255,255,255)</h5>
thresh = cv2.adaptiveThreshold(grayscaled, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 9)

#in result pic will be white tone color(pixel value= 255) so replace 255 to (255,255,255), to convert white tone pixel to white.
# make background of input white where thresh is white
result = imgwarp.copy()
result[thresh==255] = (255,255,255)

imshow(imgwarp,result_norm,warp,result,mode='BGR',size=(15,15),rows=2,padding=0)

#@title 📑 Select Picture 📑{ run: "auto" }
Image = "Scanned Picture" #@param ["Original Picture", "Shadow Removal", "Scanned Picture","Scanned Picture Ver.2"]
print('You selected',Image) 
if Image == 'Original Picture':
  imshow(imgwarp,size=(15,15),mode='BGR')
elif Image == 'Shadow Removal':
  imshow(result_norm,size=(15,15),mode='BGR')
elif Image == 'Scanned Picture':
  imshow(warp,size=(15,15),mode='BGR')
elif Image == 'Scanned Picture Ver.2':
  imshow(result,size=(15,15),mode='BGR')

"""<h1>Result✨<h1>"""

imshow(img,Cornerf,imgwarp,warp,rows=1,size=(20,20),mode='BGR',padding=0)