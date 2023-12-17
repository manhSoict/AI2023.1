import pygame, sys, os, random
from pygame.locals import *

SCRIPT_PATH = sys.path[0]

pygame.mixer.pre_init(22050, 16, 2, 512)
JS_STARTBUTTON = 0  # button number to start the game. this is a matter of personal preference, and will vary from device to device
pygame.mixer.init()

clock = pygame.time.Clock()
pygame.init()

window = pygame.display.set_mode((1, 1))
pygame.display.set_caption("Pacman")

screen = pygame.display.get_surface()

img_Background = pygame.image.load(
    os.path.join(SCRIPT_PATH, "res", "backgrounds", "1.gif")
).convert()


ghostcolor = {}
ghostcolor[0] = (255, 0, 0, 255)
ghostcolor[1] = (255, 128, 255, 255)
ghostcolor[2] = (128, 255, 255, 255)
ghostcolor[3] = (255, 128, 0, 255)
ghostcolor[4] = (50, 50, 255, 255)  # blue, vulnerable ghost
ghostcolor[5] = (255, 255, 255, 255)  # white, flashing ghost


class game:
    def __init__(self):
        self.levelNum = 0
        self.score = 0
        self.lives = 3

        # game "mode" variable
        # 1 = normal
        # 2 = hit ghost
        # 3 = game over
        # 4 = wait to start
        # 5 = wait after eating ghost
        # 6 = wait after finishing level
        self.mode = 0
        self.modeTimer = 0
        self.ghostTimer = 0
        self.ghostValue = 0


        self.SetMode(3)

        # camera variables
        self.screenPixelPos = (
            0,
            0,
        )  # absolute x,y position of the screen from the upper-left corner of the level
        self.screenNearestTilePos = (
            0,
            0,
        )  # nearest-tile position of the screen from the UL corner
        self.screenPixelOffset = (
            0,
            0,
        )  # offset in pixels of the screen from its nearest-tile position

        self.screenTileSize = (23, 21)
        self.screenSize = (self.screenTileSize[1] * 16, self.screenTileSize[0] * 16)

        # numerical display digits
        self.digit = {}
        for i in range(0, 10, 1):
            self.digit[i] = pygame.image.load(
                os.path.join(SCRIPT_PATH, "res", "text", str(i) + ".gif")
            ).convert()
        self.imLife = pygame.image.load(
            os.path.join(SCRIPT_PATH, "res", "text", "life.gif")
        ).convert()
        self.imGameOver = pygame.image.load(
            os.path.join(SCRIPT_PATH, "res", "text", "gameover.gif")
        ).convert()
        self.imReady = pygame.image.load(
            os.path.join(SCRIPT_PATH, "res", "text", "ready.gif")
        ).convert()
        self.imLogo = pygame.image.load(
            os.path.join(SCRIPT_PATH, "res", "text", "logo.gif")
        ).convert()

    # def StartNewGame(self):
    #     self.levelNum = 1
    #     self.score = 0
    #     self.lives = 3

    #     self.SetMode(4)
    #     thisLevel.LoadLevel(thisGame.GetLevelNum())

    def DrawNumber(self, number, x, y):
        strNumber = str(int(number))
        for i in range(0, len(strNumber), 1):
            iDigit = int(strNumber[i])
            screen.blit(self.digit[iDigit], (x + i * 9, y))

    # def SmartMoveScreen(self):
    #     possibleScreenX = player.x - self.screenTileSize[1] / 2 * 16
    #     possibleScreenY = player.y - self.screenTileSize[0] / 2 * 16

    #     if possibleScreenX < 0:
    #         possibleScreenX = 0
    #     elif possibleScreenX > thisLevel.lvlWidth * 16 - self.screenSize[0]:
    #         possibleScreenX = thisLevel.lvlWidth * 16 - self.screenSize[0]

    #     if possibleScreenY < 0:
    #         possibleScreenY = 0
    #     elif possibleScreenY > thisLevel.lvlHeight * 16 - self.screenSize[1]:
    #         possibleScreenY = thisLevel.lvlHeight * 16 - self.screenSize[1]

    # thisGame.MoveScreen(possibleScreenX, possibleScreenY)

    # def MoveScreen(self, newX, newY):
    #     self.screenPixelPos = (newX, newY)
    #     self.screenNearestTilePos = (
    #         int(newY / 16),
    #         int(newX / 16),
    #     )  # nearest-tile position of the screen from the UL corner
    #     self.screenPixelOffset = (
    #         newX - self.screenNearestTilePos[1] * 16,
    #         newY - self.screenNearestTilePos[0] * 16,
    #     )

    def GetScreenPos(self):
        return self.screenPixelPos

    def GetLevelNum(self):
        return self.levelNum

    def SetMode(self, newMode):
        self.mode = newMode
        self.modeTimer = 0
        # print " ***** GAME MODE IS NOW ***** " + str(newMode)

class node ():

    def __init__ (self):
        self.g = -1 # movement cost to move from previous node to this one (usually +10)
        self.h = -1 # estimated movement cost to move from this node to the ending node (remaining horizontal and vertical steps * 10)
        self.f = -1 # total movement cost of this node (= g + h)
        # parent node - used to trace path back to the starting node at the end
        self.parent = (-1, -1)
        # node type - 0 for empty space, 1 for wall (optionally, 2 for starting node and 3 for end)
        self.type = -1

class path_finder ():

    def __init__ (self):
        # map is a 1-DIMENSIONAL array.
        # use the Unfold( (row, col) ) function to convert a 2D coordinate pair
        # into a 1D index to use with this array.
        self.map = {}
        self.size = (-1, -1) # rows by columns

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
        self.neighborSet = [ (0, -1), (0, 1), (-1, 0), (1, 0) ]

    def ResizeMap (self, numRows, numCols):
        self.map = {}
        self.size = (numRows, numCols)

        # initialize path_finder map to a 2D array of empty nodes
        for row in range(0, self.size[0], 1):
            for col in range(0, self.size[1], 1):
                self.Set( row, col, node() )
                self.SetType( row, col, 0 )

    def CleanUpTemp (self):

        # this resets variables needed for a search (but preserves the same map / maze)

        self.pathChainRev = ""
        self.pathChain = ""
        self.current = (-1, -1)
        self.openList = []
        self.closedList = []

    def FindPath (self, startPos, endPos ):

        self.CleanUpTemp()

        # (row, col) tuples
        self.start = startPos
        self.end = endPos

        # add start node to open list
        self.AddToOpenList( self.start )
        self.SetG ( self.start, 0 )
        self.SetH ( self.start, 0 )
        self.SetF ( self.start, 0 )

        doContinue = True

        while (doContinue == True):

            thisLowestFNode = self.GetLowestFNode()

            if not thisLowestFNode == self.end and not thisLowestFNode == False:
                self.current = thisLowestFNode
                self.RemoveFromOpenList( self.current )
                self.AddToClosedList( self.current )

                for offset in self.neighborSet:
                    thisNeighbor = (self.current[0] + offset[0], self.current[1] + offset[1])

                    if not thisNeighbor[0] < 0 and not thisNeighbor[1] < 0 and not thisNeighbor[0] > self.size[0] - 1 and not thisNeighbor[1] > self.size[1] - 1 and not self.GetType( thisNeighbor ) == 1:
                        cost = self.GetG( self.current ) + 10

                        if self.IsInOpenList( thisNeighbor ) and cost < self.GetG( thisNeighbor ):
                            self.RemoveFromOpenList( thisNeighbor )

                        #if self.IsInClosedList( thisNeighbor ) and cost < self.GetG( thisNeighbor ):
                        #   self.RemoveFromClosedList( thisNeighbor )

                        if not self.IsInOpenList( thisNeighbor ) and not self.IsInClosedList( thisNeighbor ):
                            self.AddToOpenList( thisNeighbor )
                            self.SetG( thisNeighbor, cost )
                            self.CalcH( thisNeighbor )
                            self.CalcF( thisNeighbor )
                            self.SetParent( thisNeighbor, self.current )
            else:
                doContinue = False

        if thisLowestFNode == False:
            return False

        # reconstruct path
        self.current = self.end
        while not self.current == self.start:
            # build a string representation of the path using R, L, D, U
            if self.current[1] > self.GetParent(self.current)[1]:
                self.pathChainRev += 'R'
            elif self.current[1] < self.GetParent(self.current)[1]:
                self.pathChainRev += 'L'
            elif self.current[0] > self.GetParent(self.current)[0]:
                self.pathChainRev += 'D'
            elif self.current[0] < self.GetParent(self.current)[0]:
                self.pathChainRev += 'U'
            self.current = self.GetParent(self.current)
            self.SetType( self.current[0],self.current[1], 4)

        # because pathChainRev was constructed in reverse order, it needs to be reversed!
        for i in range(len(self.pathChainRev) - 1, -1, -1):
            self.pathChain += self.pathChainRev[i]

        # set start and ending positions for future reference
        self.SetType( self.start[0],self.start[1], 2)
        self.SetType( self.end[0],self.start[1], 3)

        return self.pathChain

    def Unfold (self, row,col):
        # this function converts a 2D array coordinate pair (row, col)
        # to a 1D-array index, for the object's 1D map array.
        return (row * self.size[1]) + col

    def Set (self, row,col, newNode):
        # sets the value of a particular map cell (usually refers to a node object)
        self.map[ self.Unfold(row, col) ] = newNode

    def GetType (self,val):
        row,col = val
        return self.map[ self.Unfold(row, col) ].type

    def SetType (self,row,col, newValue):
        self.map[ self.Unfold(row, col) ].type = newValue

    def GetF (self, val):
        row,col = val
        return self.map[ self.Unfold(row, col) ].f

    def GetG (self, val):
        row,col = val
        return self.map[ self.Unfold(row, col) ].g

    def GetH (self, val):
        row,col = val
        return self.map[ self.Unfold(row, col) ].h

    def SetG (self, val, newValue ):
        row,col = val
        self.map[ self.Unfold(row, col) ].g = newValue

    def SetH (self, val, newValue ):
        row,col = val
        self.map[ self.Unfold(row, col) ].h = newValue

    def SetF (self, val, newValue ):
        row,col = val
        self.map[ self.Unfold(row, col) ].f = newValue

    def CalcH (self, val):
        row,col = val
        self.map[ self.Unfold(row, col) ].h = abs(row - self.end[0]) + abs(col - self.end[0])

    def CalcF (self, val):
        row,col = val
        unfoldIndex = self.Unfold(row, col)
        self.map[unfoldIndex].f = self.map[unfoldIndex].g + self.map[unfoldIndex].h

    def AddToOpenList (self, val):
        row,col = val
        self.openList.append( (row, col) )

    def RemoveFromOpenList (self, val ):
        row,col = val
        self.openList.remove( (row, col) )

    def IsInOpenList (self, val ):
        row,col = val
        if self.openList.count( (row, col) ) > 0:
            return True
        else:
            return False

    def GetLowestFNode (self):
        lowestValue = 1000 # start arbitrarily high
        lowestPair = (-1, -1)

        for iOrderedPair in self.openList:
            if self.GetF( iOrderedPair ) < lowestValue:
                lowestValue = self.GetF( iOrderedPair )
                lowestPair = iOrderedPair

        if not lowestPair == (-1, -1):
            return lowestPair
        else:
            return False

    def AddToClosedList (self, val ):
        row,col = val
        self.closedList.append( (row, col) )

    def IsInClosedList (self, val ):
        row,col = val
        if self.closedList.count( (row, col) ) > 0:
            return True
        else:
            return False

    def SetParent (self, val, val2 ):
        row,col = val
        parentRow,parentCol = val2
        self.map[ self.Unfold(row, col) ].parent = (parentRow, parentCol)

    def GetParent (self, val ):
        row,col = val
        return self.map[ self.Unfold(row, col) ].parent

    def draw (self):
        for row in range(0, self.size[0], 1):
            for col in range(0, self.size[1], 1):

                thisTile = self.GetType((row, col))
                screen.blit (tileIDImage[ thisTile ], (col * 32, row * 32))

class level ():

    def __init__ (self):
        self.lvlWidth = 0
        self.lvlHeight = 0
        self.edgeLightColor = (255, 255, 0, 255)
        self.edgeShadowColor = (255, 150, 0, 255)
        self.fillColor = (0, 255, 255, 255)
        self.pelletColor = (255, 255, 255, 255)

        self.map = {}

        self.pellets = 0
        self.powerPelletBlinkTimer = 0

    def SetMapTile (self, row, col, newValue):
        self.map[ (row * self.lvlWidth) + col ] = newValue

    def GetMapTile (self, row, col):
        if row >= 0 and row < self.lvlHeight and col >= 0 and col < self.lvlWidth:
            return self.map[ (row * self.lvlWidth) + col ]
        else:
            return 0

    def IsWall (self, row, col):

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


    def CheckIfHitWall (self, possiblePlayerX, possiblePlayerY, row, col):

        numCollisions = 0

        # check each of the 9 surrounding tiles for a collision
        for iRow in range(row - 1, row + 2, 1):
            for iCol in range(col - 1, col + 2, 1):

                if  (possiblePlayerX - (iCol * 16) < 16) and (possiblePlayerX - (iCol * 16) > -16) and (possiblePlayerY - (iRow * 16) < 16) and (possiblePlayerY - (iRow * 16) > -16):

                    if self.IsWall(iRow, iCol):
                        numCollisions += 1

        if numCollisions > 0:
            return True
        else:
            return False


    def CheckIfHit (self, playerX, playerY, x, y, cushion):

        if (playerX - x < cushion) and (playerX - x > -cushion) and (playerY - y < cushion) and (playerY - y > -cushion):
            return True
        else:
            return False


    def CheckIfHitSomething (self, playerX, playerY, row, col):

        for iRow in range(row - 1, row + 2, 1):
            for iCol in range(col - 1, col + 2, 1):

                if  (playerX - (iCol * 16) < 16) and (playerX - (iCol * 16) > -16) and (playerY - (iRow * 16) < 16) and (playerY - (iRow * 16) > -16):
                    # check the offending tile ID
                    result = thisLevel.GetMapTile(iRow, iCol)

                    if result == tileID[ 'pellet' ]:
                        # got a pellet
                        thisLevel.SetMapTile(iRow, iCol, 0)
                        snd_pellet[player.pelletSndNum].play()
                        player.pelletSndNum = 1 - player.pelletSndNum

                        thisLevel.pellets -= 1

                        thisGame.AddToScore(10)

                        if thisLevel.pellets == 0:
                            # no more pellets left!
                            # WON THE LEVEL
                            thisGame.SetMode( 6 )


                    elif result == tileID[ 'pellet-power' ]:
                        # got a power pellet
                        thisLevel.SetMapTile(iRow, iCol, 0)
                        snd_powerpellet.play()

                        thisGame.AddToScore(100)
                        thisGame.ghostValue = 200

                        thisGame.ghostTimer = 360
                        for i in range(0, 4, 1):
                            if ghosts[i].state == 1:
                                ghosts[i].state = 2

                    elif result == tileID[ 'door-h' ]:
                        # ran into a horizontal door
                        for i in range(0, thisLevel.lvlWidth, 1):
                            if not i == iCol:
                                if thisLevel.GetMapTile(iRow, i) == tileID[ 'door-h' ]:
                                    player.x = i * 16

                                    if player.velX > 0:
                                        player.x += 16
                                    else:
                                        player.x -= 16

                    elif result == tileID[ 'door-v' ]:
                        # ran into a vertical door
                        for i in range(0, thisLevel.lvlHeight, 1):
                            if not i == iRow:
                                if thisLevel.GetMapTile(i, iCol) == tileID[ 'door-v' ]:
                                    player.y = i * 16

                                    if player.velY > 0:
                                        player.y += 16
                                    else:
                                        player.y -= 16

    def GetGhostBoxPos (self):

        for row in range(0, self.lvlHeight, 1):
            for col in range(0, self.lvlWidth, 1):
                if self.GetMapTile(row, col) == tileID[ 'ghost-door' ]:
                    return (row, col)

        return False

    def GetPathwayPairPos (self):

        doorArray = []

        for row in range(0, self.lvlHeight, 1):
            for col in range(0, self.lvlWidth, 1):
                if self.GetMapTile(row, col) == tileID[ 'door-h' ]:
                    # found a horizontal door
                    doorArray.append( (row, col) )
                elif self.GetMapTile(row, col) == tileID[ 'door-v' ]:
                    # found a vertical door
                    doorArray.append( (row, col) )

        if len(doorArray) == 0:
            return False

        chosenDoor = random.randint(0, len(doorArray) - 1)

        if self.GetMapTile( doorArray[chosenDoor][0],doorArray[chosenDoor][1] ) == tileID[ 'door-h' ]:
            # horizontal door was chosen
            # look for the opposite one
            for i in range(0, thisLevel.lvlWidth, 1):
                if not i == doorArray[chosenDoor][1]:
                    if thisLevel.GetMapTile(doorArray[chosenDoor][0], i) == tileID[ 'door-h' ]:
                        return doorArray[chosenDoor], (doorArray[chosenDoor][0], i)
        else:
            # vertical door was chosen
            # look for the opposite one
            for i in range(0, thisLevel.lvlHeight, 1):
                if not i == doorArray[chosenDoor][0]:
                    if thisLevel.GetMapTile(i, doorArray[chosenDoor][1]) == tileID[ 'door-v' ]:
                        return doorArray[chosenDoor], (i, doorArray[chosenDoor][1])

        return False

    def PrintMap (self):

        for row in range(0, self.lvlHeight, 1):
            outputLine = ""
            for col in range(0, self.lvlWidth, 1):

                outputLine += str( self.GetMapTile(row, col) ) + ", "

            # print outputLine

    def DrawMap (self):

        self.powerPelletBlinkTimer += 1
        if self.powerPelletBlinkTimer == 60:
            self.powerPelletBlinkTimer = 0

        for row in range(-1, thisGame.screenTileSize[0] +1, 1):
            outputLine = ""
            for col in range(-1, thisGame.screenTileSize[1] +1, 1):

                # row containing tile that actually goes here
                actualRow = thisGame.screenNearestTilePos[0] + row
                actualCol = thisGame.screenNearestTilePos[1] + col

                useTile = self.GetMapTile(actualRow, actualCol)
                if not useTile == 0 and not useTile == tileID['door-h'] and not useTile == tileID['door-v']:
                    # if this isn't a blank tile

                    if useTile == tileID['pellet-power']:
                        if self.powerPelletBlinkTimer < 30:
                            screen.blit (tileIDImage[ useTile ], (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]) )

                    elif useTile == tileID['showlogo']:
                        screen.blit (thisGame.imLogo, (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]) )

                    elif useTile == tileID['hiscores']:
                            screen.blit(thisGame.imHiscores,(col*16-thisGame.screenPixelOffset[0],row*16-thisGame.screenPixelOffset[1]))

                    else:
                        screen.blit (tileIDImage[ useTile ], (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]) )

    def LoadLevel (self, levelNum):

        self.map = {}

        self.pellets = 0

        f = open(os.path.join(SCRIPT_PATH,"res","levels",str(levelNum) + ".txt"), 'r')
        # ANDY -- edit this
        #fileOutput = f.read()
        #str_splitByLine = fileOutput.split('\n')
        lineNum=-1
        rowNum = 0
        useLine = False
        isReadingLevelData = False

        for line in f:

          lineNum += 1

            # print " ------- Level Line " + str(lineNum) + " -------- "
          while len(line)>0 and (line[-1]=="\n" or line[-1]=="\r"): line=line[:-1]
          while len(line)>0 and (line[0]=="\n" or line[0]=="\r"): line=line[1:]
          str_splitBySpace = line.split(' ')


          j = str_splitBySpace[0]

          if (j == "'" or j == ""):
                # comment / whitespace line
                # print " ignoring comment line.. "
                useLine = False
          elif j == "#":
                # special divider / attribute line
                useLine = False

                firstWord = str_splitBySpace[1]

                if firstWord == "lvlwidth":
                    self.lvlWidth = int( str_splitBySpace[2] )
                    # print "Width is " + str( self.lvlWidth )

                elif firstWord == "lvlheight":
                    self.lvlHeight = int( str_splitBySpace[2] )
                    # print "Height is " + str( self.lvlHeight )

                elif firstWord == "edgecolor":
                    # edge color keyword for backwards compatibility (single edge color) mazes
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.edgeLightColor = (red, green, blue, 255)
                    self.edgeShadowColor = (red, green, blue, 255)

                elif firstWord == "edgelightcolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.edgeLightColor = (red, green, blue, 255)

                elif firstWord == "edgeshadowcolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.edgeShadowColor = (red, green, blue, 255)

                elif firstWord == "fillcolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.fillColor = (red, green, blue, 255)

                elif firstWord == "pelletcolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.pelletColor = (red, green, blue, 255)

                elif firstWord == "fruittype":
                    thisFruit.fruitType = int( str_splitBySpace[2] )

                elif firstWord == "startleveldata":
                    isReadingLevelData = True
                        # print "Level data has begun"
                    rowNum = 0

                elif firstWord == "endleveldata":
                    isReadingLevelData = False
                    # print "Level data has ended"

          else:
                useLine = True


            # this is a map data line
          if useLine == True:

                if isReadingLevelData == True:

                    # print str( len(str_splitBySpace) ) + " tiles in this column"

                    for k in range(0, self.lvlWidth, 1):
                        self.SetMapTile(rowNum, k, int(str_splitBySpace[k]) )

                        thisID = int(str_splitBySpace[k])
                        if thisID == 4:
                            # starting position for pac-man

                            player.homeX = k * 16
                            player.homeY = rowNum * 16
                            self.SetMapTile(rowNum, k, 0 )

                        elif thisID >= 10 and thisID <= 13:
                            # one of the ghosts

                            ghosts[thisID - 10].homeX = k * 16
                            ghosts[thisID - 10].homeY = rowNum * 16
                            self.SetMapTile(rowNum, k, 0 )

                        elif thisID == 2:
                            # pellet

                            self.pellets += 1

                    rowNum += 1


        # reload all tiles and set appropriate colors
        GetCrossRef()

        # load map into the pathfinder object
        path.ResizeMap( self.lvlHeight, self.lvlWidth )

        for row in range(0, path.size[0], 1):
            for col in range(0, path.size[1], 1):
                if self.IsWall( row, col ):
                    path.SetType( row, col, 1 )
                else:
                    path.SetType( row, col, 0 )

        # do all the level-starting stuff
        self.Restart()

    # def Restart (self):

    #     for i in range(0, 4, 1):
    #         # move ghosts back to home

    #         ghosts[i].x = ghosts[i].homeX
    #         ghosts[i].y = ghosts[i].homeY
    #         ghosts[i].velX = 0
    #         ghosts[i].velY = 0
    #         ghosts[i].state = 1
    #         ghosts[i].speed = 1
    #         ghosts[i].Move()

    #         # give each ghost a path to a random spot (containing a pellet)
    #         (randRow, randCol) = (0, 0)

    #         while not self.GetMapTile(randRow, randCol) == tileID[ 'pellet' ] or (randRow, randCol) == (0, 0):
    #             randRow = random.randint(1, self.lvlHeight - 2)
    #             randCol = random.randint(1, self.lvlWidth - 2)

    #         # print "Ghost " + str(i) + " headed towards " + str((randRow, randCol))
    #         ghosts[i].currentPath = path.FindPath( (ghosts[i].nearestRow, ghosts[i].nearestCol), (randRow, randCol) )
    #         ghosts[i].FollowNextPathWay()

    #     thisFruit.active = False

    #     thisGame.fruitTimer = 0

    #     player.x = player.homeX
    #     player.y = player.homeY
    #     player.velX = 0
    #     player.velY = 0

    #     player.anim_pacmanCurrent = player.anim_pacmanS
    #     player.animFrame = 3

# # create the pacman
# player = pacman()

# create a path_finder object
path = path_finder()

tileIDName = {} # gives tile name (when the ID# is known)
tileID = {} # gives tile ID (when the name is known)
tileIDImage = {} # gives tile image (when the ID# is known)

thisGame = game()
thisLevel = level()

while True:
    # CheckIfCloseButton( pygame.event.get() )

    # if thisGame.mode == 1:
    #     # normal gameplay mode
    #     CheckInputs()

    #     thisGame.modeTimer += 1
    #     player.Move()
    #     for i in range(0, 4, 1):
    #         ghosts[i].Move()
    #     thisFruit.Move()

    # elif thisGame.mode == 2:
    #     # waiting after getting hit by a ghost
    #     thisGame.modeTimer += 1

    #     if thisGame.modeTimer == 90:
    #         thisLevel.Restart()

    #         thisGame.lives -= 1
    #         if thisGame.lives == -1:
    #             thisGame.updatehiscores(thisGame.score)
    #             thisGame.SetMode( 3 )
    #             thisGame.drawmidgamehiscores()
    #         else:
    #             thisGame.SetMode( 4 )

    # elif thisGame.mode == 3:
    #     # game over
    #     CheckInputs()

    # elif thisGame.mode == 4:
    #     # waiting to start
    #     thisGame.modeTimer += 1

    #     if thisGame.modeTimer == 90:
    #         thisGame.SetMode( 1 )
    #         player.velX = player.speed

    # elif thisGame.mode == 5:
    #     # brief pause after munching a vulnerable ghost
    #     thisGame.modeTimer += 1

    #     if thisGame.modeTimer == 30:
    #         thisGame.SetMode( 1 )

    # elif thisGame.mode == 6:
    #     # pause after eating all the pellets
    #     thisGame.modeTimer += 1

    #     if thisGame.modeTimer == 60:
    #         thisGame.SetMode( 7 )
    #         oldEdgeLightColor = thisLevel.edgeLightColor
    #         oldEdgeShadowColor = thisLevel.edgeShadowColor
    #         oldFillColor = thisLevel.fillColor

    # elif thisGame.mode == 7:
    #     # flashing maze after finishing level
    #     thisGame.modeTimer += 1

    #     whiteSet = [10, 30, 50, 70]
    #     normalSet = [20, 40, 60, 80]

    #     if not whiteSet.count(thisGame.modeTimer) == 0:
    #         # member of white set
    #         thisLevel.edgeLightColor = (255, 255, 255, 255)
    #         thisLevel.edgeShadowColor = (255, 255, 255, 255)
    #         thisLevel.fillColor = (0, 0, 0, 255)
    #         GetCrossRef()
    #     elif not normalSet.count(thisGame.modeTimer) == 0:
    #         # member of normal set
    #         thisLevel.edgeLightColor = oldEdgeLightColor
    #         thisLevel.edgeShadowColor = oldEdgeShadowColor
    #         thisLevel.fillColor = oldFillColor
    #         GetCrossRef()
    #     elif thisGame.modeTimer == 150:
    #         thisGame.SetMode ( 8 )

    # elif thisGame.mode == 8:
    #     # blank screen before changing levels
    #     thisGame.modeTimer += 1
    #     if thisGame.modeTimer == 10:
    #         thisGame.SetNextLevel()

    # thisGame.SmartMoveScreen()

    screen.blit(img_Background, (0, 0))

    # if not thisGame.mode == 8:
    #     thisLevel.DrawMap()

    #     if thisGame.fruitScoreTimer > 0:
    #         if thisGame.modeTimer % 2 == 0:
    #             thisGame.DrawNumber (2500, thisFruit.x - thisGame.screenPixelPos[0] - 16, thisFruit.y - thisGame.screenPixelPos[1] + 4)

    #     for i in range(0, 4, 1):
    #         ghosts[i].Draw()
    #     thisFruit.Draw()
    #     player.Draw()

    #     if thisGame.mode == 3:
    #             screen.blit(thisGame.imHiscores,(32,256))

    # if thisGame.mode == 5:
    #     thisGame.DrawNumber (thisGame.ghostValue / 2, player.x - thisGame.screenPixelPos[0] - 4, player.y - thisGame.screenPixelPos[1] + 6)

    # thisGame.DrawScore()

    pygame.display.flip()

    clock.tick(60)
