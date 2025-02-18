import numpy as np

# 创建一个NumPy数组
arr = np.array([[1, 2, 3], [4, 5, 6]])

# 将数组保存为npy文件
np.save('array.npy', arr)
print("保存npy文件成功")

# 加载npy文件
loaded_arr = np.load('array.npy')

# 打印加载的数组
print(loaded_arr)