import re, os , shutil

PATH = "/Users/Stu/Library/Application Support/Kodi/"
LIST = "/Users/Stu/Documents/PyLearn/filelist.txt"
SRCE = ""
DEST = "KodiBuildBackup/"

#FILE = "userdata/profiles/addon_data/plugin.audio.mp3streams/downloads.list"

dst = PATH + DEST
src = PATH + SRCE

with open(LIST, 'r') as fread:
    for line in fread:
        match = re.search(r'userdata',line)
        if match:
            loc = line.split('"')
            dst_file_path = dst + line.rstrip('\n')
            (root, file_name) = os.path.splitext(dst_file_path)
            head, tail = os.path.split(dst_file_path)
            if not os.path.exists(head):
                os.makedirs(head)
            src_file_path = src + line.rstrip('\n')
            shutil.copyfile(src_file_path, dst_file_path)
