import cmd
import locale
import os
import pprint
import shlex

from dropbox import client, rest, session

APP_KEY = 'vn6w5iuzrsolpix'
APP_SECRET = '4cggsz8ek8tv7bq'
ACCESS_TYPE = 'app_folder'  # should be 'dropbox' or 'app_folder' as configured for your app

class DropboxHelper:
	def __init__(self, app_key, app_secret):
		self.sess = StoredSession(app_key, app_secret, access_type=ACCESS_TYPE)
		self.api_client = client.DropboxClient(self.sess)
		self.current_path = ''
		self.sess.load_creds()

	def ls(self):
		resp = self.api_client.metadata(self.current_path)

		if 'contents' in resp:
			for f in resp['contents']:
				name = os.path.basename(f['path'])
				encoding = locale.getdefaultlocale()[1]
				print (('%s' % name).encode(encoding))

	def cd(self,path):
		"""change current working directory"""
		if path == "..":
			self.current_path = "/".join(self.current_path.split("/")[0:-1])
		else:
			self.current_path += "/" + path

	def login(self):
		"""log in to a Dropbox account"""
		try:
			self.sess.link()
		except rest.ErrorResponse, e:
			print('Error: %s' % str(e))

	def logout(self):
		"""log out of the current Dropbox account"""
		self.sess.unlink()
		self.current_path = ''

	def cat(self, path):
		"""display the contents of a file"""
		f, metadata = self.api_client.get_file_and_metadata(self.current_path + "/" + path)
		print(f.read())

	def mkdir(self, path):
		"""create a new directory"""
		self.api_client.file_create_folder(self.current_path + "/" + path)

	def rm(self, path):
		"""delete a file or directory"""
		self.api_client.file_delete(self.current_path + "/" + path)

	def mv(self, from_path, to_path):
		"""move/rename a file or directory"""
		self.api_client.file_move(self.current_path + "/" + from_path,
								  self.current_path + "/" + to_path)

	def account_info(self):
		"""display account information"""
		f = self.api_client.account_info()
		pprint.PrettyPrinter(indent=2).pprint(f)

	def get_file(self, from_path, to_path):
		"""
		Copy file from Dropbox to local file and print out out the metadata.

		Examples:
		Dropbox> get file.txt ~/dropbox-file.txt
		"""
		to_file = open(os.path.expanduser(to_path), "wb")

		f, metadata = self.api_client.get_file_and_metadata(self.current_path + "/" + from_path)
		print 'Metadata:', metadata
		to_file.write(f.read())

	def put_file(self, from_path, to_path, overwrite):
		"""
		Copy local file to Dropbox

		Examples:
		Dropbox> put ~/test.txt dropbox-copy-test.txt
		"""
		from_file = open(os.path.expanduser(from_path), "rb")

		self.api_client.put_file(self.current_path + "/" + to_path, from_file, overwrite)

	def search(self, string):
		"""Search Dropbox for filenames containing the given string."""
		results = self.api_client.search(self.current_path, string)
		for r in results:
			print("%s" % r['path'])


class StoredSession(session.DropboxSession):
	"""a wrapper around DropboxSession that stores a token to a file on disk"""
	TOKEN_FILE = "token_store.txt"

	def load_creds(self):
		try:
			stored_creds = open(self.TOKEN_FILE).read()
			self.set_token(*stored_creds.split('|'))
			print "[loaded access token]"
		except IOError:
			pass # don't worry if it's not there

	def write_creds(self, token):
		f = open(self.TOKEN_FILE, 'w')
		f.write("|".join([token.key, token.secret]))
		f.close()

	def delete_creds(self):
		os.unlink(self.TOKEN_FILE)

	def link(self):
		request_token = self.obtain_request_token()
		url = self.build_authorize_url(request_token)
		print "url:", url
		print "Please authorize in the browser. After you're done, press enter."
		raw_input()

		self.obtain_access_token(request_token)
		self.write_creds(self.token)

	def unlink(self):
		self.delete_creds()
		session.DropboxSession.unlink(self)

def main():
	if APP_KEY == '' or APP_SECRET == '':
		exit("You need to set your APP_KEY and APP_SECRET!")
	dbHelper = DropboxHelper(APP_KEY, APP_SECRET)
	dbHelper.ls()
	dbHelper.put_file("test.txt","test.txt",True)
	dbHelper.cat("test.txt")

if __name__ == '__main__':
	main()
