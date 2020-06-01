import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import pickle
from networkx.algorithms import bipartite
from networkx.algorithms import approximation as approx #連結度の検査に使う

def connectcalculator(G,start,goal):
	connect = approx.local_node_connectivity(G,start,goal) #通過駅とその次の通過駅が接続されているかを調べる							
	return connect
	

def dijkstraCalcilator(G,start,goal,mode):
	if mode == "path":
		path = nx.dijkstra_path(G,start,goal)
		return path
	elif mode == "length":
		length = nx.dijkstra_path_length(G,start,goal)/1000 
		return length

def existcheck(Station,list):
	if Station in list:
		return 0
	else:
		return 1
		
def searcheasy(Start,Goal,G,S_edge,S_revedge,SSlist):
	start = S_edge[Start]		
	goal = S_edge[Goal]
	Dway = [] #通過駅指定時の道順リスト
	Dleng :float = 0 #通過駅指定時の合計移動距離
	NewG = nx.relabel_nodes(G,S_edge)
	pathway = dijkstraCalcilator(NewG,start,goal,"path") #ダイクストラ法による経路判断
	pathleng = dijkstraCalcilator(NewG,start,goal,"length")
	print(Start+"から"+Goal+"まで最短"+str(pathleng)+"km")
	print("行き方："+Start+"\n↓")
	for i in range(1,len(pathway)-2):
		if S_revedge[str(pathway[i])] in SSlist: #乗換駅に指定されている場合、それも表示する
			print(S_revedge[str(pathway[i])]+"\n↓")
	print(Goal)
	Pathway = []
	for i in range(0,len(pathway)):
		Pathway.append(S_revedge[str(pathway[i])])
	return [Pathway,pathleng,0]

def searchhard(Start,Goal,G,S_edge,S_revedge,SSlist,way):
	CalG = nx.relabel_nodes(G,S_edge) #経路探索用のグラフ
	CalG2 = nx.relabel_nodes(G,S_edge)
	passing = [] #通過する駅のリスト
	passingcount = 0 #出発到着以外に通過しなくてはならない駅の数
	closeFlag = False #大回り不可能なことを示すフラグ
	passFlag = False #ルート上に通過駅が存在することを示すフラグ
	Tempway = []
	lenway = len(way)
	start = S_edge[Start]
	passing.append(start)
	for i in range(0,lenway):
		Way = way[i]
		passing.append(S_edge[Way])
		passingcount = passingcount+1
	goal = S_edge[Goal]
	passing.append(goal)
	Dway = [] #通過駅指定時の道順リスト
	Dleng :float = 0 #通過駅指定時の合計移動距離
	for i in range(0,passingcount+1):
		print("チェック"+str(i))
		c_check = connectcalculator(CalG,passing[i],passing[i+1])
		if i > 0 and c_check == 0:
			closeFlag = True #分断されている場合、分断フラグをon
			Dway.append(passing[i]) #終わりの駅をリストに追加
			break
							
		tempway = dijkstraCalcilator(CalG,passing[i],passing[i+1],"path")#ダイクストラ法による経路判断
		if i < passingcount:
			
			for j in range(i+2,passingcount+2):
				if passing[j] in tempway:
					tempway.remove(passing[i+1])
					tempway.remove(passing[i])
					for k in range(0,len(tempway)):
						Tempway.append(tempway[k])					
					passFlag = True
								
				while passFlag == True:
					appendFlag = False
					CalG2.remove_nodes_from(Dway)
					CalG2.remove_nodes_from(Tempway)
					c_check = connectcalculator(CalG2,passing[i],passing[i+1])
					if c_check == 0:
						closeFlag = True #分断されている場合、分断フラグをon
						Dway.append(passing[i]) #終わりの駅をリストに追加
						break
					else:
						tempway.clear()
						tempway = dijkstraCalcilator(CalG2,passing[i],passing[i+1],"path")								
						for j in range(i+2,passingcount+1):
							if passing[j] in tempway and passing[j] not in Tempway:							
								tempway.remove(passing[i+1])
								tempway.remove(passing[i])
								for k in range(0,len(tempway)):
									Tempway.append(tempway[k])	
								appendFlag = True
								break
						if appendFlag == False:									
							passFlag = False
							break	
		if(i != passingcount and closeFlag == False):
			tempway.remove(passing[i+1])#一番最後の駅はリストから外す
		if(closeFlag == True): break
		Dway = Dway + tempway
		templeng = dijkstraCalcilator(CalG,passing[i],passing[i+1],"length")
		Dleng = Dleng+templeng
		CalG.remove_nodes_from(tempway) #既に通過した駅をグラフから削除する
	if closeFlag == False:
		print(Start+"から"+Goal+"まで最短"+str(Dleng)+"km")
		print("行き方："+Start+"\n↓")
		for i in range(1,len(Dway)-2):
			if S_revedge[str(Dway[i])] in SSlist:
				print(S_revedge[str(Dway[i])]+"\n↓")
		print(Goal)
		Pathway = []
		for i in range(0,len(Dway)):
			Pathway.append(S_revedge[str(Dway[i])])
		return [Pathway,Dleng,0]
	else:
		print(Start+"から"+Goal+"までそのルートでは行けません")
		print("辿ったルート："+Start+"\n↓")
		for i in range(1,len(Dway)-1):
			if S_revedge[str(Dway[i])] in SSlist:
				print(S_revedge[str(Dway[i])]+"\n↓")
		if i !=0:
			print(S_revedge[str(Dway[i+1])])

		return [Dway,Dleng,1]
