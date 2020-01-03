# 4、线程管理
# 本虚拟系统以线程为基本运行单位，线程本身采用编程语言提供的线程机制，不模拟。系统主要包括的线程有：
# DONE:（1）数据生成线程：该线程负责生成外存数据，给定数据大小（按字节计算）、数据信息（英文字母）、存储目录、文件名后，该线程调用磁盘管理中空闲磁盘管理功能，申请所需大小的外存块，如果盘块不够给出提示。按照要求的数据组织方式，将数据存入磁盘块（按块分配磁盘），并调用目录管理功能为其在目录中建立目录项，更改空闲盘块信息。
# DONE:（2）删除数据线程：该线程调用删除目录管理中文件删除功能删除数据（内存中文件不能删除）。并回收外存空间，更新空闲盘块信息。
# DONE:（3）执行线程：选择目录中的文件，执行线程将文件数据从外存调入内存，为此，首先需要调用内存管理的空闲空间管理功能，为该进程申请4块空闲内存，如果没有足够内存则给出提示，然后根据目录中文件存储信息将文件数据从外存读入内存，此间如果4块内存不够存放文件信息，需要进行换页（选择的换页策略见分组要求），欢出的页面存放到磁盘兑换区。允许同时运行多个执行线程。文件数据在内存块的分布通过线程的页表（模拟）进行记录。
# DONE:（4）线程互斥：对于64B的内存，线程需要互斥访问，避免产生死锁。不能访问内存的线程阻塞，等待被唤醒。

import threading
import disk
import dir
import ram


# FIXED：在根据文件名从FCB中查找时，没有考虑到文件重名的冲突；
# FIXED：考虑在所有涉及FCB查找的代码中添加对文件路径的判断；只有文件路径和文件名全部一致时，才允许访问对应FCB
# FIXED:所有调用ram模块里方法的代码都在临界区，要先获取锁才能调用ram模块方法

# 数据生成线程
def data_generator(data_size_i, data_content_i, file_dir_i, filename_i):
    """
    根据参数将数据写入磁盘，调用目录管理给出文件目录
    :param data_size_i:数据大小，以字节为单位计算；int
    :param data_content_i:数据信息，英文字符；str
    :param file_dir_i:要存储的目录；str
    :param filename_i:文件名；str
    :return:成功返回1，否则返回0
    """

    data_size = int(data_size_i)
    data_content = data_content_i
    file_dir = str(file_dir_i)
    filename = str(filename_i)

    try:
        free_list = disk.malloc_free_blocks(data_size)
        if free_list is -1:
            # 没有足够空闲空间
            raise BufferError
        else:  # 正常执行
            # 写FCB块
            for item in dir.FCB:
                if item.is_occupied is 0:  # 第一个未被占用的FCB块
                    item.occupy(is_occupied=1, filename=filename, file_dir=file_dir, start_point=disk.FAT[0])
                    break

            # 写目录文件
            dir.file_to_dir(filename=filename, file_dir=file_dir)

            # 按偏移量写文件到disk.image
            with open("disk.image", mode="ab+", encoding='utf-8') as disk_image:
                a = 0
                i = 0
                for p in free_list:
                    disk_image.seek(p * 4)
                    if a + 4 * i < len(data_content):
                        disk_image.write(data_content[a:a + 4 * i].encode(encoding='ascii'))
                    else:
                        disk_image.write(data_content[a:len(data_content)].encode(encoding='ascii'))
                        # disk_image.write((4 - len(data_content) + a) * b'\xff')  # 不足4B进行补齐

                    a = a + 4 * i
                    i = i + 1

            # FIXME: 数组下标可能错误
            # 更新FAT表
            for i in range(0, len(free_list)):
                disk.FAT[free_list[i]] = free_list[i + 1]
            disk.FAT[1 + len(free_list)] = -2  # 文件末尾

            return 1

    except BufferError:
        print("没有足够磁盘空间可用，或是其他未知错误")
        return 0


# 删除数据线程
def data_delete(file_dir_i, filename_i):
    """
    按给出的文件名删除磁盘上的文件，并负责回收外存空间和更新空闲盘块信息
    :param file_dir_i: 文件路径；str
    :param filename_i: 文件名；str
    :return:成功删除返回：1
            删除失败返回：0
    """
    filename = str(filename_i)
    file_dir = str(file_dir_i)

    # DONE：调用目录管理文件删除
    try:
        if_done = dir.delete_file(filename=filename, file_dir=file_dir)
        if if_done is -1:  # 文件未找到
            raise FileNotFoundError
        elif if_done is 0:  # 文件已在内存
            raise FileExistsError
        else:
            # 正常删除
            pass
    except FileNotFoundError:
        print("未在磁盘上找到该文件")
        return 0
    except FileExistsError:
        print("该文件已调入内存无法删除")
        return 0

    # DONE：回收外存空间,更新空闲盘块信息
    # 根据文件名找到FCB位置
    point = 0
    for item in dir.FCB:
        if (item.file_dir is file_dir) and (item.filename is filename):
            point = item.start_point
            item.delete()
            break

    # DONE:更新目录文件内容
    for item in dir.FCB[file_dir]:
        if item is filename:
            dir.FCB[file_dir].remove(filename)

    # DONE：回收磁盘空间,初始化数据到disk.image
    # 按偏移量写文件到disk.image
    with open("disk.image", mode="ab+", encoding='utf-8') as disk_image:
        back_blocks = 0
        while disk.FAT[point] is not -2:
            # 写空白数据
            disk_image.seek(point * 4)
            disk_image.write(b'\x00\x00\x00\x00')
            # 初始化FAT内容
            temp = point
            point = disk.FAT[point]
            disk.FAT[temp] = -1
            # 占用的块数
        # 初始化文件尾
        disk.FAT[point] = -1
        disk_image.seek(point * 4)
        disk_image.write(b'\x00\x00\x00\x00')

    return 1


def thread_start():
    """
    本模块开始的函数，调用该函数将执行多线程并发的执行线程功能
    :return:NULL
    """
    n = int(input("输入要调入文件个数"))
    filenames = []
    file_dirs = []
    for i in range(0, n):
        filename = input("输入第" + str(n + 1) + "个文件名")
        filenames.append(filename)
        file_dir = input("输入第" + str(n + 1) + "个文件目录")
        file_dirs.append(file_dir)

    thread_list = []  # 建立n线程的线程队列
    for i in range(0, n):
        thread_item = ExecThread(filename_i=filenames[i], file_dir_i=file_dirs[i])
        thread_list.append(thread_item)

    for item in thread_list:
        item.join()
        item.start()


# DONE：考虑执行线程类的实例化和并发调用执行
class ExecThread(threading.Thread):
    def __init__(self, file_dir_i, filename_i):
        """
        初始化类，提供文件名和文件路径参数
        :param file_dir_i: 文件路径；str
        :param filename_i: 文件名；str
        """
        threading.Thread.__init__(self)
        self.file_dir = str(file_dir_i)
        self.filename = str(filename_i)
        # 页表
        self.page_table = []
        for i in range(0, 4):
            item = -1
            self.page_table.append(item)

    def run(self):
        """
        主要的执行线程，执行从磁盘掉数据进入内存的功能，可以并发执行；
        :return:
        """
        # ----------------进入临界区---------------
        # 申请4块内存
        with ram.lock.acquire():
            free_block = ram.malloc_free_block()
        # ----------------退出临界区---------------

        if free_block is -1:
            # 没有空闲块可以分配
            print("没有空闲块可以分配")
            return 0
        else:
            # 正常分配
            for i in free_block:
                self.page_table.append(i)

        # 根据文件名去FCB找文件起始块的物理位置
        point = 0
        for item in dir.FCB:
            if (item.file_dir is self.file_dir) and (item.filename is self.filename):
                point = item.start_point()
                item.is_in_ram = 1
                break

        data = []
        with open("disk.image", mode="rb+", encoding='utf-8') as disk_image:
            while disk.FAT[point] is not -2:
                # 读4B数据
                disk_image.seek(point * 4)
                data.append(disk_image.read(n=4))

                point = disk.FAT[point]
            # 文件大小小于4B/不足4B的文件尾
            disk_image.seek(point * 4)
            disk_image.read(n=4)

        # ---------------------进入临界区----------------------
        # 将数据调入内存块内
        with ram.lock.acquire():
            ram.data_to_ram(data=data, free_block=free_block)
            ram.display_ram()
            ram.recycle_ram(self.page_table)
        # ---------------------退出临界区----------------------
