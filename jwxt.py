import requests
import buptYzm
from bs4 import BeautifulSoup
headers = {
    'Host': 'jwxt.bupt.edu.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def getYzm(jwxt_Session):
    hostUrl = 'http://jwxt.bupt.edu.cn'
    yzmurl = 'http://jwxt.bupt.edu.cn/validateCodeAction.do?random='
    x = jwxt_Session.get(hostUrl, headers=headers)
    content = jwxt_Session.get(yzmurl, headers=headers).content
    f = open('yz.jpg', 'wb')
    f.write(content)
    f.close()
    return buptYzm.img_to_str('yz.jpg')
	
def alignment(str1, space, align='left'):
    length = len(str1.encode('gb2312'))
    space = space - length if space >= length else 0
    if align == 'left':
        str1 = str1 + ' ' * space
    elif align == 'right':
        str1 = ' ' * space + str1
    elif align == 'center':
        str1 = ' ' * (space // 2) + str1 + ' ' * (space - space // 2)
    return str1
	
def getSco(password, username, vyzm, jwxt_Session):
    data = {'mm': password, 'type': 'sso', 'v_yzm': vyzm, 'zjh': username}
    loginUrl = 'http://jwxt.bupt.edu.cn/jwLoginAction.do'
    jwxt_Session.post(loginUrl, data=data, headers=headers).text

    url = 'http://jwxt.bupt.edu.cn/bxqcjcxAction.do'
    html = jwxt_Session.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')
    allSco = soup.find_all('tr', attrs={'class': 'odd'})
    if len(allSco) == 0:
        return 0
    print('登录成功')
    print('-'*50)
    print(
        '|',
        alignment(
            '学科',
            20,
            align='left'),
        '|',
        alignment(
            '学分',
            10,
            align='left'),
        '|',
        alignment(
            '成绩',
            10,
            align='left'),
        '|')
    for x in allSco:
        t = x.find_all('td')
        name = t[2].text.strip().replace("\n", "")
        xf = t[4].text.strip().replace("\n", "")
        sco = t[6].text.strip().replace("\n", "")
        print('-'*50)
        print(
			'|',
			alignment(
				str(name),
				20,
				align='left'),
			'|',
			alignment(
				str(xf),
				10,
				align='left'),
			'|',
			alignment(
				str(sco),
				10,
				align='left'),
			'|')
    print('-'*50)
    return 1


def start():
    print()
    username="user"
    password="passwd"
    print('用户：{} 尝试登录'.format(username))
    jwxt_Session = requests.Session()
    vyzm=getYzm(jwxt_Session)
    print('验证码识别结果:',vyzm)
    ok = getSco(password, username, vyzm, jwxt_Session)
    if ok == 0:
        return 0
    return 1


if __name__ == '__main__':
    print('-------------教务系统查分爬虫-----------')

    while True:
        result=start()
        if result==0:
            print('登录失败')
        else:
            break
	
    input('按回车结束')
    
