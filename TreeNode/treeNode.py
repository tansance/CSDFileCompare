#!/usr/bin/python
# -*- coding:utf-8 -*-

class TreeNode:
    """树节点类"""

    '''
    self._attrib 变量的结构（例子）
              一级属性字典（x）
    ——————————————————
    {
                  二级属性字典（y）
                ——————————
    "Basic"    : { ............. }
    "Margin"   : { ............. }
    "FileData" : { ............. }
                                    }
    '''

    # ---<initialize>-------------------------------------------------
    def __init__(self, basic_attrib = None, parent = None, deep = 0):
        """
        :param basic_attrib: dictionary, the attributes come after AbstractDataNode
        :param parent: TreeNode, the parent of current node
        :param deep: int, the deep of current node
        """
        self._attrib = {}
        self.set_attrib_x("Basic", basic_attrib)
        self._children = []
        self._parent = parent
        self._deep = deep

    # ---<destructor>---------------
    def __del__(self):
        for child in self._children:
			del child

    # ---<添加单一子节点>-----------------
    def add_child(self, child_node):
        """
        :param child_node: TreeNode, child of current node
        :return: void
        """
        self._children.append(child_node)

    # ---<添加多个子节点>-------------------
    def add_children(self, children_list):
        """
        :param children_list: [TreeNode], a list of children of current node
        :return: void
        """
        for child in children_list:
            self.add_child(child)

    # ---<设置节点等级>-------
    def set_deep(self, deep):
        """
        :param deep: int, deep of current node in the tree
        :return: void
        """
        self._deep = deep

    # ---<设置节点父节点>----------
    def set_parent(self, parent):
        """
        :param parent: TreeNode, parent of current node
        :return: void
        """
        self._parent = parent

    # ---<设置一级属性字典>------------------
    def set_attrib_x(self, attrib_x, value):
        """
        :param attrib_x: String, key for value
        :param value: dictionary, attribute of current node
        :return: void
        """
        self._attrib[attrib_x] = value

    # ---<设置attrib_x下的二级属性>-------------------
    def set_attrib_y(self,attrib_x, attrib_y, value):
        """
        :param attrib_x: String, key level 1
        :param attrib_y: String, sub-key level 2
        :param value: String, attribute of current node
        :return: void
        """
        if attrib_x in self._attrib:
            self._attrib[attrib_x][attrib_y] = value
        else:
            self._attrib[attrib_x] = {attrib_y: value}

    # ---<返回节点属性>--------------------------------------,{String|String}|String, attrib_x:String, attrib_y:String
    def get_attrib(self, attrib_x = None, attrib_y = None):
        """
        :param attrib_x: String, key for dictionary attrib
        :param attrib_y: String, sub-key of sub-dictionary attrib
        :return: {{}} if attrib_x is None, {} if only attrib_y is None, String if both argument is not None
        """
        if attrib_x == None:
            return self._attrib
        elif attrib_y == None :
            return self._attrib[attrib_x]
        else:
            return self._attrib[attrib_x][attrib_y]

    # ---<返回父节点>---------
    def get_parent(self):
        """
        :return: TreeNode, parent of current node
        """
        return self._parent

    # ---<返回节点的深度>---
    def get_deep(self):
        """
        :return: int, deep of current node
        """
        return self._deep

    # ---<返回子节点列表>----
    def get_children(self):
        """
        :return: [TreeNode], return a list of child of current node
        """
        return self._children

    # ---<前序深度优先打印树>---------------------------------------------
    def print_tree(self,attrib_x = "Basic", attrib_y = "Name", deep = 0):
        """
        :param attrib_x: String, key for dictionary attrib
        :param attrib_y: String, sub-key of sub-dictionary attrib
        :param deep: int, the deep of root of current subtree
        :return: void
        """
        try:
            tabs = ""
            it = iter(range(deep))
            for i in it:
                tabs += "\t"
            # 打印全部属性
            if attrib_x == "*":
                print tabs, self._attrib["Basic"]["Name"], self._attrib
            # 打印一级属性下的全部属性
            elif attrib_y == "*":
                print tabs, self._attrib["Basic"]["Name"], self._attrib[attrib_x]
            # 打印对应的二级属性
            else:
                print tabs, self._attrib["Basic"]["Name"], self._attrib[attrib_x][attrib_y]
            # 打印子节点
            if len(self._children) != 0:
                deep += 1
            it = iter(self._children)
            for child in it:
                child.print_tree(attrib_x, attrib_y, deep)
        except Exception:
            print "Print Tree Error: 0"

