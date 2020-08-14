if __name__ == '__main__':
    data = (1, 2, 3, 4, 5)
    print(data)
    data = [1, 2, 3, 4, 5]
    print(tuple(data))
    data[2] = data[3] = 11
    print(tuple(data))

