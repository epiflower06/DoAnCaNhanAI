
# ======================= PHẦN 1: THƯ VIỆN VÀ KHỞI TẠO =======================
import pygame
import sys
import heapq
import os
import random
import math
import time
import copy
from collections import deque, defaultdict
import matplotlib.pyplot as plt
import numpy as np
import ctypes
if sys.platform == 'win32':
    ctypes.windll.user32.SetProcessDPIAware()
pygame.init()

# ======================= PHẦN 2: CẤU HÌNH GIAO DIỆN VÀ BIẾN =======================
# Kích thước cửa sổ game
screen_width = 800
screen_height = 750
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("8 Puzzle")

white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 128, 0)
light_green = (144, 238, 144)
blue = (173, 216, 230)
light_yellow = (255, 255, 204)

font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 20)

# Kích thước của mỗi ô vuông trong puzzle
cell_size = 60
puzzle_margin = 5  # khoảng cách giữa các ô

visited_nodes_value = "0"
generated_nodes_value = "0"

# ======================= PHẦN 3: CẤU TRÚC GIAO DIỆN =======================
# Vị trí bảng trạng thái bắt đầu
start_state_rect = pygame.Rect(50, 150, 3 * cell_size, 3 * cell_size)
puzzle_width = 3 * cell_size
puzzle_height = 3 * cell_size
puzzle_x = start_state_rect.x
puzzle_y = start_state_rect.y

# Các nút điều khiển chính
button_run_rect = pygame.Rect(300, 50, 70, 30)   # Nút RUN
button_stop_rect = pygame.Rect(400, 50, 70, 30)  # Nút STOP
button_exit_rect = pygame.Rect(500, 50, 70, 30)  # Nút EXIT
button_chart_rect = pygame.Rect(600, 50, 70, 30)
active_button = None  
button_skip_rect = pygame.Rect(700, 50, 70, 30)  # Nút SKIP
skip_active = False 
animation_delay = 300  
fast_delay = 50

# Vị trí bảng trạng thái đích
goal_state_rect = pygame.Rect(50, 400, 3 * cell_size, 3 * cell_size)
goal_x = goal_state_rect.x
goal_y = goal_state_rect.y

# Vị trí vùng hiển thị đường đi kết quả
path_rect = pygame.Rect(280, 150, 250, 180)

input_text = ""  
input_active = False  
input_rect = pygame.Rect(50, 340, 180, 30) 
error_message = ""  
error_rect = pygame.Rect(50, 375, 180, 20)
cursor_visible = True  
last_cursor_toggle = 0  
cursor_blink_interval = 500

# Chart combobox
chart_dropdown_open = False
chart_dropdown_rect = pygame.Rect(300, 400, 200, 30)
selected_chart_group = None


algorithm_results = {}

# ======================= PHẦN 4: RADIO BUTTON & THỐNG KÊ =======================

# Vị trí nút chọn chế độ nhập tay và ngẫu nhiên
nhap_radio_rect = pygame.Rect(50, 90, 20, 20)
random_radio_rect = pygame.Rect(150, 90, 20, 20)
selected_input_method = None

# Vị trí hiển thị thông tin thời gian và số bước giải
thoi_gian_text_pos = (550, 150)
so_buoc_text_pos = (550, 180)
visited_nodes_text_pos = (550, 210)
generated_nodes_text_pos = (550, 240)
thoi_gian_value = "0.00 s"  # Thời gian giải thuật
so_buoc_value = "0"         # Số bước đã thực hiện
step_index = 0
last_update = pygame.time.get_ticks()
delay = 300  # thời gian giữa các bước (ms)

solution_time_text_pos = (550, 270)
solution_time_value = "0.00 s"
scroll_offset = 0
max_scroll = 0
scroll_speed = 20


# ======================= PHẦN 5: TRẠNG THÁI BÀI TOÁN =======================

#start_state = [[1, 2, 3], [4, 5, 6], [0, 7, 8]]
start_state = [[2, 0, 3], [1, 4, 6], [7, 5, 8]]
#start_state = [[2, 3, 6], [1, 5, 0], [4, 7, 8]]

goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

# Các biến điều khiển giải thuật và animation
solution_path = []         # Danh sách các bước từ start đến goal
solving = False            # Cờ báo có đang chạy giải thuật không
animation_start_time = 0   # Thời điểm bắt đầu chạy animation
animation_step = 0         # Bước hiện tại đang hiển thị
animation_delay = 0.3      # Độ trễ giữa các bước (giây)
last_animation_time = pygame.time.get_ticks()    # Thời điểm cập nhật animation gần nhất
paused_time = 0
# ======================= PHẦN 6: HÀM TIỆN ÍCH =======================

# Sinh puzzle ngẫu nhiên từ 0 đến 8 và chuyển thành ma trận 3x3
def generate_random_puzzle():
    numbers = list(range(9))
    random.shuffle(numbers)
    return [numbers[i:i + 3] for i in range(0, 9, 3)]


# Vẽ bảng puzzle tại vị trí (x, y), cho biết đây là start hay goal để tô màu phù hợp
def draw_puzzle(state, x, y, is_start_state=False):
    global animation_step, solution_path
    if isinstance(state, tuple):
        try:
            state = [list(row) for row in state]
        except Exception:
            return  
        
    # Kiểm tra tính hợp lệ của ma trận
    if not (isinstance(state, list) and len(state) == 3 and
            all(isinstance(row, list) and len(row) == 3 for row in state)):
        return  
    for i in range(3):
        for j in range(3):
            num = state[i][j]
            cell_x = x + j * cell_size
            cell_y = y + i * cell_size

            if is_start_state:
                if num == 0:  
                    if is_equal(state, goal_state):
                        cell_color = light_green  
                    elif animation_step > 0 and solution_path:  
                        cell_color = light_yellow 
                    else:
                        cell_color = blue  
                else:
                    cell_color = blue  
                    if num == goal_state[i][j] and num != 0:
                        cell_color = light_green  
            else:
                cell_color = light_green

            # Vẽ ô
            pygame.draw.rect(screen, cell_color, (cell_x, cell_y, cell_size, cell_size))
            pygame.draw.rect(screen, black, (cell_x, cell_y, cell_size, cell_size), 2)

            if num != 0:
                text = font.render(str(num), True, black)
                text_rect = text.get_rect(center=(cell_x + cell_size // 2,
                                                  cell_y + cell_size // 2))
                screen.blit(text, text_rect)

def validate_input(text):
    global error_message
    cleaned = text.replace(",", " ").replace("  ", " ").strip().split()
    if len(cleaned) != 9:
        error_message = "Enter exactly 9 numbers"
        return None
    try:
        numbers = [int(x) for x in cleaned]
    except ValueError:
        error_message = "Use numbers 0-8 only"
        return None
    if sorted(numbers) != list(range(9)):
        error_message = "Use 0-8 exactly once"
        return None
    state = [numbers[i:i+3] for i in range(0, 9, 3)]
    if not is_solvable(state):
        error_message = "Puzzle is unsolvable"
        return None
    error_message = ""
    return state

# ======================= PHẦN 7: VẼ GIAO DIỆN CHÍNH (GUI) =======================


def draw_gui():
    global so_buoc_value, scroll_offset, max_scroll, last_cursor_toggle, cursor_visible
    screen.fill(white)
    now = pygame.time.get_ticks()
    if now - last_cursor_toggle > cursor_blink_interval:
        cursor_visible = not cursor_visible
        last_cursor_toggle = now
    if active_button == "run":
        pygame.draw.rect(screen, green, button_run_rect)
    else:
        pygame.draw.rect(screen, white, button_run_rect)
        pygame.draw.rect(screen, green, button_run_rect, 3)
    text_run = font.render("Run", True, black)
    screen.blit(text_run, (button_run_rect.x + 15, button_run_rect.y + 5))

    if active_button == "stop":
        pygame.draw.rect(screen, green, button_stop_rect)
    else:
        pygame.draw.rect(screen, white, button_stop_rect)
        pygame.draw.rect(screen, green, button_stop_rect, 3)
    text_stop = font.render("Stop", True, black)
    screen.blit(text_stop, (button_stop_rect.x + 10, button_stop_rect.y + 5))

    if active_button == "exit":
        pygame.draw.rect(screen, green, button_exit_rect)
    else:
        pygame.draw.rect(screen, white, button_exit_rect)
        pygame.draw.rect(screen, green, button_exit_rect, 3)
    text_exit = font.render("Exit", True, black)
    screen.blit(text_exit, (button_exit_rect.x + 10, button_exit_rect.y + 5))

    if skip_active:
        pygame.draw.rect(screen, green, button_skip_rect)
    else:
        pygame.draw.rect(screen, white, button_skip_rect)
        pygame.draw.rect(screen, green, button_skip_rect, 3)
    text_skip = font.render("Skip", True, black)
    screen.blit(text_skip, (button_skip_rect.x + 10, button_skip_rect.y + 5))
    
    text_start = font.render("Start state", True, black)
    screen.blit(text_start, (start_state_rect.x, start_state_rect.y - 25))
    pygame.draw.rect(screen, green, start_state_rect, 2)
    draw_puzzle(start_state, puzzle_x, puzzle_y, is_start_state=True)

    text_goal = font.render("Goal state", True, black)
    screen.blit(text_goal, (goal_state_rect.x, goal_state_rect.y - 25))  # Moved to (50, 375)
    pygame.draw.rect(screen, green, goal_state_rect, 2)
    draw_puzzle(goal_state, goal_x, goal_y)

    text_path = font.render("Path", True, black)
    screen.blit(text_path, (path_rect.x, path_rect.y - 25))  # Moved to (450, 125)
    pygame.draw.rect(screen, green, path_rect, 2)
    if solution_path and animation_step > 0:
        x, y = path_rect.x + 10, path_rect.y + 10
        line_height = 15
        max_width = path_rect.width - 20
        current_y = y
        path_positions = []
        for i, item in enumerate(solution_path[:animation_step]):
            state = item[0] if isinstance(item, tuple) else item
            state_display = [row[:] for row in state]
            state_str = f"Step {i}: {str(state_display)}"
            text_surface = small_font.render(state_str, True, black)
            text_width, text_height = small_font.size(state_str)
            if text_width > max_width:
                state_str = f" Step {i}: {str(state_display)[:int(max_width/10)]}..."
                text_surface = small_font.render(state_str, True, black)
                text_width, text_height = small_font.size(state_str)
            screen_y = current_y - scroll_offset
            if path_rect.y <= screen_y < path_rect.y + path_rect.height:
                screen.blit(text_surface, (x, screen_y))
            path_positions.append((x, current_y, text_width, text_height))
            current_y += line_height
        if path_positions:
            max_scroll = max(0, path_positions[-1][1] + path_positions[-1][3] - path_rect.y - path_rect.height + 5)
            if animation_step > 0:
                latest_y = path_positions[-1][1]
                latest_height = path_positions[-1][3]
                desired_scroll = latest_y + latest_height - (path_rect.y + path_rect.height) + 5
                scroll_offset = max(0, min(desired_scroll, max_scroll))
        else:
            max_scroll = 0
    else:
        scroll_offset = 0
        max_scroll = 0

    text_nhap = font.render("Input", True, black)
    screen.blit(text_nhap, (nhap_radio_rect.x + 30, nhap_radio_rect.y))
    pygame.draw.circle(screen, black, nhap_radio_rect.center, 10, 2)
    if selected_input_method == "Input":
        pygame.draw.circle(screen, green, nhap_radio_rect.center, 7)

    text_random = font.render("Random", True, black)
    screen.blit(text_random, (random_radio_rect.x + 30, random_radio_rect.y))
    pygame.draw.circle(screen, black, random_radio_rect.center, 10, 2)
    if selected_input_method == "Random":
        pygame.draw.circle(screen, green, random_radio_rect.center, 7)

    if selected_input_method == "Input":
        pygame.draw.rect(screen, white, input_rect)
        pygame.draw.rect(screen, black, input_rect, 2)
        display_text = input_text + ("|" if input_active and cursor_visible else "")
        input_surface = font.render(display_text, True, black)
        text_width = input_surface.get_width()
        if text_width > input_rect.width - 10:
            display_text = display_text[-(input_rect.width//10):]  
            input_surface = font.render(display_text, True, black)
        screen.blit(input_surface, (input_rect.x + 5, input_rect.y + 5))
        error_surface = small_font.render(error_message, True, (255, 0, 0))
        screen.blit(error_surface, (error_rect.x, error_rect.y))

    text_thoi_gian = font.render(f"Real Time: {thoi_gian_value}", True, black)
    screen.blit(text_thoi_gian, thoi_gian_text_pos)  
    
    text_so_buoc = font.render(f"Steps: {so_buoc_value}", True, black)
    screen.blit(text_so_buoc, so_buoc_text_pos) 

    text_visited_nodes = font.render(f"Visited Nodes: {visited_nodes_value}", True, black)
    screen.blit(text_visited_nodes, visited_nodes_text_pos) 

    text_generated_nodes = font.render(f"Generated Nodes: {generated_nodes_value}", True, black)
    screen.blit(text_generated_nodes, generated_nodes_text_pos)  

    text_solution_time = font.render(f"Solution Time: {solution_time_value}", True, black)
    screen.blit(text_solution_time, solution_time_text_pos)

    pygame.draw.rect(screen, blue, dropdown_rect)
    text_thuattoan = font.render(selected_algorithm_name if selected_algorithm_name else "Select Algorithm", True, black)
    screen.blit(text_thuattoan, (dropdown_rect.x + 5, dropdown_rect.y + 5))

    if dropdown_open:
        for i, option in enumerate(dropdown_options):
            pygame.draw.rect(screen, blue, dropdown_options_rects[i])
            pygame.draw.rect(screen, black, dropdown_options_rects[i], 2)
            text_option = font.render(option, True, black)
            screen.blit(text_option, (dropdown_options_rects[i].x + 5, dropdown_options_rects[i].y + 5))

    text_thoi_gian = font.render(f"Real Time: {thoi_gian_value}", True, black)
    screen.blit(text_thoi_gian, thoi_gian_text_pos)
    text_so_buoc = font.render(f"Steps: {so_buoc_value}", True, black)
    screen.blit(text_so_buoc, so_buoc_text_pos)
    text_visited_nodes = font.render(f"Visited Nodes: {visited_nodes_value}", True, black)
    screen.blit(text_visited_nodes, visited_nodes_text_pos)
    text_generated_nodes = font.render(f"Generated Nodes: {generated_nodes_value}", True, black)
    screen.blit(text_generated_nodes, generated_nodes_text_pos)
    text_solution_time = font.render(f"Solution Time: {solution_time_value}", True, black)
    screen.blit(text_solution_time, solution_time_text_pos)

    pygame.draw.rect(screen, blue, chart_dropdown_rect)
    chart_display_text = selected_chart_group if selected_chart_group else "Select Chart Group"
    text_chart_dropdown = font.render(chart_display_text, True, black)
    screen.blit(text_chart_dropdown, (chart_dropdown_rect.x + 5, chart_dropdown_rect.y + 5))

    if chart_dropdown_open:
        for i, group in enumerate(chart_groups):
            pygame.draw.rect(screen, blue, chart_group_rects[i])
            pygame.draw.rect(screen, black, chart_group_rects[i], 2)
            text_option = font.render(group, True, black)
            screen.blit(text_option, (chart_group_rects[i].x + 5, chart_group_rects[i].y + 5))
            
    pygame.display.flip()

# ======================= PHẦN 8: HÀM TÌM Ô TRỐNG VÀ SINH TRẠNG THÁI KẾ =======================

# Tìm vị trí ô trống trong ma trận
def find_blank(state):
    if isinstance(state, tuple):
        state = [list(row) for row in state] # Nếu là tuple, chuyển về list
    for r in range(3):
        for c in range(3):
            if state[r][c] == 0:
                return r, c # Trả về vị trí hàng, cột của ô trống
    raise ValueError("No blank (0) in this state")

# Tạo tất cả các trạng thái con có thể từ trạng thái hiện tại bằng cách di chuyển ô trống
def successors(state):
    blank_r, blank_c = find_blank(state)#vị trí ô trống
    possible_moves = []
    # Di chuyển lên
    if blank_r > 0:
        new_state = [row[:] for row in state]#sao chép ma trận
        new_state[blank_r][blank_c], new_state[blank_r - 1][blank_c] = new_state[blank_r - 1][blank_c], new_state[blank_r][blank_c]
        possible_moves.append(new_state)
    #xuống
    if blank_r < 2:
        new_state = [row[:] for row in state]
        new_state[blank_r][blank_c], new_state[blank_r + 1][blank_c] = new_state[blank_r + 1][blank_c], new_state[blank_r][blank_c]
        possible_moves.append(new_state)
    # trái
    if blank_c > 0:
        new_state = [row[:] for row in state]
        new_state[blank_r][blank_c], new_state[blank_r][blank_c - 1] = new_state[blank_r][blank_c - 1], new_state[blank_r][blank_c]
        possible_moves.append(new_state)
    #phải
    if blank_c < 2:
        new_state = [row[:] for row in state]
        new_state[blank_r][blank_c], new_state[blank_r][blank_c + 1] = new_state[blank_r][blank_c + 1], new_state[blank_r][blank_c]
        possible_moves.append(new_state)
    return possible_moves

def is_equal(state1, state2):
    return all(state1[i][j] == state2[i][j] for i in range(3) for j in range(3))
#-----------------------PHẦN 9: NHÓM THUẬT TOÁN UNIFORMED SEARCH (Không Heuristic)------------------------------------------
#=================================Thuật toán Breadth - first Search===================================
def bfs(start, goal):
    global solution_time_value
    start_time = time.perf_counter()
    visited = set()# Tập trạng thái đã thăm
    queue = deque([(start, [], 0, 0)])# Hàng đợi lưu (trạng thái hiện tại, đường đi)
    all_steps = []
    while queue:
        state, path, visited_nodes, generated_nodes = queue.popleft()# Lấy phần tử đầu hàng đợi
        key = str(state)
        if key in visited:
            continue
        visited.add(key)
        visited_nodes += 1
        all_steps.append((state, visited_nodes, generated_nodes))
        if state == goal:
            result = [(s, v, g) for s, v, g in all_steps if s in path + [state]]
            end_time = time.perf_counter()
            solution_time_value = f"{end_time - start_time:.5f} s"
            return result if result else [(start, 0, 0)]
        generated_nodes += len(successors(state))
        for next_state in successors(state):
            queue.append((next_state, path + [state], visited_nodes, generated_nodes))
    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return [(start, visited_nodes, generated_nodes)]
#***************************Thuật toán Depth - first Search ***********************************
def dfs(start, goal, depth_limit=300):
    global solution_time_value
    start_time = time.perf_counter()
    visited = set()
    stack = [(start, None, 0, 0)]
    parent = {str(start): None}
    all_steps = []
    visited_nodes = 0
    generated_nodes = 0
    while stack:
        state, _, v_nodes, g_nodes = stack.pop()
        key = str(state)
        if key in visited:
            continue
        visited.add(key)
        visited_nodes = v_nodes + 1
        all_steps.append((state, visited_nodes, g_nodes))
        if state == goal:
            path = []
            current = state
            while current is not None:
                for s, v, g in all_steps:
                    if s == current:
                        path.append((s, v, g))
                        break
                current = parent.get(str(current))
            return path[::-1] if path else [(start, visited_nodes, generated_nodes)]
        if len([k for k, p in parent.items() if p == state]) >= depth_limit:
            continue
        next_states = successors(state)
        generated_nodes = g_nodes + len(next_states)
        for next_state in next_states:
            if str(next_state) not in visited:
                stack.append((next_state, state, visited_nodes, generated_nodes))
                parent[str(next_state)] = state
    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return [(start, visited_nodes, generated_nodes)]
#================================Thuật toán Uniform Cost Search==========================================
def ucs(start, goal):
    global solution_time_value
    start_time = time.perf_counter()
    heap = []
    visited = set()
    heapq.heappush(heap, (0, start, None, 0, 0))
    parent = {str(start): None}
    all_steps = []
    visited_nodes = 0
    generated_nodes = 0
    while heap:
        cost, state, _, v_nodes, g_nodes = heapq.heappop(heap)
        key = str(state)
        if key in visited:
            continue
        visited.add(key)
        visited_nodes = v_nodes + 1
        all_steps.append((state, visited_nodes, g_nodes))
        if state == goal:
            path = []
            current = state
            while current is not None:
                for s, v, g in all_steps:
                    if s == current:
                        path.append((s, v, g))
                        break
                current = parent.get(str(current))
            return path[::-1] if path else [(start, visited_nodes, generated_nodes)]
        next_states = successors(state)
        generated_nodes = g_nodes + len(next_states)
        for next_state in next_states:
            if str(next_state) not in visited:
                heapq.heappush(heap, (cost + 1, next_state, state, visited_nodes, generated_nodes))
                parent[str(next_state)] = state
    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return [(start, visited_nodes, generated_nodes)]

#***************************Thuật toán Iterative Deepening ***********************************
def iterative_deepening(start, goal):
    global solution_time_value
    start_time = time.perf_counter()
    def dls(state, limit, parent_map, visited, visited_nodes, generated_nodes):
        key = str(state)
        if key in visited:
            return None, visited_nodes, generated_nodes
        visited.add(key)
        visited_nodes += 1
        all_steps.append((state, visited_nodes, generated_nodes))
        if state == goal:
            return [state], visited_nodes, generated_nodes
        if limit <= 0:
            return None, visited_nodes, generated_nodes
        next_states = successors(state)
        generated_nodes += len(next_states)
        for next_state in next_states:
            if str(next_state) not in visited:
                parent_map[str(next_state)] = state
                result, new_visited, new_generated = dls(next_state, limit - 1, parent_map, visited, visited_nodes, generated_nodes)
                visited_nodes, generated_nodes = new_visited, new_generated
                if result:
                    return [state] + result, visited_nodes, generated_nodes
        return None, visited_nodes, generated_nodes

    all_steps = []
    visited_nodes = 0
    generated_nodes = 0
    for depth in range(1, 50):
        visited = set()
        parent_map = {str(start): None}
        result, visited_nodes, generated_nodes = dls(start, depth, parent_map, visited, visited_nodes, generated_nodes)
        if result:
            path = []
            current = result[-1]
            while current is not None:
                for s, v, g in all_steps:
                    if s == current:
                        path.append((s, v, g))
                        break
                current = parent_map.get(str(current))
            end_time = time.perf_counter()
            solution_time_value = f"{end_time - start_time:.5f} s"
            return path[::-1] if path else [(start, visited_nodes, generated_nodes)]
    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.2f} s"
    return [(start, visited_nodes, generated_nodes)]
#-----------------------------------------------------------------------------------------
# ======================= PHẦN 10: INFORMED SEARCH (Có sử dụng heuristic) =======================

# ----------- Hàm heuristic: Tính tổng khoảng cách Manhattan từ mỗi ô đến vị trí đúng -----------
def heuristic(state):
    distance = 0
    for i in range(3):
        for j in range(3):
            val = state[i][j]
            if val != 0:
                # Vị trí đúng của ô val trong goal state
                goal_i = (val - 1) // 3
                goal_j = (val - 1) % 3
                distance += abs(i - goal_i) + abs(j - goal_j)
    return distance# Giá trị càng thấp càng gần đích

#==========================Thuật toán Greedy Search====================================
def greedy(start, goal):
    global solution_time_value
    start_time = time.perf_counter()
    heap = []
    visited = set()
    heapq.heappush(heap, (heuristic(start), start, None, 0, 0))
    parent = {str(start): None}
    all_steps = []
    visited_nodes = 0
    generated_nodes = 0
    while heap:
        h, state, _, v_nodes, g_nodes = heapq.heappop(heap)
        key = str(state)
        if key in visited:
            continue
        visited.add(key)
        visited_nodes = v_nodes + 1
        all_steps.append((state, visited_nodes, g_nodes))
        if state == goal:
            path = []
            current = state
            while current is not None:
                for s, v, g in all_steps:
                    if s == current:
                        path.append((s, v, g))
                        break
                current = parent.get(str(current))
            end_time = time.perf_counter()
            solution_time_value = f"{end_time - start_time:.2f} s"
            return path[::-1] if path else [(start, visited_nodes, generated_nodes)]
        next_states = successors(state)
        generated_nodes = g_nodes + len(next_states)
        for next_state in next_states:
            if str(next_state) not in visited:
                heapq.heappush(heap, (heuristic(next_state), next_state, state, visited_nodes, generated_nodes))
                parent[str(next_state)] = state
    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return [(start, visited_nodes, generated_nodes)]
#=============================Thuật toán A* ==================================
def astar(start, goal):
    global solution_time_value
    start_time = time.perf_counter()
    heap = []
    visited = set()
    heapq.heappush(heap, (heuristic(start), 0, start, [], 0, 0))  # (f, g, state, path, visited_nodes, generated_nodes)
    all_steps = []
    while heap:
        f, g, state, path, visited_nodes, generated_nodes = heapq.heappop(heap)
        key = str(state)
        if key in visited:
            continue
        visited.add(key)
        visited_nodes += 1
        all_steps.append((state, visited_nodes, generated_nodes))
        if state == goal:
            result = [(s, v, g) for s, v, g in all_steps if s in path + [state]]
            return result if result else [(start, 0, 0)]
        generated_nodes += len(successors(state))
        for next_state in successors(state):
            heapq.heappush(heap, (g + 1 + heuristic(next_state), g + 1, next_state, path + [state], visited_nodes, generated_nodes))
    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return [(start, visited_nodes, generated_nodes)]
#============================Thuật toán Iterative Deepening A* =======================================
def ida_star(start, goal):
    global solution_time_value
    start_time = time.perf_counter()
    def search(state, g, threshold, parent_map, visited, visited_nodes, generated_nodes):
        f = g + heuristic(state)
        if f > threshold:
            return f, None, visited_nodes, generated_nodes
        key = str(state)
        if key in visited:
            return f, None, visited_nodes, generated_nodes
        visited.add(key)
        visited_nodes += 1
        all_steps.append((state, visited_nodes, generated_nodes))
        if state == goal:
            return f, [state], visited_nodes, generated_nodes
        min_cost = float("inf")
        next_states = successors(state)
        generated_nodes += len(next_states)
        for next_state in next_states:
            if str(next_state) not in visited:
                parent_map[str(next_state)] = state
                new_cost, result, new_visited, new_generated = search(next_state, g + 1, threshold, parent_map, visited, visited_nodes, generated_nodes)
                visited_nodes, generated_nodes = new_visited, new_generated
                if result:
                    return new_cost, [state] + result, visited_nodes, generated_nodes
                min_cost = min(min_cost, new_cost)
        return min_cost, None, visited_nodes, generated_nodes

    all_steps = []
    threshold = heuristic(start)
    visited_nodes = 0
    generated_nodes = 0
    while True:
        visited = set()
        parent_map = {str(start): None}
        new_threshold, result, visited_nodes, generated_nodes = search(start, 0, threshold, parent_map, visited, visited_nodes, generated_nodes)
        if result:
            path = []
            current = result[-1]
            while current is not None:
                for s, v, g in all_steps:
                    if s == current:
                        path.append((s, v, g))
                        break
                current = parent_map.get(str(current))
            end_time = time.perf_counter()
            global solution_time_value
            solution_time_value = f"{end_time - start_time:.5f} s"
            return path[::-1] if path else [(start, visited_nodes, generated_nodes)]
        if new_threshold == float("inf"):
            end_time = time.perf_counter()
            solution_time_value = f"{end_time - start_time:.2f} s"
            return [(start, visited_nodes, generated_nodes)]
        threshold = new_threshold

# ======================= PHẦN 11: LOCAL SEARCH (Tìm kiếm cục bộ, không duyệt toàn bộ) =======================
# ----------- Simple Hill Climbing: Leo dốc đơn giản, đi tới hàng xóm tốt hơn -----------
def simple_hillclimbing(start, goal):
    global solution_time_value
    start_time = time.perf_counter()
    current = start
    current_h = heuristic(current)
    path = [(current, 0, 0)]
    visited = set()
    visited_nodes = 0
    generated_nodes = 0
    while True:
        key = str(current)
        if key in visited:
            break
        visited.add(key)
        visited_nodes += 1
        neighbors = successors(current)
        generated_nodes += len(neighbors)
        best_neighbor = None
        best_h = current_h
        for neighbor in neighbors:
            h = heuristic(neighbor)
            if h < best_h:
                best_h = h
                best_neighbor = neighbor
        if best_neighbor is None:
            break
        current = best_neighbor
        current_h = best_h
        path.append((current, visited_nodes, generated_nodes))
        if current == goal:
            return path
    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return [(start, visited_nodes, generated_nodes)] if not path[-1][0] == goal else path
# ----------- Steepest Ascent Hill Climbing: Luôn chọn hàng xóm tốt nhất -----------
def steepest_climbing(start, goal):
    global solution_time_value
    start_time = time.perf_counter()
    current = start
    current_h = heuristic(current)
    path = [(current, 0, 0)]
    visited = set()
    visited_nodes = 0
    generated_nodes = 0
    while True:
        key = str(current)
        if key in visited:
            break
        visited.add(key)
        visited_nodes += 1
        neighbors = successors(current)
        generated_nodes += len(neighbors)
        best_neighbor = None
        best_h = current_h
        for neighbor in neighbors:
            h = heuristic(neighbor)
            if h < best_h:
                best_h = h
                best_neighbor = neighbor
        if best_neighbor is None:
            break
        current = best_neighbor
        current_h = best_h
        path.append((current, visited_nodes, generated_nodes))
        if current == goal:
            end_time = time.perf_counter()
            solution_time_value = f"{end_time - start_time:.5f} s"
            return path
    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return [(start, visited_nodes, generated_nodes)] if not path[-1][0] == goal else path
# ----------- Stochastic Hill Climbing: Chọn ngẫu nhiên một hàng xóm tốt hơn -----------
def stochastic_hill_climbing(start, goal):
    global solution_time_value
    start_time = time.perf_counter()
    current = start
    current_h = heuristic(current)
    path = [(current, 0, 0)]
    visited = set()
    visited_nodes = 0
    generated_nodes = 0
    while True:
        key = str(current)
        if key in visited:
            break
        visited.add(key)
        visited_nodes += 1
        neighbors = successors(current)
        generated_nodes += len(neighbors)
        better_neighbors = [neighbor for neighbor in neighbors if heuristic(neighbor) < current_h]
        if not better_neighbors:
            break
        current = random.choice(better_neighbors)
        current_h = heuristic(current)
        path.append((current, visited_nodes, generated_nodes))
        if current == goal:
            end_time = time.perf_counter()
            solution_time_value = f"{end_time - start_time:.5f} s"
            return path
    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return [(start, visited_nodes, generated_nodes)] if not path[-1][0] == goal else path
# ----------- Beam Search: Giữ lại một số trạng thái tốt nhất ở mỗi vòng -----------
def beam_search(start, goal, beam_width=3, max_loop=1000):
    global solution_time_value
    start_time = time.perf_counter()
    current_states = [(heuristic(start), start, [(start, 0, 0)])]
    visited = set()
    visited_nodes = 0
    generated_nodes = 0
    loop = 0
    while loop < max_loop:
        all_neighbors = []
        for h, state, path in current_states:
            key = str(state)
            if key in visited:
                continue
            visited.add(key)
            visited_nodes += 1
            neighbors = successors(state)
            generated_nodes += len(neighbors)
            for neighbor in neighbors:
                if str(neighbor) not in visited:
                    all_neighbors.append((heuristic(neighbor), neighbor, path + [(neighbor, visited_nodes, generated_nodes)]))
        if not all_neighbors:
            break
        all_neighbors.sort(key=lambda x: x[0])
        current_states = all_neighbors[:min(beam_width, len(all_neighbors))]
        for h, state, path in current_states:
            if state == goal:
                end_time = time.perf_counter()
                solution_time_value = f"{end_time - start_time:.5f} s"
                return path
        loop += 1
    for h, state, path in current_states:
        if state == goal:
            end_time = time.perf_counter()
            solution_time_value = f"{end_time - start_time:.5f} s"
            return path
    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return [(start, visited_nodes, generated_nodes)]

# ----------- Simulated Annealing: Chấp nhận tạm thời trạng thái xấu để thoát cực trị cục bộ -----------
def sa(start, goal, initial_temp=2000, cooling_rate=0.97, min_temp=0.01, max_steps=1000, max_restarts=3):
    global solution_time_value
    start_time = time.perf_counter()

    if not is_valid_state(start) or not is_solvable(start):
        return [(start, 0, 0)]

    def clean_path(path):
        if not path:
            return []
        cleaned = [path[0]]
        for state, v, g in path[1:]:
            if not is_equal(state, cleaned[-1][0]):
                cleaned.append((state, v, g))
        return cleaned

    visited_nodes = 0
    generated_nodes = 0
    best_path = []
    best_heuristic = float('inf')

    start = [row[:] for row in start] if isinstance(start[0], list) else [list(row) for row in start]

    for _ in range(max_restarts):
        current = [row[:] for row in start]
        current_h = heuristic(current)
        path = [(current, visited_nodes, generated_nodes)]
        temp = initial_temp
        step = 0
        no_progress_count = 0

        while temp > min_temp and step < max_steps:
            if is_equal(current, goal):
                end_time = time.perf_counter()
                solution_time_value = f"{end_time - start_time:.5f} s"
                return clean_path(path)

            neighbors = successors(current)
            generated_nodes += len(neighbors)
            if not neighbors:
                break

            # Ưu tiên chọn trạng thái tốt hơn ngẫu nhiên
            neighbors.sort(key=heuristic)
            next_state = neighbors[0] if random.random() < 0.3 else random.choice(neighbors)

            next_h = heuristic(next_state)
            delta_e = next_h - current_h
            if delta_e <= 0 or random.random() < math.exp(-delta_e / max(temp, 1e-10)):
                current = next_state
                current_h = next_h
                visited_nodes += 1
                path.append((current, visited_nodes, generated_nodes))
                if current_h < best_heuristic:
                    best_heuristic = current_h
                    best_path = path[:]
                    no_progress_count = 0
                else:
                    no_progress_count += 1
            else:
                no_progress_count += 1

            if no_progress_count > 150:
                break
            temp *= cooling_rate
            step += 1

    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return clean_path(best_path) if best_path else [(start, visited_nodes, generated_nodes)]



# -------------------GENETIC ALGORITHM (Giải thuật di truyền)-------------------
# ----------- Hàm thực thi một chuỗi bước di chuyển lên trạng thái bắt đầu -----------
def apply_moves(state, moves):
    current = [row[:] for row in state]
    states = [current]
    for dr, dc in moves:
        try:
            r, c = find_blank(current)
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_state = [row[:] for row in current]
                new_state[r][c], new_state[nr][nc] = new_state[nr][nc], new_state[r][c]
                states.append(new_state)
                current = new_state
            else:
                break
        except ValueError:
            break
    return states, current

def ga_fitness(moves, start, goal):
    _, final_state = apply_moves(start, moves)
    distance = heuristic(final_state)
    return -distance - len(moves) * 0.15  # Stronger penalty for move length

def ga_crossover(p1, p2):
    if not p1 or not p2:
        return p1 if p1 else p2
    point = random.randint(0, min(len(p1), len(p2)))
    return p1[:point] + p2[point:]

def ga_mutate(moves, start):
    if not moves:
        return [random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])]
    moves = moves[:]
    idx = random.randint(0, len(moves) - 1)
    if random.random() < 0.5 and len(moves) < 40:
        moves.insert(idx, random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)]))
    elif random.random() < 0.5 and len(moves) > 1:
        moves.pop(random.randint(0, len(moves) - 1))
    else:
        moves[idx] = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
    return moves

def ga_random_moves():
    return [random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)]) for _ in range(random.randint(15, 25))]

def genetic_algorithm(start, goal, max_gen=150, pop_size=100, mutation_rate=0.4):
    global solution_time_value
    start_time = time.perf_counter()
    if not is_valid_state(start) or not is_solvable(start):
        solution_time_value = "0.000 s"
        return [(start, 0, 0)]

    population = [ga_random_moves() for _ in range(pop_size)]
    best_moves = []
    best_fitness = float('-inf')
    visited = set()
    visited_nodes = 0
    generated_nodes = 0
    no_progress_count = 0

    for gen in range(max_gen):
        fitnesses = []
        for moves in population:
            states, final_state = apply_moves(start, moves)
            state_key = tuple(tuple(row) for row in final_state)
            if state_key not in visited:
                visited.add(state_key)
                visited_nodes += 1
            generated_nodes += len(states) - 1
            fitness = ga_fitness(moves, start, goal)
            fitnesses.append((fitness, moves))
            if is_equal(final_state, goal):
                path = [(s, visited_nodes - len(states) + i + 1, generated_nodes) for i, s in enumerate(states)]
                end_time = time.perf_counter()
                solution_time_value = f"{end_time - start_time:.5f} s"
                return path

        fitnesses.sort(reverse=True)
        best = fitnesses[0][1]
        current_fitness = fitnesses[0][0]
        if current_fitness > best_fitness:
            best_fitness = current_fitness
            best_moves = best
            no_progress_count = 0
        else:
            no_progress_count += 1

        if no_progress_count >= 150:
            break

        new_pop = [best]
        while len(new_pop) < pop_size:
            p1, p2 = random.choices(population[:20], k=2)
            child = ga_crossover(p1, p2)
            if random.random() < mutation_rate:
                child = ga_mutate(child, start)
            new_pop.append(child)
        population = new_pop

    states, final_state = apply_moves(start, best_moves)
    path = [(s, visited_nodes - len(states) + i + 1, generated_nodes) for i, s in enumerate(states)]
    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return path if states else [(start, visited_nodes, generated_nodes)]

#--------------------------PHẦN 13: NHÓM THUẬT TOÁN COMPLEX ENVIRONMENT---------------------------------------
#======================Thuật toán Sensorless BFS===========================================
# Trong bài toán này, ta không biết chính xác trạng thái ban đầu mà chỉ có một tập hợp các trạng thái có thể xảy ra (belief state).
# Mỗi hành động phải áp dụng lên toàn bộ tập hợp này → thuật toán phải xử lý các trạng thái đồng thời.

# Hàm kiểm tra trạng thái có giải được hay không dựa vào số lần hoán vị (tính chẵn lẻ)
def is_solvable(state):
    flat = [cell for row in state for cell in row if cell != 0]  # Bỏ ô trống (0), dồn ma trận thành 1 hàng
    inversions = sum(1 for i in range(len(flat)) for j in range(i+1, len(flat)) if flat[i] > flat[j])  # Đếm số cặp nghịch thế
    blank_row = find_blank(state)[0]  # Lấy chỉ số dòng của ô trống
    return (inversions + blank_row) % 2 == 0  # Tổng nghịch thế + vị trí ô trống phải chẵn => trạng thái hợp lệ
print(is_solvable(start_state))
# Thuật toán BFS áp dụng cho bài toán belief state (nhiều trạng thái cùng lúc, không xác định trạng thái ban đầu chính xác)
def sensorless_bfs(initial_states, goal_state):
    global solution_time_value
    start_time = time.perf_counter()
    if not initial_states or not is_valid_state(initial_states[0]) or not is_solvable(initial_states[0]):
        solution_time_value = "0.000 s"
        return [(initial_states[0], 0, 0)] if initial_states else [(goal_state, 0, 0)]

    initial_belief = frozenset([tuple(tuple(row) for row in state) for state in initial_states])
    visited = set()
    queue = deque([(initial_belief, [])])
    parent_map = {initial_belief: None}
    all_steps = []
    visited_nodes = 0
    generated_nodes = 0

    while queue:
        belief_state, path = queue.popleft()
        if belief_state in visited:
            continue
        visited.add(belief_state)
        visited_nodes += 1
        all_steps.append((initial_states[0], visited_nodes, generated_nodes))

        goal_tuple = tuple(tuple(row) for row in goal_state)
        if any(s == goal_tuple for s in belief_state):
            solution = [[row[:] for row in initial_states[0]]]
            current = solution[0]
            for dr, dc in path:
                r, c = find_blank(current)
                nr, nc = r + dr, c + dc
                if 0 <= nr < 3 and 0 <= nc < 3:
                    new_state = [row[:] for row in current]
                    new_state[r][c], new_state[nr][nc] = new_state[nr][nc], new_state[r][c]
                    solution.append(new_state)
                    current = new_state
            result = [(s, visited_nodes, generated_nodes) for s in solution]
            end_time = time.perf_counter()
            solution_time_value = f"{end_time - start_time:.5f} s"
            return result if result else [(initial_states[0], visited_nodes, generated_nodes)]

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_belief = set()
            for state in belief_state:
                state_list = [list(row) for row in state]
                try:
                    r, c = find_blank(state_list)
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 3 and 0 <= nc < 3:
                        new_state = [row[:] for row in state_list]
                        new_state[r][c], new_state[nr][nc] = new_state[nr][nc], new_state[r][c]
                        next_belief.add(tuple(tuple(row) for row in new_state))
                        generated_nodes += 1
                except ValueError:
                    continue
            if next_belief:
                next_belief_key = frozenset(next_belief)
                if next_belief_key not in visited:
                    queue.append((next_belief_key, path + [(dr, dc)]))
                    parent_map[next_belief_key] = belief_state

    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return [(initial_states[0], visited_nodes, generated_nodes)]



# ========================== Thuật toán AND-OR Search ==============================
# Giải bài toán trong không gian belief (có nhiều trạng thái đầu vào), trả về kế hoạch nếu có
def and_or_search(belief, goal, visited=None, depth=0, max_depth=200):
    global solution_time_value
    start_time = time.perf_counter()

    if visited is None:
        visited = set()
        visited_nodes = 0
        generated_nodes = 0
    else:
        visited_nodes = len(visited)
        generated_nodes = 0

    if isinstance(belief, list):
        belief = frozenset([tuple(tuple(row) for row in belief)])
    elif not isinstance(belief, frozenset):
        belief = frozenset(belief)

    if depth > max_depth:
        end_time = time.perf_counter()
        solution_time_value = f"{end_time - start_time:.5f} s"
        return None, visited_nodes, generated_nodes

    belief_key = frozenset(belief)
    if belief_key in visited:
        end_time = time.perf_counter()
        solution_time_value = f"{end_time - start_time:.5f} s"
        return None, visited_nodes, generated_nodes
    visited.add(belief_key)
    visited_nodes += 1

    goal_tuple = tuple(tuple(row) for row in goal)
    if any(state == goal_tuple for state in belief):
        end_time = time.perf_counter()
        solution_time_value = f"{end_time - start_time:.5f} s"
        return [], visited_nodes, generated_nodes

    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        next_belief = set()
        for state in belief:
            try:
                state_list = [list(row) for row in state]
                r, c = find_blank(state_list)
                nr, nc = r + dr, c + dc
                if 0 <= nr < 3 and 0 <= nc < 3:
                    new_state = [row[:] for row in state_list]
                    new_state[r][c], new_state[nr][nc] = new_state[nr][nc], new_state[r][c]
                    next_belief.add(tuple(tuple(row) for row in new_state))
                    generated_nodes += 1
            except Exception:
                continue

        if next_belief:
            plan_rest, v_count, g_count = and_or_search(next_belief, goal, visited.copy(), depth + 1, max_depth)
            visited_nodes = max(visited_nodes, v_count)
            generated_nodes = max(generated_nodes, g_count)
            if plan_rest is not None:
                end_time = time.perf_counter()
                solution_time_value = f"{end_time - start_time:.5f} s"
                return [("Move", (dr, dc))] + plan_rest, visited_nodes, generated_nodes

    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return None, visited_nodes, generated_nodes


# ================= NHÓM THUẬT TOÁN CSP======================== 
# ---------------------Backtracking Search --------------------
def backtracking_search(state, goal, visited=None, path=None, depth=0, depth_limit=100, visited_nodes=0, generated_nodes=0, start_time=None):
    global solution_time_value

    if start_time is None:
        start_time = time.perf_counter()

    if visited is None:
        visited = set()
    if path is None:
        path = []

    # Kiểm tra định dạng trạng thái
    if not (isinstance(state, list) and len(state) == 3 and
            all(isinstance(row, list) and len(row) == 3 for row in state)):
        return [(state, visited_nodes, generated_nodes)]

    # Nếu đạt trạng thái đích
    if is_equal(state, goal):
        solution_time_value = f"{time.perf_counter() - start_time:.5f} s"
        return path + [(state, visited_nodes + 1, generated_nodes)]

    # Nếu vượt quá độ sâu
    if depth >= depth_limit:
        return []

    # Dạng hashable để lưu visited
    state_tuple = tuple(tuple(row) for row in state)
    if state_tuple in visited:
        return []

    visited.add(state_tuple)
    visited_nodes += 1

    # Sinh successors và tăng generated
    next_states = successors(state)
    generated_nodes += len(next_states)

    for next_state in next_states:
        result = backtracking_search(
            next_state,
            goal,
            visited.copy(),
            path + [(state, visited_nodes, generated_nodes)],
            depth + 1,
            depth_limit,
            visited_nodes,
            generated_nodes,
            start_time
        )
        if result:
            return result

    return []




#-----------Thuật toán Min-Conflicts-----------------------
def is_valid_state(state):
    if not (isinstance(state, list) and len(state) == 3):
        return False
    flat = []
    for row in state:
        if not (isinstance(row, list) and len(row) == 3):
            return False
        flat.extend(row)
    return sorted(flat) == list(range(9))  # Phải chứa 0-8 duy nhất

def min_conflicts(start, goal, max_steps=1000, max_restarts=5):
    global solution_time_value
    start_time = time.perf_counter()
    if not is_valid_state(start) or not is_solvable(start):
        end_time = time.time()
        solution_time_value = f"{end_time - start_time:.5f} s"
        return [(start, 0, 0)]

    def count_conflicts(state):
        return heuristic(state)

    best_path = []
    best_path_conflicts = float('inf')
    visited_nodes = 0
    generated_nodes = 0

    for restart in range(max_restarts):
        current = [row[:] for row in start]
        path = [(current, visited_nodes, generated_nodes)]
        visited = set()
        visited.add(tuple(tuple(row) for row in current))
        visited_nodes += 1
        step = 0
        stuck_count = 0

        while step < max_steps:
            if is_equal(current, goal):
                end_time = time.perf_counter()
                solution_time_value = f"{end_time - start_time:.5f} s"
                return path
            neighbors = successors(current)
            generated_nodes += len(neighbors)
            if not neighbors:
                break
            current_conflicts = count_conflicts(current)
            best_neighbor = None
            best_conflicts = current_conflicts

            random.shuffle(neighbors)
            for neighbor in neighbors:
                conflicts = count_conflicts(neighbor)
                if conflicts < best_conflicts:
                    best_conflicts = conflicts
                    best_neighbor = neighbor

            if best_neighbor is None:
                stuck_count += 1
                if stuck_count > 50:
                    break
                best_neighbor = random.choice(neighbors)
            else:
                stuck_count = 0

            current = best_neighbor
            state_tuple = tuple(tuple(row) for row in current)
            if state_tuple in visited:
                neighbors = successors(current)
                generated_nodes += len(neighbors)
                if not neighbors:
                    break
                current = random.choice(neighbors)
                state_tuple = tuple(tuple(row) for row in current)
            visited.add(state_tuple)
            visited_nodes += 1
            path.append((current, visited_nodes, generated_nodes))
            step += 1

            if best_conflicts < best_path_conflicts:
                best_path = path[:]
                best_path_conflicts = best_conflicts

        if best_path and (not best_path or count_conflicts(best_path[-1][0]) < best_path_conflicts):
            best_path_conflicts = count_conflicts(best_path[-1][0])
    end_time = time.perf_counter()
    solution_time_value = f"{end_time - start_time:.5f} s"
    return best_path if best_path and is_equal(best_path[-1][0], goal) else [(start, visited_nodes, generated_nodes)]

# ================= NHÓM THUẬT TOÁN Reinforcement Learning==================
# -----------------Q-Learning Agent ------------------
# Các hằng số biểu diễn hướng di chuyển
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
actions = ['up', 'down', 'left', 'right']

# Hàm thực hiện hành động trên trạng thái
def move(state, action):
    r, c = find_blank(state)
    new = [row[:] for row in state]
    if action == 'up' and r > 0:
        new[r][c], new[r-1][c] = new[r-1][c], new[r][c]
    elif action == 'down' and r < 2:
        new[r][c], new[r+1][c] = new[r+1][c], new[r][c]
    elif action == 'left' and c > 0:
        new[r][c], new[r][c-1] = new[r][c-1], new[r][c]
    elif action == 'right' and c < 2:
        new[r][c], new[r][c+1] = new[r][c+1], new[r][c]
    else:
        return None
    return new

# Trả về tất cả các trạng thái kế tiếp hợp lệ
def successorss(state):
    moves = []
    for a in ['up', 'down', 'left', 'right']:
        ns = move(state, a)
        if ns:
            moves.append(ns)
    return moves

# Định nghĩa lớp Q-Learning
class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2, episodes=5000):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.99995
        self.episodes = episodes
        self.actions = ['up', 'down', 'left', 'right']
        self.q_table = defaultdict(lambda: {a: 0.0 for a in self.actions})
        self.trained = False

    def serialize(self, state):
        return tuple(num for row in state for num in row)

    def get_reward(self, state, next_state, goal_state):
        if is_equal(next_state, goal_state):
            return 100
        current_h = heuristic(state)
        next_h = heuristic(next_state)
        return (current_h - next_h) * 0.1 - 1

    def choose_action(self, state, explore=True):
        s = self.serialize(state)
        if explore and random.random() < self.epsilon:
            return random.choice(self.actions)
        valid_actions = [a for a in self.actions if move(state, a) is not None]
        if not valid_actions:
            return random.choice(self.actions)
        q_values = [self.q_table[s][a] for a in valid_actions]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(valid_actions, q_values) if q == max_q]
        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state):
        s = self.serialize(state)
        ns = self.serialize(next_state)
        current_q = self.q_table[s][action]
        next_q = max(self.q_table[ns].values(), default=0)
        self.q_table[s][action] = current_q + self.alpha * (reward + self.gamma * next_q - current_q)

    def train(self, start_state, goal_state):
        if self.trained:
            return
        for episode in range(self.episodes):
            state = copy.deepcopy(start_state)
            for step in range(100):
                action = self.choose_action(state, explore=True)
                next_state = move(state, action)
                if next_state is None:
                    continue
                reward = self.get_reward(state, next_state, goal_state)
                self.learn(state, action, reward, next_state)
                state = next_state
                if is_equal(state, goal_state):
                    break
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.trained = True

    def solve(self, start_state, goal_state):
        global solution_time_value
        start_time = time.perf_counter()
        path = [(copy.deepcopy(start_state), 0, 0)]
        state = copy.deepcopy(start_state)
        steps = 0
        max_steps = 50
        visited = {self.serialize(state)}
        visited_nodes = 1
        generated_nodes = 0
        while steps < max_steps and not is_equal(state, goal_state):
            action = self.choose_action(state, explore=False)
            next_state = move(state, action)
            if next_state is None:
                break
            ser = self.serialize(next_state)
            generated_nodes += len(successorss(state))
            if ser in visited:
                break
            path.append((next_state, visited_nodes, generated_nodes))
            visited.add(ser)
            visited_nodes += 1
            state = next_state
            steps += 1
        end_time = time.perf_counter()
        solution_time_value = f"{end_time - start_time:.5f} s"
        return path
dropdown_open = False
agent = QLearningAgent(alpha=0.1, gamma=0.9, epsilon=0.2, episodes=5000)

algorithms = {
    #nhóm Uninformed search
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
    "Iterative Deepening": iterative_deepening,
    #nhóm Informed search
    "A*": astar,
    "IDA*": ida_star,
    "Greedy": greedy,
    #nhóm Local search
    "Simple HC": simple_hillclimbing,
    "Steepest Ascent HC": steepest_climbing,
    "Stochastic HC": stochastic_hill_climbing,
    "S Annealing": sa,
    "Beam Search": beam_search,
    "Genetic Algorithm": genetic_algorithm,
    #nhóm Complex environment
    "Sensorless BFS": sensorless_bfs,
    "AND OR": and_or_search,
    #nhóm CSP (Constraint satisfaction problem)
    "Backtracking": lambda s, g: backtracking_search(s, g),
    "Min-Conflicts": min_conflicts,
    #nhóm Reinforcement learning
    "Q-learning": lambda s, g: agent.solve(s, g)
}



algorithm_groups = {
    "Uninformed Search": {
        "BFS": bfs,
        "DFS": dfs,
        "UCS": ucs,
        "Iterative Deepening": iterative_deepening
    },
    "Informed Search": {
        "A*": astar,
        "IDA*": ida_star,
        "Greedy": greedy
    },
    "Local Search": {
        "Simple HC": simple_hillclimbing,
        "Steepest Ascent HC": steepest_climbing,
        "Stochastic HC": stochastic_hill_climbing,
        "S Annealing": sa,
        "Beam Search": beam_search,
        "Genetic Algorithm": genetic_algorithm
    },
    "Complex Envir": {
        "Sensorless BFS": sensorless_bfs,
        "AND OR": and_or_search
    },
    "CSP": {
        "Backtracking": lambda s, g: backtracking_search(s, g),
        "Min-Conflicts": min_conflicts
    },
    "R Learning": {
        "Q-learning": lambda s, g: agent.solve(s, g)
    }
}

selected_algorithm_name = "Select Algorithm"
selected_algorithm_func = None
dropdown_rect = pygame.Rect(50, 50, 200, 30)
dropdown_options = list(algorithms.keys())
dropdown_options_rects = [pygame.Rect(50, 80 + i * 30, 200, 30) for i in range(len(dropdown_options))]

# Chart combobox (complete definition)
chart_groups = list(algorithm_groups.keys())
chart_group_rects = [pygame.Rect(300, 430 + i * 30, 200, 30) for i in range(len(chart_groups))]

def animate_solution():
    global animation_step, last_animation_time, start_state, visited_nodes_value, generated_nodes_value
    if animation_step < len(solution_path):
        now = pygame.time.get_ticks()
        if now - last_animation_time > animation_delay:
            item = solution_path[animation_step]
            state = item[0] if isinstance(item, tuple) else item
            start_state = state
            if isinstance(start_state, tuple):
                start_state = [list(row) for row in start_state]
            visited_nodes_value = str(item[1]) if isinstance(item, tuple) else "0"
            generated_nodes_value = str(item[2]) if isinstance(item, tuple) else "0"
            animation_step += 1
            last_animation_time = now

# Chart window settings
chart_window = None
chart_window_width = 1000
chart_window_height = 600
chart_window_active = False
close_button_rect = pygame.Rect(900, 550, 80, 30)  # Close button in chart window

def generate_group_charts(group_name):
    if group_name not in algorithm_groups:
        print(f"Error: Group {group_name} not found")
        return []

    algo_names = []
    solution_times = []
    steps = []
    visited_nodes = []
    generated_nodes = []

    print(f"Generating chart for group: {group_name}")
    for algo_name in algorithm_groups[group_name].keys():
        key = f"{group_name}:{algo_name}"
        if key in algorithm_results:
            result = algorithm_results[key]
            algo_names.append(algo_name)
            solution_times.append(result["time"])
            steps.append(result["steps"])
            visited_nodes.append(result["visited"])
            generated_nodes.append(result["generated"])
            print(f"{algo_name}: steps={result['steps']}, time={result['time']}, visited={result['visited']}, generated={result['generated']}")
        else:
            print(f"No data for {algo_name} in {group_name}")

    if not algo_names:
        print(f"No data available for group {group_name}")
        return []

    fig, ax1 = plt.subplots(figsize=(9, 5), dpi=100)
    x = np.arange(len(algo_names))
    bar_width = 0.35

    ax1.bar(x - bar_width/2, steps, bar_width, label='Steps', color='yellow')
    ax1.bar(x + bar_width/2, solution_times, bar_width, label='Solution Time (s)', color='blue')
    ax1.set_xlabel('Algorithm')
    ax1.set_ylabel('Steps / Time (s)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(algo_names, rotation=45, ha='right')
    ax1.legend(loc='upper left')
    ax1.tick_params(axis='y', labelsize=10)
    ax1.tick_params(axis='x', labelsize=10)

    ax2 = ax1.twinx()
    ax2.plot(x, visited_nodes, marker='o', label='Visited Nodes', color='red')
    ax2.plot(x, generated_nodes, marker='s', label='Generated Nodes', color='green')
    ax2.set_ylabel('Nodes')
    ax2.legend(loc='upper right')
    ax2.tick_params(axis='y', labelsize=10)

    plt.title(f'{group_name}: Algorithm Performance Comparison', fontsize=12)
    fig.tight_layout()

    output_file = f'{group_name.replace(" ", "_").lower()}_chart.png'
    output_file = os.path.abspath(output_file)
    plt.savefig(output_file, bbox_inches='tight', format='png', dpi=100)
    plt.close(fig)

    if os.path.exists(output_file):
        print(f"Chart saved successfully: {output_file}")
    else:
        print(f"Error: Failed to save chart: {output_file}")
    return [output_file]



def open_chart_window(chart_file):
    global chart_window, chart_window_active
    if chart_window_active:
        chart_window = None
        chart_window_active = False
        pygame.display.set_mode((screen_width, screen_height))
        draw_gui()

    chart_file = os.path.abspath(chart_file)
    print(f"Opening chart window for: {chart_file}")

    if not os.path.exists(chart_file):
        print(f"Error: Chart file not found: {chart_file}")
        pygame.display.set_mode((screen_width, screen_height))
        draw_gui()
        return

    try:
        chart_window = pygame.display.set_mode((chart_window_width, chart_window_height))
        pygame.display.set_caption(f"Chart: {selected_chart_group}")
        chart_window_active = True

        chart_image = pygame.image.load(chart_file)
        img_width, img_height = chart_image.get_size()
        print(f"Chart image loaded: {img_width}x{img_height}")

        if img_width > chart_window_width - 20 or img_height > chart_window_height - 60:
            aspect_ratio = img_width / img_height
            if (chart_window_width - 20) / (chart_window_height - 60) > aspect_ratio:
                new_height = chart_window_height - 60
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = chart_window_width - 20
                new_height = int(new_width / aspect_ratio)
            chart_image = pygame.transform.smoothscale(chart_image, (new_width, new_height))
            print(f"Scaled chart to: {new_width}x{new_height}")

        chart_window.fill(white)
        chart_window.blit(chart_image, ((chart_window_width - chart_image.get_width()) // 2, 10))

        pygame.draw.rect(chart_window, green, close_button_rect)
        text_close = font.render("Close", True, black)
        chart_window.blit(text_close, (close_button_rect.x + 10, close_button_rect.y + 5))

        pygame.display.flip()
        print("Chart window displayed")
    except Exception as e:
        print(f"Error displaying chart: {e}")
        chart_window = None
        chart_window_active = False
        pygame.display.set_mode((screen_width, screen_height))
        draw_gui()

def start_solving():
    global solving, solution_path, thoi_gian_value, so_buoc_value, animation_step, animation_start_time, visited_nodes_value, generated_nodes_value, solution_time_value
    if not solving and selected_algorithm_func is not None:
        solving = True
        solution_path = []
        animation_step = 0
        animation_start_time = time.time()
        thoi_gian_value = "0.00 s"
        so_buoc_value = "Calculating..."
        visited_nodes_value = "Calculating..."
        generated_nodes_value = "Calculating..."
        solution_time_value = "Calculating..."
        start_time = time.perf_counter()
        if selected_algorithm_name == "AND OR":
            belief = [row[:] for row in start_state]
            solution = []
            plan, visited_nodes, generated_nodes = and_or_search(belief, goal_state)
            #print(f"AND-OR Output: Plan={plan}, Visited={visited_nodes}, Generated={generated_nodes}, Steps={len(plan)}")
            if plan is not None:
                current = [row[:] for row in start_state]
                solution = [(current, 0, 0)]
                num_steps = len(plan)
                if num_steps > 0:
                    min_visited = num_steps * 2
                    min_generated = num_steps * 4
                    visited_nodes = max(visited_nodes, min_visited)
                    generated_nodes = max(generated_nodes, min_generated)
                    visited_per_step = visited_nodes / (num_steps + 1)
                    generated_per_step = generated_nodes / (num_steps + 1)
                    step_visited = 0
                    step_generated = 0
                    for step, (action, (dr, dc)) in enumerate(plan, 1):
                        r, c = find_blank(current)
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 3 and 0 <= nc < 3:
                            new_state = [row[:] for row in current]
                            new_state[r][c], new_state[nr][nc] = new_state[nr][nc], new_state[r][c]
                            step_visited += visited_per_step
                            step_generated += generated_per_step
                            solution.append((new_state, int(min(step_visited, visited_nodes)), int(min(step_generated, generated_nodes))))
                            current = new_state
                    #print(f"AND-OR Solution: {[(s, v, g) for s, v, g in solution]}")
                else:
                    solution = [(current, visited_nodes, generated_nodes)]
            else:
                solution = [(belief, visited_nodes, generated_nodes)]
        elif selected_algorithm_name == "Sensorless BFS":
            if not (isinstance(start_state, list) and len(start_state) == 3 and
                    all(isinstance(row, list) and len(row) == 3 for row in start_state)):
                solution = [(start_state, 0, 0)]
            elif not is_solvable(start_state):
                print("Puzzle is unsolvable")
                solution = [(start_state, 0, 0)]
            else:
                solution = sensorless_bfs([start_state], goal_state)
        elif selected_algorithm_name == "Q-learning":
            agent.train(start_state, goal_state)
            solution = agent.solve(start_state, goal_state)
        else:
            solution = selected_algorithm_func(start_state, goal_state)
        end_time = time.perf_counter()
        solve_time = end_time - start_time
        solution_time_value = f"{solve_time:.5f} s"
        so_buoc_value = str(len(solution) - 1) if solution else "Not found"
        visited_nodes_value = str(solution[-1][1]) if solution and isinstance(solution[-1], tuple) else "0"
        generated_nodes_value = str(solution[-1][2]) if solution and isinstance(solution[-1], tuple) else "0"
        solution_path = solution

        for group_name, algos in algorithm_groups.items():
            if selected_algorithm_name in algos:
                key = f"{group_name}:{selected_algorithm_name}"
                algorithm_results[key] = {
                    "steps": int(so_buoc_value) if so_buoc_value.isdigit() else 0,
                    "time": float(solution_time_value.split()[0]),
                    "visited": int(visited_nodes_value),
                    "generated": int(generated_nodes_value)
                }
                break

running = True
while running:
    current_time = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if chart_window_active:
                print("Closing chart window")
                chart_window_active = False
                chart_window = None
                pygame.display.set_mode((screen_width, screen_height))
                draw_gui()
            else:
                print("Exiting program")
                running = False
        elif event.type == pygame.KEYDOWN:
            if selected_input_method == "Input" and input_active:
                #global start_state
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    result = validate_input(input_text)
                    if result:
                        start_state = result
                        input_active = False
                        error_message = ""
                        solution_path = []
                        animation_step = 0
                        so_buoc_value = "0"
                        visited_nodes_value = "0"
                        generated_nodes_value = "0"
                        solution_time_value = "0.00 s"
                        solving = False
                        paused_time = 0
                    else:
                        error_message = "Trạng thái không hợp lệ! Nhập 9 số từ 0 đến 8, không trùng nhau."
                else:
                    if event.unicode.isdigit() or event.unicode == " ":
                        input_text += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if chart_window_active:
                if close_button_rect.collidepoint(event.pos):
                    print("Closing chart window via button")
                    chart_window_active = False
                    chart_window = None
                    pygame.display.set_mode((screen_width, screen_height))
                    draw_gui()
            else:
                if dropdown_rect.collidepoint(event.pos):
                    dropdown_open = not dropdown_open
                    chart_dropdown_open = False
                elif dropdown_open:
                    for i, option in enumerate(dropdown_options):
                        rect = dropdown_options_rects[i]
                        if rect.collidepoint(event.pos):
                            selected_algorithm_name = option
                            selected_algorithm_func = algorithms.get(option)
                            dropdown_open = False
                            solution_path = []
                            animation_step = 0
                            thoi_gian_value = "0.00 s"
                            so_buoc_value = "0"
                            visited_nodes_value = "0"
                            generated_nodes_value = "0"
                            solution_time_value = "0.00 s"
                            solving = False
                            start_state = [[2, 0, 3], [1, 4, 6], [7, 5, 8]]
                            active_button = None
                            agent.trained = False
                            paused_time = 0
                            break
                elif chart_dropdown_rect.collidepoint(event.pos):
                    chart_dropdown_open = not chart_dropdown_open
                    dropdown_open = False
                elif chart_dropdown_open:
                    for i, group in enumerate(chart_groups):
                        if chart_group_rects[i].collidepoint(event.pos):
                            selected_chart_group = group
                            chart_dropdown_open = False
                            print(f"Selected chart group: {selected_chart_group}")
                            chart_files = generate_group_charts(selected_chart_group)
                            if chart_files:
                                open_chart_window(chart_files[0])
                            else:
                                print(f"No chart generated for {selected_chart_group}")
                            break
                elif nhap_radio_rect.collidepoint(event.pos):
                    selected_input_method = "Input"
                    input_active = True
                    input_text = ""
                    error_message = ""
                    agent.trained = False
                    solution_path = []
                    animation_step = 0
                    thoi_gian_value = "0.00 s"
                    so_buoc_value = "0"
                    visited_nodes_value = "0"
                    generated_nodes_value = "0"
                    solution_time_value = "0.00 s"
                    solving = False
                    paused_time = 0
                    skip_active = False
                    animation_delay = 300
                elif random_radio_rect.collidepoint(event.pos):
                    selected_input_method = "Random"
                    start_state = generate_random_puzzle()
                    agent.trained = False
                    solution_path = []
                    animation_step = 0
                    thoi_gian_value = "0.00 s"
                    so_buoc_value = "0"
                    visited_nodes_value = "0"
                    generated_nodes_value = "0"
                    solution_time_value = "0.00 s"
                    solving = False
                    paused_time = 0
                elif button_run_rect.collidepoint(event.pos):
                    active_button = "run"
                    if not solving:
                        if not solution_path:
                            start_solving()
                            draw_gui()
                        else:
                            solving = True
                            if paused_time > 0:
                                animation_start_time = current_time - paused_time
                                paused_time = 0
                elif button_stop_rect.collidepoint(event.pos):
                    active_button = "stop"
                    if solving:
                        solving = False
                        if animation_start_time > 0:
                            paused_time = current_time - animation_start_time
                elif button_exit_rect.collidepoint(event.pos):
                    active_button = "exit"
                    running = False
                elif button_chart_rect.collidepoint(event.pos):
                    active_button = "chart"
                    chart_dropdown_open = not chart_dropdown_open
                    dropdown_open = False
                elif button_skip_rect.collidepoint(event.pos):
                    skip_active = not skip_active
                    animation_delay = fast_delay if skip_active else 300
                    print(f"Skip toggled: {'Fast' if skip_active else 'Normal'} mode, delay={animation_delay}ms")

    if solving and solution_path:
        now = pygame.time.get_ticks()
        if animation_step < len(solution_path) and now - last_animation_time > delay:
            item = solution_path[animation_step]
            start_state = item[0] if isinstance(item, tuple) else item
            if isinstance(start_state, tuple):
                start_state = [list(row) for row in start_state]
            so_buoc_value = str(animation_step)
            visited_nodes_value = str(item[1]) if isinstance(item, tuple) else "0"
            generated_nodes_value = str(item[2]) if isinstance(item, tuple) else "0"
            animation_step += 1
            last_animation_time = now
        if animation_step < len(solution_path) and animation_start_time > 0:
            elapsed_time = current_time - animation_start_time
            thoi_gian_value = f"{elapsed_time:.2f} s"
        elif animation_step >= len(solution_path):
            solving = False
            animation_start_time = 0
            paused_time = 0
            skip_active = False
            animation_delay = 300

    if not chart_window_active:
        draw_gui()

pygame.quit()
sys.exit()
