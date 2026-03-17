import time
from dataclasses import dataclass, field
from typing import List


@dataclass
class GridStats:
    timestamp: float
    execution_time: float
    masks_tried: int
    success: bool
    cells_filled: int = 0
    recovered: bool = False


@dataclass
class PipelineMetrics:
    start_time: float = field(default_factory=time.time)
    total_grids_analyzed: int = 0
    total_grids_solved: int = 0
    total_grids_failed: int = 0
    total_grids_recovered: int = 0
    total_cells_filled: int = 0
    total_masks_tried: int = 0
    grid_history: List[GridStats] = field(default_factory=list)

    def start_grid(self):
        return time.time()

    def record_grid(self, start_timestamp, masks_tried, success, cells_filled=0, recovered=False):
        execution_time = time.time() - start_timestamp

        self.total_grids_analyzed += 1
        self.total_masks_tried += masks_tried
        self.total_cells_filled += cells_filled

        if success:
            self.total_grids_solved += 1
        else:
            self.total_grids_failed += 1

        if recovered:
            self.total_grids_recovered += 1

        grid_stat = GridStats(
            timestamp=start_timestamp,
            execution_time=execution_time,
            masks_tried=masks_tried,
            success=success,
            cells_filled=cells_filled,
            recovered=recovered
        )
        self.grid_history.append(grid_stat)

    def get_total_runtime(self):
        return time.time() - self.start_time

    def get_success_rate(self):
        if self.total_grids_analyzed == 0:
            return 0.0
        return (self.total_grids_solved / self.total_grids_analyzed) * 100

    def get_recovery_rate(self):
        if self.total_grids_failed == 0:
            return 0.0
        return (self.total_grids_recovered / self.total_grids_failed) * 100

    def get_average_execution_time(self):
        if not self.grid_history:
            return 0.0
        total_time = sum(stat.execution_time for stat in self.grid_history)
        return total_time / len(self.grid_history)

    def get_average_masks_per_grid(self):
        if self.total_grids_analyzed == 0:
            return 0.0
        return self.total_masks_tried / self.total_grids_analyzed

    def get_summary(self):
        return {
            "total_runtime": round(self.get_total_runtime(), 2),
            "grids_analyzed": self.total_grids_analyzed,
            "grids_solved": self.total_grids_solved,
            "grids_failed": self.total_grids_failed,
            "grids_recovered": self.total_grids_recovered,
            "success_rate": round(self.get_success_rate(), 2),
            "recovery_rate": round(self.get_recovery_rate(), 2),
            "total_cells_filled": self.total_cells_filled,
            "total_masks_tried": self.total_masks_tried,
            "avg_execution_time": round(self.get_average_execution_time(), 3),
            "avg_masks_per_grid": round(self.get_average_masks_per_grid(), 2)
        }

    def print_summary(self):
        summary = self.get_summary()
        print("\n" + "=" * 50)
        print("STATISTIQUES DE LA SESSION")
        print("=" * 50)
        print(f"Durée totale: {summary['total_runtime']}s")
        print(f"Grilles analysées: {summary['grids_analyzed']}")
        print(f"Grilles résolues: {summary['grids_solved']}")
        print(f"Grilles échouées: {summary['grids_failed']}")
        print(f"Grilles repêchées: {summary['grids_recovered']}")
        print(f"Taux de succès: {summary['success_rate']}%")
        print(f"Taux de repêchage: {summary['recovery_rate']}%")
        print(f"Cases cochées: {summary['total_cells_filled']}")
        print(f"Masques essayés: {summary['total_masks_tried']}")
        print(f"Temps moyen/grille: {summary['avg_execution_time']}s")
        print(f"Masques moyens/grille: {summary['avg_masks_per_grid']}")
        print("=" * 50 + "\n")

    def print_live_stats(self):
        recovery_display = f" | Repêchées: {self.total_grids_recovered}" if self.total_grids_recovered > 0 else ""
        print(f"\r[Grilles: {self.total_grids_analyzed} | Résolues: {self.total_grids_solved} | "
              f"Échouées: {self.total_grids_failed}{recovery_display} | Taux: {self.get_success_rate():.1f}%]", end="")

    def reset(self):
        self.start_time = time.time()
        self.total_grids_analyzed = 0
        self.total_grids_solved = 0
        self.total_grids_failed = 0
        self.total_grids_recovered = 0
        self.total_cells_filled = 0
        self.total_masks_tried = 0
        self.grid_history.clear()