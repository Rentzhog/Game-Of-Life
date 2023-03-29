from cmu_graphics import *
import math

app.width = 940
app.height = 540

app.background = 'black'

app.stepsPerSecond = 60

class Input:

    keysHeld = []
    keyPressed = None
    keyReleased = None
    mousePressed = False
    mouseHeld = False
    mousePos = [0, 0]

    @staticmethod
    def resetInputs():
        # Reset Input at the end
        Input.keysHeld = []
        Input.keyPressed = None
        Input.keyReleased = None
        Input.mousePressed = False
        Input.mouseHeld = False

class World:
    scale = 10
    offsetX = 0
    offsetY = 0
    startPanX = 0
    startPanY = 0

    buffer = scale/10

    objects = []

    @staticmethod
    def drawWorld():
        for o in World.objects:
            if(hasattr(o, 'draw')):
                o.draw()


    @staticmethod
    def updateWorld():

        for o in World.objects:
            if(hasattr(o, 'update')):
                o.update()

        World.updatePanAndZoom()

        #Draw the world after all updates
        World.drawWorld()

    @staticmethod
    def updatePanAndZoom():
        mX = Input.mousePos[0]
        mY = Input.mousePos[1]

        if('space' in Input.keysHeld):
            if(Input.mousePressed):
                World.startPanX = mX
                World.startPanY = mY

            if(Input.mouseHeld):
                World.offsetX -= (mX - World.startPanX) / World.scale
                World.offsetY -= (mY - World.startPanY) / World.scale

                World.startPanX = mX
                World.startPanY = mY


        mxPreZoom_WS, myPreZoom_WS = World.ScreenToWorld(mX, mY)

        if('q' in Input.keysHeld or 'Q' in Input.keysHeld):
            World.scale *= 1.03

        if('e' in Input.keysHeld or 'E' in Input.keysHeld):
            if(World.scale * 0.97 > 1):
                World.scale *= 0.97

        
        mxPostZoom_WS, myPostZoom_WS = World.ScreenToWorld(mX, mY)

        World.offsetX += (mxPreZoom_WS - mxPostZoom_WS)
        World.offsetY += (myPreZoom_WS - myPostZoom_WS)

    @staticmethod
    def centerScreenToWorldPoint(x, y):
        World.offsetX = (-app.width/(2 * World.scale)) + x
        World.offsetY = (-app.height/(2 * World.scale)) + y

    @staticmethod
    def WorldToScreen(worldX, worldY):
        screenX = (worldX - World.offsetX) * World.scale
        screenY = (worldY - World.offsetY) * World.scale

        return screenX, screenY

    @staticmethod
    def ScreenToWorld(screenX, screenY):
        worldX = screenX / World.scale + World.offsetX
        worldY = screenY / World.scale + World.offsetY

        return worldX, worldY

class Grid:
    def __init__(self, size, leftSS, topSS, color=rgb(28, 28, 28)):
        self.size = size
        self.top = topSS
        self.left = leftSS
        self.color = color

        self.cells = []
        
        self.linesH, self.linesV = self.initDraw()

        self.simStarted = False
        self.simCount = 0

        World.objects.append(self)

    def update(self):
        if(Input.keyPressed == '0'):
            World.centerScreenToWorldPoint(self.size/2, self.size/2)
        elif(Input.keyPressed == 'enter'):
            self.simStarted = not self.simStarted
            print('ye')

        if(not 'space' in Input.keysHeld and (Input.mouseHeld or Input.mousePressed)):
            cellX, cellY = self.screenPosToCellCoords(Input.mousePos[0], Input.mousePos[1])
            if('tab' in Input.keysHeld):
                condition, cell = self.getCellOnCoords(cellX, cellY)
                if(condition):
                    self.removeCell(cell)
            else:
                self.addCell(cellX, cellY)

        if(self.simStarted):
            self.simCount += 1
            if(self.simCount == 2):
                self.calculateNextGen()
                self.simCount = 0

    def calculateNextGen(self):
        killCells = []

        emptyCells = []
        emptyCellsAliveNeighboors = []
        
        for cell in self.cells:
            neighboors = self.getNeighboorsOfCell(cell.x, cell.y)
            aliveCells = 0
            for n in range(len(neighboors)):
                condition, neighboorCell = self.getCellOnCoords(neighboors[n][0], neighboors[n][1])
                
                if(condition):
                    aliveCells += 1
                else:
                    if([neighboors[n][0], neighboors[n][1]] not in emptyCells):
                        emptyCellsAliveNeighboors.append(1)
                        emptyCells.append([neighboors[n][0], neighboors[n][1]])
                    else:
                        emptyCellsAliveNeighboors[emptyCells.index([neighboors[n][0], neighboors[n][1]])] += 1

            if(aliveCells < 2 or aliveCells > 3):
                killCells.append(cell)

        for i in emptyCells:
            if(emptyCellsAliveNeighboors[emptyCells.index(i)] == 3):
                self.addCell(i[0], i[1])

        for c in killCells:
            self.removeCell(c)

    def getNeighboorsOfCell(self, cellX, cellY):
        neighboors = []
        neighboors.append([cellX - 1, cellY - 1])
        neighboors.append([cellX, cellY - 1])
        neighboors.append([cellX + 1, cellY - 1])
        neighboors.append([cellX + 1, cellY])
        neighboors.append([cellX + 1, cellY + 1])
        neighboors.append([cellX, cellY + 1])
        neighboors.append([cellX - 1, cellY + 1])
        neighboors.append([cellX - 1, cellY])

        return neighboors

    def screenPosToCellCoords(self, screenX, screenY):
        worldX, worldY = World.ScreenToWorld(screenX, screenY)

        cellX = min(max(math.floor(worldX), 0), grid.size - 1)
        cellY = min(max(math.floor(worldY), 0), grid.size - 1)

        return cellX, cellY

    def getCellOnCoords(self, x, y):
        for cell in self.cells:
            if(cell.x == x and cell.y == y):
                return True, cell
            
        return False, None

    def removeCell(self, cell):
        if(cell in self.cells):
            cell.delete()

    def addCell(self, cellX, cellY):
        hasCell, cell = self.getCellOnCoords(cellX, cellY)
        if(not hasCell):
            Cell(self, cellX, cellY)
        else:
            print('Cell already exists on coords')

    def initDraw(self):
        horizontalLines = []
        verticalLines = []

        count = 0

        ### MAKE GRID ###
        for i in range(self.size + 1):
            count += 1
            # Horizontal Lines
            startX_H = 0 + self.left
            startY_H = i + self.top
            endX_H = self.size + self.left
            endY_H = i + self.top

            SS_startX_H, SS_startY_H = World.WorldToScreen(startX_H, startY_H)
            SS_endX_H, SS_endY_H = World.WorldToScreen(endX_H, endY_H)

            lineH = Line(SS_startX_H, SS_startY_H, SS_endX_H, SS_endY_H, lineWidth=World.buffer, fill=self.color)

            horizontalLines.append(lineH)
            app.group.add(lineH)

            # Vertical Lines
            startX_V = i + self.left
            startY_V = 0 + self.top
            endX_V = i + self.left
            endY_V = self.size + self.top

            SS_startX_V, SS_startY_V = World.WorldToScreen(startX_V, startY_V)
            SS_endX_V, SS_endY_V = World.WorldToScreen(endX_V, endY_V)

            lineV = Line(SS_startX_V, SS_startY_V, SS_endX_V, SS_endY_V, lineWidth=World.buffer, fill=self.color)

            verticalLines.append(lineV)
            app.group.add(lineV)


        return horizontalLines, verticalLines

    def draw(self):

        worldLeft, worldTop = World.ScreenToWorld(0, 0)
        worldRight, worldBottom = World.ScreenToWorld(app.width, app.height)

        ### MAKE GRID ###
        for i in range(len(self.linesH)):
            self.linesH[i].visible = True
            if(i >= worldTop and i <= worldBottom):
                # Horizontal Lines
                startX_H = 0 + self.left
                startY_H = i + self.top
                endX_H = self.size + self.left
                endY_H = i + self.top

                SS_startX_H, SS_startY_H = World.WorldToScreen(startX_H, startY_H)
                SS_endX_H, SS_endY_H = World.WorldToScreen(endX_H, endY_H)

                self.linesH[i].x1 = SS_startX_H
                self.linesH[i].y1 = SS_startY_H

                self.linesH[i].x2 = SS_endX_H
                self.linesH[i].y2 = SS_endY_H

                self.linesH[i].lineWidth = World.buffer

            else:
                self.linesH[i].visible = False
        
        for i in range(len(self.linesV)):
            self.linesV[i].visible = True
            if(i >= worldLeft and i <= worldRight):
                # Vertical Lines
                startX_V = i + self.left
                startY_V = 0 + self.top
                endX_V = i + self.left
                endY_V = self.size + self.top

                SS_startX_V, SS_startY_V = World.WorldToScreen(startX_V, startY_V)
                SS_endX_V, SS_endY_V = World.WorldToScreen(endX_V, endY_V)

                self.linesV[i].x1 = SS_startX_V
                self.linesV[i].y1 = SS_startY_V

                self.linesV[i].x2 = SS_endX_V
                self.linesV[i].y2 = SS_endY_V

                self.linesV[i].lineWidth = World.buffer
            
            else:
                self.linesV[i].visible = False

class Cell:
    def __init__(self, grid, gridX, gridY):
        self.x = gridX
        self.y = gridY
        self.grid = grid

        grid.cells.append(self)

        self.square = self.initDraw()
        
        World.objects.append(self)
    
    def delete(self):
        self.grid.cells.remove(self)
        if(self.square):
            app.group.remove(self.square)
        World.objects.remove(self)
    
    def initDraw(self):
        screenX, screenY = World.WorldToScreen(self.x, self.y)
        
        newRect = Rect(screenX + World.buffer/2, screenY + World.buffer/2, World.scale - World.buffer, World.scale - World.buffer, fill='white')

        app.group.add(newRect)

        return newRect

    def draw(self):
        worldLeft, worldTop = World.ScreenToWorld(0, 0)
        worldRight, worldBottom = World.ScreenToWorld(app.width, app.height)
        if((self.x < worldRight and self.x + 1 > worldLeft) and (self.y < worldBottom and self.y + 1 > worldTop)):
            if(self.square):
                self.square.visible = True

                screenX, screenY = World.WorldToScreen(self.x, self.y)

                self.square.left = screenX + World.buffer/2
                self.square.top = screenY + World.buffer/2
                self.square.width = World.scale - World.buffer
                self.square.height = World.scale - World.buffer
            else:
                self.square = self.initDraw()
        elif(self.square):
            app.group.remove(self.square)
            self.square = None

class Cursor:
    def __init__(self, grid):
        self.grid = grid
        self.drawing = self.initDraw()

        World.objects.append(self)

    def initDraw(self):

        cursorRect = Rect(0, 0, World.scale - World.buffer, World.scale - World.buffer, fill='white', opacity=40)
        app.group.add(cursorRect)
        
        return cursorRect

    def draw(self):
        hoverCellX, hoverCellY = grid.screenPosToCellCoords(Input.mousePos[0], Input.mousePos[1])

        screenX, screenY = World.WorldToScreen(hoverCellX, hoverCellY)

        if('tab' in Input.keysHeld):
            color = 'red'
        else:
            color = 'white'

        self.drawing.left = screenX + World.buffer/2
        self.drawing.top = screenY + World.buffer/2
        self.drawing.width = World.scale - World.buffer
        self.drawing.height = World.scale - World.buffer

        self.drawing.fill = color

grid = Grid(200, 0, 0)
cursor = Cursor(grid)

World.centerScreenToWorldPoint(grid.size/2, grid.size/2)

def onStep():
    World.updateWorld()
    cursor.drawing.toFront()

    Input.resetInputs()


def onKeyHold(keys):
    Input.keysHeld = keys

def onKeyPress(key):
    Input.keyPressed = key

def onKeyRelease(key):
    Input.keyReleased = key
    

def onMousePress(mX, mY):
    Input.mousePos = [mX, mY]
    Input.mousePressed = True

def onMouseDrag(mX, mY):
    Input.mousePos = [mX, mY]
    Input.mouseHeld = True

def onMouseMove(mX, mY):
    Input.mousePos = [mX, mY]

cmu_graphics.run()

