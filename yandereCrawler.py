import requests
from bs4 import BeautifulSoup
import multiprocessing


def mainfunc():
    x = int(input('输入页数:'))
    print('正在读取所有链接...')
    imgpagelists = pagerunner(x)
    imgpagelist = listextender(imgpagelists)
    print('已成功读取所有图片页面链接：\n', imgpagelist)
    savepath = input('输入保存路径开始下载:')+'\\'
    p = multiprocessing.Pool(processes=6)
    for imglink in imgpagelist:
        p.apply_async(downloader, (savepath, imglink))
    p.close()
    p.join()
    print('下载已全部完成！')
    contn = input('是否继续？[y/n]:')
    if contn == 'y':
        mainfunc()
    else:
        exit()


def downloader(savepath, imglink):
    link = link_resolver(imglink).get('href')
    filepath = savepath + imglink.strip('https://yande.re/post/show/') + link[-4:]
    file_saver(link, filepath)


def pagerunner(x):
    imgpagelists = []
    for a in range(x):
        imgpagelists.append(showlink_crawler(a))
    return imgpagelists


def listextender(pagelists):
    imgpagelist = []
    for lists in pagelists:
        for l in lists:
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
    print('图片文件' + link.strip('https:'), '正在保存至：' + filepath + '...')
    try:
        with open(filepath):
            print('当前图片重复，不保存')
    except FileNotFoundError:
        pic = requests.get(link, timeout=30)
        with open(filepath, 'wb') as fp:
            fp.write(pic.content)
            print('图片已成功保存至{}'.format(filepath))


if __name__ == '__main__':
    multiprocessing.freeze_support()
    mainfunc()
