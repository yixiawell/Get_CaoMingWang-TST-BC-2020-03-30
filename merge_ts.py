import os, re


def merge_ts(path):
    file_list = os.listdir(path)
    comp_filename = re.compile("(.*?m3u8)$")
    file_name = [i for i in file_list if comp_filename.findall(i)]
    if file_name:
        num = 0
        book = open(path + "\\" + file_name[0].replace("m3u8", "mp4"), "wb+")
        with open(path + "\\" + file_name[0], "r+") as f:
            m3u8_list = f.readlines()
        m3u8_list = [i.replace("\n", "") for i in m3u8_list if i.find("#")]
        m3u8_name = [i[i.rfind("/") + 1:] for i in m3u8_list]
        for name in m3u8_name:
            print(name)
            try:
                with open(path + "\\" + name, "rb+") as f:
                    a = f.read()
                book.write(a)
                os.remove(path + "\\" + name)
            except:
                with open(path + "\\未合并.txt", "a+") as f:
                    f.write(name)
                    f.write("\n")
                num += 1
                continue
        book.close()
        print("合并已完成，文件名为:{},共处理{}个文件,未成功处理{}个文件".format(file_name[0].replace("m3u8", "mp4"), len(m3u8_name), num))
    else:
        print("对不起，该目录不存在m3u8文件，无法合并")

if __name__ == '__main__':
    while True:
        path = input("请输入需要合并文件的绝对路径：")
        merge_ts(path)
