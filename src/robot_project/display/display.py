import time
from typing import Optional, List, Dict
import pygame
from PIL import Image, ImageSequence
import os
import textwrap

###################################################################################
############################## Código Display Nuevo ###############################
###################################################################################

class Display:
    """Pantalla táctil para mostrar información visual con animaciones GIF"""
    
    def __init__(self, screen_size=(1024, 600), fps=60, bg_color=(0, 0, 0)):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(screen_size)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Simulador de Interacción Robot")
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.bg_color = bg_color
        self.text_color = (255, 255, 255)
        self.button_color = (0, 100, 200)
        self.button_text_color = (255, 255, 255)
        
        # Cargar font
        try:
            font_path = os.path.join("Fonts", "LilitaOne-Regular.ttf") 
            self.font_question = pygame.font.Font(font_path, 50)
            self.font_options = pygame.font.Font(font_path, 24)
            self.font_body = pygame.font.Font(font_path, 28)
        except pygame.error:
            print("Advertencia: No se encontró la fuente personalizada. Usando fuente por defecto.")
            self.font_question = pygame.font.Font(None, 60)
            self.font_options = pygame.font.Font(None, 40)
            self.font_body = pygame.font.Font(None, 30)
        
        
        self.animations = {}
        self.current_state_name = None
        self.current_frames = []
        self.frame_index = 0
        self._last_update = 0
        self.loop_animation = True
        
        # Imágenes adicionales (QR, etc)
        self.images = {}
        
        # Control de ejecución
        self.running = True
        
    def load_gif(self, name, filepath, scale=None):
        """Carga un archivo GIF como animación"""
        if not os.path.exists(filepath):
            print(f"Advertencia: No se encontró el archivo GIF: {filepath}")
            return
        pil_img = Image.open(filepath)
        frames = []
        for frame in ImageSequence.Iterator(pil_img):
            duration = int(frame.info.get("duration", 100))
            frame_rgba = frame.convert("RGBA")
            surface = pygame.image.fromstring(frame_rgba.tobytes(), frame_rgba.size, "RGBA").convert_alpha()
            if scale:
                surface = pygame.transform.scale(surface, scale)
            frames.append((surface, duration))
        if frames:
            self.animations[name] = frames
            print(f"-> Animación '{name}' cargada correctamente.")
            
    def load_image(self, name, filepath, scale=None):
        """Carga una imagen estática (PNG, JPG, etc)"""
        if not os.path.exists(filepath):
            print(f"Advertencia: No se encontró el archivo de imagen: {filepath}")
            return
        try:
            image = pygame.image.load(filepath).convert_alpha()
            if scale:
                image = pygame.transform.smoothscale(image, scale)
            self.images[name] = image
            print(f"-> Imagen '{name}' cargada correctamente.")
        except pygame.error as e:
            print(f"Error al cargar la imagen {filepath}: {e}")
            
    def set_expression(self, name, loop = True):
        """Establece la expresión/animación actual"""
        if name in self.animations and self.current_state_name != name:
            self.current_state_name = name
            self.current_frames = self.animations[name]
            self.frame_index = 0
            self._last_update = pygame.time.get_ticks()
            self.loop_animation = loop

    def update_animation(self):
        """Actualiza el frame de la animación actual. Retorna True si terminó el ciclo."""
        if not self.current_frames: 
            return False
        
        now = pygame.time.get_ticks()
        _, duration = self.current_frames[self.frame_index]
        
        if now - self._last_update > duration:
            self.frame_index += 1
            self._last_update = now
            
            if self.frame_index >= len(self.current_frames):
                if self.loop_animation:
                    self.frame_index = 0
                else:
                    # Mantiene el último frame si no es loop
                    self.frame_index = len(self.current_frames) - 1 
                return True # Devuelve True para indicar que el ciclo terminó
        return False
            
    def draw_background_animation(self):
        """Dibuja el fondo con la animación actual"""
        self.screen.fill(self.bg_color)
        if self.current_frames:
            surface, _ = self.current_frames[self.frame_index]
            rect = surface.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(surface, rect)
            
    def draw_multiline_text(self, text, position, font, max_width, color=None):
        """Dibuja texto con múltiples líneas centrado"""
        if color is None:
            color = self.text_color
        wrapped_lines = textwrap.wrap(text, width=max_width)
        y = position[1]
        for line in wrapped_lines:
            text_surface = font.render(line, True, color)
            rect = text_surface.get_rect(center=(position[0], y))
            self.screen.blit(text_surface, rect)
            y += font.get_height()
            
    def draw_button(self, text, rect, font):
        """Dibuja un botón interactivo"""
        pygame.draw.rect(self.screen, self.button_color, rect, border_radius=15)
        text_surf = font.render(text, True, self.button_text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_image(self, image_name_or_surface, position_center):
        """Dibuja una imagen en la posición especificada"""
        
        if isinstance(image_name_or_surface, str):
            if image_name_or_surface not in self.images:
                return
            image_surface = self.images[image_name_or_surface]
        else:
            image_surface = image_name_or_surface
            
        rect = image_surface.get_rect(center=position_center)
        self.screen.blit(image_surface, rect)

    def process_events(self):
        """Procesa eventos de pygame. Retorna False si se debe cerrar la aplicación."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                return False
        return True
    
    def update_display(self):
        """Actualiza la pantalla y mantiene el FPS"""
        pygame.display.flip()
        self.clock.tick(self.fps)
    
    def render_frame(self, text="", show_qr=False):
        """Renderiza un frame completo con animación, texto opcional y/o código QR"""
        self.draw_background_animation()
        
        if show_qr and "qr" in self.images:
            # Dibuja el QR centrado arriba
            self.draw_image("qr", (self.width // 2, self.height // 2 - 50))
            # Texto abajo del QR
            if text:
                self.draw_multiline_text(text, 
                                        (self.width // 2, self.height - 100), 
                                        self.font_body, 
                                        max_width=60)
        elif text:
            # Solo texto en la parte inferior
            self.draw_multiline_text(text, 
                                    (self.width // 2, self.height - 100), 
                                    self.font_body, 
                                    max_width=60)
        
        self.update_display()
        
###################################################################################
################################ Código anterior ##################################
###################################################################################

    def show_feedback_box(self, title: str, lines: List[str], icon: str = ""):
        """
        Muestra un cuadro de retroalimentación visual simulado.

        Args:
            title: Título del cuadro
            lines: Lista de líneas de texto
            icon: Emoji o icono opcional
        """
        width = 50
        print("\n" + "┌" + "─" * width + "┐")
        print(f"│ {icon} {title:<{width-4}} │")
        print("│" + " " * width + "│")

        for line in lines:
            # Dividir líneas largas
            if len(line) > width - 4:
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + word) < width - 4:
                        current_line += word + " "
                    else:
                        print(f"│ {current_line:<{width-2}} │")
                        current_line = word + " "
                if current_line:
                    print(f"│ {current_line:<{width-2}} │")
            else:
                print(f"│ {line:<{width-2}} │")

        print("└" + "─" * width + "┘")

    def show_classification_result(self, correct: bool, item: str, container: str,
                                   extra_info: str = ""):
        """
        Muestra el resultado de clasificación (Nivel 1).

        Args:
            correct: Si fue correcta la clasificación
            item: Nombre del residuo
            container: Contenedor correcto
            extra_info: Información adicional educativa
        """
        if correct:
            self.show_feedback_box(
                "✓ ¡Correcto!",
                [
                    f"🗑️  {item} → {container}",
                    extra_info if extra_info else ""
                ],
                "✅"
            )
        else:
            self.show_feedback_box(
                "ℹ️ Te ayudo con eso",
                [
                    f"🗑️  {item} → {container}",
                    extra_info if extra_info else ""
                ],
                "🤖"
            )

    def show_quiz_question(self, question: str, options: List[Dict[str, str]],
                          timer_seconds: int = 10) -> Optional[str]:
        """
        Muestra una pregunta de quiz (Nivel 2).

        Args:
            question: Texto de la pregunta
            options: Lista de opciones [{'key': 'A', 'text': 'Orgánico', 'icon': '🟢'}]
            timer_seconds: Segundos para responder

        Returns:
            Letra de la opción seleccionada (A, B, C)
        """
        width = 50
        print("\n" + "┌" + "─" * width + "┐")
        print(f"│ 🎮 DESAFÍO RÁPIDO{' ' * (width - 18)}│")
        print("│" + " " * width + "│")
        print(f"│ {question:<{width-2}} │")
        print("│" + " " * width + "│")

        for opt in options:
            opt_text = f"  [{opt['key']}] {opt['icon']} {opt['text']}"
            print(f"│ {opt_text:<{width-2}} │")

        print("│" + " " * width + "│")
        print(f"│ ⏱️  {timer_seconds} segundos{' ' * (width - 17)}│")
        print("└" + "─" * width + "┘")

        # Simular selección
        print(f"\n[PANTALLA TÁCTIL] Selecciona una opción ({', '.join([o['key'] for o in options])}): ", end="")
        response = input().strip().upper()

        if response in [o['key'] for o in options]:
            return response
        else:
            print("⚠️ Opción inválida, se considera sin respuesta")
            return None

    def show_quiz_result(self, correct: bool, selected: str, correct_answer: str,
                        points: int, explanation: str, streak: int = 0):
        """
        Muestra el resultado de un quiz (Nivel 2).

        Args:
            correct: Si la respuesta fue correcta
            selected: Opción seleccionada
            correct_answer: Opción correcta
            points: Puntos ganados
            explanation: Explicación educativa
            streak: Racha de respuestas correctas
        """
        if correct:
            streak_stars = "⭐" * min(streak, 5)
            self.show_feedback_box(
                f"✓ ¡CORRECTO! +{points} puntos",
                [
                    explanation,
                    f"Racha: {streak_stars} ({streak} seguidas)" if streak > 0 else ""
                ],
                "🎉"
            )
        else:
            self.show_feedback_box(
                f"ℹ️ Casi... +{points // 2} puntos",
                [
                    f"Respuesta correcta: {correct_answer}",
                    f"💡 {explanation}"
                ],
                "📚"
            )

    def show_impact_stats(self, item: str, local_impact: str,
                         total_recycled: int, total_impact: Dict[str, str],
                         ranking: str = ""):
        """
        Muestra estadísticas de impacto personalizadas (Nivel 3).

        Args:
            item: Residuo reciclado
            local_impact: Impacto local específico
            total_recycled: Total de items reciclados por el usuario
            total_impact: Dict con impactos acumulados
            ranking: Posición en ranking (opcional)
        """
        width = 50
        print("\n" + "┌" + "─" * width + "┐")
        print(f"│ 🌍 TU IMPACTO HOY{' ' * (width - 16)}│")
        print("│" + " " * width + "│")
        print(f"│ {local_impact:<{width-2}} │")
        print("│" + " " * width + "│")
        print(f"│ 📊 TU IMPACTO TOTAL:{' ' * (width - 22)}│")
        print(f"│ • {total_recycled} items reciclados{' ' * (width - 25 - len(str(total_recycled)))}│")

        for key, value in total_impact.items():
            line = f"• {value}"
            print(f"│ {line:<{width-2}} │")

        if ranking:
            print("│" + " " * width + "│")
            print(f"│ {ranking:<{width-2}} │")

        print("└" + "─" * width + "┘")

    def show_achievement_unlocked(self, achievement_name: str, achievement_icon: str,
                                  description: str, points: int):
        """
        Muestra un logro desbloqueado.

        Args:
            achievement_name: Nombre del logro
            achievement_icon: Icono del logro
            description: Descripción
            points: Puntos otorgados
        """
        self.show_feedback_box(
            "🏆 ¡LOGRO DESBLOQUEADO!",
            [
                f"{achievement_icon} {achievement_name}",
                description,
                f"🎁 +{points} Eco-Puntos"
            ],
            "✨"
        )

    def clear(self):
        """Limpia la pantalla (simula borrado de display)."""
        print("\n" + "🖥️  [DISPLAY] Pantalla limpiada\n")
