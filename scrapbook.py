#coding:utf-8
import os,sys,ConfigParser
import gtk,gtk.glade,gobject
import sqlite3,webkit,json

userhome = os.path.expanduser('~')
configfile = os.path.join(userhome,'.config','scrapbook','scrapbook')
browser = os.path.join(userhome,'.config','chromium','Default','databases')
browserdev = os.path.join(userhome,'.config','google-chrome','Default','databases')
list = {'stable':browser,'dev':browserdev}

class BookGtk():
	path = ''
	#初始化
	def __init__(self):
		self.builder = gtk.Builder()
		self.builder.add_from_file('scrapbook.ui')
		self.builder.connect_signals(self)
		self.liststore = self.builder.get_object('liststore')
		self.treestore = self.builder.get_object('treestore')
		self.itemlist = self.builder.get_object('itemlist')
		self.treeviewcolumn = self.builder.get_object('treeviewcolumn1')
		self.webkit_sw = self.builder.get_object('webkit_sw')
		self.webview = webkit.WebView()
		if(1):
			db = self.read_config()
			if(db):
				self.chrome_scrapbook(self,db)
				#self.treeviewcolumn.settitle()
			else:
				self.show_wizard(self)
		self.webkit_sw.add(self.webview)
		self.webview.load_html_string('<h1>StandBy</h1>','about:labs')

	#初始化/讀取配置文件
	def read_config(self):
		if os.path.isfile(configfile):
			print '>>>loading'
		elif os.path.isdir(os.path.join(userhome,'.config','scrapbook')):
			print '>>>mkfile'
			open(configfile,'w').close()
		else:
			print '>>>mkdir/mkfile'
			os.mkdir(os.path.join(userhome,'.config','scrapbook'))
			open(configfile,'w').close()
		self.config = ConfigParser.ConfigParser()
		self.config.read(configfile)
		if(self.config.has_section('global')):
			#.has_option#.remove_option#.remove_section#.sections#.options#.add_section#.set
			if(self.config.has_option('global','last')):
				return self.config.get('global', 'last')
		else:
			self.config.add_section('global')
			self.config.add_section('chrome-scrapbook')
			self.config.add_section('firefox-scrapbook')
			self.config.add_section('firefox-zotero')

	#關於對話框
	def show_about(self,widget):
		self.about = self.builder.get_object('about')
		self.about.run()
		self.about.hide()

	def show_wizard(self,widget):
		self.liststore.clear()
		self.wizard = self.builder.get_object('wizard')
		self.wizard_treeview = self.builder.get_object('wizard_treeview')
		self.wizard_treeviewcolumn = self.builder.get_object('wizard_treeviewcolumn')
		treelist = []
		for key,value in list.items():
			dbcon = sqlite3.connect(os.path.join(value,'Databases.db'))
			cur = dbcon.cursor()
			cur.execute("select id,origin,estimated_size from databases where name='scrapbook'")
			content = cur.fetchall()
			dbcon.close()
			for item in content:
				temp = []
				if key == 'dev':
					temp.append('Chromium')
				elif key == 'stable':
					temp.append('GoogleChrome')
				if item[1].split('_')[1] == 'gokffdfnlmampchciemmflgbckijpmlb':
					temp.append('Chrome-Scrapbook')
				else:
					temp.append('Chrome-Scrapbook Dev')
				temp.append(item[2])
				temp.append(os.path.join(value,item[1],str(item[0])))
				treelist.append(temp)
		for item in treelist:
			self.liststore.append([item[1]+' / '+item[0],item[3]])
		response = self.wizard.run()
		if response == gtk.RESPONSE_OK:
			row = self.wizard_treeview.get_selection().get_selected_rows()[1][0]
			db = self.wizard_treeview.get_model()[row][1]
			self.chrome_scrapbook(self,db)
			self.treeviewcolumn.set_title(self.wizard_treeview.get_model()[row][0])
		self.wizard.hide()

	def chrome_scrapbook(self,widget,db):
		def on_click(widget, row, col):
			model = widget.get_model()
			cur.execute('select content from document_contents where id='+model[row][1]+';')
			content = cur.fetchall()
			#self.webview.set_custom_encoding(chardet.detect(content[0])['encoding'])
			self.webview.load_html_string(content[0][0],'scrapbook://content')
		self.config.set('global','last',db)
		dbcon = sqlite3.connect(db)
		cur = dbcon.cursor()
		cur.execute('select id, header from documents order by created desc;')
		templist = cur.fetchall()
		self.treestore.clear()
		for item in templist:
			self.treestore.append(None,[item[1],item[0]])
		self.itemlist.connect('row-activated', on_click)

	def firefox_scrapbook(self,widget):
		pass

	def firefox_zotero(self,widget):
		pass

	def do_quit(self,widget):
		self.config.write(open(configfile,'w'))
		gtk.main_quit()

if __name__ == '__main__':
	BookGtk()
	gtk.main()