N = 4
def get_inv(arr):
    inv_cnt = 0
    for i in range(N**2):
        for j in range(i + 1, N**2):
            inv_cnt += (arr[j] and arr[i] and arr[i] > arr[j])
    return inv_cnt

def find_pos(puzzle):
    for index, lst in enumerate(puzzle):
        if 0 in lst:
            return N - index

def is_soluble(puzzle):
    pos = find_pos(puzzle)
    inv = get_inv([num for row in puzzle for num in row]) & 1
    if pos % 2:
        return inv
    else:
        return inv ^ 1

with open('puzzles.txt', 'r') as f:
    puzzles = f.read().splitlines()

puzzles = [i for i in puzzles if '|' in i]

flag = ""
for i in range(128):
    puzzle = []
    for row in puzzles[i * N: i * N + N]:
        row = row.split('|')[1:-1]
        puzzle.append([])
        for index, num in enumerate(row):
            try:
                puzzle[-1].append(int(num))
            except:
                puzzle[-1].append(0)

    flag = str(is_soluble(puzzle)) + flag

print('SharifCTF{%016x}' % int(flag, 2))
