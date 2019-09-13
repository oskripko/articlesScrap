import newspaper
import csv
from newspaper import Article
import feedparser
from urllib.request import Request, urlopen
from urllib.parse import urljoin
import pickle
import nltk
from bs4 import BeautifulSoup as soup

source = {}
crushed = {}
result = {}

nltk.download('punkt')

def extractArticle(url):
	article = Article(url=url)
	try:
		article.download()
	except Exception as e:
		print(e)
	if article == None:
		print(f'no content in {url}')
		#try another thing
	else:
		try:
			article.parse()
		except Exception as e:
			print(e)
		print(article.title)
		return article

def extractFeedByParser(currentUrl):
	common_feed_urls = ['feed', 'feeds', 'rss']
	common_feed_urls = [urljoin(currentUrl, url) for url in common_feed_urls]
	for feedUrl in common_feed_urls:
		paper = feedparser.parse(feedUrl)
		if len(paper['entries']) > 1 :
			return paper['entries']
	



with open('categories.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    currentCategory = ''
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
        	if len(row[0]) != 0: 
        		currentCategory = row[0]
        		source[currentCategory] = []
        		source[currentCategory].append(row[1])
        	else: 
        		source[currentCategory].append(row[1])

for category, urls in source.items():
	extractedLinks = []
	for url in urls:
		try:
			paper = newspaper.build(url)
		except Exception as e:
			print(e)
		print(f'size is {paper.size()} for url {url}')
		if paper.size() == 0:
			entries = extractFeedByParser(url)
			if entries != None:
				for entry in entries[:5]:
					extractedLinks.append(entry['link'])
				source[category].remove(url)
				#to crushed
		else:
			if category not in result:
				result[category] = []
			for article in paper.articles[:5]:
				try:
					article.download()
					article.parse()
					article.nlp()
					req = Request(article.url , headers={'User-Agent': 'Mozilla/5.0'})
					webpage = urlopen(req).read()
					page_soup = soup(webpage, "html.parser")
					metatag = page_soup.find("meta", {"property": "og:image"})
					articleData = {
						'title': article.title,
						'author': article.authors,
						'content': article.text,
					}
					if metatag != None and metatag["content"] != None:
						print(metatag["content"])
						articleData['image'] = metatag["content"]
					result[category].append(articleData)
				except Exception as e:
					print(e)
			source[category].remove(url)
	source[category].extend(extractedLinks)
for category, urls in source.items():
	for url in urls:
		article = extractArticle(url)
		if article != None:
			if category not in result:
				result[category] = []
			try:
				req = Request(url , headers={'User-Agent': 'Mozilla/5.0'})
				webpage = urlopen(req).read()
				page_soup = soup(webpage, "html.parser")
				metatag = page_soup.find("meta", {"property": "og:image"})
				articleData = {
					'title': article.title,
					'author': article.authors,
					'content': article.text,
				}
				if metatag != None and metatag["content"] != None:
					print(metatag["content"])
					articleData['image'] = metatag["content"]
				result[category].append(articleData)
			except Exception as e:
				print(e)

with open('result.pickle', 'wb') as handle:
    pickle.dump(result, handle, protocol=pickle.HIGHEST_PROTOCOL)

# paper = feedparser.parse('https://fusiontantra.com/blog-2/feed')
# print(paper.entries[0]['link'] )
# print(len(paper['entries']))