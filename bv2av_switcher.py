from typing import Optional


# 代码来源：https://www.zhihu.com/question/381784377/answer/1099438784，用于av号和bv号互相转换
class Video:
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = {}
    for i in range(58):
        tr[table[i]] = i
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608

    def __init__(self, av: Optional[int] = None, bv: Optional[str] = None, *args):
        self.av = int(av)
        self.bv = bv
        if av is None and bv is None:
            raise ValueError("请提供av号或bv号其中的一个！")
        if av is None:
            self.av = self.bv2av()
        if bv is None:
            self.bv = self.av2bv()

    def bv2av(self):
        r = 0
        for i in range(6):
            r += self.tr[self.bv[self.s[i]]] * 58 ** i
        return (r - self.add) ^ self.xor

    def av2bv(self):
        x = (self.av ^ self.xor) + self.add
        r = list('BV1  4 1 7  ')
        for i in range(6):
            r[self.s[i]] = self.table[x // 58 ** i % 58]
        return ''.join(r)
