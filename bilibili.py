import os, random, re, time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from urllib.request import urlretrieve
from PIL import Image
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from lxml import etree

ACCOUNT = 'xxxxxxx'
PASSWORD = 'xxxxxxx'
border = 6
class CrackGeetest:
    def __init__(self):
        self.url = 'https://passport.bilibili.com/login'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 10)
        self.account = ACCOUNT
        self.password = PASSWORD

    def get_geetest_image_location(self):
        # 定义乱序的完整图片和缺口图片的元素列表
        bg = []
        fullbg = []
        # 完整图片和缺口图片的xpath地址
        bg_xpath = '//*[@id="gc-box"]/div/div[1]/div[2]/div[1]/a[1]/div[1]/div'
        fullbg_xpath = '//*[@id="gc-box"]/div/div[1]/div[2]/div[1]/a[2]/div[1]/div'
        # 完整图片和缺口图片的style属性的xpath地址
        bg_url_xpath = bg_xpath + '[1]/@style'
        fullbg_url_xpath = fullbg_xpath + '[1]/@style'
        # 若元素列表都为空
        while bg == [] and fullbg == []:
            # 网页源码
            page_html = crack.browser.page_source
            # 提取所有乱序的完整图片和缺口图片
            selector = etree.HTML(page_html)
            bg = selector.xpath(bg_xpath)
            fullbg = selector.xpath(fullbg_xpath)
        # 提取完整图片和缺口图片的元素的style属性中的内容, 其中包括url和乱序图片位置信息
        bg_url_attr = selector.xpath(bg_url_xpath)[0]
        fullbg_url_attr = selector.xpath(fullbg_url_xpath)[0]
        # 提取完整图片和缺口图片的url
        bg_url = bg_url_attr.split('\"')[1].replace('webp', 'jpg')
        fullbg_url = fullbg_url_attr.split('\"')[1].replace('webp', 'jpg')
        # 定义完整图片和缺口图片的位置信息列表
        bg_location_list = []
        fullbg_location_list = []
        # 遍历所有乱序缺口图片
        for i in range(len(bg)):
            # 定义乱序的缺口图片的位置信息, 以{‘x’：int, ‘y’：int}的字典形式
            bg_location = {}
            bg_location['x'] = int(selector.xpath(bg_xpath + '[{}]/@style'.format(i+1))[0].split(' ')[-2].strip('px'))
            bg_location['y'] = int(selector.xpath(bg_xpath + '[{}]/@style'.format(i+1))[0].split(' ')[-1].strip('px;'))
            # 将位置信息字典加入位置信息列表中
            bg_location_list.append(bg_location)
            print(bg_location_list)
        # 遍历所有乱序完整图片
        for i in range(len(fullbg)):
            fullbg_location = {}
            fullbg_location['x'] = int(selector.xpath(fullbg_xpath + '[{}]/@style'.format(i+1))[0].split(' ')[-2].strip('px'))
            fullbg_location['y'] = int(selector.xpath(fullbg_xpath + '[{}]/@style'.format(i+1))[0].split(' ')[-1].strip('px;'))
            fullbg_location_list.append(fullbg_location)
            print(fullbg_location_list)
        # 创建图片目录
        self.mk_image_dir()
        # 将乱序的完整图片和缺口图片下载至本地目录Images中
        urlretrieve(url=bg_url, filename='Images/bg.jpg')
        print('缺口图片下载完成')
        urlretrieve(url=fullbg_url, filename='Images/fullbg.jpg')
        print('完整图片下载完成')
        return bg_location_list, fullbg_location_list

    def mk_image_dir(self):
        if not os.path.exists('Images'):
            os.mkdir('Images')


    def merge_images(self, filename, location_list):
        # 打开乱序图片(完整或缺口)
        img = Image.open(filename)
        # 创建一个新的图片, 以RGB模式, 宽度为260px, 高度为116px, 用来容纳复原后的图片
        new_img = Image.new('RGB', (260, 116))
        # 将图片分为上半部分和下半部分, 定义复原图片的上部分和下部分列表
        img_list_upper = []
        img_list_lower = []
        # 遍历乱序图片的位置信息(完整或缺口)
        for location in location_list:
            # 若‘y’：-58, 则为图片的上部分, 将其加入图片上部分列表, 该列表内的图片的顺序为复原后的顺序
            if location['y'] == -58:
                img_list_upper.append(img.crop((abs(location['x']), 58, abs(location['x'])+10, 116)))
            # 若‘y’：0,则为图片的下部分,将其加入图片下部分列表
            if location['y'] == 0:
                img_list_lower.append(img.crop((abs(location['x']), 0, abs(location['x'])+10, 58)))
        # 初始化复原图片的左位置值
        x_offset = 0
        # 将上部分图片列表中图片取出
        for img_upper in img_list_upper:
            # 将取出后的图片从左边位置0px开始粘贴至新创建的图片的上半部分,
            new_img.paste(img_upper, (x_offset, 0))
            # 累加图片宽度
            x_offset += img_upper.size[0]

        x_offset = 0
        for img_lower in img_list_lower:
            new_img.paste(img_lower, (x_offset, 58))
            x_offset += img_lower.size[0]
        # 将复原后的图片储存至本地Images目录
        new_img.save(filename.split('.')[0] + '1.jpg')
        return new_img

    def get_gap(self, img1, img2):
        # 初始滑块位置对应的需移动的验证码的右端的位置为60px, 从60px的右边区域开始比对复原图片的像素
        left = 60
        # 横坐标从60px至260px
        for i in range(left, img1.size[0]):
            # 纵坐标从0px至116px
            for j in range(img1.size[1]):
                # 若像素不同, 则返回该横坐标
                if not self.is_px_equal(img1, img2, i, j):
                    left = i
                    return left
        return left

    def is_px_equal(self, img1, img2, x, y):
        # 加载图片
        pix1 = img1.load()[x,y]
        pix2 = img2.load()[x,y]
        # 初始化像素比对的最大阈值
        threshold = 60
        # 若在R, G, B上的像素差都小于阈值, 则返回True
        if abs(pix1[0]-pix2[0]) < threshold and abs(pix1[1]-pix2[1]) < threshold and abs(pix1[2]-pix2[2]) < threshold:
            return True
        else:
            return False

    def get_slider(self):
        try:
            slider = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="gc-box"]/div/div[3]/div[2]')))
            return slider
        except TimeoutError:
            print('加载失败')

    def get_tracks(self, distance):
        tracks = []
        # 初始位置
        current = 0
        # 减速阈值
        mid = distance * 7 / 8
        # 每次移动0.2s时间的路程
        t = 0.2
        # 初始速度
        v = 0
        while current < distance:
            if current < mid:
                a = random.uniform(2, 5)
            else:
                a = -(random.uniform(12.5, 13.5))
            v0 = v
            v = v0 + a * t
            x = v0 * t + 1/2 * a * t**2
            current += x
            absx = current - distance
            if 0.6 < absx < 1:
                x = x - 0.53
                tracks.append(round(x, 2))
            elif 1 < absx < 1.5:
                x = x - 1.4
                tracks.append(round(x, 2))
            elif 1.5 < absx < 3:
                x = x - 1.8
                tracks.append(round(x, 2))
            else:
                tracks.append(round(x, 2))
        return tracks

    def move_to_gap(self, slider, tracks):
        action = ActionChains(self.browser)
        # 按住滑块
        action.click_and_hold(slider).perform()
        for x in tracks:
            # 按轨迹移动滑块
            action.move_by_offset(xoffset=x,yoffset=-1).perform()
            action = ActionChains(self.browser)
        time.sleep(0.6)
        # 释放滑块
        action.release().perform()

    def success(self):
        try:
            if re.findall('gt_success', self.browser.page_source, re.S):
                print('验证成功')
                return True
            else:
                print('验证失败')
                return False
        except TimeoutError:
            print('加载超时')

    def login(self):
        try:
            submit_xpath = '//*[@id="login-app"]/div/div[2]/div[3]/div[3]/div/div/ul/li[5]/a[1]'
            submit = self.browser.find_element_by_xpath(submit_xpath)
            submit.click()
            print('登录成功')
            time.sleep(20)
            self.browser.close()
            return True
        except:
            print('登录失败')
            return False

    def input(self):
        # 获取账号输入框对象
        account = self.wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
        # 获取密码输入框对象
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
        # 输入账号
        account.send_keys(self.account)
        time.sleep(2)
        # 输入密码
        password.send_keys(self.password)

if __name__ == '__main__':
    try:
        while True:
            crack = CrackGeetest()
            # 打开登录页面
            crack.browser.get(crack.url)
            # 输入账号密码
            crack.input()
            time.sleep(2)
            # 抓取乱序验证码图片位置参数, 并将完整验证码和缺口验证码图片下载至本地
            bg_location_list, fullbg_location_list = crack.get_geetest_image_location()
            # 重组乱序验证码图片, 恢复至原验证码图片
            img1 = crack.merge_images('Images/fullbg.jpg', fullbg_location_list)
            img2 = crack.merge_images('Images/bg.jpg', bg_location_list)
            # 计算滑块与缺口之间的横向距离, 并取一定裕量
            distance = crack.get_gap(img1, img2) * 1.138
            distance -= border
            # 获取滑块对象
            slider = crack.get_slider()
            # 模拟人手操作滑块的运动轨迹
            tracks = crack.get_tracks(distance)
            # 将滑块拖至缺口处
            crack.move_to_gap(slider, tracks)
            time.sleep(0.5)
            SUCCESS = crack.success()
            if SUCCESS and crack.login():
                break
    except Exception:
        print('程序出错')