#!/usr/bin/python
# -*- coding:utf-8 -*-

from GUI.Main_Window import Ui_MainWindow
from PyQt4 import QtGui, QtCore
from CompFile.compareFile import CompareFile
from UtilitiesSVN.UtilitiesSVN import UtilitiesSVN
import os
import sys


DIFF_LIST = {
	"changed": 0,
	"deleted": 1,
	"added": 2
}

# ---<index of diff_tuples>--------------
ATTRIB_1 = 0
ATTRIB_2 = 1
REFER_VALUE = 2
CUR_VALUE = 3

# ---<index of tree_widget_res_detail>---
DIFF_SHOW = {
	"attrib": 0,
	"refer_value": 1,
	"cur_value": 2
}

# ---<text content of items selected from tree_widget_res_tree>---
ITEM_NAME = 0
ITEM_STATUS = 1

# ---<node status>---
UNIFORM = "Uniform"
CHANGED = "Changed"
ADDED = "Added"
DELETED = "Deleted"
MOVED = "Moved"

# ---<combox content>----------
LOCAL_VERSION = 'Local Version'

# ---<attrib changing phrase>---
CHANGE_FROM = 'Changed from '
CHANGE_TO = ' to '

# ---<table widget index>-------
REVISION_INDEX = 0
AUTHOR_INDEX = 1
DATE_INDEX = 2
MESSAGE_INDEX = 3

# ---<popup window, selected file not in svn>---
POPUP_TITLE_NOT_IN_SVN = 'Hint'
POPUP_CONTENT_NOT_IN_SVN = 'The file choosen need be included in SVN.'

# ---<popup window, search content not found>---
POPUP_TITLE_SEARCH_404 = 'Not found'
POPUP_CONTENT_SEARCH_404 = 'Sorry, no item matched.'

# ---<default item index of control file combo box>---
CONTROL_FILE_DEFAULT_INDEX = 1


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
	'''
	主窗口
	'''

	# ---<初始化类，并将GUI的信号与槽函数捆绑>------
	def __init__(self, parent = None):
		super(MainWindow, self).__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.tableWidget_log_info.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.ui.tree_widget_res_detail.setColumnWidth(0, 70)
		self.ui.tree_widget_res_detail.setColumnWidth(1, 130)

		self._svn_client = UtilitiesSVN()
		self._qt2res_node = {}
		self._log_combo = {}
		self._search_res = []
		self._search_name = ''
		self._cur_search_item = 0
		# ---<绑定信号与槽函数>-----------------------------------
		self.ui.start_compare.clicked.connect(self.start_compare)
		self.ui.button_browser_file_new.clicked.connect(self.browser_file_new)
		self.ui.tree_widget_res_tree.itemClicked.connect(self.show_detail)
		self.ui.tableWidget_log_info.itemDoubleClicked.connect(self.double_click_compare)
		self.ui.button_search_item.clicked.connect(self.search_item)

	# ---<浏览并获得需对比的文件路径>--------
	def browser_file_new(self):
		fileName_choose = QtGui.QFileDialog.getOpenFileName(self,"Select File",os.getcwd(),"CSD Files(*.csd)")
		if fileName_choose == "":
			print "canceled"
			return
		print "seleted file:", fileName_choose
		self.clear_table()
		local_file_path = str(fileName_choose)
		self._svn_client.set_local_file_path(local_file_path)
		# ---<测试所选文件是否已接受subversion>----------------
		if self._svn_client.get_url() is None:
			QtGui.QMessageBox.information(self, QtCore.QString.fromUtf8(POPUP_TITLE_NOT_IN_SVN), QtCore.QString.fromUtf8(POPUP_CONTENT_NOT_IN_SVN))
			return
		self.ui.lineEdit_new_file_path.setText(fileName_choose)
		self._search_name = ''
		self.get_log_info()

	# ---<清空tableWidget_log_info中的内容（除表头）>-----
	def clear_table(self):
		r = self.ui.tableWidget_log_info.rowCount()
		while r != -1:
			self.ui.tableWidget_log_info.removeRow(r)
			r -= 1

	# ---<获得选中文件的日志信息，刷新GUI>--------------------
	def get_log_info(self):
		log = self._svn_client.get_log()
		row = 0
		combo_box_items = QtCore.QStringList([])
		self._log_combo.clear()
		# ---<更新日志信息及下拉框>---------------------------------
		for l in log:
			item = {}
			self.ui.tableWidget_log_info.insertRow(row)
			for k in l.iterkeys():
				if k == 'revision':
					col = 0
					item['revision'] = 'Revision: ' + QtCore.QString(str(l[k].number)) + ' | '
					table_item = QtGui.QTableWidgetItem(QtCore.QString(str(l[k].number)))
					self._log_combo[l[k].number] = row + 1
				elif k == 'author':
					col = 1
					item['author'] = 'Author: ' + QtCore.QString(l[k]) + ' | '
					table_item = QtGui.QTableWidgetItem(QtCore.QString(l[k]))
				elif k == 'date':
					col = 2
					item['date'] = 'Date: ' + QtCore.QString(l[k]) + ' | '
					table_item = QtGui.QTableWidgetItem(QtCore.QString(l[k]))
				elif k == 'message':
					col = 3
					table_item = QtGui.QTableWidgetItem(QtCore.QString.fromUtf8(l[k]))
				else:
					continue
				print QtCore.QString.toUtf8(table_item.text())
				self.ui.tableWidget_log_info.setItem(row, col, table_item)
			combo_box_items.append(item['revision'] + item['author'] + item['date'])
			row += 1
		file_path = str(self.ui.lineEdit_new_file_path.text())
		file_name = file_path[file_path.rfind('/')+1:]
		print 'Loading log', file_name, 'completed.'
		self.ui.label_svn_info.setText('Log Info:(' + file_name + ')')
		self.add_comboBox_items(combo_box_items)

	# ---<添加可选文本到下拉框>----------------------
	def add_comboBox_items(self, combo_box_items):
		"""
		:param combo_box_items: list, items need insert into combo_box
		:return: void
		"""
		self.ui.comboBox_new_file.clear()
		self.ui.comboBox_new_file.addItem(LOCAL_VERSION)
		self.ui.comboBox_new_file.addItems(combo_box_items)
		self.ui.comboBox_old_file.clear()
		self.ui.comboBox_old_file.addItem(LOCAL_VERSION)
		self.ui.comboBox_old_file.addItems(combo_box_items)
		self.ui.comboBox_old_file.setCurrentIndex(CONTROL_FILE_DEFAULT_INDEX)

	# ---<通过双击log的list开始对比文件>----------------
	def double_click_compare(self):
		cur_row = self.ui.tableWidget_log_info.currentItem().row()
		cur_index = self._log_combo[int(self.ui.tableWidget_log_info.item(cur_row, REVISION_INDEX).text())]
		self.ui.comboBox_old_file.setCurrentIndex(cur_index)
		self.start_compare()

	# ---<获取下拉框当前选中项的Revision号码>----------
	def get_revision(self, combo_box):
		"""
		:param combo_box: String, current content of combo_box
		:return: int, revision number
		"""
		if combo_box == LOCAL_VERSION:
			return -1
		else:
			cur_item = str(QtCore.QString.toUtf8(combo_box))
			cur_item = cur_item[10:]
			pos = cur_item.find(' ')
			rev_num = int(cur_item[0:pos])
			return rev_num

	# ---<将所需文件暂存到本地>-----------------------
	def load_file(self, combo_box, type):
		"""
		:param combo_box: String, current content of combo_box
		:param type: String, 'new' or 'old'
		:return: String, path of file, combo_box points to
		"""
		import os
		new_file_path = str(self.ui.lineEdit_new_file_path.text())
		# ---<若是本地文件，则直接返回本地文件的地址>---------------
		if combo_box == LOCAL_VERSION:
			return new_file_path
		# ---<若不是本地文件，则将文件内容暂时转存到本地并返回地址>--
		else:
			pos = new_file_path.rfind('/')
			file_name = new_file_path[pos + 1:]
			rev_num = self.get_revision(combo_box)
			print 'Loading file:', file_name, 'Revision:', rev_num
			file_content = str(self._svn_client.load_file_content(rev_num))
			cur_path = os.getcwd() + '\\' + 'temp'
			if not os.path.exists(cur_path):
				os.makedirs(cur_path)
			print 'Create compare version file temporarily at:', cur_path
			old_file_path = cur_path + '\\' + 'temp_' + type + '_' + file_name
			print 'Old file path:', old_file_path
			old_file = open(old_file_path, "w")
			old_file.write(file_content)
			old_file.close()
			print 'Loading file:', old_file_path, 'completed'
			return old_file_path

	# ---<如文件是临时文件，则在对比完成后将其删除>---------
	def remove_temp_file(self, combo_box, file_path):
		"""
		:param combo_box:  String, current content of combo_box
		:param file_path: String, path of file need judge deleting it or not
		:return: void
		"""
		if combo_box == LOCAL_VERSION:
			return
		os.remove(file_path)

	# ---<将treeWidget中有变更/删除/新增/移动节点的分支展开>---
	def expand_changed_node(self, cur_node):
		"""
		:param cur_node: QTreeWidgetItem, root of current subtree
		:return: void
		"""
		# ---<先将节点展开>-------------------
		is_changed = False
		cur_node.setExpanded(True)
		child_count = cur_node.childCount()
		idx = 0
		while idx < child_count:
			if self.expand_changed_node(cur_node.child(idx)):
				is_changed = True
			idx += 1
		# ---<抵达叶节点后，开始判断是否需要保留展开状态>-------
		if cur_node.text(1) != 'Uniform' or is_changed:
			return True
		else:
			cur_node.setExpanded(False)
			return False

	# ---<开始对比按钮: 对比两个选中的文件，并将结果在tree_widget_res_tree中展示>---------
	def start_compare(self):
		self.ui.tree_widget_res_tree.clear()
		new_file_path = self.load_file(self.ui.comboBox_new_file.currentText(), 'new')
		old_file_path = self.load_file(self.ui.comboBox_old_file.currentText(), 'old')
		# ---<开始对比>-----------------------------------------------------------------
		res = CompareFile(new_file_path, old_file_path)
		res_root = res.get_root()
		qt_root = QtGui.QTreeWidgetItem(self.ui.tree_widget_res_tree)
		qt_root.setText(0, res_root.get_attrib("PropertyGroup", "Name"))
		qt_root.setText(1, res_root.get_attrib("CompResult", "Status"))
		qt_root.text(1)
		# ---<添加(qt_root: res_root)到_qt2res_node字典,为访问节点属性备用>--------------
		self._qt2res_node[qt_root] = res_root
		self.set_color(qt_root)
		self.add_list(res_root.get_children(), qt_root)
		self.ui.tree_widget_res_tree.addTopLevelItem(qt_root)
		# ---<重设“对比结果”标签为“对比结果：对比文件名 vs 参照文件名”>----------------
		rev_temp = self.get_revision(self.ui.comboBox_new_file.currentText())
		if rev_temp < 0:
			label_comp = LOCAL_VERSION
		else:
			label_comp = 'Revision ' + str(rev_temp)
		rev_temp = self.get_revision(self.ui.comboBox_old_file.currentText())
		if rev_temp < 0:
			label_refer = LOCAL_VERSION
		else:
			label_refer = 'Revision ' + str(rev_temp)
		self.ui.label_compare_res.setText('Compare Result: ' + 'Differences between ' + label_comp + ' and ' + label_refer)
		# ---<展开有变更的节点>---------------------------------------------------------
		self.expand_changed_node(qt_root)
		# ---<删除临时文件>-------------------------------------------------------------
		self.remove_temp_file(self.ui.comboBox_new_file.currentText(), new_file_path)
		self.remove_temp_file(self.ui.comboBox_old_file.currentText(), old_file_path)
		cur_path = os.getcwd() + '\\' + 'temp'
		if os.path.exists(cur_path):
			os.removedirs(cur_path)

	# ---<依据tree_widget_res_tree中节点变更状态为其设置背景色>----------------
	def set_color(self, tree_node):
		"""
		:param tree_node: QTreeWidgetItem, the node need set background color
		:return: void
		"""
		# ---<有更改的节点>---------------------------------------------------
		if tree_node.text(ITEM_STATUS) == CHANGED:      # 黄色
			tree_node.setBackground(ITEM_NAME, QtGui.QColor(250, 240, 150))
			tree_node.setBackground(ITEM_STATUS, QtGui.QColor(250, 240, 150))
		# ---<新增的节点>-----------------------------------------------------
		elif tree_node.text(ITEM_STATUS) == ADDED:      # 绿色
			tree_node.setBackground(ITEM_NAME, QtGui.QColor(197, 248, 200))
			tree_node.setBackground(ITEM_STATUS, QtGui.QColor(197, 248, 200))
		# ---<被删除的节点>---------------------------------------------------
		elif tree_node.text(ITEM_STATUS) == DELETED:    # 红色
			tree_node.setBackground(ITEM_NAME, QtGui.QColor(249, 152, 159))
			tree_node.setBackground(ITEM_STATUS, QtGui.QColor(249, 152, 159))
		# ---<被移动的节点>---------------------------------------------------
		elif tree_node.text(ITEM_STATUS) == MOVED:      # 灰色
			tree_node.setBackground(ITEM_NAME, QtGui.QColor(249, 243, 236))
			tree_node.setBackground(ITEM_STATUS, QtGui.QColor(249, 243, 236))

	# ---<将一个list中的所有节点（TreeNode）添加到tree_widget_res_tree中>--------
	def add_list(self, node_list, tree_root):
		"""
		:param node_list: [TreeNode], list of nodes need insert into tree_widge_res_tree as child of tree_root
		:param tree_root: QTreeWidgetItem, act as parent of nodes in node_list
		:return: void
		"""
		for node in node_list:
			qt_node = QtGui.QTreeWidgetItem(tree_root)
			qt_node.setText(0, node.get_attrib("Basic","Name"))
			qt_node.setText(1, node.get_attrib("CompResult", "Status"))
			# ---<添加 (qt_root: node) 到_qt2res_node字典>----------------
			self._qt2res_node[qt_node] = node
			self.set_color(qt_node)
			self.add_list(node.get_children(), qt_node)

	# ---<展示资源文件>---------------
	def show_resource(self, item):
		"""
		:param item: QTreeWidgetItem, the widget selected to display its resource included
		:return: void
		"""
		# ---<获取csd文件路径>--------------------------------------
		file_path = str(self.ui.lineEdit_new_file_path.text())
		pos = file_path.rfind("/")
		file_path = file_path[0:pos]
		# ---<获取资源文件绝对路径>----------------------------------
		origin = self._qt2res_node[item]
		try:
			ctype = origin.get_attrib().get("Basic").get("ctype")
			if ctype != None:
				if ctype == "ImageViewObjectData":
					resource_path = file_path + "/" + origin.get_attrib("FileData", "Path")
				elif ctype == "ButtonObjectData":
					resource_path = file_path + "/" + origin.get_attrib("NormalFileData", "Path")
				else:
					self.ui.label_resource.setText("No Resource Included.")
					return
				print 'Loading resource from:', resource_path
				test = open(resource_path)
				source = QtGui.QPixmap(resource_path)
				# ---<若资源文件尺寸大于展示框，则将其按原长款比缩放>------------------------------------------------------
				if source.height() > self.ui.label_resource.height() or source.width() > self.ui.label_resource.width():
					source = source.scaled(self.ui.label_resource.width(), self.ui.label_resource.height(),
					                       QtCore.Qt.KeepAspectRatio)
				self.ui.label_resource.setPixmap(source)
		except KeyError:
			print "Key value error: ctype"
		except Exception:
			print "Value error: resource path"
			self.ui.label_resource.setText("Value error: resource path. Make sure the compared files are in right position.")

	# ---<展示“一致”，“新增”，“删除”节点变化的具体信息>--------
	def show_detail_uad(self, item):
		"""
		:param item: QTreeWidgetItem, selected tree widget item
		:return: void
		"""
		root = QtGui.QTreeWidgetItem(self.ui.tree_widget_res_detail)
		root.setText(DIFF_SHOW["attrib"], "None")
		root.setText(DIFF_SHOW["refer_value"], "None")
		self.ui.tree_widget_res_detail.addTopLevelItem(root)
		self.show_resource(item)

	# ---<生成引用序列>--------------------
	def generate_reference(self, item):
		"""
		:param item: QTreeWidgetItem, selected tree widget item
		:return: void
		"""
		node = self._qt2res_node[item]
		refer = node.get_attrib('Basic', 'Name')
		node = node.get_parent()
		parent = node.get_parent()
		while parent.get_parent() != None:
			refer = node.get_attrib('Basic', 'Name') + '.' + refer
			node = parent
			parent = node.get_parent()
		self.ui.lineEdit_refer_text.setText(QtCore.QString(refer))

	# ---<展示“更改”节点变化的具体信息>--------------------------------
	# item: 被选择的节点
	# category: 具体信息的三种分类: 被变更的属性, 新增的属性, 被删除的属性
	# category_chinese: 三种信息分类对应的中文
	def show_detail_c(self, item, category, category_chinese):
		"""
		:param item: QTreeWidgetItem, selected tree widget item
		:param category: String, category of attribute, including 'changed', 'added', 'deleted'
		:param category_chinese: String, chinese version of category
		:return: void
		"""
		diff = self._qt2res_node[item].get_attrib("CompResult", "Detail") # diff = [[changed attributes], [added attributes], [deleted attributes]]
		diff_dic = {}
		root_display = QtGui.QTreeWidgetItem()
		root_display.setText(DIFF_SHOW["attrib"], category_chinese)
		# ---<将变更的信息按照属性一级分类聚合到一起>------------------
		for tpl in diff[DIFF_LIST[category]]:
			value = diff_dic.get(tpl[ATTRIB_1])
			if value == None:
				diff_dic[tpl[ATTRIB_1]] = [tpl]
			else:
				value.append(tpl)
		# ---<按照一级分类显示被变更的属性>----------------------------
		for key in diff_dic.iterkeys():
			node_display = QtGui.QTreeWidgetItem(root_display)
			node_display.setText(DIFF_SHOW["attrib"], key)
			for attrib in diff_dic[key]:
				node_attrib = QtGui.QTreeWidgetItem(node_display)
				node_attrib.setText(DIFF_SHOW["attrib"], attrib[ATTRIB_2])
				refer_value = attrib[REFER_VALUE]
				cur_value = attrib[CUR_VALUE]
				if refer_value is None:
					refer_value = 'None'
				if cur_value is None:
					cur_value = 'None'
				node_attrib.setText(DIFF_SHOW["refer_value"], CHANGE_FROM + QtCore.QString(str(refer_value)))
				node_attrib.setText(DIFF_SHOW["cur_value"], CHANGE_TO + QtCore.QString(str(cur_value)))
			node_display.setExpanded(True)
		if root_display.childCount() != 0:
			self.ui.tree_widget_res_detail.addTopLevelItem(root_display)
		# ---<展开节点>--------------------------------------------------
		root_display.setExpanded(True)
		i = 0
		while i < root_display.childCount():
			root_display.child(i).setExpanded(True)
			i += 1

	# ---<展示被选中节点的变更信息>---
	def show_detail(self, item):
		"""
		:param item: QTreeWidgetItem, selected tree widget item
		:return: void
		"""
		self.ui.tree_widget_res_detail.clear()
		self.generate_reference(item)

		# ---<对于一致，新增，删除的节点，直接显示无属性变化>--------------------
		node_name = item.text(ITEM_STATUS)
		if node_name == UNIFORM or node_name == ADDED or node_name == DELETED:
			self.show_detail_uad(item)
			return

		# ---<对于变更的节点，展示其被改变，新增，被删除的属性>---
		self.show_detail_c(item, "changed", CHANGED)
		self.show_detail_c(item, "added", ADDED)
		self.show_detail_c(item, "deleted", DELETED)

		self.show_resource(item)

	# ---<搜索并高亮控件>----------------------------------
	def search_item(self):
		# ---<如果搜索内容为空，则直接结束函数>-------------
		if self.ui.lineEdit_search_item.text() == '':
			return

		# ---<若搜索内容与上次有变更，则重新搜索整棵树,更新search_res列表>---
		if self._search_name != self.ui.lineEdit_search_item.text():
			self._search_name = self.ui.lineEdit_search_item.text()
			root = self.ui.tree_widget_res_tree.invisibleRootItem()
			self._cur_search_item = 0
			self._search_res = []
			self.search_item_subtree(root, self._search_name)

		# ---<若无匹配结果，则弹窗提示，并结束函数>-----------------------------------------------
		len_search_res = len(self._search_res)
		if len_search_res == 0:
			QtGui.QMessageBox.information(self, QtCore.QString.fromUtf8(POPUP_TITLE_SEARCH_404),
			                              QtCore.QString.fromUtf8(POPUP_CONTENT_SEARCH_404))
			return

		# ---<循环高亮列表里的下一个匹配项>-------------------------------------------------------
		self.ui.tree_widget_res_tree.setCurrentItem(self._search_res[self._cur_search_item])
		self.ui.tree_widget_res_tree.setFocus()
		self._cur_search_item += 1
		self._cur_search_item = self._cur_search_item % len_search_res

	# ---<搜索以root为根的子树下与name相同名称的节点>---
	def search_item_subtree(self, root, name):
		"""
		:param root: QTreeWidgetItem, root of current subtree searching
		:param name: String, name of widget is searching
		:return: void
		"""
		if root.text(0) == name:
			self._search_res.append(root)
		child_count = root.childCount()
		if child_count == 0:
			return
		i = 0
		while i < child_count:
			item = root.child(i)
			self.search_item_subtree(item, name)
			i += 1
		return


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	myapp = MainWindow()
	myapp.show()
	sys.exit(app.exec_())
