import time
from typing import Optional, List, Dict
from pathlib import Path
import pygame
from PIL import Image, ImageSequence
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
        pygame.display.set_caption("Simulador de Interacción Robot PERI")
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.bg_color = bg_color
        self.text_color = (255, 255, 255)
        self.button_color = (0, 100, 200)
        self.button_text_color = (255, 255, 255)
        
        # Cargar font usando pathlib
        # Buscar en múltiples ubicaciones posibles
        display_dir = Path(__file__).parent  # Directorio donde está display.py
        project_root = display_dir.parent.parent  # Raíz del proyecto
        
        # Posibles ubicaciones de la fuente
        font_paths = [
            display_dir / "Fonts" / "LilitaOne-Regular.ttf",  # Junto a display.py
            project_root / "Fonts" / "LilitaOne-Regular.ttf",  # En raíz del proyecto
            Path("Fonts") / "LilitaOne-Regular.ttf",  # Relativa al directorio de ejecución
        ]
        
        font_loaded = False
        for font_path in font_paths:
            if font_path.exists():
                try:
                    self.font_question = pygame.font.Font(str(font_path), 50)
                    self.font_options = pygame.font.Font(str(font_path), 36)
                    self.font_body = pygame.font.Font(str(font_path), 28)
                    print(f"✅ Fuente cargada desde: {font_path}")
                    font_loaded = True
                    break
                except pygame.error as e:
                    print(f"⚠️  Error al cargar fuente desde {font_path}: {e}")
                    continue
        
        if not font_loaded:
            print("⚠️  No se encontró la fuente personalizada. Usando fuente por defecto.")
            self.font_question = pygame.font.Font(None, 60)
            self.font_options = pygame.font.Font(None, 45)
            self.font_body = pygame.font.Font(None, 34)
        
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
        """
        Carga un archivo GIF como animación.
        
        Args:
            name: Nombre identificador de la animación
            filepath: Ruta al archivo (str o Path)
            scale: Tupla (ancho, alto) para escalar
        """
        # Convertir a Path para manejo robusto
        gif_path = Path(filepath)
        
        if not gif_path.exists():
            print(f"⚠️  Advertencia: No se encontró el archivo GIF: {gif_path}")
            return
            
        try:
            pil_img = Image.open(str(gif_path))
            frames = []
            for frame in ImageSequence.Iterator(pil_img):
                duration = int(frame.info.get("duration", 100))
                frame_rgba = frame.convert("RGBA")
                surface = pygame.image.fromstring(
                    frame_rgba.tobytes(), 
                    frame_rgba.size, 
                    "RGBA"
                ).convert_alpha()
                
                if scale:
                    surface = pygame.transform.scale(surface, scale)
                frames.append((surface, duration))
                
            if frames:
                self.animations[name] = frames
                print(f"✅ Animación '{name}' cargada: {gif_path.name}")
        except Exception as e:
            print(f"❌ Error al cargar GIF '{name}' desde {gif_path}: {e}")
            
    def load_image(self, name, filepath, scale=None):
        """
        Carga una imagen estática (PNG, JPG, etc).
        
        Args:
            name: Nombre identificador de la imagen
            filepath: Ruta al archivo (str o Path)
            scale: Tupla (ancho, alto) para escalar
        """
        # Convertir a Path para manejo robusto
        img_path = Path(filepath)
        
        if not img_path.exists():
            print(f"⚠️  Advertencia: No se encontró el archivo de imagen: {img_path}")
            return
            
        try:
            image = pygame.image.load(str(img_path)).convert_alpha()
            if scale:
                image = pygame.transform.smoothscale(image, scale)
            self.images[name] = image
            print(f"✅ Imagen '{name}' cargada: {img_path.name}")
        except pygame.error as e:
            print(f"❌ Error al cargar imagen '{name}' desde {img_path}: {e}")
            
    def set_expression(self, name, loop=True):
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
    
    def quit(self):
        """Cierra pygame y limpia recursos"""
        self.running = False
        pygame.quit()
        print("✅ Display cerrado correctamente")
    
    # ========== NUEVOS MÉTODOS PARA QUIZ DE VERDADERO/FALSO ==========
    
    def show_true_false_question(self, question_text: str, timeout_seconds: int = 10) -> Optional[bool]:
        """
        Muestra una pregunta de verdadero/falso con botones táctiles.
        
        Args:
            question_text: Texto de la pregunta
            timeout_seconds: Tiempo límite para responder
            
        Returns:
            True, False, o None si se agota el tiempo
        """
        # Configuración de botones
        button_width = 300
        button_height = 120
        button_spacing = 80
        
        # Posiciones de los botones (centrados horizontalmente)
        center_x = self.width // 2
        buttons_y = self.height - 180
        
        true_button_rect = pygame.Rect(
            center_x - button_width - button_spacing // 2,
            buttons_y,
            button_width,
            button_height
        )
        
        false_button_rect = pygame.Rect(
            center_x + button_spacing // 2,
            buttons_y,
            button_width,
            button_height
        )
        
        # Colores
        true_color = (34, 139, 34)  # Verde
        false_color = (220, 20, 60)  # Rojo
        hover_brightness = 1.3
        
        # Timer
        start_time = pygame.time.get_ticks()
        
        # Loop de la pregunta
        while True:
            # Procesar eventos
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if true_button_rect.collidepoint(mouse_pos):
                        return True
                    elif false_button_rect.collidepoint(mouse_pos):
                        return False
            
            # Verificar timeout
            elapsed = (pygame.time.get_ticks() - start_time) / 1000
            if elapsed > timeout_seconds:
                return None
            
            remaining = int(timeout_seconds - elapsed)
            
            # Actualizar animación de fondo
            self.update_animation()
            
            # Dibujar fondo y animación
            self.draw_background_animation()
            
            # Dibujar pregunta
            self.draw_multiline_text(
                question_text,
                (self.width // 2, 150),
                self.font_question,
                max_width=45,
                color=(255, 255, 255)
            )
            
            # Dibujar timer
            timer_text = f"⏱️ {remaining}s"
            timer_surface = self.font_body.render(timer_text, True, (255, 255, 255))
            timer_rect = timer_surface.get_rect(center=(self.width // 2, buttons_y - 60))
            self.screen.blit(timer_surface, timer_rect)
            
            # Detectar hover para resaltar botones
            true_hover = true_button_rect.collidepoint(mouse_pos)
            false_hover = false_button_rect.collidepoint(mouse_pos)
            
            # Dibujar botón VERDADERO
            true_draw_color = true_color
            if true_hover:
                true_draw_color = tuple(min(int(c * hover_brightness), 255) for c in true_color)
            
            pygame.draw.rect(self.screen, true_draw_color, true_button_rect, border_radius=20)
            pygame.draw.rect(self.screen, (255, 255, 255), true_button_rect, width=3, border_radius=20)
            
            true_text = self.font_options.render("✓ VERDADERO", True, (255, 255, 255))
            true_text_rect = true_text.get_rect(center=true_button_rect.center)
            self.screen.blit(true_text, true_text_rect)
            
            # Dibujar botón FALSO
            false_draw_color = false_color
            if false_hover:
                false_draw_color = tuple(min(int(c * hover_brightness), 255) for c in false_color)
            
            pygame.draw.rect(self.screen, false_draw_color, false_button_rect, border_radius=20)
            pygame.draw.rect(self.screen, (255, 255, 255), false_button_rect, width=3, border_radius=20)
            
            false_text = self.font_options.render("✗ FALSO", True, (255, 255, 255))
            false_text_rect = false_text.get_rect(center=false_button_rect.center)
            self.screen.blit(false_text, false_text_rect)
            
            # Actualizar display
            pygame.display.flip()
            self.clock.tick(self.fps)
    
    def show_quiz_result_screen(self, is_correct: bool, explanation: str, 
                               points_earned: int, display_time: float = 4.0):
        """
        Muestra el resultado del quiz en pantalla con animación.
        
        Args:
            is_correct: Si la respuesta fue correcta
            explanation: Explicación de la respuesta
            points_earned: Puntos ganados
            display_time: Tiempo para mostrar el resultado (segundos)
        """
        # Cambiar expresión según resultado
        if is_correct:
            if hasattr(self, 'set_expression'):
                self.set_expression("feliz")
            result_color = (34, 139, 34)  # Verde
            result_text = f"🎉 ¡CORRECTO! +{points_earned} puntos"
        else:
            if hasattr(self, 'set_expression'):
                self.set_expression("neutro")
            result_color = (255, 165, 0)  # Naranja
            result_text = f"💡 Casi... +{points_earned} puntos"
        
        start_time = pygame.time.get_ticks()
        
        while (pygame.time.get_ticks() - start_time) / 1000 < display_time:
            # Procesar eventos (solo para no bloquear)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
            
            # Actualizar animación
            self.update_animation()
            
            # Dibujar fondo
            self.draw_background_animation()
            
            # Dibujar resultado
            result_surface = self.font_question.render(result_text, True, result_color)
            result_rect = result_surface.get_rect(center=(self.width // 2, 120))
            self.screen.blit(result_surface, result_rect)
            
            # Dibujar explicación
            self.draw_multiline_text(
                explanation,
                (self.width // 2, 250),
                self.font_body,
                max_width=55,
                color=(255, 255, 255)
            )
            
            # Actualizar display
            pygame.display.flip()
            self.clock.tick(self.fps)
        
###################################################################################
################################ Código anterior ##################################
###################################################################################

    def show_feedback_box(self, title: str, lines: List[str], icon: str = ""):
        """
        Muestra un cuadro de retroalimentación visual simulado en consola.

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
        Muestra una pregunta de quiz (Nivel 2) - MÉTODO LEGACY.
        
        NOTA: Este método está deprecado. Usa show_true_false_question() para el nuevo sistema.

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
        Muestra el resultado de un quiz (Nivel 2) - MÉTODO LEGACY.
        
        NOTA: Este método está deprecado. Usa show_quiz_result_screen() para el nuevo sistema.

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
