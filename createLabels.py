# """ from screencaptures create labels for each picture """
# import os
# from PIL import Image, ImageChops



# # generated list of snapshots and their scores
# dir = "screenCaptures/"
# fileNames = []
# for filename in os.listdir(dir):
#     if (filename == '.DS_Store'): continue
#     if (filename.split(".")[0][-1] == '1'): continue #dont use scoring pictues
#     nextFile = filename.split(".")[0][0:-1] + '1' + '.png'
#     if (not os.path.exists(dir + nextFile)): continue #dont use files without scoring pictues
#     fileNames.append([filename, nextFile])
# fileNames.sort(key= lambda x: int(x[0].split(".")[0].split("e")[1]))

# for filePair in fileNames:
#     im1 = Image.open(dir + filePair[0])
#     im2 = Image.open(dir + filePair[1])
#     diff = ImageChops.difference(im1, im2)
#     print(diff)
#     # width, height = im.size
#     # pix = im.load()
#     # for i in range(width):
#     #     for j in range(height):
#     #         if ((pix[i, j][0] < 10)): print(pix[i, j], i, j)