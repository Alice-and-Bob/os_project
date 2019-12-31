# 1、磁盘管理
# 建立一个4KB大小的文件模拟磁盘，按逻辑将其划分为1024块，每块大小4B。其中900块用于存放普通数据，124块用于存储兑换数据。
# 存储管理需要支持：
# DONE:（1）数据组织：对需要存放的文件数据加以组织管理显式连接（FAT）方式
# DONE:（2）空闲块管理：能够查询并返回当前剩余的空闲块，对空闲块管理可以采用FAT
# DONE:（3）兑换区管理：能够写入、读出兑换区数据。


free_blocks = 1024  # int型变量，用于指出当前磁盘上共有多少块空闲，初始应为1024块
swapping_start = 900  # int型变量，用于标明对换区起始盘块号

# 初始化一个虚拟磁盘，写1024*4字节
Disk = open("disk.image", mode='ab')
for i in range(0, 1024 * 4):
    Disk.write(b'\x00')

FAT = []  # FAT表，一个一维数组，下标范围为[0,1023]
"""
    FAT表项状态：
        -1 初始化未用
        -2 文件末尾
        others 正常表示块地址
"""
for i in range(0, 1024):  # 初始化FAT表，默认表项为-1即不可用
    FAT.append(-1)


def swapping_area_write(point, data):
    """
    对换区写操作，每次写一个块，4B
    :param data: bytes类型，要写入的4B数据内容
    :param point:写指针
    :return:NULL
    """
    pass


def swapping_area_read(point):
    """
    对换区读操作，每次读一个块，4B
    :param point:读指针
    :return: bytes(data)，根据指针读出的字节型的4B
    """
    pass


def malloc_free_blocks(block_number):
    """
    用于分配当前磁盘上空闲的块，并维护free_block，以实时反映当前空闲块数量
    :param block_number: 调用者想要得到的空闲块的数量，范围应在[1,free_blocks]之内
    :return: 返回一个list，内容是一列范围在[0,1023]的数字，即块号；若没有足够空闲块分配，则返回-1表示无空闲空间
    """
    pass


def free_block_manage():
    """
    用于管理当前磁盘上空闲的块，可以查询并返回当前的空闲块块号
    :return: list(free_blocks)；块号序列
    """