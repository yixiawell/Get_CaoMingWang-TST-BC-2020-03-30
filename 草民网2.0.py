import requests, os, re,concurrent.futures, merge_ts
from bs4 import BeautifulSoup
from urllib import parse

headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36"
        }
class CaoMingWang():
    def __init__(self):
        self.index_name = None  # 视频名称


    def get_post(self, movie_name):
        post_url = "https://www.cmdy5.com/index.php?m=vod-search"
        data = {
            "wd": "{}".format(movie_name)
        }
        req = requests.post(url=post_url, data=data, headers=headers)
        soup = BeautifulSoup(req.text, "lxml")
        titles = soup.select(".link-hover")
        xuanzhe = ["{}.{}".format(i, titles[i]["title"]) for i in range(len(titles))]
        if not xuanzhe:
            print("对不起，您搜索的视频未上架！！！")
            exit()
            return None
        for x in xuanzhe:
            print(x)
        xuhao = input("请输入需要查看的电视剧序号：")
        shiping_url = "https://www.cmdy5.com{}".format(titles[int(xuhao)]["href"])
        self.index_name = titles[int(xuhao)]["title"]
        if not os.path.exists(r".\2\{}".format(self.index_name)):
            os.mkdir(r".\2\{}".format(self.index_name))
        self.get_episodes(shiping_url)

    def get_html(self, url):
        req = requests.get(url,headers=headers,verify=False,timeout=20)
        return req

    def get_episodes(self,url):
        '''
        :param url: move_url
        :return: 每一集的url以及每集url对应的集数
        '''
        if os.path.exists(r".\2\{}\vido_dir.txt".format(self.index_name)):
            return 1
        html = self.get_html(url).text
        soup = BeautifulSoup(html, "lxml")
        episodes_urls_names = soup.select("#vlink_1 ul li a")
        episodes_urls = [i["href"] for i in episodes_urls_names]
        html = self.get_html(episodes_urls[0]).text
        soup = BeautifulSoup(html,"lxml")
        episodes_urls = soup.select(".player.mb .main script")[0]["src"]
        episodes_urls = "https://www.cmdy5.com{}".format(episodes_urls)
        episodes_urls = self.get_html(episodes_urls).text
        jishu_url_list = episodes_urls.split("%u7")
        episodess_urls = []
        episodess_names = []
        for jishu_url_one in jishu_url_list[1:len(jishu_url_list) - 1]:
            j = parse.unquote(jishu_url_one)
            jishu_com = re.compile(r"b2c(\d{2})%u9")
            jishu = "第{}集".format(jishu_com.findall(j)[0])
            url_com = re.compile(r"(http.*?)\W+$")
            url = parse.unquote(url_com.findall(j)[0])
            if jishu not in episodess_names:
                episodess_urls.append(url)
                episodess_names.append(jishu)

        sl = episodes_urls[episodes_urls.rfind("b2c"):len(episodes_urls) - 3]
        sl = parse.unquote(sl)
        jishu_com = re.compile(r"b2c(\d{2})%u96c6")
        try:
            jishu = "第{}集".format(jishu_com.findall(sl)[0])
        except:
            jishu = "第01集"
        url = sl[sl.rfind("http"):]
        if jishu not in episodess_names:
            episodess_urls.append(url)
            episodess_names.append(jishu)

        episodess_list = zip(episodess_urls,episodess_names)
        if not os.path.exists(r".\2\{}".format(self.index_name)):
            os.mkdir(r".\2\{}".format(self.index_name))
        with open(r".\2\{}\vido_dir.txt".format(self.index_name), "w+") as f:
            for e in episodess_list:
                x = ",".join(e)
                f.write(x)
                f.write("\n")
        return 1

class SetNumber(CaoMingWang):
    def __init__(self):
        self.m3u8_url = None
        self.index_url = None  # 视频主机url
        self.set_number = None  # 视频集数

    def get_m3u8url(self, url, set_number):
        '''
        :param url:每一集的url
        :return: None
        '''
        self.set_number = set_number
        if url.find("m3u8") > -1:
            print("你好")
            self.get_m3u8txt(url)
            return None
        html = self.get_html(url).text
        compile_m3u8url = re.compile(r"'(.*?m3u8)'")
        m3u8url = compile_m3u8url.findall(html)
        # print(m3u8url)
        #判断能否通过正则获取m3u8地址
        if len(m3u8url) > 0:
            m3u8url = m3u8url[0]
        else:
            compile_m3u8url = re.compile(r'"(.*?m3u8.*?)"')
            m3u8url = compile_m3u8url.findall(html)
            print(m3u8url)
            if len(m3u8url) > 0:
                m3u8url = m3u8url[0]
            else:
                print("无法获取m3u8url地址，程序即将退出。。。")
                exit()
                return None
        #判断m3u8url中是否包含http，如果有提取index_url备用
        if m3u8url.find("http") > -1:
            compile_indexurl = re.compile(r"(http.*?//.*?/)")
            self.index_url = compile_indexurl.findall(m3u8url)
            if len(self.index_url) > 0:
                self.index_url = self.index_url[0]
            else:
                print("主机名未知无法请求，系统将退出。。。")
                exit()
                return None
        else:
            compile_url = re.compile(r"(http.*?com)")
            indexurl = compile_url.findall(url)[0]
            m3u8url = parse.urljoin(indexurl, m3u8url)
            compile_indexurl = re.compile(r"(http.*?/)index")
            self.index_url = compile_indexurl.findall(m3u8url)
            if len(self.index_url) > 0:
                self.index_url = self.index_url[0]
        print("m3u8url", m3u8url)
        self.get_m3u8txt(m3u8url)

    def get_m3u8txt(self,url):
        '''
        :param url: m3u8地址
        :return: 生成m3u8txt文件
        '''
        # self.m3u8_url = url
        self.index_url = url[:url.find("/", 10)]
        if os.path.exists(r".\2\{}\{}\{}.m3u8".format(self.index_name, self.set_number,self.set_number)):
            path = r".\2\{}\{}".format(self.index_name, self.set_number)
            self.get_ts_txt(path)
            return None
        html = self.get_html(url).text
        #判断m3u8是否需要重定向
        if html.find("m3u8") > -1:
            self.index_url = url[:url.find("index")]
            print(self.index_url)
            compile_m3u8url2 = re.compile(r"(.*?m3u8)")
            m3u8url2 = compile_m3u8url2.findall(html)
            print(self.index_url)
            if len(m3u8url2) > 0:
                m3u8url2 = parse.urljoin(self.index_url, m3u8url2[0])
                self.index_url = m3u8url2[:m3u8url2.rfind("index")]
                html = self.get_html(m3u8url2).text
        #判断文件夹是否存在，若不存在自动增加
        if not os.path.exists(r".\2\{}".format(self.index_name)):
            os.mkdir(r".\2\{}".format(self.index_name))
        if not os.path.exists(r".\2\{}\{}".format(self.index_name, self.set_number)):
            os.mkdir(r".\2\{}\{}".format(self.index_name, self.set_number))
        with open(r".\2\{}\{}\{}.m3u8".format(self.index_name, self.set_number,self.set_number), "w+") as f:
            f.write(html)
        path = r".\2\{}\{}".format(self.index_name, self.set_number)
        self.get_ts_txt(path)
        return None

    def get_ts_txt(self,path):
        paths = os.path.join(path, "{}.m3u8".format(self.set_number))
        if not os.path.exists(paths):
            print("指定路径不存在，系统即将退出")
            exit()
        with open(paths, "r+") as f:
            ts_txt = f.readlines()
        ts_urllist = []
        ts_namelist = [i for i in ts_txt if i.find("#") == -1]
        ts_name = []
        #拼接m3u8url时判断m3u8是否存在”/“
        for t in ts_namelist:
            if t.find("/") > -1:
                t1 = t[t.rfind("/") + 1:]
                ts_name.append(t1)
            else:
                ts_name.append(t)
            if t.find("http") > -1:
                self.m3u8_url = t[:t.rfind("/")+1]
        if not self.m3u8_url:
            self.m3u8_url = self.index_url
        ts_urllist = [parse.urljoin(self.m3u8_url, i).replace("\n", "") for i in ts_txt if i.find("#") == -1]

        for num9 in range(3):
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as thread:
                fun1 = [thread.submit(self.get_ts_vido, ts_urllist[t].replace("\n",""),ts_name[t].replace("\n",""),path) for t in range(len(ts_urllist))]
        merge_ts.merge_ts(path)

    def get_ts_vido(self, url, name, path):
        '''
        :param url: ts_url
        :param name: 每个ts文件的文件名
        :return:
        '''
        
        if name.find("/") > -1:
            name = name[name.rfind("/") + 1:]
        print("正在下载{}".format(name))
        url = url.strip().replace("\n", "")
        print(url)
        a = os.path.join(path, name)
        if not os.path.exists(a):
            html = self.get_html(url).content
            with open(a, "wb+") as f:
                f.write(html)
            print("{}已下载完成".format(name))
        else:
            print("该{}文件已存在，无需下载。。。".format(name))
            return None













def main():
    movie = SetNumber()
    movie_name = input("请输入需要查找的影片：")
    movie_url = movie.get_post(movie_name)
    if not os.path.exists(r".\2"):
        os.mkdir(r".\2")
    if movie_name:
        a = input("以获取视频列表是否开始下载：（是/否）")
        if a == "是":
            if not os.path.exists(r".\2\{}\vido_dir.txt".format(movie.index_name)):
                print("视频地址不存在，请重新获取")
                exit()
            with open(r".\2\{}\vido_dir.txt".format(movie.index_name), "r+") as f:
                vido_dir = f.readlines()
            download_number = len(os.listdir(r".\2\{}".format(movie.index_name))) - 1
            sum_number = len(vido_dir)
            last_number = os.listdir(r".\2\{}".format(movie.index_name))[-1]
            vido_dir = [i.split(",") for i in vido_dir]
            print("已下载了{}集，最后下载的集数为：{}，该视频共有{}集，剩余{}集未下载".format(download_number,last_number,sum_number,sum_number-download_number))
            startnumb = int(input("请输入开始下载的集数:"))
            downloadnumber = int(input("请输入下载几集"))
            for v in vido_dir[startnumb - 1:startnumb - 1 + downloadnumber]:
                movie.get_m3u8url(v[0], v[1].replace("\n", ""))
            print("已下载完成")



if __name__ == '__main__':
    main()
