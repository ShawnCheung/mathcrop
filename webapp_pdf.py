"""
Simple app to upload an image via a web form 
and view the inference results on the image in the browser.
"""
import argparse
import time
import os
from PIL import Image
import cv2
import torch
import numpy as np
import copy
from flask import Flask, render_template, request, redirect
from pdf2image import convert_from_path, convert_from_bytes
from mathpix import pic2latex, picbatch2latex, picbatch2latexv2

app = Flask(__name__)

@app.route("/forward", methods=["GET", "POST"])
def move_forward():
    global ind, maxpage, formulalist
    ind += 1
    if ind>=maxpage:
        ind = maxpage-1
    if formulalist[ind]==[]:
        pass
    elif formulalist[ind][0].endswith(".txt"):
        formulalist[ind] = picbatch2latexv2(namelist[ind], formulalist[ind])
    return render_template("landing_page.html", page=pagelist[ind],namelist=namelist[ind], formulalist=formulalist[ind], num = len(namelist[ind]))

@app.route("/backward", methods=["GET", "POST"])
def move_backward():
    global ind,maxpage
    ind -= 1
    if ind<=0:
        ind = 0
    return render_template("landing_page.html", page=pagelist[ind],namelist=namelist[ind], formulalist=formulalist[ind], num = len(namelist[ind]))

@app.route("/", methods=["GET", "POST"])
def predict():
    global ind
    global maxpage
    global pagelist
    global namelist
    global formulalist
    ind = 0
    
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if not file:
            return
        # img_bytes = file.read()
        # img = Image.open(io.BytesIO(img_bytes))
        os.makedirs("./static/tmp/"+file.filename[:-4], exist_ok=True)
        file.save("./static/tmp/"+file.filename[:-4]+"/"+file.filename)
        images=convert_from_path("./static/tmp/"+file.filename[:-4]+"/"+file.filename)
        imgs = [np.array(img).astype(np.uint8) for img in images]
        math_imgs = copy.deepcopy(imgs)
        results = model(imgs, size=640)
        results.render(labels=False)  # updates results.imgs with boxes and labels

        pagelist = []
        namelist = []
        # formulalist = []
        formulalistpath = []
        for i, pred in enumerate(results.pred):
            box = pred.cpu().numpy().astype(np.int)
            box = box[np.argsort(box[:,1])]
            math = [math_imgs[i][bb[1]-5:bb[3]+5, bb[0]-5:bb[2]+5, :] for bb in box]
            os.makedirs("./static/tmp/"+file.filename[:-4]+"/{}".format(i),exist_ok=True)
            
            pagename = "./static/tmp/"+file.filename[:-4]+"/{}/page_{}.jpg".format(i,i)
            pagelist.append(pagename)
            cv2.imwrite(pagename, results.imgs[i])

            nl = []
            fl = []
            for j, m in enumerate(math):
                namepic = "./static/tmp/"+file.filename[:-4]+"/{}/formula_{}.jpg".format(i,j)
                namemath = "./static/tmp/"+file.filename[:-4]+"/{}/formula_{}.txt".format(i,j)
                cv2.imwrite(namepic, m)
                # math = pic2latex(namepic, namemath)
                nl.append(namepic)
                fl.append(namemath)
            namelist.append(nl)
            formulalistpath.append(fl)
        maxpage=len(namelist)
        # formulalist = picbatch2latex(namelist, formulalistpath)
        formulalist = formulalistpath
        return render_template("landing_page.html",page=pagelist[ind],namelist=namelist[ind], formulalist=formulalist[ind], num = len(namelist[ind]))
    return render_template("index.html")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask app exposing yolov5 models")
    parser.add_argument("--port", default=5000, type=int, help="port number")
    args = parser.parse_args()

    # model = torch.hub.load(
    #     "ultralytics/yolov5", "yolov5s", pretrained=True, force_reload=True, autoshape=True
    # )  # force_reload = recache latest code
    model = torch.hub.load("../yolov5", "custom", path="../yolov5/runs/train/exp5/weights/best.pt", source="local")
    model.eval()
    app.run(host="0.0.0.0", port=args.port)  # debug=True causes Restarting with stat
