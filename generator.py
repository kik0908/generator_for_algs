from random import randint, uniform
import math
import json
import poly_point_isect
from time import time_ns
import os.path
from multiprocessing import Process

LEN_COEF = 0.9


def _time_it(func):
    def wrapper(*args, **kwargs):
        start = time_ns()
        ans = func(*args, **kwargs)
        print("Time is", time_ns() - start)
        return ans

    return wrapper


def generate_line(max_x: int, max_y: int, max_len: int, min_x: int = 0, min_y: int = 0):
    x0, y0 = randint(min_x, max_x), randint(min_y, max_y)
    x1, y1 = randint(min_x, max_x), randint(min_y, max_y)

    dx = x1 - x0
    dy = y1 - y0
    c = (dx**2 + dy**2) ** 0.5
    cc = 1
    if c > max_len:
        x1 = x0 + math.floor((dx) * (max_len / c) * cc)
        y1 = y0 + math.floor((dy) * (max_len / c) * cc)
    return (x0, y0), (x1, y1)


def generate_line_with_intersection(
    point1: tuple[int, int],
    point2: tuple[int, int],
    max_x: int,
    max_y: int,
    max_r: int,
    max_len: int,
):
    x_left, x_right = min(point1[0], point2[0]), max(point1[0], point2[0])
    x_left, x_right = max(0, x_left - max_r), min(max_x, x_right + max_r)
    x_midddle = (x_left + x_right) // 2

    y_up, y_down = max(point1[1], point2[1]), min(point1[1], point2[1])
    y_up, y_down = min(max_y, y_up + max_r), max(0, y_down - max_r)
    y_middle = (y_down + y_up) // 2

    _generate_p1 = lambda: (randint(x_left, x_midddle), randint(y_middle, y_up))
    _generate_p2 = lambda: (randint(x_midddle, x_right), randint(y_down, y_middle))

   
    p1, p2 = _generate_p1(), _generate_p2()
    
    while poly_point_isect.isect_segments(((point1, point2), (p1, p2))) == []:
        p1, p2 = _generate_p1(), _generate_p2()

    return p1, p2


def generate_lines_k(
    n: int, k: int, max_x: int, max_y: int, max_len: int
) -> list[tuple[int, int]]:
    assert k < n
    ans = []

    cur_k = 0

    for i in range(n):
        if (n - i) + cur_k == k and cur_k < k:
            idx = randint(0, i - 1)
            seg = generate_line_with_intersection(
                ans[idx][0], ans[idx][1], max_x, max_y, 5, max_len
            )
            cur_k = len(poly_point_isect.isect_segments(ans + [seg]))
            cur_max_len = max_len
            while cur_k > k:
                idx = randint(0, i - 1)
                seg = generate_line_with_intersection(
                    ans[idx][0], ans[idx][1], max_x, max_y, 5, cur_max_len
                )
                cur_k = len(poly_point_isect.isect_segments(ans + [seg]))
                cur_max_len = max(2, cur_max_len * LEN_COEF)

            ans.append(seg)
            if cur_k == k:
                return ans
            elif cur_k < k:
                continue
        else:
            seg = generate_line(max_x, max_y, max_len)
            cur_k = len(poly_point_isect.isect_segments(ans + [seg]))
            cur_max_len = max_len
            while cur_k > k:
                seg = generate_line(max_x, max_y, cur_max_len)
                cur_k = len(poly_point_isect.isect_segments(ans + [seg]))
                cur_max_len = max(3, cur_max_len * LEN_COEF)
            ans.append(seg)

    return ans


def generate_lines(
    n: int, k: int, max_x: int, max_y: int, max_len: int
) -> list[tuple[int, int]]:
    assert k < n
    ans = []

    cur_k = 0

    for i in range(n):
        if (n - i) + cur_k == k and cur_k < k:
            idx = randint(0, i - 1)
            seg = generate_line_with_intersection(
                ans[idx][0], ans[idx][1], max_x, max_y, 5, max_len
            )
            ans.append(seg)
        else:
            ans.append(generate_line(max_x, max_y, max_len))

        cur_k = len(poly_point_isect.isect_segments(ans))

    return ans




def func_n(n, k, max_x, max_y, max_len):
    while True:
        try:
            ans = generate_lines_k(n, k, max_x, max_y, max_len)
            break
        except Exception as e:
            print("N =", n, e)

    with open(f"./n_tmp/{n}_{k}.json", "w") as file:
        json.dump(ans, file)


def func_k(n, k, max_x, max_y, max_len):
    while True:
        try:
            ans = generate_lines_k(n, k, max_x, max_y, max_len)
            break
        except Exception as e:
            print("K =", k, e)

    with open(f"./k_tmp/{n}_{k}.json", "w") as file:
        json.dump(ans, file)


def _generate_n_const_to_file(
    n: int, max_x: int, max_y: int, max_len: int, fisrt: int, delta: int, points: int
):
    prcs = []
    for i in range(points):
        k = fisrt * (delta**i)
        if os.path.exists(f"./n_tmp/{n}_{k}.json") is True:
            with open(f"./n/{n}_{k}.json", "w") as file_to:
                with open(f"./n_tmp/{n}_{k}.json", "r") as file_from:
                    file_to.write(file_from.read())

        elif os.path.exists(f"./n_tmp/{n}_{k}.json") is False:
            prcs.append(
                Process(
                    target=func_n, args=(n, k, max_x, max_y, max_len), daemon=True
                )
            )
    for i in prcs:
        i.start()
    for i in prcs:
        i.join()

    prcs = []
    for i in range(points):
        k = fisrt * (delta**i)
        if os.path.exists(f"./n_tmp/{n}_{k*delta}.json") is True:
            with open(f"./n_2/{n}_{k*delta}.json", "w") as file_to:
                with open(f"./n_tmp/{n}_{k*delta}.json", "r") as file_from:
                    file_to.write(file_from.read())

        elif os.path.exists(f"./n_tmp/{n}_{k*delta}.json") is False:
            prcs.append(
                Process(
                    target=func_n, args=(n, k * delta, max_x, max_y, max_len), daemon=True
                )
            )
    for i in prcs:
        i.start()
    for i in prcs:
        i.join()


def _generate_k_const_to_file(
    k: int, max_x: int, max_y: int, max_len: int, fisrt: int, delta: int, points: int
):
    prcs = []
    for i in range(points):
        n = fisrt * (delta**i)

        if os.path.exists(f"./k_tmp/{n}_{k}.json") is True:
            with open(f"./k/{n}_{k}.json", "w") as file_to:
                with open(f"./k_tmp/{n}_{k}.json", "r") as file_from:
                    file_to.write(file_from.read())

        elif os.path.exists(f"./k_tmp/{n}_{k}.json") is False:
            prcs.append(
                    Process(
                        target=func_k, args=(n, k, max_x, max_y, max_len), daemon=True
                    )
                )
            
    for i in prcs:
        i.start()
    for i in prcs:
        i.join()

    prcs = []

    for i in range(points):
        n = fisrt * (delta**i)
        if os.path.exists(f"./k_tmp/{n*delta}_{k}.json") is True:
            with open(f"./k_2/{n*delta}_{k}.json", "w") as file_to:
                with open(f"./k_tmp/{n*delta}_{k}.json", "r") as file_from:
                    file_to.write(file_from.read())

        elif os.path.exists(f"./k_tmp/{n*delta}_{k}.json") is False:
            prcs.append(
                    Process(
                        target=func_k, args=(n*delta, k, max_x, max_y, max_len), daemon=True
                    )
                )

    for i in prcs:
        i.start()
    for i in prcs:
        i.join()


x = 20000
y = 20000
max_len = 500
points_k = 8
points_n = 7


if __name__ == "__main__":
    print("generate k start")
    _generate_k_const_to_file(1, x, y, max_len, 2, 2, points_k)
    _generate_k_const_to_file(1, x, y, max_len, 2, 2, points_k)

    _generate_k_const_to_file(2, x, y, max_len, 3, 2, points_k)
    _generate_k_const_to_file(2, x, y, max_len, 3, 2, points_k)

    _generate_k_const_to_file(3, x, y, max_len, 4, 2, points_k)
    _generate_k_const_to_file(3, x, y, max_len, 4, 2, points_k)

    _generate_k_const_to_file(4, x, y, max_len, 5, 2, points_k)
    _generate_k_const_to_file(4, x, y, max_len, 5, 2, points_k)

    _generate_k_const_to_file(5, x, y, max_len, 6, 2, points_k)
    _generate_k_const_to_file(5, x, y, max_len, 6, 2, points_k)

    print("generate k end")

    print("generate n start")
    _generate_n_const_to_file(270, x, y, max_len, 1, 2, points_n)
    _generate_n_const_to_file(270, x, y, max_len, 1, 2, points_n)

    _generate_n_const_to_file(520, x, y, max_len, 2, 2, points_n)
    _generate_n_const_to_file(520, x, y, max_len, 2, 2, points_n)

    _generate_n_const_to_file(780, x, y, max_len, 3, 2, points_n)
    _generate_n_const_to_file(780, x, y, max_len, 3, 2, points_n)

    _generate_n_const_to_file(1030, x, y, max_len, 4, 2, points_n)
    _generate_n_const_to_file(1030, x, y, max_len, 4, 2, points_n)

    _generate_n_const_to_file(1300, x, y, max_len, 5, 2, points_n)
    _generate_n_const_to_file(1300, x, y, max_len, 5, 2, points_n)
    print("generate n end")
