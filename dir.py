# 2、目录管理
# 为写入模拟磁盘的数据文件建立目录，目录可以是单级文件目录、双级文件目录、树形结构目录。在目录中选择某个文件可以将其数据读入模拟内存。
# 目录中包含文件名、文件所有者、创建时间、文件结构、在磁盘中存放的地址等信息。目录管理需要支持：
# DONE:（1）新建目录：在目录中新建空目录
# DONE:（2）删除目录：删除空目录
# DONE:（3）为文件建立目录项：一个文件被创建后，为该文件创建目录项，并将文件相关信息写入目录中。
# DONE:（4）删除文件：删除目录中某个文件，删除其在磁盘中的数据，并删除目录项。如果被删除文件已经读入内存应该阻止删除，完成基本的文件保护。

import disk


class FcbBlock:
    """
    文件控制块，在实例化时应初始化为一个数组
    """
    filename = ""  # 文件名
    file_dir = ""  # 文件路径
    start_point = -1  # 文件第一个起始块的物理块号
    # file_size = 0  # 文件大小，以字节为计
    is_occupied = 0  # 标明本FCB是否被占用；默认为0未被占用

    def occupy(self, filename, file_dir, start_point, file_size, is_occupied):
        """
        在要占用一个FCB时进行初始化
        :param file_size:
        :param filename:
        :param file_dir:
        :param start_point:
        :param is_occupied:
        :return: NULL
        """
        self.filename = filename
        self.file_dir = file_dir
        self.start_point = start_point
        # self.file_size = file_size
        self.is_occupied = is_occupied

        # disk.number_of_free_blocks -= 1 + file_size // 4  # 目前的空闲块数减去要占用的块数

    def delete(self):
        """
        回收FCB，全部属性初始化
        :return: NULL
        """
        self.filename = ""  # 文件名
        self.file_dir = ""  # 文件路径
        self.start_point = -1  # 文件第一个起始块的物理块号
        # self.file_size = 0  # 文件大小，以字节为计
        self.is_occupied = 0  # 标明本FCB是否被占用；默认为0未被占用


# 初始化一个FCB表，大小为1024，下标为[0,1023]
FCB = []
for i in range(0, 1024):
    a = FcbBlock()
    FCB.append(a)

# 二级文件目录
dir = {}


def new_dir(dir_name):
    """
    新建一个目录，放在dir的统一管理下
    :param dir_name:新建的目录名；str
    :return: NULL
    """
    # dir_item = {'dir_name': ["filename1", "filename2", "filename3"]}
    dir[str(dir_name)] = []


def delete_dir(dir_name):
    """
    删除一个空的目录，非空目录经确认后可以强制删除
    :param dir_name: 要删除的空目录名；str
    :return: NULL
    """
    if dir[dir_name] is []:
        dir.pop(dir_name)
    else:
        flag = input("要删除的目录非空，继续？y/n")
        if flag is ('y' or 'Y'):
            dir.pop(dir_name)
        else:
            print("取消删除操作")


def file_to_dir(filename, file_dir):
    """
    根据给定的文件名和文件目录将文件归档到目录中，在目录中记录下文件信息
    :param filename:
    :param file_dir:
    :return:NULL
    """
    try:
        dir[file_dir].append(filename)
    except KeyError:
        print("没有该文件目录，将自动创建目录")
        dir[file_dir] = [filename]


def delete_file(filename, file_dir):
    """
    删除功能，用于删除数据；根据FCB表的状态判断某文件是否在内存中，若在内存则拒绝删除操作否则根据文件名删除文件并做好提示
    :param file_dir:
    :param filename:
    :return:可以安全删除：1
            因为在内存中而不可以删除：0
            因为未找到文件名对应的文件而无法删除：-1
    """
    for fcb_item in FCB:
        if (fcb_item.filename is filename) and (fcb_item.file_dir is file_dir):  # 目标路径下的文件存在
            if fcb_item.is_occupied:  # 在内存
                # print("要删除的文件在内存中")
                return 0
            else:  # 存在且不在内存
                return 1
        else:
            return -1
