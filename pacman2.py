import pygame, sys, os, random
import math
from pygame.locals import *


SCRIPT_PATH = sys.path[0]
NO_GIF_TILES = [23]

clock = pygame.time.Clock()
pygame.init()

window = pygame.display.set_mode((1, 1))
pygame.display.set_caption("Pacman")
WIDTH = 21
HEIGHT = 25
screen = pygame.display.set_mode([WIDTH * 16, HEIGHT * 16])
# screen = pygame.display.get_surface()

img_Background = pygame.image.load(
    os.path.join(SCRIPT_PATH, "res", "backgrounds", "1.gif")
).convert()
imgPath = pygame.image.load(
    os.path.join(SCRIPT_PATH, "res", "tiles", "path.gif")
).convert()

ghostcolor = {}
ghostcolor[0] = (255, 0, 0, 255)


class game:
    def __init__(self):
        self.levelNum = 8
        self.mode = 1
        self.modeTimer = 0
        self.screenPixelPos = (0, 0)
        self.screenNearestTilePos = (0, 0)
        self.screenPixelOffset = (0, 0)

        self.screenTileSize = (23, 21)
        self.screenSize = (self.screenTileSize[1] * 16, self.screenTileSize[0] * 16)
        self.imLife = pygame.image.load(
            os.path.join(SCRIPT_PATH, "res", "text", "life.gif")
        ).convert()

    def SetMode(self, newMode):
        self.mode = newMode

    def MoveScreen(self, newX, newY):
        self.screenPixelPos = (newX, newY)
        self.screenNearestTilePos = (
            int(newY / 16),
            int(newX / 16),
        )
        self.screenPixelOffset = (
            newX - self.screenNearestTilePos[1] * 16,
            newY - self.screenNearestTilePos[0] * 16,
        )

    def GetScreenPos(self):
        return self.screenPixelPos

    def GetLevelNum(self):
        return self.levelNum


class node:
    def __init__(self):
        self.g = -1
        self.h = -1
        self.f = -1
        self.parent = (-1, -1)
        self.type = -1


class path_finder:
    def __init__(self):
        self.map = {}
        self.size = (-1, -1)  # rows by columns

        self.pathChainRev = ""
        self.pathChain = ""

        # starting and ending nodes
        self.start = (-1, -1)
        self.end = (-1, -1)

        # current node (used by algorithm)
        self.current = (-1, -1)

        # open and closed lists of nodes to consider (used by algorithm)
        self.openList = []
        self.closedList = []

        # used in algorithm (adjacent neighbors path finder is allowed to consider)
        self.neighborSet = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    def ResizeMap(self, numRows, numCols):
        self.map = {}
        self.size = (numRows, numCols)

        # initialize path_finder map to a 2D array of empty nodes
        for row in range(0, self.size[0], 1):
            for col in range(0, self.size[1], 1):
                self.Set(row, col, node())
                self.SetType(row, col, 0)

    def CleanUpTemp(self):
        # this resets variables needed for a search (but preserves the same map / maze)

        self.pathChainRev = ""
        self.pathChain = ""
        self.current = (-1, -1)
        self.openList = []
        self.closedList = []

    def FindPath(self, startPos, endPos):
        self.CleanUpTemp()

        # (row, col) tuples
        self.start = startPos
        self.end = endPos

        # add start node to open list
        self.AddToOpenList(self.start)
        self.SetG(self.start, 0)
        self.SetH(self.start, 0)
        self.SetF(self.start, 0)

        doContinue = True

        while doContinue == True:
            thisLowestFNode = self.GetLowestFNode()

            if not thisLowestFNode == self.end and not thisLowestFNode == False:
                self.current = thisLowestFNode
                self.RemoveFromOpenList(self.current)
                self.AddToClosedList(self.current)

                for offset in self.neighborSet:
                    thisNeighbor = (
                        self.current[0] + offset[0],
                        self.current[1] + offset[1],
                    )

                    if (
                        not thisNeighbor[0] < 0
                        and not thisNeighbor[1] < 0
                        and not thisNeighbor[0] > self.size[0] - 1
                        and not thisNeighbor[1] > self.size[1] - 1
                        and not self.GetType(thisNeighbor) == 1
                    ):
                        cost = self.GetG(self.current) + 10

                        if self.IsInOpenList(thisNeighbor) and cost < self.GetG(
                            thisNeighbor
                        ):
                            self.RemoveFromOpenList(thisNeighbor)

                        if not self.IsInOpenList(
                            thisNeighbor
                        ) and not self.IsInClosedList(thisNeighbor):
                            self.AddToOpenList(thisNeighbor)
                            self.SetG(thisNeighbor, cost)
                            self.CalcH(thisNeighbor)
                            self.CalcF(thisNeighbor)
                            self.SetParent(thisNeighbor, self.current)
            else:
                doContinue = False

        if thisLowestFNode == False:
            return False

        # reconstruct path
        self.current = self.end
        while not self.current == self.start:
            # build a string representation of the path using R, L, D, U
            if self.current[1] > self.GetParent(self.current)[1]:
                self.pathChainRev += "R"
            elif self.current[1] < self.GetParent(self.current)[1]:
                self.pathChainRev += "L"
            elif self.current[0] > self.GetParent(self.current)[0]:
                self.pathChainRev += "D"
            elif self.current[0] < self.GetParent(self.current)[0]:
                self.pathChainRev += "U"
            self.current = self.GetParent(self.current)
            self.SetType(self.current[0], self.current[1], 4)

        # because pathChainRev was constructed in reverse order, it needs to be reversed!
        for i in range(len(self.pathChainRev) - 1, -1, -1):
            self.pathChain += self.pathChainRev[i]

        # set start and ending positions for future reference
        self.SetType(self.start[0], self.start[1], 2)
        self.SetType(self.end[0], self.start[1], 3)

        return self.pathChain

    def Unfold(self, row, col):
        return (row * self.size[1]) + col

    def Set(self, row, col, newNode):
        # sets the value of a particular map cell (usually refers to a node object)
        self.map[self.Unfold(row, col)] = newNode

    def GetType(self, val):
        row, col = val
        return self.map[self.Unfold(row, col)].type

    def SetType(self, row, col, newValue):
        self.map[self.Unfold(row, col)].type = newValue

    def GetF(self, val):
        row, col = val
        return self.map[self.Unfold(row, col)].f

    def GetG(self, val):
        row, col = val
        return self.map[self.Unfold(row, col)].g

    def GetH(self, val):
        row, col = val
        return self.map[self.Unfold(row, col)].h

    def SetG(self, val, newValue):
        row, col = val
        self.map[self.Unfold(row, col)].g = newValue

    def SetH(self, val, newValue):
        row, col = val
        self.map[self.Unfold(row, col)].h = newValue

    def SetF(self, val, newValue):
        row, col = val
        self.map[self.Unfold(row, col)].f = newValue

    def CalcH(self, val):
        row, col = val
        self.map[self.Unfold(row, col)].h = abs(row - self.end[0]) + abs(
            col - self.end[0]
        )
        # self.map[self.Unfold(row, col)].h = abs(row - self.end[0])

    def CalcF(self, val):
        row, col = val
        unfoldIndex = self.Unfold(row, col)
        self.map[unfoldIndex].f = self.map[unfoldIndex].g + self.map[unfoldIndex].h

    def AddToOpenList(self, val):
        row, col = val
        self.openList.append((row, col))

    def RemoveFromOpenList(self, val):
        row, col = val
        self.openList.remove((row, col))

    def IsInOpenList(self, val):
        row, col = val
        if self.openList.count((row, col)) > 0:
            return True
        else:
            return False

    def GetLowestFNode(self):
        lowestValue = 1000  # start arbitrarily high
        lowestPair = (-1, -1)

        for iOrderedPair in self.openList:
            if self.GetF(iOrderedPair) < lowestValue:
                lowestValue = self.GetF(iOrderedPair)
                lowestPair = iOrderedPair

        if not lowestPair == (-1, -1):
            return lowestPair
        else:
            return False

    def AddToClosedList(self, val):
        row, col = val
        self.closedList.append((row, col))

    def IsInClosedList(self, val):
        row, col = val
        if self.closedList.count((row, col)) > 0:
            return True
        else:
            return False

    def SetParent(self, val, val2):
        row, col = val
        parentRow, parentCol = val2
        self.map[self.Unfold(row, col)].parent = (parentRow, parentCol)

    def GetParent(self, val):
        row, col = val
        return self.map[self.Unfold(row, col)].parent

    def draw(self):
        for row in range(0, self.size[0], 1):
            for col in range(0, self.size[1], 1):
                thisTile = self.GetType((row, col))
                screen.blit(tileIDImage[thisTile], (col * 32, row * 32))


class pacman:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.velX = 0
        self.velY = 0
        self.speed = 2

        self.nearestRow = 0
        self.nearestCol = 0

        self.homeX = 0
        self.homeY = 0

        self.anim = pygame.image.load(
            os.path.join(SCRIPT_PATH, "res", "sprite", "pacman-r 8.gif")
        ).convert()

    def Draw(self):
        if thisGame.mode == 3:
            return False

        screen.blit(
            self.anim,
            (self.x, self.y),
        )


class ghost:
    def __init__(self, ghostID):
        self.x = 0
        self.y = 0
        self.velX = 0
        self.velY = 0
        self.speed = 1

        self.nearestRow = 0
        self.nearestCol = 0
        self.cost = -1
        self.addend = False
        self.id = ghostID
        self.state = 1

        self.homeX = 0
        self.homeY = 0

        self.currentPath = ""
        self.adrPath = (-1, -1)
        self.visited = []
        self.anim = {}
        for i in range(1, 7, 1):
            self.anim[i] = pygame.image.load(
                os.path.join(SCRIPT_PATH, "res", "sprite", "ghost " + str(i) + ".gif")
            ).convert()

            # change the ghost color in this frame
            for y in range(0, 16, 1):
                for x in range(0, 16, 1):
                    if self.anim[i].get_at((x, y)) == (255, 0, 0, 255):
                        # default, red ghost body color
                        self.anim[i].set_at((x, y), (255, 0, 0, 255))

        self.animFrame = 1
        self.animDelay = 0

    def Draw(self):
        if thisGame.mode == 3:
            return False

        if self.state == 1:
            screen.blit(
                self.anim[self.animFrame],
                (
                    self.x,
                    self.y,
                ),
            )

        self.animDelay += 1
        if self.animDelay == 2:
            self.animFrame += 1

            if self.animFrame == 7:
                # wrap to beginning
                self.animFrame = 1

            self.animDelay = 0

    def Move(self):
        self.x += self.velX
        self.y += self.velY

        self.nearestRow = int(((self.y + 8) / 16))
        self.nearestCol = int(((self.x + 8) / 16))

        if (self.x % 16) == 0 and (self.y % 16) == 0:
            self.cost += 1
            self.adrPath = (self.x, self.y)
            self.visited.append(self.adrPath)

            if self.currentPath:
                self.currentPath = self.currentPath[1:]
                self.FollowNextPathWay()

            else:
                self.x = self.nearestCol * 16
                self.y = self.nearestRow * 16

                # chase pac-man
                self.currentPath = path.FindPath(
                    (self.nearestRow, self.nearestCol),
                    (player.nearestRow, player.nearestCol),
                )
                self.FollowNextPathWay()

    def FollowNextPathWay(self):
        if not self.currentPath == False:
            if len(self.currentPath) > 0:
                if self.currentPath[0] == "L":
                    (self.velX, self.velY) = (-self.speed, 0)
                elif self.currentPath[0] == "R":
                    (self.velX, self.velY) = (self.speed, 0)
                elif self.currentPath[0] == "U":
                    (self.velX, self.velY) = (0, -self.speed)
                elif self.currentPath[0] == "D":
                    (self.velX, self.velY) = (0, self.speed)

            else:
                self.currentPath = path.FindPath(
                    (self.nearestRow, self.nearestCol),
                    (player.nearestRow, player.nearestCol),
                )
                self.FollowNextPathWay()

    def IsEnd(self):
        if (
            (self.x == player.x - 1 and self.y == player.y)
            or (self.x == player.x + 1 and self.y == player.y)
            or (self.x == player.x and self.y == player.y - 1)
            or (self.x == player.x - 1 and self.y == player.y + 1)
        ):
            thisGame.SetMode(1)
            if self.addend == False:
                self.cost += 1
                self.addend = True


class level:
    def __init__(self):
        self.lvlWidth = 0
        self.lvlHeight = 0
        self.edgeLightColor = (255, 255, 0, 255)
        self.edgeShadowColor = (255, 150, 0, 255)
        self.fillColor = (0, 255, 255, 255)
        self.pelletColor = (255, 255, 255, 255)

        self.map = {}

    def SetMapTile(self, row, col, newValue):
        self.map[(row * self.lvlWidth) + col] = newValue

    def GetMapTile(self, row, col):
        if row >= 0 and row < self.lvlHeight and col >= 0 and col < self.lvlWidth:
            return self.map[(row * self.lvlWidth) + col]
        else:
            return 0

    def IsWall(self, row, col):
        if row > thisLevel.lvlHeight - 1 or row < 0:
            return True

        if col > thisLevel.lvlWidth - 1 or col < 0:
            return True

        # check the offending tile ID
        result = thisLevel.GetMapTile(row, col)

        # if the tile was a wall
        if result >= 100 and result <= 199:
            return True
        else:
            return False

    def GetPathwayPairPos(self):
        doorArray = []

        for row in range(0, self.lvlHeight, 1):
            for col in range(0, self.lvlWidth, 1):
                if self.GetMapTile(row, col) == tileID["door-h"]:
                    # found a horizontal door
                    doorArray.append((row, col))
                elif self.GetMapTile(row, col) == tileID["door-v"]:
                    # found a vertical door
                    doorArray.append((row, col))

        if len(doorArray) == 0:
            return False

        chosenDoor = random.randint(0, len(doorArray) - 1)

        if (
            self.GetMapTile(doorArray[chosenDoor][0], doorArray[chosenDoor][1])
            == tileID["door-h"]
        ):
            for i in range(0, thisLevel.lvlWidth, 1):
                if not i == doorArray[chosenDoor][1]:
                    if (
                        thisLevel.GetMapTile(doorArray[chosenDoor][0], i)
                        == tileID["door-h"]
                    ):
                        return doorArray[chosenDoor], (doorArray[chosenDoor][0], i)
        else:
            for i in range(0, thisLevel.lvlHeight, 1):
                if not i == doorArray[chosenDoor][0]:
                    if (
                        thisLevel.GetMapTile(i, doorArray[chosenDoor][1])
                        == tileID["door-v"]
                    ):
                        return doorArray[chosenDoor], (i, doorArray[chosenDoor][1])

        return False

    def PrintMap(self):
        for row in range(0, self.lvlHeight, 1):
            outputLine = ""
            for col in range(0, self.lvlWidth, 1):
                outputLine += str(self.GetMapTile(row, col)) + ", "

            # print outputLine

    def DrawMap(self):
        for row in range(-1, thisGame.screenTileSize[0] + 1, 1):
            outputLine = ""
            for col in range(-1, thisGame.screenTileSize[1] + 1, 1):
                # row containing tile that actually goes here
                actualRow = thisGame.screenNearestTilePos[0] + row
                actualCol = thisGame.screenNearestTilePos[1] + col

                useTile = self.GetMapTile(actualRow, actualCol)
                if (
                    not useTile == 0
                    and not useTile == tileID["door-h"]
                    and not useTile == tileID["door-v"]
                ):
                    screen.blit(
                        tileIDImage[useTile],
                        (
                            col * 16 - thisGame.screenPixelOffset[0],
                            row * 16 - thisGame.screenPixelOffset[1],
                        ),
                    )

    def LoadLevel(self, levelNum):
        self.map = {}

        f = open(
            os.path.join(SCRIPT_PATH, "res", "levels", str(levelNum) + ".txt"), "r"
        )
        lineNum = -1
        rowNum = 0
        useLine = False
        isReadingLevelData = False

        for line in f:
            lineNum += 1
            while len(line) > 0 and (line[-1] == "\n" or line[-1] == "\r"):
                line = line[:-1]
            while len(line) > 0 and (line[0] == "\n" or line[0] == "\r"):
                line = line[1:]
            str_splitBySpace = line.split(" ")

            j = str_splitBySpace[0]

            if j == "'" or j == "":
                useLine = False
            elif j == "#":
                # special divider / attribute line
                useLine = False

                firstWord = str_splitBySpace[1]

                if firstWord == "lvlwidth":
                    self.lvlWidth = int(str_splitBySpace[2])

                elif firstWord == "lvlheight":
                    self.lvlHeight = int(str_splitBySpace[2])

                elif firstWord == "edgecolor":
                    # edge color keyword for backwards compatibility (single edge color) mazes
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.edgeLightColor = (red, green, blue, 255)
                    self.edgeShadowColor = (red, green, blue, 255)

                elif firstWord == "edgelightcolor":
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.edgeLightColor = (red, green, blue, 255)

                elif firstWord == "edgeshadowcolor":
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.edgeShadowColor = (red, green, blue, 255)

                elif firstWord == "fillcolor":
                    red = int(str_splitBySpace[2])
                    green = int(str_splitBySpace[3])
                    blue = int(str_splitBySpace[4])
                    self.fillColor = (red, green, blue, 255)

                elif firstWord == "startleveldata":
                    isReadingLevelData = True
                    rowNum = 0

                elif firstWord == "endleveldata":
                    isReadingLevelData = False

            else:
                useLine = True

            if useLine == True:
                if isReadingLevelData == True:
                    for k in range(0, self.lvlWidth, 1):
                        self.SetMapTile(rowNum, k, int(str_splitBySpace[k]))

                        thisID = int(str_splitBySpace[k])
                        if thisID == 4:
                            # starting position for pac-man

                            player.x = k * 16
                            player.y = rowNum * 16
                            self.SetMapTile(rowNum, k, 0)

                        elif thisID == 10:
                            # and thisID <= 13:
                            # one of the ghosts

                            AIghost.x = k * 16
                            AIghost.homeX = k * 16
                            AIghost.y = rowNum * 16
                            AIghost.homeY = rowNum * 16
                            self.SetMapTile(rowNum, k, 0)

                    rowNum += 1

        GetCrossRef()

        path.ResizeMap(self.lvlHeight, self.lvlWidth)

        for row in range(0, path.size[0], 1):
            for col in range(0, path.size[1], 1):
                if self.IsWall(row, col):
                    path.SetType(row, col, 1)
                else:
                    path.SetType(row, col, 0)


def GetCrossRef():
    f = open(os.path.join(SCRIPT_PATH, "res", "crossref.txt"), "r")
    lineNum = 0
    useLine = False

    for i in f.readlines():
        while len(i) > 0 and (i[-1] == "\n" or i[-1] == "\r"):
            i = i[:-1]
        while len(i) > 0 and (i[0] == "\n" or i[0] == "\r"):
            i = i[1:]
        str_splitBySpace = i.split(" ")

        j = str_splitBySpace[0]

        if j == "'" or j == "" or j == "#":
            useLine = False
        else:
            useLine = True

        if useLine == True:
            tileIDName[int(str_splitBySpace[0])] = str_splitBySpace[1]
            tileID[str_splitBySpace[1]] = int(str_splitBySpace[0])

            thisID = int(str_splitBySpace[0])
            if not thisID in NO_GIF_TILES:
                tileIDImage[thisID] = pygame.image.load(
                    os.path.join(
                        SCRIPT_PATH, "res", "tiles", str_splitBySpace[1] + ".gif"
                    )
                ).convert()
            else:
                tileIDImage[thisID] = pygame.Surface((16, 16))

            for y in range(0, 16, 1):
                for x in range(0, 16, 1):
                    if tileIDImage[thisID].get_at((x, y)) == (255, 206, 255, 255):
                        # wall edge
                        tileIDImage[thisID].set_at((x, y), thisLevel.edgeLightColor)

                    elif tileIDImage[thisID].get_at((x, y)) == (132, 0, 132, 255):
                        # wall fill
                        tileIDImage[thisID].set_at((x, y), thisLevel.fillColor)

                    elif tileIDImage[thisID].get_at((x, y)) == (255, 0, 255, 255):
                        # pellet color
                        tileIDImage[thisID].set_at((x, y), thisLevel.edgeShadowColor)

                    # elif tileIDImage[thisID].get_at((x, y)) == (128, 0, 128, 255):
                    # pellet color
                    # tileIDImage[thisID].set_at((x, y), thisLevel.pelletColor)

        lineNum += 1


def CheckIfCloseButton(events):
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit(0)


def PressToStart():
    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        print("press")
        thisGame.SetMode(2)


def SetVelGhost(AIghost):
    if thisGame.mode == 1:
        AIghost.speed = 0
    elif thisGame.mode == 2:
        AIghost.speed = 1


def DrawPath():
    for Adr in AIghost.visited:
        x, y = Adr[0], Adr[1]
        screen.blit(imgPath, (x, y))


img_Cost = pygame.image.load(
    os.path.join(SCRIPT_PATH, "res", "text", "cost.gif")
).convert()
digit = {}
for i in range(0, 10, 1):
    digit[i] = pygame.image.load(
        os.path.join(SCRIPT_PATH, "res", "text", str(i) + ".gif")
    ).convert()


def DrawCost():
    screen.blit(img_Cost, (15 * 16, 4))
    strNumber = str(int(AIghost.cost))
    for i in range(0, len(strNumber), 1):
        iDigit = int(strNumber[i])
        screen.blit(digit[iDigit], ((28 + i) * 10, 4))


path = path_finder()

tileIDName = {}
tileID = {}
tileIDImage = {}


player = pacman()
AIghost = ghost(1)

thisGame = game()
thisLevel = level()
thisLevel.LoadLevel(1)
thisGame.SetMode(2)

# print(AIghost.x, AIghost.y)
# print(player.x, player.y)
# print(thisGame.mode)
while True:
    player.nearestRow = int(((player.y + 8) / 16))
    player.nearestCol = int(((player.x + 8) / 16))
    SetVelGhost(AIghost)
    CheckIfCloseButton(pygame.event.get())
    # PressToStart()
    # print(thisGame.mode)
    screen.blit(img_Background, (0, 0))
    DrawPath()
    # thisGame.SmartMoveScreen()
    thisLevel.DrawMap()

    player.Draw()
    AIghost.IsEnd()
    if thisGame.mode == 2:
        AIghost.Move()
    AIghost.Draw()
    # print((AIghost.currentPath))
    DrawCost()
    pygame.display.flip()

    clock.tick(60)
