import gv


class Graph():
	def __init__(self, minv, maxv):
		self.gr = gv.graph('py')
		self.set_style()
		self.set_value_range(minv, maxv)
		return
	
	def set_value_range(self, minv, maxv):
		if minv == maxv: maxv += 1
		self.minv = minv
		self.maxv = maxv
		self.minlen = 1
		self.maxlen = 2.4
		self.dx = pow(((self.maxlen - self.minlen) / (self.maxv - self.minv)), 2)
		return

	def add_node(self, node_id, label):
		n = gv.node(self.gr, node_id)
		gv.setv(n, 'label', label)
		return

	def add_edge(self, node1, node2, value):
		length = self.minlen + pow((self.maxv - value), 2) * self.dx
		e = gv.edge(self.gr, node1, node2)
		gv.setv(e, 'len', str(length))
		gv.setv(e, 'label', str(value))
		return

	def render(self, form='png', filename=None, label=None):
		gv.layout(self.gr, 'neato')
		if label: gv.setv(self.gr, 'label', label)
		gv.render(self.gr, form)
		return

	def set_style(self):
		node_style = [('style', 'filled'), ('fillcolor', 'royalblue'), ('penwidth', '0'), 
				('shape', 'box'), ('width', '.6'), ('height', '.05'), ('fontname', 'Ubuntu'),
				('fontsize', '10'), ('fontcolor', 'white')]
		n = gv.protonode(self.gr)
		for (a, v) in node_style:
			gv.setv(n, a, v)
		
		edge_style = [('fontname', 'Ubuntu-bold'), ('fontsize', '8'), ('penwidth', '1'), ('color', 'gray73')]
		e = gv.protoedge(self.gr)
		for (a, v) in edge_style:
			gv.setv(e, a, v)

		graph_style = [('size', '1000,600'), ('ratio', '0.6'), ('epsilon', '0.001'), ('maxiter', '10000')]
		for (a, v) in graph_style:
			gv.setv(self.gr, a, v)

		return

if __name__ == '__main__':
	g = Graph(1, 50)

	g.add_node('A', 'Amol')
	g.add_node('B', 'Bill')
	g.add_edge('A', 'B', 1)
	g.add_edge('A', 'C', 20)
	g.add_edge('C', 'D', 7)
	g.add_edge('A', 'D', 50)
	g.render()

	quit()

