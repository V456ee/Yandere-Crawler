import requests
from bs4 import BeautifulSoup
import multiprocessing


def mainfunc():
    print('您的CPU核心数为：{0}\n本程序将启用{0}个异步进程抓取图片'.format(multiprocessing.cpu_count()))
    xy = pageinput()
    x = xy[0]
    y = xy[1]
    print('正在读取所有链接...')
    p = multiprocessing.Pool()
    imgpagelists = p.map(showlink_crawler, range(x, y))
    imgpagelist = listextender(imgpagelists)
    print('已成功读取所有图片页面链接：\n', imgpagelist)
    savepath = input('输入保存路径开始下载:')+'\\'
    custom(savepath)
    for imglink in imgpagelist:
        p.apply_async(downloader, (savepath, imglink,))
    p.close()
    p.join()
    print('下载已全部完成！')
    contn = input('是否继续？[y/n]:')
    if contn == 'y':
        mainfunc()
    else:
        exit()


def pageinput():
    try:
        x = input('输入你希望下载的起始页码(默认为1):')
        if x == '':
            x = 1
        else:
            x = int(x)
        y = input('输入你希望下载的最终页码:')
        y = int(y) + 1
        if x != 0 and x < y:
            return x, y
        else:
            print('您的输入有误，请输入半角数字，并确保起始页码不为零且小于最终页码！')
            pageinput()
    except ValueError:
        print('您的输入有误，请输入半角数字，并确保起始页码不为零且小于最终页码！')
        pageinput()


def custom(savepath):
    usercus = input(
        '在开始下载前是否需要清空log文件？如果您首次使用可任意选择，否则可能导致重复下载。\n'
        '请输入y或n进行选择(y:是，n:否):')
    if usercus == 'y':
        with open(savepath + 'log.json', 'w', encoding='utf-8')as logtext:
            logtext.writelines('*********************Download Log*********************\n')
    else:
        pass


def downloader(savepath, imglink):
    link = link_resolver(imglink).get('href')
    imgnm = imglink.strip('https://yande.re/post/show/') + link[-4:]
    try:
        with open(savepath + 'log.json', 'r', encoding='utf-8')as logread:
            logs = logread.readlines()
        if imgnm + '\n' in logs:
            print('图片{}已有下载记录，不再下载'.format(imgnm))
        else:
            with open(savepath + 'log.json', 'a', encoding='utf-8')as logwrite:
                logwrite.writelines(imgnm + '\n')
            filepath = savepath + imgnm
            file_saver(link, filepath)
    except FileNotFoundError:
        with open(savepath + 'log.json', 'w', encoding='utf-8')as logtext:
            logtext.write('*********************Download Log*********************\n')
            print('未找到log文件，已在保存路径下创建新的log文件')
        downloader(savepath, imglink)


def listextender(pagelists):
    imgpagelist = []
    for lis in pagelists:
        for l in lis:
            imgpagelist.append(l)
    return imgpagelist


def showlink_crawler(a):
    url = "https://yande.re/post?page={}".format(a)
    data = requests.get(url, headers=
                        {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0"}
                        )
    soup = BeautifulSoup(data.text, 'lxml')
    images = soup.select('#post-list-posts > li > div.inner > a.thumb')
    imgpages = ['https://yande.re'+img.get('href') for img in images]
    return imgpages


def link_resolver(i):
        imglink = requests.get(
            i, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0"}
        )
        isoup = BeautifulSoup(imglink.text, 'lxml')
        if len(isoup.select('#png')) != 0:
            links = isoup.select('#png')
        else:
            links = isoup.select('#highres')
        return links[0]


def file_saver(link, filepath):
    print('正在保存图片文件' + link.strip('https:'), '至：' + filepath + '...')
    try:
        with open(filepath):
            print('当前图片已存在，不保存')
    except FileNotFoundError:
        pic = requests.get(link, timeout=30)
        with open(filepath, 'wb') as fp:
            fp.write(pic.content)
            print('图片已成功保存至{}'.format(filepath))


if __name__ == '__main__':
    multiprocessing.freeze_support()
    mainfunc()
