# str = "Hello World!"
# print(str[-1])

# age = int(input("尝试输入数字:"))
# print(age)

"""
# 读取文件全部并打印
f = open("./resources/poem.txt", "r", encoding="utf-8")
print(f"1:")
print(f.read() + "\n")
f.close()

# 读取文件前10字节字符
f = open("./resources/poem.txt", "r", encoding="utf-8")
print(f"2:")
print(f.read(10) + "\n")
f.close()

# 读取文件第一行，遇到\n结束
f = open("./resources/poem.txt", "r", encoding="utf-8")
print(f"3:")
print(f.readline())
f.close()

# 按行读取文件全部并打印
f = open("./resources/poem.txt", "r", encoding="utf-8")
print(f"4:")
line = f.readline()
while line != "":
    print(line)
    line = f.readline()
f.close()

# 一次读取全部行存入列表
f = open("./resources/poem.txt", "r", encoding="utf-8")
print(f"5:")
lines = f.readlines()
print(lines)
for line in lines:
    print(line)
f.close()

# with的使用，使用后能够自动关闭文件
print(f"6:")
with open("./resources/poem.txt", "r", encoding="utf-8") as f:
    print(f.read())

# 尝试读取有格式的docx文件
print(f"7:")
with open("./resources/poem.docx", "r", encoding="utf-8") as f:
    print(f.read())
"""
import json

'''
# 1. 写入文件
text = f"寒雨连江夜入吴，\n平明送客楚山孤。\n洛阳亲友如相问，\n一片冰心在玉壶。"
with open("./resources/poem2.txt", "w", encoding="utf-8") as f:
    f.write(text)

# 2. 为文件追加内容
text2 = f"\n王昌龄[唐代]"
with open("./resources/poem2.txt", "a", encoding="utf-8") as f:
    f.write(text2)

# 3. 同时对文件写入和读取
text3 = f"\n————芙蓉楼送辛渐"
with open("./resources/poem2.txt", "r+", encoding="utf-8") as f:
    print(f.read())
    f.write(text3)
'''
'''
d = dict({'a': 'i am a', 'b': 'i am b', 'c': 'i am c'})
print(d.keys()[1])  # 错误用法
print(list(d.keys())[1])
'''

str={'a':'a'}
print(str['a'])
print(str['b'])