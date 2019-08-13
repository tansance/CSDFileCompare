#!/usr/bin/python
# -*- coding:utf-8 -*-

import pysvn

class UtilitiesSVN:
	"""SVN工具"""
	"""pysvn 官方文档: http://pysvn.tigris.org/docs/pysvn_prog_ref.html#pysvn_client_methods"""

	# ---<initialize>-------------------------------------------------------
	def __init__(self, local_file_path = None, svnurl = None):
		"""
		:param local_file_path: String, the path of file want to connect to svn
		:param svnurl: String, SVN url
		"""
		self._svnurl = svnurl
		self._local_file_path = local_file_path
		self.client = pysvn.Client()

	# ---<设置本地文件路径，并依此配置相应svnurl>-------
	def set_local_file_path(self, local_file_path):
		"""
		:param local_file_path: String, the path of file want to connect to svn
		:return: void
		"""
		self._local_file_path = local_file_path
		self._svnurl = self.get_url()

	# ---<对【文件夹】的路径进行操作>------------------------------
	# 检出svnurl对应文件夹中的文件到本地指定路径
	def check_out_file(self, svnurl_dir_path, local_repo_path):
		"""
		:param svnurl_dir_path: String, SVN url path points to the directory you want to check out
		:param local_repo_path: String, path you want to put directory checked out
		:return: void
		"""
		"""check_out directory in svn to local repository; arguments: svnurl_dir_path, local_repo_dir_path"""
		import os
		if svnurl_dir_path is None or local_repo_path is None:
			return
		if not self.client.is_url(svnurl_dir_path):
			print 'SVN url provided is not a valid url.'
			return
		if not os.path.isdir(local_repo_path):
			print 'local repository should refers to a directory, not a file.'
			return
		self.client.checkout(svnurl_dir_path, local_repo_path)

	# ---<获取仓库目录列表(对文件夹）>------------------------------------------------------
	def get_file_list(self, svnurl_dir_path, revision_num):
		"""
		:param svnurl_dir_path:  String, SVN url path points to the directory you want to check
		:param revision_num:  revision num of directory
		:return: list, list of files in SVN url path
		"""
		"""get file list in given dir path; arguments: svnurl_dir_path, revision_num"""
		if svnurl_dir_path is None:
			print 'SVN url unset.'
			return
		revision = pysvn.Revision(pysvn.opt_revision_kind.number, revision_num)
		file_list = self.client.ls(svnurl_dir_path, revision)
		return file_list

	# ---<对【文件】的路径进行操作>---------------------------
	# 获取仓库文件信息
	def get_info(self):
		"""
		:return: entries (like dictionary), including various info about a file, such as file's url
		"""
		"""get information of given file; argument: None"""
		try:
			entry = self.client.info(self._local_file_path)
		except Exception:
			print 'Get info failed.'
			return
		return entry

	# ---<获取文件的svnurl>----------------------------
	def get_url(self):
		"""
		:return: string, SVN url points to the file stored in self._local_file_path
		"""
		"""get url of given file; argument: None"""
		entry = self.get_info()
		if entry is None:
			return
		return entry['url']

	# ---<获取服务器仓库中，SVNurl指向的【文件】最近数目为limit_num条log信息>--------
	def get_log(self, limit_num = 0):
		"""
		:param: int, the number of log info you want to load
				if limit_num = 0, there will be no limit.
		:return: dictionary, keys['author', 'date', 'message', 'revision' ...]
		"""
		import time
		rev_start = pysvn.Revision(pysvn.opt_revision_kind.head)
		self._svnurl = self.get_url()
		if self._svnurl is None:
			return
		log = self.client.log(self._svnurl, rev_start, limit=limit_num, discover_changed_paths=True)
		i = 0
		while i < len(log):
			log[i]['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log[i].date))
			i += 1
		return log

	# ---<从仓库获取版本号为revision_num的文件内容>-----------------------
	def load_file_content(self, revision_num):
		"""
		:param revision_num: int, the version you want to load
		:return: string, file content
		"""
		revision = pysvn.Revision(pysvn.opt_revision_kind.number, revision_num)
		print 'Loading file from:', self._svnurl, 'Revision num:', revision_num
		return self.client.cat(self._svnurl, revision)

	# ---<对比文件>--------------------------------------------------------
	def diff(self, svn_file, svn_re, local_file, local_re):
		"""
		:param svn_file: String, path of file on svn
		:param svn_re: int, revision number of local file
		:param local_file: String, path of local file
		:param local_re: int ,revision number of local file
		:return: String, containing the diff output
		"""
		"""compare files; arguments: svn_file_path, svn_revision, local_file_path, local_revision"""
		import os
		temp_path = self._local_file_path + '/' + 'temp'
		if not os.path.exists(temp_path):
			os.makedirs(temp_path)
		svn_rev = pysvn.Revision(pysvn.opt_revision_kind.number, svn_re)
		local_rev = pysvn.Revision(pysvn.opt_revision_kind.number, local_re)
		return self.client.diff(temp_path, url_or_path =self._svnurl + '/' + svn_file, revision1=svn_rev, url_or_path2=self._local_file_path + '/' + local_file, revision2=local_rev)
