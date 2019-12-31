class FcbBlock:
    """
    文件控制块，在实例化时应初始化为一个数组
    """
    filename = ""  # 文件名
    file_dir = ""  # 文件路径
    start_point = -1  # 文件第一个起始块的物理块号

    is_occupied = 0  # 标明本FCB是否被占用；默认为0未被占用

    def occupy(self, filename, file_dir, start_point, is_occupied):
        """
        在要占用一个FCB时进行初始化
        :param filename:
        :param file_dir:
        :param start_point:
        :param is_occupied:
        :return: NULL
        """
        self.filename = filename
        self.file_dir = file_dir
        self.start_point = start_point
        self.is_occupied = is_occupied

    def delete(self):
        """
        回收FCB，全部属性初始化
        :return: NULL
        """
        filename = ""  # 文件名
        file_dir = ""  # 文件路径
        start_point = -1  # 文件第一个起始块的物理块号
        is_occupied = 0  # 标明本FCB是否被占用；默认为0未被占用


# 初始化一个FCB表，大小为1024，下标为[0,1023]
FCB = []
for i in range(0, 1024):
    a = FcbBlock()
    FCB.append(a)


def delete(filename, file_dir):
    """
    删除功能，用于删除数据；根据FCB表的状态判断某文件是否在内存中，若在内存则拒绝删除操作否则根据文件名删除文件并做好提示
    :param filename: 
    :return:可以安全删除：1
            因为在内存中而不可以删除：0
            因为未找到文件名对应的文件而无法删除：-1
    """
    pass
