import random
import typing
from math import sqrt

def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Juice",  
        "color": "#EEEEEE",  
        "head": "ski",  
        "tail": "flake",  #
    }
def start(game_state: typing.Dict):
    print("GAME START")
def end(game_state: typing.Dict):
    print("GAME OVER\n")
  

def move(game_state: typing.Dict) -> typing.Dict:
  
  ##########################
  ### DEFENSIVE MOVEMENT ###
  ##########################
  
  open_space = {"up": True, "down": True, "left": True, "right": True}
  is_move_safe = {"up": True, "down": True, "left": True, "right": True}
  is_move_food = {"up": False, "down": False, "left": False, "right": False}
  manhatten_move = {"up": False, "down": False, "left": False, "right": False}

  # Avoid board edges
  board_width = game_state["board"]["width"]
  board_height = game_state["board"]["height"]
  my_head = game_state["you"]["body"][0] 
  my_length = len(game_state["you"]["body"])
  
  up = my_head['y'] + 1
  down = my_head['y'] - 1
  right = my_head['x'] + 1
  left = my_head['x'] - 1
  
  if up == board_height:
    open_space['up'] = False
    is_move_safe['up'] = False
  if down == -1:
    open_space['down'] = False
    is_move_safe['down'] = False
  if left == -1:
    open_space['left'] = False
    is_move_safe['left'] = False
  if right == board_width:
    open_space['right'] = False
    is_move_safe['right'] = False

  # Avoid my body
  my_body = [(list(length.values())[0], list(length.values())[1]) for length in game_state['you']['body'][1:]]
  if (left, my_head['y']) in my_body:
    open_space['left'] = False
  if (right, my_head['y'],) in my_body:
    open_space['right'] = False
  if (my_head['x'], up) in my_body:
    open_space['up'] = False
  if (my_head['x'], down) in my_body:
    open_space['down'] = False

  # Avoid body coordinates
  temp = []
  snake_info = []
  
  for snake in game_state['board']['snakes']:
    body = snake['body']
    temp.append([(list(length.values())[0], list(length.values())[1]) for length in body])
    
    temp_dict = {}
    temp_dict['head'] = snake['body'][0]
    if temp_dict['head'] == my_head:
      continue
    else:
      temp_dict['length'] = len(snake['body'])
      snake_info.append(temp_dict)
    
  bodies = [length for snake in temp for length in snake]
  bodies = list(set(bodies))

  for coordinate in bodies:
    if (my_head['x'], up) == coordinate:
      is_move_safe['up'] = False
    if (my_head['x'], down) == coordinate:
      is_move_safe['down'] = False
    if (left, my_head['y']) == coordinate:
      is_move_safe['left'] = False
    if (right, my_head['y']) == coordinate:
      is_move_safe['right'] = False
  
  # Avoid losing head collisions
  for snake in snake_info:
    if snake['length'] >= my_length:
      x = snake['head']['x']
      y = snake['head']['y']
      if (right, my_head['y']) in ((x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)):
        is_move_safe['right'] = False
      if (left, my_head['y']) in ((x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)):
        is_move_safe['left'] = False
      if (my_head['x'], up) in ((x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)):
        is_move_safe['up'] = False
      if (my_head['x'], down) in ((x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)):
        is_move_safe['down'] = False   

  # Avoid hazards
  hazards = [(list(hazard.values())[0], list(hazard.values())[1]) for hazard in game_state['board']['hazards']]
  hazards = list(set(hazards))
  for hazard in hazards:
    if (my_head['x'], up) == hazard:
      is_move_safe['up'] = False
    if (my_head['x'], down) == hazard:
      is_move_safe['down'] = False
    if (left, my_head['y']) == hazard:
      is_move_safe['left'] = False
    if (right, my_head['y']) == hazard:
      is_move_safe['right'] = False
  
  ##########################
  ### OFFENSIVE MOVEMENT ###
  ##########################

  # Seek food
  food = []
  foods = game_state['board']['food']
  for food_ in foods:
    location = tuple([food_[key] for key in food_])
    food.append(location)
  if (right, my_head['y']) in food:
    is_move_food['right'] = True
  if (left, my_head['y']) in food:
    is_move_food['left'] = True
  if (my_head['x'], up) in food:
    is_move_food['up'] = True 
  if (my_head['x'], down) in food:
    is_move_food['down'] = True

  min_distance = 100
  closest_food = None
  for piece in food:
    distance_x = sqrt((my_head['x'] - piece[0]) ** 2)
    distance_y = sqrt((my_head['y'] - piece[1]) ** 2)
    distance = distance_x + distance_y
    if distance < min_distance:
      min_distance = distance
      closest_food = piece
  
  # Find largest open space
  surrounding = [(x2, y2) for x2 in range(-2, 3) for y2 in range(-2, 3)]
  grid = [(x, y) for x in range(11) for y in range(11)]
  open_areas = {}
  for cell in grid:
    i = 0
    for cell_ in surrounding:
      coord = tuple(x + y for x, y in zip(cell, cell_))
      if coord not in bodies and coord in grid:
        i += 1
    open_areas[cell] = i
    
  max_space = max(open_areas.values())
  open_cells = [x for x, y in open_areas.items() if y == max_space]
  open_cell = random.choice(open_cells)
  
  # Manhatten path to target space
  if game_state['you']['health'] < 101:
    target = closest_food
    trgt = 'food'
  else:
    target = open_cell
    trgt = 'space'
    
  next_moves = [(my_head['x'], down), (my_head['x'], up), 
                (left, my_head['y']), (right, my_head['y'])]
  
  manhatten_values = {}
  for x, y in next_moves:
    x1 = sqrt((x - target[0]) ** 2)
    y1 = sqrt((y - target[1]) ** 2)
    total = x1 + y1
    manhatten_values[(x, y)] = total
    
  min_distance = min(manhatten_values.values())
  moves_coords = [x for x, y in manhatten_values.items() if y == min_distance]
  move_coord = random.choice(moves_coords)

  temp = (my_head['x'] - move_coord[0], my_head['y'] - move_coord[1])
  if temp == (1, 0):
    manhatten_move['left'] = True
  elif temp == (-1, 0):
    manhatten_move['right'] = True
  elif temp == (0, 1):
    manhatten_move['down'] = True
  elif temp == (0, -1):
    manhatten_move['up'] = True

  
  # Flood fill to avoid trapping self
  def traps(trap):
    temp = (my_head['x'] - trap[0], my_head['y'] - trap[1])
    if temp == (-1, 0):
      is_move_safe['right'] = False
    elif temp == (1, 0):
      is_move_safe['left'] = False
    elif temp == (0, -1):
      is_move_safe['up'] = False
    elif temp == (0, 1):
      is_move_safe['down'] = False
  
  next_moves = []
  for move in is_move_safe:
    if is_move_safe[move] == True:
      next_moves.append(move)
      
  edges = bodies + hazards  
  
  for move in next_moves:
    explored = []
    explore = []
    open_spaces = []
    
    if move == 'up' or move == 'down':
      x = my_head['x']
      y = up if move == 'up' else down
    else:
      x = right if move == 'right' else left
      y = my_head['y']
    explore.append((x, y))
    while explore:
      x1, y1 = explore.pop()
      explored.append((x1, y1))
      open_spaces.append((x1, y1))
      for i in range (-1, 2):
        x2 = x1 + i
        y2 = y1 
        if x2 > 10 or x2 < 0 or y2 > 10 or y2 < 0:
          continue
        elif (x2, y2) not in explored and (x2, y2) in edges:
          explored.append((x2, y2))
        elif (x2, y2) not in explored and (x2, y2) not in open_spaces:
          open_spaces.append((x2, y2))
          explore.append((x2, y2))
      for j in range (-1, 2):
        x3 = x1 
        y3 = y1 + j
        if x3 > 10 or x3 < 0 or y3 > 10 or y3 < 0:
          continue
        elif (x3, y3) not in explored and (x3, y3) in edges:
          explored.append((x3, y3))
        elif (x3, y3) not in explored and (x3, y3) not in open_spaces:
          open_spaces.append((x3, y3))
          explore.append((x3, y3))
    if my_length > 15:
      if len(open_spaces) < (my_length * 1.25):
        traps((x, y))
    elif len(open_spaces) < (my_length * 1.5):
      traps((x, y))


  # Return best move
  manhatten_moves = []
  for move in manhatten_move:
    if manhatten_move[move] == True:
      manhatten_moves.append(move)
  
  # no_head = []
  # for move in is_move_safe:
  #   if is_move_safe[move] == True:
  #     no_head.append(move)
      
  # open_square = []   
  # for move in open_space:
  #   if open_space[move] == True:
  #     open_square.append(move)

  # food_moves = []
  # for move in is_move_food:
  #   if is_move_food[move] == True:
  #     food_moves.append(move)

  # no_head_open_square = []
  # for move in no_head:
  #   if move in open_square:
  #     no_head_open_square.append(move)

  # best_moves_food = []
  # for move in no_head_open_square:
  #   if move in food_moves:
  #     best_moves_food.append(move)
      
  # manhatten_move_ = []
  # for move in no_head_open_square:
  #   if move in manhatten_moves:
  #     manhatten_move_.append(move)

  # for move in is_move_safe:
  #   if is_move_safe[move] == False:
  #     print(move)
  #     if move in manhatten_move_:
  #       print(move)
  #       manhatten_move.remove(move)
  #     if move in best_moves_food:
  #       print(move)
  #       best_moves_food.remove(move)
  #     if move in no_head_open_square:
  #       print(move)
  #       no_head_open_square.remove(move)
  #     if move in food_moves:
  #       print(move)
  #       food_moves.remove(move)
  #     if move in no_head:
  #       print(move)
  #       no_head.remove(move)
  #     if move in open_square:
  #       print(move)
  #       open_square.remove(move)
  #     if move in manhatten_moves:
  #       print(move)
  #       manhatten_moves.remove(move)
  
  # if manhatten_move_:
  #   next_move = random.choice(manhatten_move_)
  #   print(f"Move {game_state['turn']}: Manhatten Move ({trgt}) - {next_move}")
  #   return {"move": next_move, 
  #           "shout": 'DROOOOOPINGGGG!!'}
  # if best_moves_food:
  #   next_move = random.choice(best_moves_food)
  #   print(f"Move {game_state['turn']}: Best Move Food - {next_move}")
  #   return {"move": next_move, 
  #           "shout": 'DROOOOOPINGGGG!!'}
  # elif no_head_open_square:
  #   next_move = random.choice(no_head_open_square)
  #   print(f"Move {game_state['turn']}: Best Move - {next_move}")
  #   return {"move": next_move, 
  #           "shout": 'DROOOOOPINGGGG!!'}
  # elif open_square:
  #   next_move = random.choice(open_square)
  #   print(f"Move {game_state['turn']}: In Bounds Move - {next_move}")
  #   return {"move": next_move, 
  #           "shout": 'DROOOOOPINGGGG!!'}
  # else:
  #   next_move = random.choice(['up', 'down', 'left', 'right'])
  #   print(f"Move {game_state['turn']}: Random Move - {next_move}")
  #   return {"move": next_move,
  #           "shout": 'DROOOOOPINGGGG!!'}  
  safe_move = []
  for move in is_move_safe:
    if is_move_safe[move] == True:
      safe_move.append(move)

  if manhatten_moves:
    for move in manhatten_moves:
      if safe_move:
        if move in safe_move:
          next_move = move
          print(f"Move {game_state['turn']}: Manhatten Move - {next_move}")
          return {"move": next_move, "shout": 'DROOOOOPINGGGG!!'} 
      
  if safe_move:
    next_move = random.choice(safe_move)
    print(f"Move {game_state['turn']}: Safe Move - {next_move}")
    return {"move": next_move, "shout": 'DROOOOOPINGGGG!!'} 
  else:
    random_move = []
    if ((my_head['x'], up)) not in edges and up < 10:
      random_move.append('up')
    elif ((my_head['x'], down)) not in edges and down > 0:
      random_move.append('down')
    elif ((left, my_head['y'])) not in edges and left > 0:
      random_move.append('left')
    elif ((right, my_head['y'])) not in edges and right < 10:
      random_move.append('right')
    if random_move:
      other_move = random.choice(random_move)
      print(f"Move {game_state['turn']}: Other Move - {other_move}")
      return {"move": other_move, "shout": 'DROOOOOPINGGGG!!'} 
    else:
      temp_moves = ['up', 'down', 'left', 'right']
      move = random.choice(temp_moves)
      print(f"Move {game_state['turn']}: Other Move - {move}")
      return {"move": move, "shout": 'DROOOOOPINGGGG!!'} 
  
  #   next_move = random.choice(best_moves_food)
  #   print(f"Move {game_state['turn']}: Best Move Food - {next_move}")
  #   return {"move": next_move, 
  #           "shout": 'DROOOOOPINGGGG!!'}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
