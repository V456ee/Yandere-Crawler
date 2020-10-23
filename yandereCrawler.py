import requests
from bs4 import BeautifulSoup
import multiprocessing
import json
import os


def mainfunc():
    cpu_count = multiprocessing.cpu_count()
    print('您的CPU核心数为：{0}\n本程序将启用{0}个异步进程抓取图片'.format(cpu_count))
    # 调用用户输入
    page_range_tag = pageinput()
    #读取起止页，tag
    start_page = page_range_tag[0]
    end_page = page_range_tag[1]
    tag = page_range_tag[2]
    print('正在读取所有链接...')
    p = multiprocessing.Pool()
    #整理参数
    page_with_tag = []
    for page in range(start_page, end_page):
        page_add = (page, tag)
        page_with_tag.append(page_add)
    #解析所有图片详情页链接
    imgpage_lists = p.map(showlink_crawler, page_with_tag)
    #解压嵌套列表
    imgpagelist = listextender(imgpage_lists)
    if len(imgpagelist):
        print('已成功读取所有图片页面链接：\n', imgpagelist)
        savepath = savepath_wr()
        #路径不存在时创建新文件夹
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        custom(savepath)
        for imglink in imgpagelist:
            p.apply_async(downloader, (savepath, imglink))
        p.close()
        p.join()
        print('下载已全部完成！')
        continue_ask = input('是否继续？[y/n]:')
        if continue_ask == 'y' or 'Y':
            mainfunc()
        else:
            exit()
    #列表为空==当前tag无结果
    else:
        print('未能搜索到任何图片，请尝试更换TAG')
        mainfunc()


def savepath_wr():
    try:
        with open('usrconfig.json', 'r') as config:
            saveconfig = json.load(config)
        savepath = saveconfig['SavePath']
        save_ask = input('检测到上次保存配置为\n{}\n如无需更改请输入“y”，或输入新的保存位置：'.format(savepath))
        if save_ask == 'y' or 'Y':
            return savepath
        else:    #将新路径存入配置文件
            save_ask = save_ask+'\\'
            save_ask = save_ask.replace('\\', '/')
            savepath_config = {'SavePath': save_ask+'\\'}
            with open('usrconfig.json', 'w') as config:
                json.dump(savepath_config, config)
            return savepath
    except FileNotFoundError:
        savepath = input('未检测到配置文件，请输入保存位置：')+'\\'
        savepath = savepath.replace('\\', '/')
        savepath_config = {'SavePath': savepath}
        with open('usrconfig.json', 'w') as config:
            json.dump(savepath_config, config)
        return savepath



def pageinput():
    try:
        tag = input('输入你希望下载的图片tag(选填):')
        tag = tag.replace(" ", "_")
        print(tag)
        start_page = input('输入你希望下载的起始页码(默认为1):')
        if start_page == '':
            start_page = 1
        else:
            start_page = int(start_page)
        end_page = input('输入你希望下载的最终页码:')
        end_page = int(end_page) + 1
        if start_page != 0 and start_page < end_page:
            return start_page, end_page, tag
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
    if usercus == 'y' or 'Y':
        with open(savepath + 'log.json', 'w', encoding='utf-8')as logtext:
            logtext.writelines('*********************Download Log*********************\n')
    else:
        pass


def downloader(savepath, imglink):
    link = link_resolver(imglink).get('href')
    imgnm = imglink.strip('https://yande.re/post/show/') + link[-4:]
    try:
        #用于下载过图片后被手动删除的情况，如为误删可先清空log以重下
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


def showlink_crawler(page_range):
    page = page_range[0]
    tag = page_range[1]
    url = "https://yande.re/post?page={0}&tags={1}".format(page, tag)
    print(url)
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
        i=0
        while i < 3:
            try:
                pic = requests.get(link, timeout=(30, 600))
                i = 3
            except requests.exceptions.RequestException as timeout_err:
                print(timeout_err)
                i += 1
        with open(filepath, 'wb') as fp:
            fp.write(pic.content)
            print('图片已成功保存至{}'.format(filepath))


if __name__ == '__main__':
    multiprocessing.freeze_support()
    mainfunc()
