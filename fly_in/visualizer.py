# import math
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# import matplotlib.colors as mcolors

# from .graph import Graph


# class MapVisualizer:
#     """Beautiful Matplotlib 2D animation for Fly-in drone simulation."""

#     def __init__(self, parsed_map, turns: list[list[str]]) -> None:
#         self.graph: Graph = parsed_map.graph
#         self.turns = turns
#         self.nb_drones = parsed_map.nb_drones
#         self.start_hub = parsed_map.start_hub
#         self.end_hub = parsed_map.end_hub

#         # Безопасно достаем словарь зон (подстрой под свой Graph, если нужно)
#         self.zones = getattr(self.graph, 'zones', {})
#         if not self.zones and hasattr(self.graph, '_zones'):
#             self.zones = getattr(self.graph, '_zones')

#         # Статичные смещения для дронов, чтобы они не слипались в одну точку (эффект роя)
#         self.drone_offsets = {}
#         for i in range(1, self.nb_drones + 1):
#             d_id = f"D{i}"
#             # Немного математики для красивого распределения по кругу
#             angle = i * 137.5 * math.pi / 180
#             radius = 0.15 + 0.1 * (i % 3)
#             self.drone_offsets[d_id] = (radius * math.cos(angle), radius * math.sin(angle))

#     def _get_coords(self, target: str) -> tuple[float, float]:
#         """Возвращает (x, y) для зоны или промежуточного канала."""
#         if target in self.zones:
#             z = self.zones[target]
#             return (z.x, z.y)
#         elif "-" in target:
#             # Если дрон в пути по restricted зоне (D1-zoneA-zoneB), ставим его посередине
#             z1, z2 = target.split("-")
#             if z1 in self.zones and z2 in self.zones:
#                 return (
#                     (self.zones[z1].x + self.zones[z2].x) / 2,
#                     (self.zones[z1].y + self.zones[z2].y) / 2
#                 )
#         return (0.0, 0.0)

#     def play(self) -> None:
#         """Запускает графический плеер симуляции."""
#         fig, ax = plt.subplots(figsize=(12, 8))
        
#         # Темная тема для красоты
#         ax.set_facecolor('#1e1e1e')
#         fig.patch.set_facecolor('#1e1e1e')
#         ax.set_title("Fly-in Mission Control", color='white', pad=20, fontsize=16, fontweight='bold')
        
#         # 1. Отрисовка карты (Граней/Связей)
#         drawn_edges = set()
#         adj = getattr(self.graph, 'adjacency', getattr(self.graph, '_adjacency', {}))
        
#         for z_name, zone in self.zones.items():
#             if z_name in adj:
#                 for neighbor in adj[z_name]:
#                     edge = tuple(sorted([z_name, neighbor]))
#                     if edge not in drawn_edges and neighbor in self.zones:
#                         nz = self.zones[neighbor]
#                         # Рисуем пунктирные линии связи
#                         ax.plot([zone.x, nz.x], [zone.y, nz.y], color='#444444', linestyle='--', zorder=1)
#                         drawn_edges.add(edge)

#         # 2. Отрисовка карты (Узлов/Зон)
#         for z_name, zone in self.zones.items():
#             # Если цвет из парсера не поддерживается, делаем его серым
#             color = zone.color if zone.color and zone.color in mcolors.CSS4_COLORS else '#555555'
            
#             # Точка зоны
#             ax.scatter(zone.x, zone.y, s=400, c=color, edgecolors='white', linewidth=1.5, zorder=2)
#             # Подпись зоны
#             ax.text(zone.x, zone.y + 0.35, z_name, color='white', ha='center', fontsize=9, zorder=4)

#         # 3. Подготовка роя дронов
#         drone_scatter = ax.scatter([], [], s=60, c='cyan', edgecolors='white', zorder=3)
#         turn_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white', fontsize=14, fontweight='bold')

#         # Рассчитываем позиции дронов на каждый кадр (ход)
#         drone_pos = {f"D{i}": self.start_hub for i in range(1, self.nb_drones + 1)}
#         frames_data = [drone_pos.copy()]
        
#         for turn_moves in self.turns:
#             for move in turn_moves:
#                 parts = move.split("-")
#                 d_id = parts[0]
#                 target = "-".join(parts[1:])  # Собирает zoneA-zoneB обратно, если нужно
#                 drone_pos[d_id] = target
#             frames_data.append(drone_pos.copy())

#         # Функция обновления для анимации
#         def update(frame_idx: int):
#             current_positions = frames_data[frame_idx]
#             x_coords = []
#             y_coords = []
            
#             for d_id, target in current_positions.items():
#                 cx, cy = self._get_coords(target)
#                 ox, oy = self.drone_offsets[d_id]
#                 x_coords.append(cx + ox)
#                 y_coords.append(cy + oy)
                
#             drone_scatter.set_offsets(list(zip(x_coords, y_coords)))
#             turn_text.set_text(f"Turn: {frame_idx} / {len(self.turns)}")
#             return drone_scatter, turn_text

#         # Запуск анимации (500 мс на один ход)
#         anim = animation.FuncAnimation(
#             fig, update, frames=len(frames_data), 
#             interval=500, blit=True, repeat=False
#         )
        
#         plt.axis('equal') # Сохраняем пропорции карты
#         plt.axis('off')   # Скрываем оси координат
#         plt.tight_layout()
#         plt.show()
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors

from .graph import Graph


class MapVisualizer:
    """Upgraded 2D visualizer for Fly-in with smooth easing, path tracing, and progress bars."""

    SUB_FRAMES_PER_MOVE = 20
    HOLD_FRAMES_AT_END = 40

    def __init__(self, parsed_map, turns: list[list[str]]) -> None:
        self.graph: Graph = parsed_map.graph
        self.turns = turns
        self.nb_drones = parsed_map.nb_drones
        self.start_hub = parsed_map.start_hub
        self.end_hub = parsed_map.end_hub

        self.zones = getattr(self.graph, 'zones', getattr(self.graph, '_zones', {}))

        self.drone_offsets = {}
        for i in range(1, self.nb_drones + 1):
            angle = i * 137.5 * math.pi / 180
            radius = 0.12 + 0.06 * (i % 3)
            self.drone_offsets[f"D{i}"] = (radius * math.cos(angle), radius * math.sin(angle))

    def _get_coords(self, target: str) -> tuple[float, float]:
        if target in self.zones:
            z = self.zones[target]
            return (float(z.x), float(z.y))
        elif "-" in target:
            z1, z2 = target.split("-")
            if z1 in self.zones and z2 in self.zones:
                return (
                    (self.zones[z1].x + self.zones[z2].x) / 2.0,
                    (self.zones[z1].y + self.zones[z2].y) / 2.0
                )
        return (0.0, 0.0)

    def play(self) -> None:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bg_color = '#0f172a'
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        drawn_edges = set()
        adj = getattr(self.graph, 'adjacency', getattr(self.graph, '_adjacency', {}))
        
        for z_name, zone in self.zones.items():
            if z_name in adj:
                for neighbor in adj[z_name]:
                    edge = tuple(sorted([z_name, neighbor]))
                    if edge not in drawn_edges and neighbor in self.zones:
                        nz = self.zones[neighbor]
                        ax.plot(
                            [zone.x, nz.x], [zone.y, nz.y],
                            color='#334155', linestyle='-', linewidth=2, zorder=1
                        )
                        drawn_edges.add(edge)

        active_path_line, = ax.plot([], [], color='#facc15', linestyle='--', linewidth=3, zorder=1.5, alpha=0.9)

        for z_name, zone in self.zones.items():
            color = zone.color.lower() if zone.color and zone.color.lower() in mcolors.CSS4_COLORS else '#64748b'
            
            if z_name == self.start_hub:
                color = '#10b981'
            elif z_name == self.end_hub:
                color = '#ef4444'

            ax.scatter(zone.x, zone.y, s=550, c=color, edgecolors='#ffffff', linewidth=1.5, zorder=2)
            ax.text(
                zone.x, zone.y + 0.35, z_name,
                color='#f8fafc', ha='center', fontsize=11, fontweight='bold', zorder=4,
                bbox=dict(facecolor='#000000', alpha=0.4, edgecolor='none', boxstyle='round,pad=0.2')
            )

        turn_text = ax.text(0.02, 0.94, '', transform=ax.transAxes, color='#38bdf8', fontsize=15, fontweight='bold')
        move_text = ax.text(0.02, 0.89, '', transform=ax.transAxes, color='#94a3b8', fontsize=12)
        stats_text = ax.text(0.02, 0.83, '', transform=ax.transAxes, color='#cbd5e1', fontsize=11)
        
        progress_bg, = ax.plot([0.02, 0.98], [0.03, 0.03], transform=ax.transAxes, color='#1e293b', linewidth=4)
        progress_bar, = ax.plot([], [], transform=ax.transAxes, color='#38bdf8', linewidth=4)

        drone_dots = ax.scatter([], [], s=90, c='#06b6d4', edgecolors='#ffffff', linewidth=1.5, zorder=3)

        current_positions = {f"D{i}": self.start_hub for i in range(1, self.nb_drones + 1)}
        atomic_moves = []

        for turn_idx, turn_moves in enumerate(self.turns, start=1):
            turn_total_moves = len(turn_moves)
            for sub_idx, move in enumerate(turn_moves, start=1):
                parts = move.split("-")
                d_id = parts[0]
                target = "-".join(parts[1:])
                from_pos = current_positions[d_id]
                
                atomic_moves.append({
                    "d_id": d_id,
                    "from": from_pos,
                    "to": target,
                    "turn": turn_idx,
                    "sub_idx": sub_idx,
                    "sub_total": turn_total_moves,
                    "move_str": move,
                    "base_positions": current_positions.copy()
                })
                current_positions[d_id] = target

        total_moves = len(atomic_moves)
        total_move_frames = total_moves * self.SUB_FRAMES_PER_MOVE if total_moves > 0 else 0
        total_frames = total_move_frames + self.HOLD_FRAMES_AT_END

        def update(frame_idx: int):
            if frame_idx >= total_move_frames:
                active_positions = current_positions.copy()
                turn_str = f"Turn: {len(self.turns)} / {len(self.turns)} (Completed)"
                move_str = "Status: Simulation Finished"
                active_path_line.set_data([], [])
                progress_bar.set_data([0.02, 0.98], [0.03, 0.03])
            else:
                move_idx = frame_idx // self.SUB_FRAMES_PER_MOVE
                raw_progress = (frame_idx % self.SUB_FRAMES_PER_MOVE) / self.SUB_FRAMES_PER_MOVE
                
                progress = raw_progress * raw_progress * (3.0 - 2.0 * raw_progress)

                move_info = atomic_moves[move_idx]
                active_positions = move_info["base_positions"].copy()
                
                moving_drone = move_info["d_id"]
                p_start = self._get_coords(move_info["from"])
                p_end = self._get_coords(move_info["to"])

                cx = p_start[0] + (p_end[0] - p_start[0]) * progress
                cy = p_start[1] + (p_end[1] - p_start[1]) * progress

                active_positions[moving_drone] = (cx, cy)
                
                active_path_line.set_data([p_start[0], p_end[0]], [p_start[1], p_end[1]])
                
                sim_progress = frame_idx / total_move_frames
                bar_end = 0.02 + (0.96 * sim_progress)
                progress_bar.set_data([0.02, bar_end], [0.03, 0.03])
                
                turn_str = f"Turn: {move_info['turn']} / {len(self.turns)} [Sub-step {move_info['sub_idx']}/{move_info['sub_total']}]"
                move_str = f"Action: {move_info['move_str']}"

            x_coords, y_coords = [], []
            for d_id, pos in active_positions.items():
                if isinstance(pos, tuple):
                    cx, cy = pos
                else:
                    cx, cy = self._get_coords(pos)

                ox, oy = self.drone_offsets[d_id]
                x_coords.append(cx + ox)
                y_coords.append(cy + oy)

            if frame_idx >= total_move_frames:
                delivered_count = sum(1 for pos in current_positions.values() if pos == self.end_hub)
            else:
                delivered_count = sum(1 for pos in active_positions.values() if isinstance(pos, str) and pos == self.end_hub)

            drone_dots.set_offsets(list(zip(x_coords, y_coords)))

            turn_text.set_text(turn_str)
            move_text.set_text(move_str)
            stats_text.set_text(f"Drones Total: {self.nb_drones}\nDelivered: {delivered_count}")

            return drone_dots, turn_text, move_text, stats_text, active_path_line, progress_bar

        anim = animation.FuncAnimation(
            fig, update, frames=total_frames + 1,
            interval=40, blit=False, repeat=False
        )

        plt.axis('equal')
        plt.axis('off')
        plt.tight_layout()
        plt.show()