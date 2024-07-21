import pygame
import adventure # Importa el módulo 'adventure'

# Define las direcciones de movimiento del personaje como listas de coordenadas
LEFT_BLOCK = [[1, 0]]  # Mover a la izquierda
RIGHT_BLOCK = [[-1, 0]] # Mover a la derecha
TOP_BLOCK = [[0, 1]]   # Mover hacia arriba
BOTTOM_BLOCK = [[0, -1]] # Mover hacia abajo

# Combina todas las direcciones en una sola lista
ALL_BLOCK = LEFT_BLOCK + RIGHT_BLOCK + TOP_BLOCK + BOTTOM_BLOCK

# Define los nombres de las animaciones del personaje
SPRITE_FALL = "fall"  # Animación de caída
SPRITE_JUMP = "jump"  # Animación de salto
SPRITE_DJUMP = "djump" # Animación de doble salto
SPRITE_IDLE = "idle"  # Animación de inactividad
SPRITE_RUN = "run"   # Animación de carrera

# Define las velocidades y la potencia de salto
MOV_SPEED = 320  # Velocidad de movimiento horizontal
JUMP_POWER = 380  # Potencia del salto normal
DJUMP_POWER = 280 # Potencia del doble salto


class Character:
    # Atributos del personaje
    w = 0  # Ancho del personaje
    h = 0  # Alto del personaje

    x = 0  # Posición x del personaje
    y = 0  # Posición y del personaje

    vx = 0  # Velocidad horizontal del personaje
    vy = 0  # Velocidad vertical del personaje

    status = None  # Estado actual del personaje (idle, run, jump, etc.)
    sprite = None  # Nombre del sprite actual del personaje
    delay  = 0  # Retardo para la animación del personaje

    target = None  # Bloque objetivo del personaje (para detectar colisiones)
    last_y = -99999999  # Última posición y del personaje (para detectar colisiones)
    last_blocks = None  # Últimos bloques que se comprobaron (para optimizar las colisiones)
    last_test   = None  # Última dirección de movimiento (para optimizar las colisiones)

    djump = True  # Indica si el personaje puede realizar un doble salto

    # Inicializa el personaje con las dimensiones y la posición iniciales
    def __init__(self, x, y, w, h):
        self.x = x  # Asigna la posición x inicial
        self.y = y  # Asigna la posición y inicial
        self.w = w  # Asigna el ancho del personaje
        self.h = h  # Asigna el alto del personaje
        #self.status = StatusIdle()  # Inicializa el estado del personaje como 'idle'
        self.sprite = SPRITE_IDLE  # Inicializa el sprite del personaje como 'idle'
        self.last_test = LEFT_BLOCK  # Inicializa la última dirección de movimiento como 'LEFT_BLOCK'


    # Maneja las entradas del usuario
    def handle(self, inputs):
        self.status.handle(self, inputs)  # Llama al método 'handle' del estado actual
        self.vx = 0  # Inicializa la velocidad horizontal
        if inputs[pygame.K_a]:  # Si se presiona 'A'
            self.vx = -MOV_SPEED  # Mueve a la izquierda
        elif inputs[pygame.K_d]:  # Si se presiona 'D'
            self.vx = MOV_SPEED  # Mueve a la derecha

    # Actualiza el estado y la posición del personaje
    def update(self, delay):
        self.delay = delay  # Asigna el retardo
        self.status.update(self, delay)  # Actualiza el estado del personaje
        dvx = (self.vx * delay)  # Calcula la distancia horizontal a mover
        if dvx != 0.0000:  # Si hay movimiento horizontal
            test = LEFT_BLOCK if dvx < 0 else RIGHT_BLOCK  # Determina la dirección de movimiento
            self.last_test = test  # Actualiza la última dirección de movimiento
        else:
            test = self.last_test  # Mantiene la última dirección de movimiento
        self.update_target(test)  # Actualiza el bloque objetivo
        if self.target is not None:  # Si hay un bloque objetivo
            size = adventure.default.block_size  # Obtiene el tamaño de bloque
            x, y = self.target  # Obtiene las coordenadas del bloque objetivo
            t_x  = (((x + 1) * size + 1) if dvx < 0 else (x *  size) - 1)  # Calcula la posición x del bloque objetivo
            w    = 0 if dvx < 0 else self.w  # Calcula el ancho del personaje para la colisión

            # Colisión con la izquierda
            if test == LEFT_BLOCK:
                if (self.x + dvx) - t_x < 0:  # Si el personaje choca con el bloque objetivo
                    self.x = t_x - w  # Ajusta la posición x del personaje
                    dvx = 0  # Anula el movimiento horizontal
            # Colisión con la derecha
            else:
                if (self.x + w + dvx) - t_x > 0:
                    self.x = t_x - w  
                    dvx = 0  

        # Actualiza la posición x del personaje
        self.x += dvx 
        # Actualiza la posición y del personaje
        self.y += (self.vy * delay)

    # Dibuja el personaje en el canvas
    def draw(self, canvas):
        r = self.last_test == LEFT_BLOCK  # Indica si el personaje está mirando a la izquierda
        # Dibuja el sprite del personaje según su estado
        if self.status.name == "idle" or self.status.name == "run" or self.status.name == "djump":
            i = self.status.index % self.status.count  # Obtiene el índice del sprite actual
            p = adventure.default.texture.get_texture(self.sprite, r)  # Obtiene la textura del sprite
            s = p.subsurface((i * self.w, 0, self.w, self.h))  # Extrae el sub-rectángulo del sprite
        else:
            s = adventure.default.texture.get_texture(self.sprite, r)  # Obtiene la textura del sprite
        canvas.blit(s, (self.x, self.y))  # Dibuja el sprite en el canvas
        # Dibuja el bloque objetivo (para debug)
        if self.target is not None:
            x, y = self.target
            pygame.draw.rect(adventure.default.canvas, (100, 0, 0), (x * 32, y * 32, 32, 32))

    # Obtiene el rectángulo del bloque actual que ocupa el personaje
    def get_current_block(self):
        block_size = adventure.default.block_size  # Obtiene el tamaño del bloque
        x = self.x / block_size  # Calcula la coordenadas
        y = self.y / block_size  
        c_w = self.x + self.w  # Calcula la coordenada x del borde derecho del personaje
        c_h = self.y + self.h  # Calcula la coordenada y del borde inferior del personaje
        c_w1 = c_w / block_size - x  # Calcula el ancho del bloque en términos de bloques
        c_h1 = c_h / block_size - y  # Calcula el alto del bloque en términos de bloques
        # Ajusta el ancho y alto para que incluyan los bloques parciales
        w = c_w1 + 1 if ((c_w % block_size) > 0.5) else c_w1 
        h = c_h1 + 1 if ((c_h % block_size) > 0.5) else c_h1 
        return pygame.Rect(x, y, w, h)  # Devuelve el rectángulo del bloque

    # Obtiene los bloques circundantes al bloque actual del personaje
    def get_surrounding_block(self, test):
        r = self.get_current_block()  # Obtiene el rectángulo del bloque actual
        test_w = range(-1, r.w * 2)  # Genera un rango para el ancho del bloque
        test_h = range(-1, r.h * 2)  # Genera un rango para el alto del bloque
        result = []  # Inicializa la lista de bloques circundantes
        # Itera sobre los bloques circundantes
        for offset_y in range(0, r.h * 2 + r.h % 2):
            pos_y = r.y + test_h[offset_y]  
            for offset_x in range(0, r.w * 2 + r.w % 2):
                pos_x = r.x + test_w[offset_x]  
                # Itera sobre la lista de direcciones de prueba
                for t in test:
                    mx, my = t  # Obtiene el desplazamiento x e y de la dirección
                    # Si el punto de prueba está dentro del rectángulo del bloque
                    if r.collidepoint(pos_x + mx, pos_y + my):
                        result.append((pos_x, pos_y))  # Agrega el bloque a la lista de resultados
        return result  # Devuelve la lista de bloques circundantes

    # Actualiza el bloque objetivo del personaje (para detección de colisiones)
    def update_target(self, test):
        self.last_blocks = self.get_surrounding_block(test)  # Obtiene los bloques circundantes
        adventure.default.draw_blocks()  # Dibuja los bloques (para debug)
        self.target = None  # Inicializa el bloque objetivo
        flag = False  # Bandera para indicar si se encontró un bloque objetivo
        # Itera sobre los bloques circundantes
        for block in self.last_blocks:
            x, y = block  # Obtiene las coordenadas del bloque
            b = adventure.default.get_block_id(x, y)  # Obtiene el ID del bloque
            # Si el bloque no es nulo y no se encontró un bloque objetivo antes
            if b is not None and flag is False:
                self.target = block  # Asigna el bloque como objetivo
                flag = True  # Establece la bandera como verdadera
                x, y = block  # Obtiene las coordenadas del bloque
                pygame.draw.rect(adventure.default.canvas, (0, 100, 0), (x * 32, y * 32, 32, 32))  # Dibuja el bloque objetivo

    # Maneja las acciones al colisionar con un bloque
    def on_collision(self, b_id):
        block = adventure.default.blocks[b_id]  # Obtiene el bloque del diccionario de bloques
        # Si el bloque tiene la propiedad "collision"
        if "collision" in block:
            # Si la propiedad "collision" es "died"
            if block["collision"] == "died":
                adventure.default.restart()  # Reinicia el juego
            # Si la propiedad "collision" es "jump"
            elif block["collision"] == "jump":
                #self.status = StatusDJump()  # Cambia el estado a 'djump'
                self.sprite = SPRITE_DJUMP  # Cambia el sprite a 'djump'
                self.djump = False  # Deshabilita el doble salto
                self.vy = -600  # Aplica la potencia del salto
        # Si el bloque tiene la propiedad "transport"
        if "transport" in block:
            adventure.default.load_level(block["transport"])  # Carga el nivel indicado