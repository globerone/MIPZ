def check_horizontal(board, row, col, color):
  count = 1
  for i in range(1, 5):
    if col + i < 19 and board[row][col + i] == color:
      count += 1
    else:
      break
  return count

def check_vertical(board, row, col, color):
  count = 1
  for i in range(1, 5):
    if row + i < 19 and board[row + i][col] == color:
      count += 1
    else:
      break
  return count

def check_diagonal_top_left_bottom_right(board, row, col, color):
  count = 1
  for i in range(1, 5):
    if row + i < 19 and board[row + i][col] == color:
      count += 1
    else:
      break
  return count

def check_diagonal_bottom_left_top_right(board, row, col, color):
  count = 1
  for i in range(1, 5):
    if row + i < 19 and col - i >= 0 and board[row + i][col - i] == color:
      count += 1
    else:
      break
  return count

def check_five(board, row, col):
  color = board[row][col]

  for check in [check_horizontal, check_vertical, check_diagonal_top_left_bottom_right, check_diagonal_bottom_left_top_right]:
    if check(board, row, col, color) == 5:
      return True, row, col
  
  return False, None, None

def check_winner(board):
  for row in range(19):
    for col in range(19):
      if board[row][col] != 0:
        win, win_row, win_col = check_five(board, row, col)
        if win:
          return (1 if board[row][col] == 1 else 2), (win_row, win_col)
  return 0, None


def main():
  try:
    with open('data.txt', 'r') as file:
        count = int(file.readline())
        if 1 > count > 11:
          print("Number of tast cases is too high")
          return 
        for num_test_cases in range(count):
          array = []
          for line in range(19):
            row = [int(num) for num in file.readline().strip()]
            array.append(row)
          winner, win_pos = check_winner(array)
          print(winner)
          if winner != 0:
            print(win_pos[0] + 1, win_pos[1] + 1)
  except(ValueError):
    print('Wrong input file')
    return

if __name__ == "__main__":
  main()