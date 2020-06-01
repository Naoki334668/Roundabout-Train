#coding utf-8
import tkinter as tk
import os
import json
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import pickle
import Searchbrain
from PIL import Image, ImageTk
from networkx.algorithms import bipartite
from networkx.algorithms import approximation as approx #連結度の検査に使う

G = nx.Graph() #JR東日本大回り乗車可能領域全駅を入れたグラフ
SG = nx.Graph() #乗り換えに使う駅のみに縮約したグラフ
dir = os.getcwd()+"\\Parts" #駅名ソース用のファイルを指定
os.chdir(dir) #移動
S_result = None
S_map = None
with open("Stationedge.txt","r",encoding="utf_8-sig") as St: #駅の接続リストを読み込む
	G = nx.parse_edgelist(St)
with open("SSedge.txt","r",encoding="utf_8-sig") as St: # 簡略グラフ用接続リスト
	SG = nx.parse_edgelist(St)
with open("Allstationlist.txt","r",encoding="utf_8-sig") as St:#駅名をリスト化
	Slist = [s.strip() for s in St.readlines()]
with open("Spechialstation.txt","r",encoding="utf_8-sig") as St:#乗り換えに使う駅をリスト化
	SSlist = [s.strip() for s in St.readlines()]
with open("駅名を数に置換.txt","r",encoding="utf_8-sig") as St:#辞書
	S_edge = json.load(St)
with open("数を駅名に置換.txt","r",encoding="utf_8-sig") as St:#辞書（strで召喚しないと死）
	S_revedge = json.load(St)
with open("routemaplist.txt","r",encoding="utf_8-sig") as St:
	maplist = [s.strip() for s in St.readlines()]

class Mainwindow(tk.Frame):
	def enter(self,event):
		if(S_result is None or S_result.winfo_exists()):
			pass
		Mainwindow.search(self)
		
	def __init__(self, master = None):
		super().__init__(master)
		tki.bind("<Return>",self.enter)
		self.pack()
		self.create_widgets()
		
	def create_widgets(self):	
		self.imagecount = 0
		self.var = tk.StringVar()
		self.var.set("大回り乗車をしよう（提案）")
		self.caution = tk.Label(tki,textvariable=self.var,fg = "red")
		self.caution.pack()
		self.lbl_1 = tk.Label(text='出発駅（変更可）')
		self.lbl_1.pack()
		self.txt_1 = tk.Entry(width=20)
		self.txt_1.insert(0,"八王子")
		self.txt_1.pack()
		self.lbl_3 = tk.Label(text="通過駅1（任意）")
		self.lbl_3.pack()
		self.txt_3 = tk.Entry(width=20)
		self.txt_3.pack()
		self.lbl_4 = tk.Label(text="通過駅2（任意）")
		self.lbl_4.pack()
		self.txt_4 = tk.Entry(width=20)
		self.txt_4.pack()
		self.lbl_2 = tk.Label(text='到着駅（変更可）')
		self.lbl_2.pack()
		self.txt_2 = tk.Entry(width=20)
		self.txt_2.insert(0,"新宿")
		self.txt_2.pack()
		self.sbtn = tk.Button(tki, text='検索', command=self.search)
		self.sbtn.pack(fill = 'none', padx=15, ipadx = 15 ,side = 'left')
		self.mapview = tk.Button(tki,text="路線図",command = self.mapv)
		self.mapview.pack(fill = 'none', padx=15, ipadx = 15 ,side = 'left')
		self.end = tk.Button(tki,text="終了", command = self.end)
		self.end.pack(fill = 'none', padx=15, ipadx = 15 ,side = 'left')
		
		
	def end(self):
		tki.quit()
	
	def downfig(self):
		if self.imagecount ==0:
			self.imagecount = len(maplist)-1
		else: 
			self.imagecount = self.imagecount -1
		self.drawmap()	
	def upfig(self):
		if self.imagecount == len(maplist)-1:
			self.imagecount = 0
		else:
			self.imagecount = self.imagecount +1
		self.drawmap()
	
	def drawmap(self):
		self.mapresult.destroy()
		self.ic = self.imagecount
		img = Image.open(maplist[self.ic])
		img_resize = img.resize((int(img.width/3),int(img.height/3)))
		self.tkimg = ImageTk.PhotoImage(img_resize)
		self.mapresult = tk.Label(S_map, image=self.tkimg, bg="black")
		self.mapresult.pack()
		
		
	def mapv(self):
		global S_map
		if(S_map is None or S_map.winfo_exists()):
			pass
		S_map = tk.Toplevel(master = self.master)
		c_down = tk.Button(S_map,text="<",command = self.downfig)
		c_down.pack(padx=30, ipadx = 30 ,side = 'left')
		end = tk.Button(S_map,text="終了", command = S_map.destroy)
		end.pack(padx=30, ipadx = 30 ,side = 'left')
		c_up = tk.Button(S_map,text=">",command = self.upfig)
		c_up.pack(padx=30, ipadx = 30 ,side = 'left')
		self.ic = self.imagecount
		img = Image.open(maplist[self.ic])
		img_resize = img.resize((int(img.width/3),int(img.height/3)))
		self.tkimg = ImageTk.PhotoImage(img_resize)
		self.mapresult = tk.Label(S_map, image=self.tkimg, bg="black")
		self.mapresult.pack()
		S_map.title("路線図")
		S_map.focus_set()
		
		
	def result(self):
		global S_result
		if(S_result is None or S_result.winfo_exists()):
			pass
		S_result = tk.Toplevel(master = self.master)
		if self.SR[2] == 1:
			self.noresult = tk.Label(S_result,text = "検索されたルートでは大回りできません",fg = "red")
			self.noresult.pack()
		else:
			self.noresult = tk.Label(S_result,text = "以上の順に通過",fg = "red")				
			self.lengresult = tk.Label(S_result,text= "乗車距離："+str(self.SR[1])+"km")
			self.lengresult.pack()
			pathresult =[]
			for i in range(0,len(self.SR[0])):
				if self.SR[0][i] in self.way:
					pathresult.append(tk.Label(S_result,text = self.SR[0][i],fg = "red"))
				else:
					pathresult.append(tk.Label(S_result,text = self.SR[0][i]))
			for i in range(0,len(self.SR[0])-1):
				if self.SR[0][i] in SSlist or self.SR[0][i] in self.way:
					pathresult[i].pack()
			pathresult[i+1].pack()
			self.noresult.pack()
		end = tk.Button(S_result,text="終了", command = S_result.destroy)
		end.pack()
		S_result.title("検索結果")
		S_result.geometry('300x700')
		S_result.focus_set()
		S_result.transient()


	def search(self):
		self.start = str((self.txt_1.get()))
		self.goal = str((self.txt_2.get()))
		self.way = [str((self.txt_3.get())),str((self.txt_4.get()))]
		while "" in self.way: self.way.remove("")
		Echeck = False
		self.able = 0
		self.path = []
		self.leng = 0
		self.SR = []#道のり、距離、移動可能の順で格納
		self.SR.clear()
		if(len(self.start) == 0 or len(self.goal) == 0):
			self.var.set("駅名が入力されていません！")
			Echeck = True
		elif(Searchbrain.existcheck(self.start,Slist)==1 or Searchbrain.existcheck(self.goal,Slist)==1):
			self.var.set("エリア内に駅がありません！")
			Echeck = True
		else:
			if len(self.way)==0:
				self.SR = Searchbrain.searcheasy(self.start,self.goal,G,S_edge,S_revedge,SSlist)
			else:
				for i in range(0,len(self.way)):
					if(Searchbrain.existcheck(self.way[i],Slist)==1):
						self.var.set("エリア内に無い駅があります！")
						Echeck = True
						break
				if Echeck == True:
					pass
				else:
					self.SR = Searchbrain.searchhard(self.start,self.goal,G,S_edge,S_revedge,SSlist,self.way)
		if Echeck == False:
			Mainwindow.result(self)			
			
if __name__ == "__main__":		
	tki = tk.Tk()
	myapp = Mainwindow(master=tki)
	myapp.master.geometry('300x250')
	myapp.master.title('大回りサーチくん')
	myapp.mainloop()