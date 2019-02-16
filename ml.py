import requests
from PIL import Image
import pytesseract
import os
from svmutil import *
from svm import *


def getYzm(i):
    jwxt_Session = requests.session()
    hostUrl = 'http://jwxt.bupt.edu.cn'
    yzmurl = 'http://jwxt.bupt.edu.cn/validateCodeAction.do?random='
    x = jwxt_Session.get(hostUrl)
    content = jwxt_Session.get(yzmurl).content
    f = open('yzm/yz_' + str(i) + '.jpg', 'wb')
    f.write(content)
    f.close()


def converImg(image):
    image = image.crop((4, 0, 56, 20))
    imgry = image.convert('L')  # 转化为灰度图
    threshold = 125
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    out = imgry.point(table, '1')
    return out


def sum_9_region(img, x, y):
    """
    9邻域框,以当前点为中心的田字框,黑点个数
    :param x:
    :param y:
    :return:
    """
    # todo 判断图片的长宽度下限
    cur_pixel = img.getpixel((x, y))  # 当前像素点的值
    width = img.width
    height = img.height

    if cur_pixel == 1:  # 如果当前点为白色区域,则不统计邻域值
        return 0

    if y == 0:  # 第一行
        if x == 0:  # 左上顶点,4邻域
            # 中心点旁边3个点
            sum = cur_pixel \
                + img.getpixel((x, y + 1)) \
                + img.getpixel((x + 1, y)) \
                + img.getpixel((x + 1, y + 1))
            return 4 - sum
        elif x == width - 1:  # 右上顶点
            sum = cur_pixel \
                + img.getpixel((x, y + 1)) \
                + img.getpixel((x - 1, y)) \
                + img.getpixel((x - 1, y + 1))

            return 4 - sum
        else:  # 最上非顶点,6邻域
            sum = img.getpixel((x - 1, y)) \
                + img.getpixel((x - 1, y + 1)) \
                + cur_pixel \
                + img.getpixel((x, y + 1)) \
                + img.getpixel((x + 1, y)) \
                + img.getpixel((x + 1, y + 1))
            return 6 - sum
    elif y == height - 1:  # 最下面一行
        if x == 0:  # 左下顶点
            # 中心点旁边3个点
            sum = cur_pixel \
                + img.getpixel((x + 1, y)) \
                + img.getpixel((x + 1, y - 1)) \
                + img.getpixel((x, y - 1))
            return 4 - sum
        elif x == width - 1:  # 右下顶点
            sum = cur_pixel \
                + img.getpixel((x, y - 1)) \
                + img.getpixel((x - 1, y)) \
                + img.getpixel((x - 1, y - 1))

            return 4 - sum
        else:  # 最下非顶点,6邻域
            sum = cur_pixel \
                + img.getpixel((x - 1, y)) \
                + img.getpixel((x + 1, y)) \
                + img.getpixel((x, y - 1)) \
                + img.getpixel((x - 1, y - 1)) \
                + img.getpixel((x + 1, y - 1))
            return 6 - sum
    else:  # y不在边界
        if x == 0:  # 左边非顶点
            sum = img.getpixel((x, y - 1)) \
                + cur_pixel \
                + img.getpixel((x, y + 1)) \
                + img.getpixel((x + 1, y - 1)) \
                + img.getpixel((x + 1, y)) \
                + img.getpixel((x + 1, y + 1))

            return 6 - sum
        elif x == width - 1:  # 右边非顶点
            # a =('%s,%s' % (x, y))
            sum = img.getpixel((x, y - 1)) \
                + cur_pixel \
                + img.getpixel((x, y + 1)) \
                + img.getpixel((x - 1, y - 1)) \
                + img.getpixel((x - 1, y)) \
                + img.getpixel((x - 1, y + 1))

            return 6 - sum
        else:  # 具备9领域条件的
            sum = img.getpixel((x - 1, y - 1)) \
                + img.getpixel((x - 1, y)) \
                + img.getpixel((x - 1, y + 1)) \
                + img.getpixel((x, y - 1)) \
                + cur_pixel \
                + img.getpixel((x, y + 1)) \
                + img.getpixel((x + 1, y - 1)) \
                + img.getpixel((x + 1, y)) \
                + img.getpixel((x + 1, y + 1))
            return 9 - sum


def clearNoise(image):
    for x in range(0, image.size[0]):
        for y in range(0, image.size[1]):
            color = sum_9_region(image, x, y)
            if color < 3:
                image.putpixel((x, y), 1)
    return image


def getClearImg():
    for i in range(100):
        filename = 'yz_' + str(i) + '.jpg'
        image = converImg(filename)
        image = clearNoise(image)
        image.save('test/' + filename)


def get_crop_imgs(img):
    """
    按照图片的特点,进行切割,这个要根据具体的验证码来进行工作. # 见原理图
    :param img:
    :return:
    """
    child_img_list = []
    for i in range(4):
        x = i * 13  # 见原理图
        y = 0
        child_img = img.crop((x, y, x + 13, y + 20))
        child_img_list.append(child_img)

    return child_img_list


def cut():
    for i in range(3000):
        filename = 'yz_' + str(i) + '.jpg'
        image = Image.open('test/' + filename)
        s = pytesseract.image_to_string(image)
        child_img_list = get_crop_imgs(image)
        for j in range(len(child_img_list)):
            try:
                if s[j] == 'm' or s[j] == 'W':
                    path = 'test3/rest/yzm_{0}_{1}.jpg'.format(i, j)
                    child_img_list[j].save(path)
                else:
                    pass
            except BaseException:
                # path = 'test3/yzm_{}_{}.jpg'.format(i, j)
                # child_img_list[j].save(path)
                pass


def get_feature(img):
    """
    获取指定图片的特征值,
    1. 按照每排的像素点,高度为10,则有10个维度,然后为6列,总共16个维度
    :param img_path:
    :return:一个维度为10（高度）的列表
    """

    width, height = img.size

    pixel_cnt_list = []
    # for y in range(height):
    #     pix_cnt_x = 0
    #     for x in range(width):
    #         if img.getpixel((x, y)) == 0:  # 黑色点
    #             pix_cnt_x += 1

    #     pixel_cnt_list.append(pix_cnt_x)

    # for x in range(width):
    #     pix_cnt_y = 0
    #     for y in range(height):
    #         if img.getpixel((x, y)) == 0:  # 黑色点
    #             pix_cnt_y += 1

    #     pixel_cnt_list.append(pix_cnt_y)
    for y in range(height):
        for x in range(width):
            if img.getpixel((x, y))==0:
                pixel_cnt_list.append(1)
            else:
                pixel_cnt_list.append(0)
    return pixel_cnt_list


def mk_train_file():
    dir_name = os.listdir('./test3')
    f = open('test.txt', 'w+')
    for item in dir_name:
        x = os.listdir('./test3/' + item)
        sumD = len(x)
        for i in range(sumD):
            try:
                path = '{}/{}/{}.jpg'.format('test3/', item, i)
                img = Image.open(path)
                features = get_feature(img)
                ans = item
                if len(ans) == 2:
                    ans = '%s' % (ord(ans[0]))
                else:
                    ans = '%s' % (ord(ans))
                for j in range(len(features)):
                    ans = ans + ' {}:{}'.format(j + 1, features[j])
                ans = ans + '\n'
                f.write(ans)
            except:
                pass
    f.close()

def getAns(image):
    f=open('last_test.txt','w+')
    imgs=get_crop_imgs(image)
    for img in imgs:
        ans='1'
        features = get_feature(img)
        for j in range(len(features)):
            ans = ans + ' {}:{}'.format(j + 1, features[j])
        ans=ans+'\n'
        f.write(ans)
    f.close()
    yt, xt = svm_read_problem('last_test.txt')
    model = svm_load_model('model_file.txt')
    p_label, p_acc, p_val = svm_predict(yt, xt, model)#p_label即为识别的结果
    name=''
    for item in p_label:
        name=name+chr(int(item))
    return name

def work():
    print('开始爬取验证码。。。')
    # for i in range(100):
    #     getYzm(i)
    # print('爬取完成\n')
    print('开始二值化。。。')
    getClearImg()
    print('二值化完成\n')
    # print('开始剪切分类。。。')
    # cut()
    # print('剪切分类完成')


def train():
    mk_train_file()
    y, x = svm_read_problem('test.txt')
    model = svm_train(y, x)
    model_path = 'model_file.txt'
    svm_save_model(model_path, model)


if __name__ == '__main__':
    for i in range(1000):
        getYzm(i)
    for i in range(1000):
        filename='yzm/yz_{}.jpg'.format(i)
        image=Image.open(filename)
        image = converImg(image)
        image = clearNoise(image)
        image.save('test/yz_{}.jpg'.format(i))
        # name=getAns(image)
        # new_file='yzm/{}.jpg'.format(name)
        # os.rename(filename,new_file)
    
    for i in range(1000):
        old='test/yz_{}.jpg'.format(i)
        image=Image.open(old)
        name=getAns(image)
        old='yzm/yz_{}.jpg'.format(i)
        new='test/{}.jpg'.format(name)
        try:
            os.rename(old,new)
        except :
            pass
        
