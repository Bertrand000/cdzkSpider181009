# -*- coding: utf-8 -*-

# 嵌套列表数据位置旋转90° 例[[1,2,3][4,5,6][,7,8,9]] -> [[1,4,7][2,5,8][3,6,9]]
def rotate_list(high_list):
    return [[high_list[i][y] for i in range(len(high_list))] for y in range(len(high_list[0]))]

if __name__ == '__main__':
    print(rotate_list([[1,2,3,4],[11,22,33,44],[1,2,3,4]]))