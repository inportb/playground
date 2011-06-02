import sys
sys.path.insert(0, "swampy.zip")

import TurtleWorld

class CoolTurtle(TurtleWorld.Turtle):
    def drawBox(self, distance):
        for i in xrange(4):
            self.fd(distance)
            self.lt(90)

if __name__ == "__main__":
    world = TurtleWorld.TurtleWorld(interactive=False)
    t = CoolTurtle()
    t.drawBox(100)
    world.wait_for_user()
