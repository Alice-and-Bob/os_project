import threading
import disk
import dir
import ram


# DONE：在根据文件名从FCB中查找时，没有考虑到文件重名的冲突；
# DONE：考虑在所有涉及FCB查找的代码中添加对文件路径的判断；只有文件路径和文件名全部一致时，才允许访问对应FCB

# TODO:所有调用ram模块里方法的代码都在临界区，要先获取锁才能调用ram模块方法

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
        else:
            # 正常执行
            for item in dir.FCB:
                if item.is_occupied is 0:  # 第一个未被占用的FCB块
                    item.occupy(is_occupied=1, filename=filename, file_dir=file_dir, start_point=disk.FAT[0])
                    break

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
        if_done = dir.delete(filename=filename, file_dir=file_dir)
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

    # DONE：回收磁盘空间,初始化数据到disk.image
    # 按偏移量写文件到disk.image
    with open("disk.image", mode="ab+", encoding='utf-8') as disk_image:
        while disk.FAT[point] is not -2:
            # 写空白数据
            disk_image.seek(point * 4)
            disk_image.write(b'\x00\x00\x00\x00')
            # 初始化FAT内容
            temp = point
            point = disk.FAT[point]
            disk.FAT[temp] = -1
        # 初始化文件尾
        disk.FAT[point] = -1
        disk_image.seek(point * 4)
        disk_image.write(b'\x00\x00\x00\x00')

    return 1


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

    # 执行线程
    def run(self):

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

        # ------------------进入临界区---------------------
        # 将数据调入内存块内
        with ram.lock.acquire():
            ram.data_to_ram(data=data, free_block=free_block)
        # ------------------退出临界区---------------------
