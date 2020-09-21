"""Main module."""

from scipy.stats import kurtosis
import numpy as np
import pandas as pd

def get_kurtosis_feature_split(data):
	"""
	Get attribute split according to Kurtosis Split

	:param data: the dataset of the node
	:returns: 
		- feature_index: the attribute index to split
		- feature_split: the attribute value to split
	"""

	kurtosis_values = kurtosis(data.astype(np.float64), fisher=False)
	kurtosis_values_log = np.log(kurtosis_values+1)
	kurtosis_values_sum_log = kurtosis_values_log.sum()

	while True:
		random_value_feature = np.random.uniform(0, kurtosis_values_sum_log)
		feature_index = np.digitize(random_value_feature, np.cumsum(kurtosis_values_log))

		min_ = np.min(data[feature_index])
		max_ = np.max(data[feature_index])
		feature_split = np.random.uniform(min_, max_)
		if min_ < feature_split < max_:
			break
			
	return feature_index, feature_split

def get_random_feature_split(data):
	"""
	Get attribute split according to Random Split

	:param data: the dataset of the node
	:returns: 
		- feature_index: the attribute index to split
		- feature_split: the attribute value to split
	"""
	choices = list(range(data.shape[1]))
	np.random.shuffle(choices)
	while len(choices) > 0:
		attribute = choices.pop()
		min_attribute = np.min(data[attribute])
		max_attribute = np.max(data[attribute])

		if min_attribute != max_attribute:
			while True:
				split_value = np.random.uniform(min_attribute, max_attribute)
				if min_attribute < split_value < max_attribute:
					break
			break

	return attribute, split_value

class Node(object):
	"""
	Node object
	"""
	def __init__(self):
		super(Node, self).__init__()
		
		self.left = None
		self.right = None

		self.split_value = None
		self.split_feature = None
		self.attribute = None

		self.data = None
		self.depth = None
		self.size = None
		self.index = None
		self.type = 0
		self.parent = None

class Root(Node):
	"""
	Node (Root) object
	"""
	def __init__(self):
		super().__init__()
		self.depth = 0
		self.index = 0		

class RandomHistogramTree(object):
	"""
	Random Histogram Tree object

	:param int max_height: max height of the tree
	:param bool split_criterion: split criterion to use: 'kurtosis' or 'random'
	"""
	def __init__(self, data = None, max_height = None, split_criterion='kurtosis'):
		super(RandomHistogramTree, self).__init__()
		self.N = 0
		self.leaves = []
		self.max_height = max_height
		self.split_criterion = split_criterion

		if data is not None:
			self.build_tree(data)
		else:
			sys.exit('Error data')

	def generate_node(self, depth=None, parent=None):
		"""
		Generates a new new

		:param int depth: depth of the node
		:param Node parent: parent node
		"""
		self.N += 1

		node = Node()
		node.depth = depth
		node.index = self.N
		node.parent = parent

		return node

	def set_leaf(self, node, data):
		"""
		Transforms generic node into leaf

		:param node: generic node to transform into leaf
		:param data: node data used to define node size and data indexes corresponding to node 
		"""
		node.type = 1
		node.size = data.shape[0]
		node.data_index = data.index
		self.leaves.append(node)

	def build(self, node, data):
		"""
		Function which recursively builds the tree

		:param node: current node
		:param data: data corresponding to current node
		"""
		# node.data_index = data.index

		if data.shape[0] == 0:
			self.error_node = node
		if data.shape[0] <= 1 :
			self.set_leaf(node, data)
			return
		if data.duplicated().sum() == data.shape[0] - 1:
			self.set_leaf(node, data)
			return
		if node.depth >= self.max_height:
			self.set_leaf(node, data)
			return

		if self.split_criterion == 'kurtosis':
			attribute, value = get_kurtosis_feature_split(data)
		elif self.split_criterion == 'random':
			attribute, value = get_random_feature_split(data)
		else:
			sys.exit('Error: Unknown split criterion')

		node.left =  self.generate_node(depth = node.depth+1, parent = node)
		node.right = self.generate_node(depth = node.depth+1, parent = node)

		node.attribute = attribute
		node.value = value

		self.build(node.left, data[data[attribute] < value])
		self.build(node.right, data[data[attribute] >= value])

	def build_tree(self, data):
		"""
		Build tree function: generates the root node and successively builds the tree recursively

		:param data: the dataset
		"""		
		self.tree_ = Root()
		self.build(self.tree_, data)

	# def get_leaves(self, node, leaves):

	# 	if node.type == 1:
	# 		leaves.append(node)
	# 		return

	# 	self.get_leaves(node.left, leaves)
	# 	self.get_leaves(node.right, leaves)

class RHF(object):
	"""
	Random Histogram Forest. Builds and ensemble of Random Histogram Trees

	:param int num_trees: number of trees
	:param int max_height: maximum height of each tree
	:param str split_criterion: split criterion to use - 'kurtosis' or 'random'
	:param bool check_duplicates: check duplicates in each leaf
	"""
	def __init__(self, num_trees = 100, max_height = 5, split_criterion='kurtosis', check_duplicates=True):
		super(RHF, self).__init__()
		self.num_trees  = num_trees
		self.max_height = max_height
		self.has_duplicates = False
		self.check_duplicates = check_duplicates
		self.split_criterion = split_criterion

	def fit(self, data):
		"""
		Fit function: builds the ensemble and returns the scores

		:param data: the dataset to fit
		:return scores: anomaly scores
		"""

		data = pd.DataFrame(data)

		self.check_hash(data)

		self.forest = []
		partial_scores = []
		scores = np.zeros(data.shape[0])

		for tree_id in range(self.num_trees):

			randomHistogramTree = RandomHistogramTree(
				data=data,
				max_height=self.max_height, 
				split_criterion=self.split_criterion
			)
			# self.forest.append(randomHistogramTree)

			if self.has_duplicates:
				for leaf in randomHistogramTree.leaves:
					samples_indexes = leaf.data_index
					p = self.data_hash[samples_indexes].nunique()/self.uniques_
					scores[samples_indexes] += np.log(1/(p))

			else:
				for leaf in randomHistogramTree.leaves:
					samples_indexes = leaf.data_index
					p = leaf.size/self.uniques_
					scores[samples_indexes] += np.log(1/(p))
					
		self.scores = scores
		return self.scores

	def check_hash(self, data):
		"""
		Checks if there are duplicates in the dataset

		:param data: dataset
		"""

		if self.check_duplicates:
			if data.duplicated().sum() > 0:
				self.has_duplicates = True
				self.get_hash(data)
				self.uniques_ = self.data_hash.nunique()
			else:
				self.uniques_ = data.shape[0]
		else:
			self.uniques_ = data.shape[0]

	def get_hash(self, data):
		"""
		Builds hash of data for duplicates identification

		:param data: dataset
		"""
		self.data_hash = data.apply(lambda row: hash('-'.join([str(x) for x in row])), axis=1)		