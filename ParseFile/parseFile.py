#!/usr/bin/python
# -*- coding:utf-8 -*-

from TreeNode.treeNode import TreeNode
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

START_DEEP = 1
SETTING_NODE_DEEP = 1

# ---<解析csd文件并返回根节点>--------------------
def parse_file(file_path):
    """
    :param file_path: string, the path of file parsed
    :return: TreeNode, root of structure tree of file, consisting of TreeNode
    """
    try:
        tree = ET.ElementTree(file = file_path)
    except BaseException:
        print "parse_file Error: 0"
    else:
        parsed_root = TreeNode(basic_attrib={"Name": "root"})
        for node in tree.iter():
            if node.tag == "ObjectData":
                # ---<开始分析提取控件节点，整合控件设置>----------------------------
                object_data = TreeNode(node.attrib, parsed_root, START_DEEP)
                object_data.add_children(merge_nodes(node, object_data, START_DEEP))
                object_data.set_parent(parsed_root)
                parsed_root.add_child(object_data)
                break
            else:
                # ---<过滤文件设置内容，文件设置内同全部合并到root节点中>-------
                if parsed_root.get_attrib().get(node.tag) is None:
                    parsed_root.set_attrib_x(node.tag, node.attrib)
                else:
                    parsed_root.get_attrib(node.tag).update(node.attrib)
        return parsed_root

# ---<将root子节点中的属性节点合并到merged_node中>-------------------------
# 将root子节点中的控件节点整理成list返回 [TreeNode]
# root : Element, merged_node : TreeNode, deep : int
def merge_nodes(root, merged_node, deep):
    """
    :param root: Element, root of structure tree constructed by xml.etree.cElementTree
    :param merged_node: TreeNode, root of current subtree
    :param deep: int, deep of children of merged_node
    :return: [TreeNode], a list of child of merged_node
    """
    children = []
    for node in root:
        if node.tag == "AbstractNodeData":
            # 获得控件节点及其基本属性
            new_child = TreeNode(node.attrib, merged_node, deep)
            new_child.add_children(merge_nodes(node, new_child, deep))
            children.append(new_child)
        elif node.tag == "Children":
            # 整合节点的子节点
            children = merge_nodes(node, merged_node, deep+1)
        else:
            # 获取控件附加属性
            merged_node.set_attrib_x(node.tag, node.attrib)
    return children
