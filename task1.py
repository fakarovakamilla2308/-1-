import tkinter as tk
from tkinter import messagebox, font, ttk
import random
from enum import Enum


class ShapeType(Enum):
    CIRCLE = "circle"
    SQUARE = "square"


class GameState(Enum):
    PLAYING = "playing"
    WIN = "win"
    LOSE = "lose"


class Shape:
    def __init__(self, canvas, shape_type, color, row, col, cell_size):
        self.canvas = canvas
        self.shape_type = shape_type
        self.color = color
        self.row = row
        self.col = col
        self.cell_size = cell_size
        self.crossed = False
        self.is_last_crossed = False
        self.is_starting = False

        # Координаты центра фигуры
        self.x = col * cell_size + cell_size // 2
        self.y = row * cell_size + cell_size // 2
        self.radius = cell_size // 3

        # ID графических элементов на холсте
        self.shape_id = None
        self.fill_id = None
        self.glow_id = None
        self.cross_id1 = None
        self.cross_id2 = None
        self.start_cross_id1 = None
        self.start_cross_id2 = None

        self.draw()

    def draw(self):
        """Рисует фигуру на холсте"""
        # Удаляем старые элементы
        if self.shape_id:
            self.canvas.delete(self.shape_id)
        if self.fill_id:
            self.canvas.delete(self.fill_id)
        if self.glow_id:
            self.canvas.delete(self.glow_id)
        if self.cross_id1:
            self.canvas.delete(self.cross_id1)
        if self.cross_id2:
            self.canvas.delete(self.cross_id2)
        if self.start_cross_id1:
            self.canvas.delete(self.start_cross_id1)
        if self.start_cross_id2:
            self.canvas.delete(self.start_cross_id2)

        # Эффект свечения для последней зачеркнутой фигуры
        if self.is_last_crossed and self.crossed:
            self.glow_id = self.canvas.create_oval(
                self.x - self.radius - 8, self.y - self.radius - 8,
                self.x + self.radius + 8, self.y + self.radius + 8,
                fill="#FFF9C4", outline=""
            )
            self.canvas.tag_lower(self.glow_id)

        # Рисуем фигуру
        if self.shape_type == ShapeType.CIRCLE:
            # Внешний круг
            self.shape_id = self.canvas.create_oval(
                self.x - self.radius, self.y - self.radius,
                self.x + self.radius, self.y + self.radius,
                outline=self.color, width=3
            )
            # Внутренний круг
            self.fill_id = self.canvas.create_oval(
                self.x - self.radius + 3, self.y - self.radius + 3,
                self.x + self.radius - 3, self.y + self.radius - 3,
                fill=self._lighten_color(self.color, 0.7), outline=""
            )
        else:  # квадрат
            # Внешний квадрат
            self.shape_id = self.canvas.create_rectangle(
                self.x - self.radius, self.y - self.radius,
                self.x + self.radius, self.y + self.radius,
                outline=self.color, width=3
            )
            # Внутренний квадрат
            self.fill_id = self.canvas.create_rectangle(
                self.x - self.radius + 3, self.y - self.radius + 3,
                self.x + self.radius - 3, self.y + self.radius - 3,
                fill=self._lighten_color(self.color, 0.7), outline=""
            )

        # Если это начальная фигура (отмечена крестиком)
        if self.is_starting and not self.crossed:
            start_cross_size = self.cell_size // 4
            self.start_cross_id1 = self.canvas.create_line(
                self.x - start_cross_size, self.y - start_cross_size,
                self.x + start_cross_size, self.y + start_cross_size,
                fill="#FF7043", width=3, dash=(4, 2)
            )
            self.start_cross_id2 = self.canvas.create_line(
                self.x + start_cross_size, self.y - start_cross_size,
                self.x - start_cross_size, self.y + start_cross_size,
                fill="#FF7043", width=3, dash=(4, 2)
            )

        # Если фигура зачеркнута
        if self.crossed:
            cross_color = "#E53935" if self.is_last_crossed else "#FF7043"
            cross_size = self.cell_size // 2.2 if self.is_last_crossed else self.cell_size // 3.2
            width = 5 if self.is_last_crossed else 3

            # Рисуем крестик
            self.cross_id1 = self.canvas.create_line(
                self.x - cross_size, self.y - cross_size,
                self.x + cross_size, self.y + cross_size,
                fill=cross_color, width=width, capstyle=tk.ROUND
            )
            self.cross_id2 = self.canvas.create_line(
                self.x + cross_size, self.y - cross_size,
                self.x - cross_size, self.y + cross_size,
                fill=cross_color, width=width, capstyle=tk.ROUND
            )

    def _lighten_color(self, color_hex, amount=0.7):
        """Осветляет цвет"""
        if color_hex.startswith('#'):
            color_hex = color_hex[1:]
        r = int(color_hex[0:2], 16)
        g = int(color_hex[2:4], 16)
        b = int(color_hex[4:6], 16)

        light_r = min(255, int(r + (255 - r) * amount))
        light_g = min(255, int(g + (255 - g) * amount))
        light_b = min(255, int(b + (255 - b) * amount))

        return f'#{light_r:02x}{light_g:02x}{light_b:02x}'

    def contains_point(self, x, y):
        """Проверяет, находится ли точка внутри фигуры"""
        if self.shape_type == ShapeType.CIRCLE:
            distance = ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5
            return distance <= self.radius
        else:  # квадрат
            return (self.x - self.radius <= x <= self.x + self.radius and
                    self.y - self.radius <= y <= self.y + self.radius)


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Зачеркни фигуры")
        self.root.configure(bg="#F5F7FA")

        # Светлая цветовая палитра
        self.COLORS = [
            "#42A5F5",  # Светло-синий
            "#EF5350",  # Светло-красный
            "#66BB6A",  # Светло-зеленый
            "#FFA726",  # Светло-оранжевый
            "#AB47BC",  # Светло-фиолетовый
            "#26C6DA",  # Бирюзовый
            "#FFCA28",  # Желтый
        ]

        # Константы
        self.GRID_SIZE = 4
        self.CELL_SIZE = 100
        self.GRID_MARGIN = 25
        self.INFO_HEIGHT = 160

        # Шрифты
        self.title_font = font.Font(family="Arial", size=22, weight="bold")
        self.normal_font = font.Font(family="Arial", size=11)
        self.bold_font = font.Font(family="Arial", size=11, weight="bold")
        self.small_font = font.Font(family="Arial", size=9)

        self.setup_ui()
        self.reset_game()

    def setup_ui(self):
        """Создает светлый пользовательский интерфейс"""
        # Основной контейнер
        main_container = tk.Frame(self.root, bg="#F5F7FA")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Верхняя информационная панель
        self.info_frame = tk.Frame(main_container, bg="#FFFFFF", bd=1, relief=tk.RAISED)
        self.info_frame.pack(fill=tk.X, pady=(0, 10))

        # Игровое поле
        self.game_frame = tk.Frame(main_container, bg="#ECEFF1", bd=1, relief=tk.SUNKEN)
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        # Холст для игрового поля
        canvas_width = self.GRID_SIZE * self.CELL_SIZE + 2 * self.GRID_MARGIN
        canvas_height = self.GRID_SIZE * self.CELL_SIZE + 2 * self.GRID_MARGIN

        self.canvas = tk.Canvas(
            self.game_frame,
            width=canvas_width,
            height=canvas_height,
            bg="#FFFFFF",
            highlightthickness=0
        )
        self.canvas.pack(expand=True, padx=15, pady=15)

        # Привязываем обработчики событий
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.bind("<Leave>", lambda e: self.canvas.config(cursor=""))

        # Создаем элементы интерфейса
        self.create_info_panel()

    def create_info_panel(self):
        """Создает информационную панель"""
        # Заголовок и статистика
        header_frame = tk.Frame(self.info_frame, bg="#FFFFFF")
        header_frame.pack(fill=tk.X, padx=20, pady=15)

        # Заголовок
        title_label = tk.Label(
            header_frame,
            text="🎯 Зачеркни фигуры",
            font=self.title_font,
            bg="#FFFFFF",
            fg="#37474F"
        )
        title_label.pack(side=tk.LEFT)

        # Статистика
        stats_frame = tk.Frame(header_frame, bg="#FFFFFF")
        stats_frame.pack(side=tk.RIGHT)

        # Ходы
        moves_frame = tk.Frame(stats_frame, bg="#F0F4F7", relief=tk.RIDGE, bd=1)
        moves_frame.pack(side=tk.LEFT, padx=5)

        tk.Label(moves_frame, text="ХОДОВ", font=self.small_font,
                 bg="#F0F4F7", fg="#546E7A").pack(pady=(3, 0))
        self.moves_label = tk.Label(moves_frame, text="0", font=("Arial", 14, "bold"),
                                    bg="#F0F4F7", fg="#263238")
        self.moves_label.pack(pady=(0, 3))

        # Прогресс
        progress_frame = tk.Frame(stats_frame, bg="#F0F4F7", relief=tk.RIDGE, bd=1)
        progress_frame.pack(side=tk.LEFT, padx=5)

        tk.Label(progress_frame, text="ПРОГРЕСС", font=self.small_font,
                 bg="#F0F4F7", fg="#546E7A").pack(pady=(3, 0))
        self.crossed_label = tk.Label(progress_frame, text="0/16", font=("Arial", 14, "bold"),
                                      bg="#F0F4F7", fg="#263238")
        self.crossed_label.pack(pady=(0, 3))

        # Кнопка новой игры
        self.new_game_btn = tk.Button(
            stats_frame,
            text="🔄 Новая игра",
            command=self.reset_game,
            font=self.normal_font,
            bg="#42A5F5",
            fg="white",
            activebackground="#2196F3",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            pady=5
        )
        self.new_game_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Правила игры
        rules_frame = tk.Frame(self.info_frame, bg="#FAFBFC", bd=1, relief=tk.SUNKEN)
        rules_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        rules_label = tk.Label(
            rules_frame,
            text="📌 Правила игры:",
            font=self.bold_font,
            bg="#FAFBFC",
            fg="#455A64",
            anchor=tk.W
        )
        rules_label.pack(fill=tk.X, padx=10, pady=(5, 2))

        rules_text = tk.Label(
            rules_frame,
            text="1. Зачеркивайте фигуры, находящиеся на одной линии (по горизонтали или вертикали)\n" +
                 "2. Цвет ИЛИ форма должны совпадать с последней зачеркнутой фигурой\n" +
                 "3. Начинайте с фигуры, отмеченной крестиком",
            font=self.small_font,
            bg="#FAFBFC",
            fg="#607D8B",
            justify=tk.LEFT,
            anchor=tk.W
        )
        rules_text.pack(fill=tk.X, padx=10, pady=(0, 5))

    def draw_grid(self):
        """Рисует игровую сетку"""
        self.canvas.delete("grid")

        # Фон поля
        grid_rect = self.canvas.create_rectangle(
            self.GRID_MARGIN,
            self.GRID_MARGIN,
            self.GRID_MARGIN + self.GRID_SIZE * self.CELL_SIZE,
            self.GRID_MARGIN + self.GRID_SIZE * self.CELL_SIZE,
            fill="#FAFAFA",
            outline="#CFD8DC",
            width=2,
            tags="grid"
        )

        # Линии сетки
        for i in range(1, self.GRID_SIZE):
            # Вертикальные линии
            x = self.GRID_MARGIN + i * self.CELL_SIZE
            self.canvas.create_line(
                x, self.GRID_MARGIN,
                x, self.GRID_MARGIN + self.GRID_SIZE * self.CELL_SIZE,
                fill="#E0E0E0", width=1, tags="grid"
            )
            # Горизонтальные линии
            y = self.GRID_MARGIN + i * self.CELL_SIZE
            self.canvas.create_line(
                self.GRID_MARGIN, y,
                self.GRID_MARGIN + self.GRID_SIZE * self.CELL_SIZE, y,
                fill="#E0E0E0", width=1, tags="grid"
            )

    def reset_game(self):
        """Сбрасывает игру и генерирует новое поле"""
        self.canvas.delete("all")
        self.draw_grid()

        # Создаем игровое поле
        self.grid = []
        self.start_row = random.randint(0, self.GRID_SIZE - 1)
        self.start_col = random.randint(0, self.GRID_SIZE - 1)

        # Заполняем поле фигурами
        for row in range(self.GRID_SIZE):
            grid_row = []
            for col in range(self.GRID_SIZE):
                shape_type = random.choice([ShapeType.CIRCLE, ShapeType.SQUARE])
                color = random.choice(self.COLORS)
                shape = Shape(self.canvas, shape_type, color, row, col, self.CELL_SIZE)

                # Сдвигаем координаты с учетом отступов
                shape.x += self.GRID_MARGIN
                shape.y += self.GRID_MARGIN

                # Отмечаем начальную фигуру
                if row == self.start_row and col == self.start_col:
                    shape.is_starting = True
                    shape.crossed = True
                    shape.is_last_crossed = True
                    self.last_crossed = shape

                grid_row.append(shape)
            self.grid.append(grid_row)

        # Перерисовываем все фигуры
        for row in self.grid:
            for shape in row:
                shape.draw()

        # Убедимся, что есть хотя бы несколько возможных ходов
        self.ensure_possible_moves()

        self.game_state = GameState.PLAYING
        self.moves = 0
        self.total_figures = self.GRID_SIZE * self.GRID_SIZE
        self.crossed_figures = 1  # Начальная фигура уже зачеркнута

        # Обновляем информационную панель
        self.update_info_panel()

    def ensure_possible_moves(self):
        """Убеждаемся, что у начальной фигуры есть хотя бы один возможный ход"""
        start_shape = self.grid[self.start_row][self.start_col]
        possible_moves = self.get_possible_moves(start_shape)

        # Если нет возможных ходов, меняем цвет или форму соседней фигуры
        if not possible_moves:
            neighbors = []
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                r, c = self.start_row + dr, self.start_col + dc
                if 0 <= r < self.GRID_SIZE and 0 <= c < self.GRID_SIZE:
                    neighbors.append(self.grid[r][c])

            if neighbors:
                neighbor = neighbors[0]
                if random.choice([True, False]):
                    neighbor.color = start_shape.color
                else:
                    neighbor.shape_type = start_shape.shape_type
                neighbor.draw()

    def get_possible_moves(self, from_shape):
        """Возвращает список возможных фигур для зачеркивания из данной позиции"""
        possible_moves = []

        # Проверяем все клетки по горизонтали и вертикали
        for row in range(self.GRID_SIZE):
            if row != from_shape.row:
                continue
            for col in range(self.GRID_SIZE):
                shape = self.grid[row][col]
                if shape != from_shape and not shape.crossed:
                    # Проверяем совпадение цвета или формы
                    if (shape.color == from_shape.color or
                            shape.shape_type == from_shape.shape_type):
                        possible_moves.append(shape)

        for col in range(self.GRID_SIZE):
            if col != from_shape.col:
                continue
            for row in range(self.GRID_SIZE):
                shape = self.grid[row][col]
                if shape != from_shape and not shape.crossed:
                    # Проверяем совпадение цвета или формы
                    if (shape.color == from_shape.color or
                            shape.shape_type == from_shape.shape_type):
                        # Убираем дубликаты (фигуры на пересечении)
                        if shape not in possible_moves:
                            possible_moves.append(shape)

        return possible_moves

    def can_cross(self, shape):
        """Можно ли зачеркнуть данную фигуру из текущей позиции"""
        if shape.crossed:
            return False

        # Проверяем, находится ли фигура на одной линии с последней зачеркнутой
        if shape.row != self.last_crossed.row and shape.col != self.last_crossed.col:
            return False

        # Проверяем совпадение цвета или формы
        if (shape.color != self.last_crossed.color and
                shape.shape_type != self.last_crossed.shape_type):
            return False

        return True

    def cross_shape(self, shape):
        """Зачеркиваем фигуру"""
        if not self.can_cross(shape):
            messagebox.showwarning("Нельзя зачеркнуть",
                                   "Эту фигуру нельзя зачеркнуть!\n\n"
                                   "Фигура должна быть:\n"
                                   "1. На одной линии с последней зачеркнутой\n"
                                   "2. Иметь тот же цвет ИЛИ ту же форму")
            return False

        # Убираем пометку "последняя зачеркнутая" с предыдущей фигуры
        if self.last_crossed:
            self.last_crossed.is_last_crossed = False
            self.last_crossed.draw()

        # Зачеркиваем новую фигуру
        shape.crossed = True
        shape.is_last_crossed = True
        self.last_crossed = shape
        shape.draw()

        self.moves += 1
        self.crossed_figures += 1

        # Обновляем информационную панель
        self.update_info_panel()

        # Проверяем условия окончания игры
        if self.crossed_figures == self.total_figures:
            self.game_state = GameState.WIN
            self.show_game_over("🎉 ПОБЕДА!",
                                f"Поздравляем! Вы зачеркнули все фигуры!\n\n"
                                f"Ходов сделано: {self.moves}")
        else:
            # Проверяем, есть ли еще возможные ходы
            possible_moves = self.get_possible_moves(shape)
            if not possible_moves:
                self.game_state = GameState.LOSE
                self.show_game_over("💢 ИГРА ОКОНЧЕНА",
                                    f"Нет возможных ходов!\n\n"
                                    f"Зачеркнуто фигур: {self.crossed_figures} из {self.total_figures}")

        return True

    def update_info_panel(self):
        """Обновляет информационную панель"""
        self.moves_label.config(text=str(self.moves))
        self.crossed_label.config(text=f"{self.crossed_figures}/{self.total_figures}")

    def show_game_over(self, title, message):
        """Показывает сообщение об окончании игры"""
        result = messagebox.askyesno(title, f"{message}\n\nХотите сыграть еще раз?")
        if result:
            self.reset_game()

    def on_canvas_click(self, event):
        """Обработчик клика мыши по холсту"""
        if self.game_state != GameState.PLAYING:
            return

        # Преобразуем координаты мыши в координаты относительно игрового поля
        x = event.x - self.GRID_MARGIN
        y = event.y - self.GRID_MARGIN

        # Проверяем, находится ли клик внутри игрового поля
        if (0 <= x < self.GRID_SIZE * self.CELL_SIZE and
                0 <= y < self.GRID_SIZE * self.CELL_SIZE):

            # Ищем фигуру, содержащую точку клика
            for row in self.grid:
                for shape in row:
                    if shape.contains_point(x, y):
                        self.cross_shape(shape)
                        return

    def run(self):
        """Запускает главный цикл игры"""
        self.root.mainloop()


def main():
    root = tk.Tk()
    root.geometry("520x720")
    root.resizable(False, False)
    root.configure(bg="#F5F7FA")

    # Центрируем окно на экране
    root.update_idletasks()
    width = 520
    height = 720
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    game = Game(root)
    game.run()


if __name__ == "__main__":
    main()