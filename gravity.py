import pygame
import os
import time as t
import numpy as np
import random


# Centers window
x, y = 300, 30
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)

# Game presets
start_time = t.time()
fps = 120
width, height = 800, 700

whitest      = (234, 234, 234)
white        = (160, 160, 160)
grey         = (129, 169, 169)  # (27, 75, 75)
black        = (  0,   0,   0)
red          = (255,   0,   0)
green        = (  0, 200,  27)
yellow       = (191, 202,  37)
velvet       = (232,  20,  20)
bluish_white = (179, 255, 251)


# cool stars
num_of_stars = 100
points = []
for i in range(num_of_stars):
    x = random.randint(0, width)
    y = random.randint(0, height)
    point = [x, y]
    points.append(point)

# print(points)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Gravity simulation")
    font = pygame.font.Font('freesansbold.ttf', 15)
    # microsoftjhengheimicrosoftjhengheiuilight
    #comicsansms

G = 6.67*10**-11
acc_x = 0
acc_y = 0


class Body():
    allow_trailing = True
    boundary_mode = False
    pause = False
    bodies = []
    every_max = 3 # the max allowed val for every
    # for some reason it doesnt work with multiples of 4
    every = 0

    def __init__(self, name, mass, pos_x, pos_y, vel_x, vel_y,
    colour, radius):

        self.name = name
        self.mass = mass
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.acc_x = acc_x
        self.acc_y = acc_y
        self.colour = colour
        self.radius = radius
        self.momentum_x = mass*vel_x
        self.momentum_y = mass*vel_y
        self.positions = []
        Body.bodies.append(self)
        self.hovered = False
        self.dragged = False

        self.text = font.render('{}'.format(self.name), True, whitest)
        # self.forces = []
        # self.vels = []
        self.tracers = []  # same as postions but for will_tracer function

    def find_force(self, mass2, sep, radius):
        '''Calculates the gravitational force between
        the object, self, and another mass, mass2, given
        their separation, sep. '''
        sep = sep if (self.radius + radius)/2 <= sep else (self.radius + radius)/2
        f = (G*self.mass*mass2)/sep**2
        return f

    def result_force(self):
        '''Calculates the resultant forces exerted by all of the
        other bodies in the system on the object, self,
        for the x and y direction returning force_x and force_y respecively'''
        result_for_x = 0
        result_for_y = 0
        for body in Body.bodies:
            if body != self:
                their_pos_x = getattr(body, 'pos_x')
                their_pos_y = getattr(body, 'pos_y')
                their_mass = getattr(body, 'mass')
                their_radius = getattr(body, 'radius')

                r_x = their_pos_x - self.pos_x  # sep in x dir
                r_y = their_pos_y - self.pos_y  # sep in y dir
                r = np.sqrt(r_x**2 + r_y**2)  # resultant

                force = self.find_force(their_mass, r, their_radius)
                result_for_x += force * (r_x/r)  # r_x/r = cos a
                result_for_y += force * (r_y/r)  # r_y/r = sin a
        return result_for_x, result_for_y

    def boundary_glitch_detector(self, radius):
        tol = 3  # tolerance for num of gltiches
        is_glitch = False
        if len(self.positions) > tol:# keeps the last tol points
            self.positions = self.positions[-tol:]
        num_of_gliches = 0
        glitched_bndry = []  # (top bottom 0 | right left 1)
        for pos_x, pos_y in self.positions:
            if pos_y - radius < 0: # top
                num_of_gliches += 1
                glitched_bndry = [0, 1+radius]
            if pos_y + radius > height: # bottom
                num_of_gliches += 1
                glitched_bndry = [0, height-radius-1]
            if pos_x + radius > width: # right
                num_of_gliches += 1
                glitched_bndry = [1, width-radius-1]
            if pos_x - radius < 0: # left
                num_of_gliches +=1
                glitched_bndry = [1, 1+radius]
        if num_of_gliches >= tol:
            is_glitch = True
        return [is_glitch, glitched_bndry]

    def  trailers(self, max_every):
        # traces prev path
        limit = 1000//max_every
        if Body.every == max_every:
            self.tracers.append((self.pos_x, self.pos_y))
            Body.every = 0
        else:
            Body.every += 1
        if len(self.tracers) > limit:
            self.tracers = self.tracers[-limit:]

    def update_motion(self):
        '''Updates acceleration, speed and position for
        object based on force_x and force_y returned by
        result_force'''
        force_x, force_y = self.result_force()

        self.acc_x = force_x/self.mass
        self.acc_y = force_y/self.mass

        self.vel_x += self.acc_x
        self.vel_y += self.acc_y

        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        # boundary Handling
        if Body.boundary_mode is True:
            rad = self.radius
            elast = 0.97 # elasticity
            if self.pos_x + rad >= width:  # right boundary
                # self.pos_x -= 1
                self.vel_x *= -elast
            if self.pos_x - rad <= 0:  # left boundary
                # self.pos_x += 1
                self.vel_x *= -elast

            if self.pos_y - rad <= 0:  # top boundary
                # self.pos_y += 1
                self.vel_y *= -elast
            if self.pos_y + rad >= height:  # bottom boundary
                # self.pos_y -= 1
                self.vel_y *= -elast

            self.positions.append([self.pos_x, self.pos_y])
            glitch_data = self.boundary_glitch_detector(rad)
            if glitch_data[0]:
                if glitch_data[1][0] == 0: # vertical glitch
                    self.pos_y = glitch_data[1][1]
                elif glitch_data[1][0] == 1: # sideways glitch
                    self.pos_x = glitch_data[1][1]

        # tracers prev path
        self.trailers(Body.every_max)


        # def will_tracer(self):
        #     smpl_frq = 100

        #     mass = self.mass
        #     pos_x = self.pos_x
        #     pos_y = self.pos_y

        #     vel_x = self.vel_x
        #     pos_y = self.vel_y

        #     depth = 100_000 # hundred k/k = hundred points
        #     forces = []

        #     for i in range(depth):
        #         if i % smpl_frq != 0:
        #             continue
        #         forcex, forcey = self.result_force()

        #         acc_x = forcex/mass
        #         acc_x = forcey/mass

        #         vel_x += acc_x
        #         vel_y += acc_y

        #         pos_x += vel_x
        #         pos_y += vel_y


        # '''we wanna take a list of forces
        # sample every x of them (x depends on sampling frequency)
        # use each sample to calculate the final postions and
        # draw them using the aaline draw func'''
        # smpl_frq = 1000
        # mass = self.mass
        # velx = self.vel_x
        # velx = self.vel_x
        # initposx = self.pos_x
        # initposx = self.pos_x

        # data = [i for i in range(23400)]
        # sampled_data = [i for i in data if data.index(i) % smpl_frq==0]
        # # now we use each value for the force and calculate the postions
        # positions = [initposx]

        # for forcex, forcey in sampled_data:
        #     pos = positions[-1]
        #     acc = force/mass
        #     velx += acc
        #     pos += vel
        #     positions.append(pos)


# template = (mass, x, y, velx, vely, accx, accy, color, radius)
sun = Body("The Sun",10**13, width//2, height//2, 0, 0, yellow, 28)
mercury = Body("The Moon",10**9, width//2 - 275, height//2, 0, -1.72, grey, 6)
earth = Body("The Earth",10**10, width//2 - 300, height//2, 0, -1.5, green, 10)
mars = Body("Venus",10**1, width//2 - 90, height//2, 0, -2.4, red, 9)
shuttle = Body("A weird planet",11*8, 100, 100, 1.4, 0,  bluish_white, 26)

# shuttle_sprite = "sisi_new.png"
# russi_sprite = "brussi2_sprt.png"
# jibril_sprite = "bijril1_sprt.png"

# shuttle_img = pygame.image.load(shuttle_sprite)
# sun_img = pygame.image.load(jibril_sprite)
# earth_img = pygame.image.load(russi_sprite)

# jibril = Body(10**12, width//2-340, height//2-20, 0.4, 1, 0, 0, velvet, 12)
# fattie = Body(1000_000_000, width//2 + 200, height//3, 1, -1, 0, 0, red, 5)


def apply_update_motion():
    '''applies the update function for each instance'''
    if Body.pause == False:
        for body in Body.bodies:
            body.update_motion()


def draw(rad, color, x=0, y=0, trail_list=None, hovered=False, text=None):
    if trail_list is not None:
        pygame.draw.aalines(screen, color, False, trail_list)
    else:
        pygame.draw.circle(screen, color, (x, y), rad)
    if hovered:
        thickness = int(rad*0.15)
        thickness = 1 if width==0 else thickness
        pygame.draw.circle(screen, whitest, (x, y), rad, thickness)

        set_o_points = []
        i, j, = 1, -40
        if x > width*3//4:
            i = -1
        if y < height//4:
            j = 40

        set_o_points = [(x,y), (x+i*(rad+5), y+j) ,(x+i*(rad+25), y+j)]
        # set_o_points = [(x,y), (x+rad+5, y+40) ,(x+rad+25, y+40)]
        pygame.draw.lines(screen, whitest, False, set_o_points, 2)


        text_rect = text.get_rect()
        txt_x, txt_y = set_o_points[-1]
        if i == -1:
            text_rect.midright = (txt_x+1, txt_y-4)
        else:
            text_rect.midleft = (txt_x-1, txt_y-4)
        screen.blit(text, text_rect)


def in_circle(rad, x, y, mouse_x, mouse_y):
    '''checks whether mouse is inside a circle'''
    value = (mouse_x-x)**2 + (mouse_y-y)**2
    if value <= rad**2:
        return True
    else:
        return False


def main():
    pygame.key.set_repeat(10, 10)
    while True:
        ctrl = False
        speed = 0.03
        multiplier = 1
        screen.fill(black)
        for x, y in points:
            draw(2, white, x=x, y=y)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                frmrate = clock.get_fps()
                print('framerate={}'.format(frmrate))
                quit()
            if pygame.mouse.get_pressed()[2] == 1:
                multiplier = 2
            # highlight capability block
            m_x, m_y = pygame.mouse.get_pos()
            for body in Body.bodies:
                rad = body.radius
                x = body.pos_x
                y = body.pos_y
                hover = in_circle(rad, x, y, m_x, m_y)
                body.hovered = True if hover else False


            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # leftclick
                    for body in Body.bodies:
                        if body.hovered and Body.pause:
                            body.dragged = True
                            break

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for body in Body.bodies:
                        body.dragged = False
                    # print(body.dragged)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DELETE:
                    Body.boundary_mode = not Body.boundary_mode
                if event.key == pygame.K_p:
                    Body.pause = not Body.pause
                if event.key == pygame.K_x:
                    Body.allow_trailing = not Body.allow_trailing

            if event.type == pygame.KEYDOWN:
                if event.mod & pygame.KMOD_SHIFT:
                    speed = 0.4*multiplier
                if event.key == pygame.K_m:
                    if ctrl:
                        shuttle.mass /= 1.2
                    else:
                        shuttle.mass *= 1.2
                        print(shuttle.mass)
                if event.key == pygame.K_o:
                    shuttle.pos_y = 100
                    shuttle.pos_x = 100
                    shuttle.vel_x, shuttle.vel_y = 0, 0

        if pygame.key.get_pressed()[pygame.K_w] == 1:
            shuttle.vel_y -= speed
        if pygame.key.get_pressed()[pygame.K_s] == 1:
            shuttle.vel_y += speed
        if pygame.key.get_pressed()[pygame.K_a] == 1:
            shuttle.vel_x -= speed
        if pygame.key.get_pressed()[pygame.K_d] == 1:
            shuttle.vel_x += speed
        if pygame.key.get_pressed()[pygame.K_SPACE] == 1:
            shuttle.vel_x *= 0.94/multiplier
            shuttle.vel_y *= 0.94/multiplier

        apply_update_motion()
        for body in Body.bodies:
            if body.dragged is True:
                body.pos_x = m_x
                body.pos_y = m_y
            x = int(body.pos_x)
            y = int(body.pos_y)
            radius = body.radius
            colour = body.colour
            trailers = body.tracers
            hovered = body.hovered
            text = body.text

            if len(trailers) > 1 and Body.allow_trailing:
                draw(radius, colour, trail_list=trailers)

            draw(radius, colour, x=x, y=y, hovered = hovered, text=text)



        pygame.display.update()
        clock.tick(fps)

if __name__ == "__main__":
    main()











# if radius == 10:
#     screen.blit(earth_img, (int(x)-30, int(y)-30))
# if radius == 28:
#     screen.blit(sun_img, (int(x)-50, int(y)-80))
# if radius == 26:
#     screen.blit(shuttle_img, (int(x)-26, int(y)-26))
