import sys, math
sys.path.insert(0, "swampy.zip") # think python's easy library. WHO CARES IF I DO THAT?! shutup.

import TurtleWorld

class CoolTurtle(TurtleWorld.Turtle):
    def drawBox(self, length):
        for i in xrange(4):
            self.fd(length)
            self.lt(90)

    def drawPolygon(self, sides, length):
        angle = 360.0 / sides;
        for i in xrange(sides):
            self.fd(length)
            self.lt(angle)

    def drawCircle(self, radius):
        c = 2 * radius * math.pi
        sides = int(round(c / 2))
        
        length = c / sides
        self.drawPolygon(sides, length)
        

if __name__ == "__main__":
    world = TurtleWorld.TurtleWorld(interactive=False)
    t = CoolTurtle()
    t.drawCircle(100)
    t.redraw()
    world.wait_for_user()
