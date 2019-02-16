from PIL import Image
from svmutil import *
from svm import *


def converImg(image):
    # 转化为灰度图
    image = image.crop((4, 0, 56, 20))
    imgry = image.convert('L')
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

    # 找到x,y周围的黑点个数
    cur_pixel = img.getpixel((x, y))
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
    # 图片降噪
    for x in range(0, image.size[0]):
        for y in range(0, image.size[1]):
            color = sum_9_region(image, x, y)
            if color < 3:
                image.putpixel((x, y), 1)
    return image


def get_crop_imgs(img):
    # 图片切割成四个小块
    child_img_list = []
    for i in range(4):
        x = i * 13  # 见原理图
        y = 0
        child_img = img.crop((x, y, x + 13, y + 20))
        child_img_list.append(child_img)

    return child_img_list


def get_feature(img):

    # 获取指定图片的特征值 每个像素点的是否为黑点
    width, height = img.size
    pixel_cnt_list = []
    for y in range(height):
        for x in range(width):
            if img.getpixel((x, y)) == 0:
                pixel_cnt_list.append(1)
            else:
                pixel_cnt_list.append(0)
    return pixel_cnt_list


def getYzm(image):
    f = open('last_test.txt', 'w+')
    imgs = get_crop_imgs(image)
    for img in imgs:
        ans = '1'
        features = get_feature(img)
        for j in range(len(features)):
            ans = ans + ' {}:{}'.format(j + 1, features[j])
        ans = ans + '\n'
        f.write(ans)
    f.close()
    yt, xt = svm_read_problem('last_test.txt')
    model = svm_load_model('model_file.txt')
    p_label, p_acc, p_val = svm_predict(yt, xt, model)  # p_label即为识别的结果
    name = ''
    for item in p_label:
        name = name + chr(int(item))
    return name


def img_to_str(path):
    image = Image.open(path)
    image = converImg(image)
    image = clearNoise(image)
    #image.save('temp.jpg')
    #image = Image.open('temp.jpg')
    result = getYzm(image)
    return result


if __name__ == '__main__':
    print(img_to_str('radomImage.jpg'))
    print(img_to_str('yz.jpg'))
