#!/usr/bin/python
# -*- coding:utf-8 -*-

from ParseFile.parseFile import parse_file

KEY_ATTRIB = {
    ("Basic", "Name")
}

CHANGE_LIST = {
    "node_compared": 0,
    "diff_detail": 1
}

# node status
UNIFORM = "Uniform"
CHANGED = "Changed"
ADDED = "Added"
DELETED = "Deleted"
MOVED = "Moved"

class CompareFile:
    """对比文档"""

    # ---<构造函数>-------------------------------------------------
    def __init__(self, file_path_compared, file_path_controlled):
        """
        :param file_path_compared: String, path of file compared
        :param file_path_controled: String, path of file used as a control value
        """
        self._root = self.compare_file(file_path_compared, file_path_controlled)

    # ---<获取根节点>-------
    def get_root(self):
        """
        :return: TreeNode, root of structure tree of file, consisting of TreeNode
        """
        return self._root

    # ---<对比两节点异同>-----------------------------------
    def compare_node(self, node_compared, node_controlled):
        """
        :param node_compared: TreeNode, node from compared file
        :param node_controlled: TreeNode, node from controlled file
        :return: [[],[],[]], list：[[changed attributes],[deleted attributes],[added attributes]]
        """
        if node_controlled.get_attrib() == node_compared.get_attrib():
            return [[], [], []]
        else:
            changed = []
            deleted = []
            added = []
            keys1_controlled = node_controlled.get_attrib().keys()
            keys1_compared = node_compared.get_attrib().keys()
            for key1_controlled in keys1_controlled:
                value1_compared = node_compared.get_attrib().get(key1_controlled)
                # ---<一级属性字典被删除--deleted>----------------------------
                if value1_compared is None:
                    for key2_controlled in node_controlled.get_attrib(key1_controlled).iterkeys():
                        diff_tuple = (key1_controlled, key2_controlled, node_controlled.get_attrib(key1_controlled, key2_controlled), None)
                        deleted.append(diff_tuple)
                # ---<初步判断一级属性字典内容不同--deleted or changed>--------------------------------------
                elif value1_compared != node_controlled.get_attrib(key1_controlled):
                    keys2_controlled = node_controlled.get_attrib(key1_controlled).keys()
                    keys2_compared = value1_compared.keys()
                    for key2_controlled in keys2_controlled:
                        value2_compared = value1_compared.get(key2_controlled)
                        # ---<进一步判断二级属性被删除--deleted>-----------------------------------------------------------------------------------
                        if value2_compared == None:
                            diff_tuple = (key1_controlled, key2_controlled, node_controlled.get_attrib(key1_controlled, key2_controlled), None)
                            deleted.append(diff_tuple)
                        # ---<进一步判断二级属性内容不同--changed>---------------------------------------------------------------------------------
                        elif value2_compared != node_controlled.get_attrib(key1_controlled, key2_controlled):
                            keys2_compared.remove(key2_controlled)
                            diff_tuple = (key1_controlled, key2_controlled, node_controlled.get_attrib(key1_controlled, key2_controlled), value2_compared)
                            changed.append(diff_tuple)
                        else:
                            keys2_compared.remove(key2_controlled)
                    # ---<判断二级属为新增>-------------------------------------------------------------------
                    for key2_compared in keys2_compared:
                        diff_tuple = (key1_controlled, key2_compared, None, value1_compared[key2_compared])
                        added.append(diff_tuple)
                    keys1_compared.remove(key1_controlled)
                else:
                    keys1_compared.remove(key1_controlled)
            # ---<判断一级属性为新增>-------------------------------------------------------------------------------------------
            for key1_compared in keys1_compared:
                for key2_compared in node_compared.get_attrib(key1_compared).iterkeys():
                    diff_tuple = (key1_compared, key2_compared, None, node_compared.get_attrib(key1_compared, key2_compared))
                    added.append(diff_tuple)
        return [changed, deleted, added]

    # ---<设置节点变更信息>----------------------------------
    def set_comp_result(self, node, status, detail):
        """
        :param node: TreeNode, the node you want to set compare result
        :param status: String, one of the following string: uniform, deleted, changed, added, moved
        :param detail: [[],[],[]], list：[[changed attributes],[deleted attributes],[added attributes]]
        :return:void
        """
        if status == UNIFORM:
            node.set_attrib_y("CompResult", "Status", status)
            node.set_attrib_y("CompResult", "Detail", None)
        else:
            node.set_attrib_y("CompResult", "Status", status)
            node.set_attrib_y("CompResult", "Detail", detail)

    # --<将以节点为根的子树全部设置为同一状态>-------------
    def set_comp_res_tree(self, node, status, detail):
        """
        :param node: TreeNode, the node you want to set compare result
        :param status: String, one of the following string: uniform, deleted, changed, added, moved
        :param detail: [[],[],[]], list：[[changed attributes],[deleted attributes],[added attributes]]
        :return: void
        """
        self.set_comp_result(node, status, detail)
        for n in node.get_children():
            self.set_comp_res_tree(n, status, detail)

    # ---<对比两个List中的Nodes的差异>--------------------------------------------------------------------------
    # 标记未变更的节点(Uniform)与已变更的节点(Changed)将疑似新增与删除的节点整理到cNode_compared,cNode_controlled里
    def comp_node_list(self, node_list_compared, node_list_controlled, c_nodes_compared, c_nodes_controlled):
        """
        :param node_list_compared: [TreeNode], a list of node will be compared
        :param node_list_controlled: [TreeNode]. a list of node used as control value
        :param c_nodes_compared: [TreeNode], a list of node from compared file, these nodes may be newly added.
        :param c_nodes_controlled: [TreeNode], a list of node from compared file, these nodes may be deleted.
        :return: void
        """
        temp_list_compared = []
        temp_list_controlled = []
        uniform_list = {} # node_controlled : node_compared
        changed_list = {} # node_controlled : node_compared
        temp_list_compared.extend(node_list_compared)
        temp_list_controlled.extend(node_list_controlled)
        index = 0
        while index < len(temp_list_controlled):
            node_controlled = temp_list_controlled[index]
            if node_controlled.get_attrib('Basic','Name') == 'Image_bg':
                print 'Image_bg'
            for node_compared in temp_list_compared:
                diff_tags = []
                diff = self.compare_node(node_compared, node_controlled)
                # ---<标记无变更节点>------------------------------------
                if len(diff[0]) + len(diff[1]) + len(diff[2]) == 0:
                    self.set_comp_result(node_controlled, UNIFORM, None)
                    self.set_comp_result(node_compared, UNIFORM, None)
                    uniform_list[node_controlled] = node_compared
                    if changed_list.get(node_controlled) != None:
                        changed_list.pop(node_controlled)
                    temp_list_compared.remove(node_compared)
                    temp_list_controlled.remove(node_controlled)
                    index -= 1
                    break
                # ---<标记有变更的节点>-------------------------------------
                for diff_tuple in diff[0]:
                    diff_tags.append((diff_tuple[0], diff_tuple[1]))
                if ("Basic", "ctype") not in diff_tags and ("Basic", "Name") not in diff_tags and ("Basic", "Tag") not in diff_tags:
                    changed_list[node_controlled] = (node_compared, diff)
            index += 1
        # ---<对比无变化节点的子树>------------------------------------------
        for node_controlled in uniform_list.keys():
            self.comp_node_list(uniform_list[node_controlled].get_children(), node_controlled.get_children(), c_nodes_compared, c_nodes_controlled)
        # ---<标记并对比有变更节点的子树>------------------------------------
        for node_controlled in changed_list.keys():
            self.set_comp_result(node_controlled, CHANGED, changed_list[node_controlled][CHANGE_LIST["diff_detail"]])
            self.set_comp_result(changed_list[node_controlled][CHANGE_LIST["node_compared"]], CHANGED, changed_list[node_controlled][CHANGE_LIST["diff_detail"]])
            self.comp_node_list(changed_list[node_controlled][CHANGE_LIST["node_compared"]].get_children(), node_controlled.get_children(), c_nodes_compared, c_nodes_controlled)
            temp_list_controlled.remove(node_controlled)
            try:
                temp_list_compared.remove(changed_list[node_controlled][CHANGE_LIST["node_compared"]])
            except ValueError:
                print 'ValueError in:', node_controlled.get_attrib('Basic', 'Name')
        for node_compared in temp_list_compared:
            c_nodes_compared.append(node_compared)
        for node_controlled in temp_list_controlled:
            c_nodes_controlled.append(node_controlled)
            # ---<将旧树中被删除的节点合并到新树中>----------------
            node_list_compared.append(node_controlled)

    # ---<对比两个文件的差异>-----------------------------------------------
    def compare_file(self, file_path_compared, file_path_controlled):
        """
        :param file_path_compared: String, path of file compared
        :param file_path_controled: String, path of file used as a control value
        :return: void
        """
        root_compared = parse_file(file_path_compared)
        root_controlled = parse_file(file_path_controlled)
        c_nodes_compared = []
        c_nodes_controlled = []
        # ---<标记节点的“一致”和“变更”两种状态>--------------------------------------------------------
        self.comp_node_list([root_compared], [root_controlled], c_nodes_compared, c_nodes_controlled)
        # ---<若根节点只是property group的name变更（即文件名变更），则不计为变更>--------------------------
        root_compared_detail = root_compared.get_attrib("CompResult","Detail")
        if root_compared_detail != None and (root_compared_detail[0]) == 1 and root_compared_detail[0][0] == ("PropertyGroup", "Name"):
            root_compared_detail.set_attrib_y("CompResult", "Status", UNIFORM)
        root_controlled_detail = root_controlled.get_attrib("CompResult", "Detail")
        if root_controlled_detail != None and (root_controlled_detail[0]) == 1 and root_controlled_detail[0][0] == ("PropertyGroup", "Name"):
            root_controlled_detail.set_attrib_y("CompResult", "Status", UNIFORM)
        # ---<标记节点的“移动”这一状态>----------------------------------------------------------------
        index_controlled = 0
        while index_controlled < len(c_nodes_controlled):
            node_controlled = c_nodes_controlled[index_controlled]
            index_compared = 0
            while index_compared < len(c_nodes_compared):
                node_compared = c_nodes_compared[index_compared]
                if node_controlled.get_attrib() == node_compared.get_attrib():
                    self.set_comp_result(node_controlled, MOVED, None)
                    self.set_comp_result(node_compared, MOVED, None)
                    c_nodes_compared.remove(node_compared)
                    c_nodes_controlled.remove(node_controlled)
                    index_controlled -= 1
                    break
                index_compared += 1
            index_controlled += 1
        # ---<标记节点的“新增”>--------------------------------
        for node_compared in c_nodes_compared:
            self.set_comp_res_tree(node_compared, ADDED, None)
        # ---<标记节点的“删除”>--------------------------------
        for node_controlled in c_nodes_controlled:
            self.set_comp_res_tree(node_controlled, DELETED, None)
        root_compared.print_tree("CompResult", "*")
        root_controlled.print_tree("CompResult", "*")
        return root_compared


