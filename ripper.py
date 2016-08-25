from bs4 import BeautifulSoup
import urllib
import urlparse
import os
import sys
import argparse

konaBaseName = "http://konachan.com/post/show/"
yandereBaseName = "https://yande.re/post/show/"
danbooruBaseName = "https://danbooru.donmai.us/posts/"
danbooruImgPrefix = "https://danbooru.donmai.us"

def handleImage(id, website, tags, out):
	class imageData:
		tags = []
		img = ""
		name = ""

	def parseUrl(url):
		getObj = urllib.urlopen(url)
		rawHtml = getObj.read()
		soup = BeautifulSoup(rawHtml, 'html.parser')

		ret = imageData();

		if website == 'danbooru':
			sidebar = soup.find(id='tag-list')
			for item in sidebar.find_all():
				if item.name[0] == 'h':
					ret.tags.append('*' + item.get_text())
				else:
					for li in item.find_all('li'):
						tag = li.find_all('a')[1].get_text()
						ret.tags.append(tag)		
		else:
			sidebar = soup.find(id='tag-sidebar')
			for li in sidebar.find_all('li'):
				tag = li.find_all('a')[1].get_text()
				ret.tags.append(tag)

		ret.img = soup.find(id='image')['src']
		
		return ret;

	
	if website == 'danbooru':
		data = parseUrl(danbooruBaseName + str(id))
	elif website == 'konachan':
		data = parseUrl(konaBaseName + str(id))
	elif website == 'yandere':
		data = parseUrl(yandereBaseName + str(id))	

	fullname = urlparse.urlparse(data.img)[2]
	filename, ext = os.path.splitext(fullname)
	newFileName = str(id) + ext
	
	if website == 'danbooru':
		urllib.urlretrieve(danbooruImgPrefix + data.img, out + newFileName)
	else:
		urllib.urlretrieve(data.img, out + newFileName)
	
	if (tags):
		f = open(out + str(id), 'w')
		for tag in data.tags:
			f.write(tag + '\n')
		f.close()

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--start', default='1', type=int, help='The image ID to start ripping from', required=True)
parser.add_argument('-e', '--end', type=int, help='The image ID to end ripping at. If not provided only the ID provided to --start will be downloaded')
parser.add_argument('-w', '--website', '--site', default='konachan', help='The website to download from', choices=['konachan', 'danbooru', 'yandere'])
parser.add_argument('-o', '--out', default='out', help='The folder to download images to')
parser.add_argument('-t', '--tags', help='Download image tags as well.', action='store_true')
opts = parser.parse_args()

if opts.start > opts.end:
	print("start can not be greater than end")
	os._exit(1)
	
if opts.end:
	end = opts.end + 1
else:
	end = opts.start + 1
	
opts.out += '/'

try:
	os.mkdirs(opts.out)
except:
	pass
try:
	os.mkdir(opts.out)
except:
	pass
	
if not os.path.isdir(opts.out):
	print("Could not create the output folder")
	os._exit(1);
	
if not os.access(opts.out, os.W_OK):
	print("Do not have permission to write to the output folder")
	os._exit(1);
	
for i in range(opts.start, end):
	print(str(i) + '/' + str(end - 1))
	sys.stdout.flush()
	try:
		handleImage(i, opts.website, opts.tags, opts.out)
	except:
		print("Failed. (Likely the image does not exist or a network error occured)")
		sys.stdout.flush()
		pass


