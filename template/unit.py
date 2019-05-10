# coding=utf-8
from google.appengine.ext import blobstore, ndb

class unit(ndb.Model):
	# 分類
	born = ndb.DateTimeProperty(auto_now_add=True)
	last = ndb.DateTimeProperty(auto_now=True)
	area = ndb.StringProperty()
	kusr = ndb.KeyProperty()
	kart = ndb.KeyProperty()
	kitm = ndb.KeyProperty()
	# 文章検索用
	name = ndb.StringProperty()
	iden = ndb.StringProperty()
	addr = ndb.StringProperty()
	ukey = ndb.StringProperty()
	usec = ndb.StringProperty()
	# 文章
	text = ndb.TextProperty()
	desc = ndb.TextProperty()
	# 数値
	time = ndb.DateTimeProperty()
	rank = ndb.IntegerProperty()
	rankview = ndb.IntegerProperty()
	ranklike = ndb.IntegerProperty()
	rankunit = ndb.IntegerProperty()
	rankrate = ndb.FloatProperty()
	# JSON
	smalljson = ndb.JsonProperty()
	largejson = ndb.JsonProperty()
	# ファイル
	smallblob = ndb.BlobProperty()
	largeblob = ndb.BlobProperty()
	smallfile = ndb.BlobKeyProperty()
	largefile = ndb.BlobKeyProperty()

	def format(s):
		return s.to_dict()

	@classmethod
	def key_by_id(cls, id):
		return ndb.Key(cls,int(id))

	@classmethod
	def delete_multi(cls, keys):
		ndb.delete_multi(keys)

	@classmethod
	def get_multi(cls, keys):
		return ndb.get_multi(keys)

	@classmethod
	def put_multi(cls, keys):
		ndb.put_multi(keys)

	@classmethod
	def _pre_delete_hook(c, k):
		self = k.get()
		blobstore.delete([self.smallfile, self.largefile])
		ndb.delete_multi(c.query(ndb.OR(c.kusr == self.key, c.kart == self.key, c.kitm == self.key)).fetch(keys_only=True))