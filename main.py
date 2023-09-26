# coding:utf-8
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import ocr
import piexif
import piexif.helper
 
from datetime import timedelta
 
#设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
 
app = Flask(__name__)
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)
 
# img_path
ocrimg_path = './static/ocr_images'

def write_exit(img_file, ocr_res):   
    user_comment = piexif.helper.UserComment.dump(ocr_res, encoding="unicode")
    exif_dict = piexif.load(img_file)
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, img_file)

def read_exit(img_file):
    exif_dict = piexif.load(img_file)
    user_comment = piexif.helper.UserComment.load(exif_dict["Exif"][piexif.ExifIFD.UserComment])
    return user_comment

def get_ocr_res(img_file):
    ocr_res = ""
    image = np.array(Image.open(img_file).convert('RGB'))
    result, text_recs, scale = ocr.model(image)
    for key in range(len(text_recs)):
        try:
            res = result[key][1]
        except KeyError:
            res = ""
        ocr_res += res
    return ocr_res    
              
@app.route('/index', methods=['POST', 'GET'])  # 添加路由
def upload():
    if request.method == 'POST':
        f = request.files['file']
        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(basepath, 'static/ocr_images', secure_filename(f.filename))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        # 图片保存在目标路径
        f.save(upload_path)
        # 获取图片对象
        img_file = "./static/ocr_images/" + f.filename
        # 调用ocr
        #ocr_res = get_ocr_res(img_file)
        ocr_res = "ARCADIA"
        # 识别结果存入图片
        write_exit(img_file, ocr_res)
    # 展示文件夹下图片     
    for root,dirs,files in os.walk(ocrimg_path):
        img_names = files   
    return render_template('index.html', imgnames=img_names,text_sea="键入文字")

@app.route('/search', methods=['POST'])  # 添加路由
def search():  
    # 检索结果列表
    ret_imgnames = []
    # 获取检索词
    search_text = request.form.get('data')
    #遍历图片 匹配检索词和ocr结果
    for root,dirs,files in os.walk(ocrimg_path):
        img_names = files
    for img_name in img_names:
        img_file = "./static/ocr_images/" + img_name
        # 读取OCR文本
        user_comment = read_exit(img_file)
        # 检索词完全在OCR结果内
        if search_text in user_comment:
            ret_imgnames.append(img_name)   
    return render_template('index.html', imgnames=ret_imgnames,text_sea=search_text)
 
if __name__ == '__main__':
    # app.debug = True
    app.run(host='127.0.0.1', port=8987, debug=True)
