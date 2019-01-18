#!/usr/local/anaconda/bin/python
#copyright: Zhenye Jiang, tronsupernova@outlook.com


from random import random
from tkinter import *
from copy import deepcopy


class Boggle():
    '''
    @param dict F 
    @param dict T
    @param int size
    @param int cellWidth
    @param array clone
    @param list soln
    @param cube ActionNow
    @param bool ActionNow_correct   
    '''
    def __init__(self, file='words.dat'):
        self.readData(file)
        self.size=5
        self.cellWidth=30
        self.newGame()

    def readData(self, file):
        self.F=dict()    
        self.T=dict()    
        obj=open(file)
        lines=obj.readlines()
        words_number=len(lines)
        for word in lines:
            word=word.strip()
            for c in word:
                if c in self.F.keys():   #计算字符分布总数
                    self.F[c]+=1
                else:
                    self.F[c]=1
            t=self.T                     #生成T字典
            for i in range(4):    
                if word[i] not in t.keys():
                    t[word[i]]=dict()
                t=t[word[i]]
            t[word[4]]=word
        for key in self.F.keys():
            self.F[key]/=words_number*5

    def ckSoln(self,soln):              #若指定路径无效，返回False；若指定路径对应单词，返回字符串单词；否则返回剩余路径对应的字典
        for index in range(len(soln)-1):
            if abs(soln[index][0]-soln[index+1][0])+abs(soln[index][1]-soln[index+1][1])>1:
                return False
        t=self.T
        for (x,y) in soln:
            c=self.board[x][y]
            if c not in t:
                return False
            t=t[c]
        return t

    def resetGame(self):
        self.board=self.clone
        self.soln=list()
        self.ActionNow=None
        self.ActionNow_correct=None  

    def newGame(self):       
        self.board=list()
        for i in range(self.size):
            t=list()
            self.board.append(t)
            for j in range(self.size):
                t.append(self.randChoice())  
        #self.board=[['b','y','u','u','n'],['s','x','o','y','r'],['h','s','l','o','r'],['t','y','a','f','n'],['b','c','r','o','c']] #供测试用
        self.soln=list()
        self.ActionNow=None
        self.ActionNow_correct=None 
        self.clone=self.board

    #按权重返回一个字母        
    def randChoice(self):   
        z=random()
        p=0
        for (key,value) in self.F.items():
            p+=value
            if p>=z:
                return key
            
    def playTK(self):
        self.initTK()
        print("<Left Click>: Choose character\n<Mid Click>: New Game\n<Right Click>: Reset Game\n<Triple Click>: Show all solutions")
        self.win.mainloop()

    def initTK(self):
        #创建窗口对象
        self.win =Tk()
        self.win.title('Boggle')
        #创建画布       
        self.canvas=Canvas(self.win,width=self.size*self.cellWidth,height=self.size*self.cellWidth,bg='white')
        self.canvas.pack()
        self.drawCanvas()
        #绑定事件
        self.canvas.bind("<Button-1>",self.extend)
        self.canvas.bind("<Button-2>",self.new)
        self.canvas.bind("<Button-3>",self.reset)
        self.canvas.bind("<Triple-Button-1>",self.getAllSolutions)
        self.canvas.focus_set()
        self.updateTK()

    #画游戏板块
    def drawCanvas(self):   
        self.canvas.create_rectangle(0,0,self.size*self.cellWidth,self.size*self.cellWidth,fill='white')
        #画格子
        for i in range(self.size):
            for j in range(self.size):
                self.canvas.create_rectangle(i*self.cellWidth,j*self.cellWidth,(i+1)*self.cellWidth,(j+1)*self.cellWidth)
        for i in range(self.size):
            for j in range(self.size):
                self.canvas.create_text(j*self.cellWidth+self.cellWidth/2,
                                        i*self.cellWidth+self.cellWidth/2,
                                        text=self.board[i][j].upper(),
                                        fill='black')

    #更新绿圈或者红圈
    def updateTK(self): 
        if self.ActionNow != None:
            if self.ActionNow_correct:
                color='green'
            else:
                color='red'
            x=self.ActionNow[0]
            y=self.ActionNow[1]
            self.canvas.create_oval(y*self.cellWidth+1, 
                                    x*self.cellWidth+1,
                                    (y+1)*self.cellWidth-1,
                                    (x+1)*self.cellWidth-1,
                                    fill=color)
            self.canvas.create_text(y*self.cellWidth+self.cellWidth/2,
                                        x*self.cellWidth+self.cellWidth/2,
                                        text=self.board[x][y].upper(),
                                        fill='black')
 
    #选中一个格子 
    def extend(self,event):         
        row=event.y//self.cellWidth
        col=event.x//self.cellWidth
        if (row,col) in self.soln:
            return
        self.ActionNow=(row,col)
        self.soln.append((row,col))
        result=self.ckSoln(self.soln)

        if type(result)==type(False):
            self.soln.pop()
            self.ActionNow_correct=False
        else:
            self.ActionNow_correct=True
        self.updateTK()
        
        if type(result)==type(''):
            self.findASolution(result)
          
    #新的游戏
    def new(self,event): 
        self.newGame()
        self.drawCanvas()
    
    #重置当前游戏
    def reset(self,event):
        self.resetGame()
        self.drawCanvas()
    
    #输出当前游戏所有解    
    def getAllSolutions(self,event):
        self.solve()

    #当用户找到了一个解
    def findASolution(self,result):
        print("You find a word:",result)
        self.resetGame()
        self.drawCanvas()
        
    #寻找所有解
    def solve(self):
        self.allSolutions=list()
        for i in range(self.size):
            for j in range(self.size):
                self.solutionPath=list()
                self.findAllSolutions((i,j))
        print("All solutions:"+str(self.allSolutions)+'\n')

    def findAllSolutions(self,coor):
        x=coor[0]
        y=coor[1]
        self.solutionPath.append(coor)
        result=self.ckSoln(self.solutionPath)
        if type(result)==type(False):
            return
        if type(result)==type(''):
            self.allSolutions.append(result)
            return
        if(x>0 and (x-1,y) not in self.solutionPath):
            self.findAllSolutions((x-1,y))
            self.solutionPath.pop()
        if(y>0 and (x,y-1) not in self.solutionPath):
            self.findAllSolutions((x,y-1))
            self.solutionPath.pop()
        if(y<4 and (x,y+1) not in self.solutionPath):
            self.findAllSolutions((x,y+1))
            self.solutionPath.pop()
        if(x<4 and (x+1,y) not in self.solutionPath):
            self.findAllSolutions((x+1,y))
            self.solutionPath.pop()

if __name__ == "__main__":
    Boggle().playTK()



