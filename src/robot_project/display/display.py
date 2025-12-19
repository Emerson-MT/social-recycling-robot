import time
import math
from typing import Optional, List, Dict
from pathlib import Path
import pygame
from PIL import Image, ImageSequence
import textwrap
import os

###################################################################################
############################## Código Display Nuevo ###############################
###################################################################################

class Display:
    """Pantalla táctil para mostrar información visual con animaciones GIF"""
    
    def __init__(self, screen_size=(1024, 600), fps=60, bg_color=(0, 0, 0)):
        # Desactivar teclado virtual en pantallas táctiles
        os.environ['SDL_VIDEO_ALLOW_SCREENSAVER'] = '1'
        os.environ['SDL_MOUSE_TOUCH_EVENTS'] = '1'
        os.environ['SDL_TOUCH_MOUSE_EVENTS'] = '0'
        
        pygame.init()
        pygame.font.init()
        
        # Configurar pantalla completa
        # Usar FULLSCREEN para pantalla completa real
        # o NOFRAME para ventana sin bordes del tamaño de la pantalla
        self.screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
        
        # Desactivar el cursor del mouse (opcional, útil para pantallas táctiles)
        pygame.mouse.set_visible(True)  # Cambiar a False si no quieres ver el cursor
        
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
        
        # Variable para almacenar la respuesta
        answer = None
        
        # Loop de la pregunta
        while answer is None:
            # Procesar eventos
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None
                    # Bloquear entrada de teclado para evitar activar teclado virtual
                    # No procesar otros eventos de teclado
                    continue
                
                # Usar MOUSEBUTTONDOWN para detectar toques táctiles
                # En pantallas táctiles, los toques se convierten en eventos de mouse
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Verificar si el toque fue en algún botón
                    touch_pos = event.pos
                    if true_button_rect.collidepoint(touch_pos):
                        answer = True
                        break
                    elif false_button_rect.collidepoint(touch_pos):
                        answer = False
                        break
                
                # También manejar eventos FINGERDOWN para soporte táctil directo
                elif event.type == pygame.FINGERDOWN:
                    # Convertir coordenadas normalizadas (0-1) a píxeles
                    finger_x = int(event.x * self.width)
                    finger_y = int(event.y * self.height)
                    finger_pos = (finger_x, finger_y)
                    
                    if true_button_rect.collidepoint(finger_pos):
                        answer = True
                        break
                    elif false_button_rect.collidepoint(finger_pos):
                        answer = False
                        break
            
            # Si ya tenemos respuesta, salir del loop
            if answer is not None:
                break
            
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
        
        return answer
    
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

    def show_djperigro_button(self) -> bool:
        """
        Muestra un botón DJPERIGRO en pantalla completa.
        
        Returns:
            True si se presionó el botón, False si se presiona ESC para salir
        """
        # Configuración del botón
        button_width = 450
        button_height = 150
        
        # Posición centrada
        center_x = self.width // 2
        center_y = self.height // 2
        
        djperigro_button_rect = pygame.Rect(
            center_x - button_width // 2,
            center_y - button_height // 2,
            button_width,
            button_height
        )
        
        # Colores estilo DJ (degradado morado/rosa)
        dj_color = (138, 43, 226)  # Azul violeta
        dj_hover = (218, 112, 214)  # Orquídea
        
        # Loop del botón
        while True:
            # Procesar eventos
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    continue
                
                # Detectar toque/click en el botón
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    touch_pos = event.pos
                    if djperigro_button_rect.collidepoint(touch_pos):
                        return True
                
                # Soporte táctil directo
                elif event.type == pygame.FINGERDOWN:
                    finger_x = int(event.x * self.width)
                    finger_y = int(event.y * self.height)
                    finger_pos = (finger_x, finger_y)
                    
                    if djperigro_button_rect.collidepoint(finger_pos):
                        return True
            
            # Actualizar animación de fondo
            self.update_animation()
            
            # Dibujar fondo
            self.draw_background_animation()
            
            # Detectar hover para efecto
            button_hover = djperigro_button_rect.collidepoint(mouse_pos)
            
            # Color del botón (más brillante en hover)
            button_color = dj_hover if button_hover else dj_color
            
            # Dibujar botón con efecto brillante
            pygame.draw.rect(self.screen, button_color, djperigro_button_rect, border_radius=30)
            
            # Borde blanco brillante
            pygame.draw.rect(self.screen, (255, 255, 255), djperigro_button_rect, width=5, border_radius=30)
            
            # Texto "DJPERIGRO"
            dj_text = self.font_question.render("DJ PERIGRO", True, (255, 255, 255))
            text_rect = dj_text.get_rect(center=djperigro_button_rect.center)
            self.screen.blit(dj_text, text_rect)
            
            # Texto de instrucción
            instruction = "🎧 Toca el botón para girar la ruleta musical"
            instruction_surface = self.font_body.render(instruction, True, (255, 255, 255))
            instruction_rect = instruction_surface.get_rect(center=(self.width // 2, center_y + button_height // 2 + 80))
            self.screen.blit(instruction_surface, instruction_rect)
            
            # Actualizar display
            pygame.display.flip()
            self.clock.tick(self.fps)

    def show_song_roulette(self, songs: List[str], duration: float = 3.0) -> str:
        """
        Muestra una ruleta de canciones que gira y selecciona una aleatoriamente.
        
        Args:
            songs: Lista de nombres de canciones disponibles
            duration: Duración del giro en segundos (default 3.0)
            
        Returns:
            Nombre de la canción seleccionada
        """
        import random
        import math
        
        if not songs:
            return None
        
        # Seleccionar canción ganadora (pero no revelar hasta el final)
        winner_index = random.randint(0, len(songs) - 1)
        winner_song = songs[winner_index]
        
        # Configuración de la ruleta
        center_x = self.width // 2
        center_y = self.height // 2
        radius = 250  # Radio de la ruleta
        
        # Colores para las secciones
        colors = [
            (255, 99, 71),   # Tomate
            (135, 206, 250), # Azul cielo
            (144, 238, 144), # Verde claro
            (255, 215, 0),   # Oro
            (255, 105, 180), # Rosa fuerte
            (147, 112, 219), # Morado medio
            (255, 165, 0),   # Naranja
            (64, 224, 208),  # Turquesa
        ]
        
        # Calcular ángulo por sección
        angle_per_song = 360 / len(songs)
        
        # Variables de animación
        start_time = time.time()
        current_rotation = 0
        rotation_speed = 0  # Velocidad inicial
        max_speed = 720  # Velocidad máxima (grados por segundo)
        
        # Loop de animación
        while True:
            # Procesar eventos (solo para cerrar)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return winner_song
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return winner_song
            
            # Calcular tiempo transcurrido
            elapsed = time.time() - start_time
            progress = min(elapsed / duration, 1.0)
            
            # Si terminó la animación, salir
            if progress >= 1.0:
                break
            
            # Animación de desaceleración (easing out)
            # Acelera al principio y desacelera al final
            if progress < 0.2:
                # Aceleración inicial
                rotation_speed = max_speed * (progress / 0.2)
            else:
                # Desaceleración
                remaining = 1.0 - progress
                rotation_speed = max_speed * remaining * 1.2
            
            # Actualizar rotación
            current_rotation += rotation_speed * (1/60)  # Asumiendo 60 FPS
            current_rotation = current_rotation % 360
            
            # Actualizar animación de fondo
            self.update_animation()
            
            # Dibujar fondo
            self.draw_background_animation()
            
            # Dibujar título
            title = "🎲 RULETA MUSICAL 🎲"
            title_surface = self.font_question.render(title, True, (255, 255, 255))
            title_rect = title_surface.get_rect(center=(center_x, 80))
            self.screen.blit(title_surface, title_rect)
            
            # Dibujar la ruleta (círculo con secciones)
            for i, song in enumerate(songs):
                # Calcular ángulo inicial y final de esta sección
                start_angle = math.radians(i * angle_per_song - current_rotation)
                end_angle = math.radians((i + 1) * angle_per_song - current_rotation)
                
                # Color de la sección
                color = colors[i % len(colors)]
                
                # Dibujar sector de la ruleta
                points = [(center_x, center_y)]
                for angle in [start_angle + j * (end_angle - start_angle) / 20 for j in range(21)]:
                    x = center_x + radius * math.cos(angle)
                    y = center_y + radius * math.sin(angle)
                    points.append((x, y))
                
                pygame.draw.polygon(self.screen, color, points)
                pygame.draw.polygon(self.screen, (255, 255, 255), points, 3)  # Borde blanco
                
                # Dibujar nombre de la canción (rotado)
                mid_angle = (start_angle + end_angle) / 2
                text_radius = radius * 0.7
                text_x = center_x + text_radius * math.cos(mid_angle)
                text_y = center_y + text_radius * math.sin(mid_angle)
                
                # Renderizar texto
                song_surface = self.font_body.render(song[:15], True, (0, 0, 0))
                # Rotar texto
                rotated_text = pygame.transform.rotate(song_surface, -math.degrees(mid_angle) + 90)
                text_rect = rotated_text.get_rect(center=(text_x, text_y))
                self.screen.blit(rotated_text, text_rect)
            
            # Dibujar círculo central
            pygame.draw.circle(self.screen, (50, 50, 50), (center_x, center_y), 40)
            pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), 40, 3)
            
            # Dibujar indicador (flecha en la parte superior)
            indicator_points = [
                (center_x, center_y - radius - 30),
                (center_x - 20, center_y - radius - 10),
                (center_x + 20, center_y - radius - 10)
            ]
            pygame.draw.polygon(self.screen, (255, 0, 0), indicator_points)
            pygame.draw.polygon(self.screen, (255, 255, 255), indicator_points, 3)
            
            # Actualizar display
            pygame.display.flip()
            self.clock.tick(60)
        
        # Animación final: mostrar ganador
        self._show_winner_announcement(winner_song)
        
        return winner_song
    
    def _show_winner_announcement(self, song_name: str, duration: float = 2.0):
        """Muestra la canción ganadora con una animación"""
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            # Procesar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            
            # Actualizar animación
            self.update_animation()
            
            # Dibujar fondo
            self.draw_background_animation()
            
            # Efecto de parpadeo
            alpha = abs(math.sin((time.time() - start_time) * 3))
            
            # Título
            title = "🎊 ¡CANCIÓN SELECCIONADA! 🎊"
            title_surface = self.font_question.render(title, True, (255, 215, 0))
            title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 2 - 80))
            self.screen.blit(title_surface, title_rect)
            
            # Nombre de la canción ganadora
            winner_color = (int(255 * alpha), 255, int(255 * alpha))
            winner_surface = self.font_question.render(song_name, True, winner_color)
            winner_rect = winner_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(winner_surface, winner_rect)
            
            # Actualizar display
            pygame.display.flip()
            self.clock.tick(60)

    def clear(self):
        """Limpia la pantalla (simula borrado de display)."""
        print("\n" + "🖥️  [DISPLAY] Pantalla limpiada\n")
