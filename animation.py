from canvas import canvas
import cv2
import os
import numpy as np
import imageio
from tqdm import tqdm

class animation():

    def __init__(
            self,
            duration=5, fps=5,
            width=200, height=200, extent=4
    ):
        
        self.duration = duration
        self.fps = fps
        self.artists = []

        self.n_frames = int(fps*duration)

        self.frames = [
            canvas(width, height, extent) for _ in
            range(self.n_frames)
        ]
        self.has_rendered = [False,]*self.n_frames
        self.timepoints = np.linspace(0, 1, self.n_frames+1)[:-1]

    def add(self, art):
        self.artists.append(art)

    def render(self, n):
        assert(0 <= n < self.n_frames)

        if not self.has_rendered[n]:

            t = self.timepoints[n]

            for art in self.artists:
                art(t, self.frames[n])

            self.has_rendered[n] = True

        return self.frames[n]

    def show(self, delay=50, repeat=True):
        while True:
            for n in range(self.n_frames):
                img = self.render(n)
                img.show(delay=delay)
            if not repeat:
                break

    def to_gif(self, f_gif):
        images = [self.render(n).img for n in range(self.n_frames)]

        # Convert from BGR to RGB
        images = [cv2.cvtColor(img, cv2.COLOR_BGR2RGB) for img in images]
        
        imageio.mimsave(f_gif, images, fps=self.fps*2,
                        palettesize=256,  subrectangles=True)
        fs = os.stat(f_gif).st_size
        print(f"Rendered {f_gif}, filesize {fs}")

#############################################################################

# This is ugggggly, need to fix

def constant(x):
    def func(self, t):
        return x
    return func

def constant2(x):
    def func(t):
        return x
    return func

#############################################################################
        

class artist():

    def __init__(self, **kwargs):

        attributes = dir(self)
        for key, val in kwargs.items():

            # Can't set attributes an object doesn't have
            if key not in attributes:
                msg = f"{key} not in class {self}"
                raise AttributeError(msg)

            # If the val is callable, that's what we use
            if callable(val):
                setattr(self, key, val)

            # Otherwise we assume it's a constant of this value
            else:
                setattr(self, key, constant2(val))

    def __call__(self, t):
        # Virtual class, need to override
        raise NotImplementedError


#############################################################################


class circle(artist):

    x = y = constant(0.0)
    r = constant(1.0)
    color = constant([255,255,255])
    thickness = constant(-1)

    def __call__(self, t, img=None):
        
        img.circle(
            self.x(t), self.y(t), self.r(t),
            self.color(t), self.thickness(t)
        )


if __name__ == "__main__":
    
    A = animation(width=75, height=75)

    line1 = lambda t: 0.5 - t
    line2 = lambda t: t - 0.5

    A.add(circle(x=line1, y=1, r=1.25,color=[150,250,0]))
    A.add(circle(x=line2, y=-1, r=1.25,color=[100,5,255]))

    A.to_gif("examples/moving_circles.gif")
    #A.show(delay=20, repeat=True)