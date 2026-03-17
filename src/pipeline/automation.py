import os
import time
from dataclasses import dataclass
from typing import Tuple
import numpy as np
import pyautogui
import cv2

from src.board import identification, extract
from src.solver import solver
from src.runner import apply_solution, starter
from src.utils.logger import logger
from src.pipeline.metrics import PipelineMetrics


@dataclass
class Config:
    assets_folder: str = 'assets'
    scroll_amount: int = 500
    processing_delay: float = 0.25

    green_button_zone: Tuple[int, int, int, int] = (500, 800, 510, 810)
    green_button_color: Tuple[int, int, int, 255] = (16, 219, 0, 255)
    green_button_timeout: float = 4.0
    green_button_click_pos: Tuple[int, int] = (505, 805)

    red_button_zone: Tuple[int, int, int, int] = (710, 770, 720, 780)
    red_button_color: Tuple[int, int, int, 255] = (219, 0, 0, 255)
    red_button_timeout: float = 0.20

    color_tolerance: int = 5
    poll_interval: float = 0.05

    topleft_region: Tuple[int, int, int, int] = (0, 0, 511, 84)
    topleft_template_path: str = 'assets/screen_checks/topleft.png'
    topleft_match_threshold: float = 0.95
    topleft_max_offset: int = 5
    recovery_click_pos: Tuple[int, int] = (400, 1000)
    recovery_wait: float = 0.5


class PicrossAutomation:
    def __init__(self, config: Config = Config()):
        self.config = config
        self.metrics = PipelineMetrics()
        self._setup_paths()
        self._cache_masks()
        self._load_topleft_template()

    def _setup_paths(self):
        self.mask_folder = os.path.join(self.config.assets_folder, 'masks')
        self.templates_folder = os.path.join(self.config.assets_folder, 'templates')

    def _cache_masks(self):
        self.mask_paths = [
            os.path.join(self.mask_folder, name)
            for name in os.listdir(self.mask_folder)
        ]
        logger.debug(f"Chargé {len(self.mask_paths)} masques en cache")

    def _load_topleft_template(self):
        if os.path.exists(self.config.topleft_template_path):
            self.topleft_template = cv2.imread(self.config.topleft_template_path)
            logger.debug(f"Template topleft chargé: {self.config.topleft_template_path}")
        else:
            self.topleft_template = None
            logger.warning(f"Template topleft non trouvé: {self.config.topleft_template_path}")

    def run(self):
        starter.wait_for_f9()
        pyautogui.scroll(self.config.scroll_amount)

        try:
            while self._process_single_game():
                self._change_game()
                self.metrics.print_live_stats()
        except KeyboardInterrupt:
            logger.info("\n\nArrêt demandé par l'utilisateur")
        finally:
            self.metrics.print_summary()

    def _process_single_game(self):
        grid_start = self.metrics.start_grid()
        time.sleep(self.config.processing_delay)
        screen_img = starter.capture()

        masks_tried = 0
        for mask_path in self.mask_paths:
            masks_tried += 1
            result = self._try_solve_with_mask(screen_img, mask_path)
            if result is not None:
                data, solution = result
                cells_filled = self._count_filled_cells(solution)
                self._apply_solution(data, solution)
                self.metrics.record_grid(grid_start, masks_tried, True, cells_filled, False)
                return True

        logger.debug("Aucune solution trouvée avec aucun masque")

        if self._check_and_recover():
            logger.info("Récupération effectuée, nouvelle tentative...")
            self.metrics.record_grid(grid_start, masks_tried, False, 0, True)
            return True

        self.metrics.record_grid(grid_start, masks_tried, False, 0, False)
        return False

    def _check_and_recover(self):
        if self.topleft_template is None:
            logger.warning("Template topleft non chargé, impossible de vérifier")
            return False

        logger.info("Vérification de la zone topleft pour récupération...")

        x1, y1, x2, y2 = self.config.topleft_region
        screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
        screen_region = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        if self._images_match(screen_region, self.topleft_template):
            logger.info("Match détecté ! Tentative de récupération...")
            x, y = self.config.recovery_click_pos
            pyautogui.mouseDown(x, y)
            pyautogui.mouseUp(x, y)
            time.sleep(self.config.recovery_wait)
            return True

        logger.warning("Pas de match topleft, pas de récupération possible")
        return False

    def _images_match(self, img1, img2):
        if img1.shape != img2.shape:
            logger.warning(f"Tailles différentes: {img1.shape} vs {img2.shape}")
            return False

        h, w = img2.shape[:2]
        max_offset = self.config.topleft_max_offset
        best_match = 0.0

        for dy in range(-max_offset, max_offset + 1):
            for dx in range(-max_offset, max_offset + 1):
                y1 = max(0, dy)
                y2 = min(h, h + dy)
                x1 = max(0, dx)
                x2 = min(w, w + dx)

                crop1 = img1[y1:y2, x1:x2]

                y1_ref = max(0, -dy)
                y2_ref = min(h, h - dy)
                x1_ref = max(0, -dx)
                x2_ref = min(w, w - dx)

                crop2 = img2[y1_ref:y2_ref, x1_ref:x2_ref]

                if crop1.shape == crop2.shape and crop1.size > 0:
                    similarity = self._calculate_similarity(crop1, crop2)
                    best_match = max(best_match, similarity)

        logger.debug(f"Meilleure similarité: {best_match:.3f} (seuil: {self.config.topleft_match_threshold})")
        return best_match >= self.config.topleft_match_threshold

    def _calculate_similarity(self, img1, img2):
        diff = cv2.absdiff(img1, img2)
        similarity = 1.0 - (np.mean(diff) / 255.0)
        return similarity

    def _try_solve_with_mask(self, screen_img, mask_path):
        data = self._extract_picross(screen_img, mask_path)
        if data is None:
            return None

        hints = self._extract_and_identify_hints(data)
        if hints is None:
            return None

        solution = self._solve_puzzle(hints)
        if solution is None:
            return None

        return data, solution

    def _extract_picross(self, screen_img, mask_path):
        logger.debug("=== EXTRACTION DU PICROSS ===")
        return extract.extract_picross_from_image(screen_img, mask_path, show=False)

    def _extract_and_identify_hints(self, data):
        logger.debug("=== EXTRACTION DES HINTS ===")
        hints = identification.extract_hints(data, show=False)

        logger.debug("=== IDENTIFICATION DES HINTS PAR TEMPLATE MATCHING ===")
        identified_hints = identification.identify_hints(hints, self.templates_folder)

        if not self._validate_hints(identified_hints["row_hints"], "Row"):
            return None

        if not self._validate_hints(identified_hints["col_hints"], "Col"):
            return None

        return identified_hints

    def _validate_hints(self, hints, hint_type):
        logger.debug(f"\n{hint_type} hints identifiés:")
        for idx, hint in enumerate(hints):
            logger.debug(f"  {hint_type} {idx}: {hint}")
            if not hint:
                logger.warning(f"  -> Pas de hint pour {hint_type} {idx}")
                return False
        return True

    def _solve_puzzle(self, identified_hints):
        logger.debug("=== RÉSOLUTION DU PICROSS 5x5 ===")
        row_hints = identified_hints["row_hints"]
        col_hints = identified_hints["col_hints"]

        solution = solver.solve_picross(row_hints, col_hints)

        if solution is not None:
            logger.info("=== SOLUTION FINALE ===")
            solver.print_grid(solution)
        else:
            logger.warning("Aucune solution trouvée avec ce masque")

        return solution

    def _apply_solution(self, data, solution):
        apply_solution.apply_solution_on_screen(picross_data=data, solution=solution)

    def _count_filled_cells(self, solution):
        return int(np.sum(solution == 1))

    def _change_game(self):
        logger.debug("Attente du bouton vert...")
        self._wait_for_color(
            self.config.green_button_zone,
            self.config.green_button_color[:3],
            self.config.green_button_timeout
        )

        logger.debug("Bouton prêt ! Click...")
        x, y = self.config.green_button_click_pos
        pyautogui.mouseDown(x, y)
        pyautogui.mouseUp(x, y)

        self._wait_for_no_color(
            self.config.red_button_zone,
            self.config.red_button_color[:3],
            self.config.red_button_timeout
        )

        pyautogui.scroll(self.config.scroll_amount)
        logger.info("Jeu changé")

    def _wait_for_color(self, zone, target_rgb, timeout):
        x1, y1, x2, y2 = zone
        start_time = time.time()

        while time.time() - start_time < timeout:
            screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
            avg_color = np.array(screenshot).mean(axis=(0, 1)).astype(int)

            if np.allclose(avg_color, target_rgb, atol=self.config.color_tolerance):
                return True

            time.sleep(self.config.poll_interval)

        return False

    def _wait_for_no_color(self, zone, unwanted_rgb, timeout):
        x1, y1, x2, y2 = zone
        start_time = time.time()

        while time.time() - start_time < timeout:
            screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
            avg_color = np.array(screenshot).mean(axis=(0, 1)).astype(int)

            if not np.allclose(avg_color, unwanted_rgb, atol=self.config.color_tolerance):
                return True

            time.sleep(self.config.poll_interval)

        return False


def main():
    automation = PicrossAutomation()
    automation.run()


if __name__ == "__main__":
    main()