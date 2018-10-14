# -*- coding: utf-8 -*-
def demo():
    a = [1,2,3,4]
    tuple(a.append(6),a.append(7),a.append(8)) if 1==1 else tuple(a.append(5))
    print(a)
if __name__ == '__main__':
    demo()