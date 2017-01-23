from lxml import html
import json
import requests
import json,re
from dateutil import parser as dateparser
from time import sleep

def ParseReviews(asin):
	amazon_url  = 'http://www.amazon.in/dp/'+asin
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
	page = requests.get(amazon_url,headers = headers).text

	parser = html.fromstring(page)
	XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
	XPATH_REVIEW_SECTION = '//div[@id="revMHRL"]/div'
	XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
	XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
	XPATH_PRODUCT_PRICE  = '//span[@id="priceblock_saleprice"]/text()'
	XPATH_PRODUCT_DESC  = '//div[@id="productDescription"]/p/text()'
	XPATH_FEATURE = '//div[@id="feature-bullets"]//ul'	
	XPATH_IMAGE	= '//div[@id="altImages"]//ul'
	XPATH_SIZE = '//select[@id="native_dropdown_selected_size_name"]'
    #XPATH_PRODUCT_DESC = '//div[@id="productDescription"]/text()'
    #//*[@id="priceblock_saleprice"]#//*[@id="price"]/table/tbody/tr[1]/td[2]/span
    #//*[@id="feature-bullets"]#//ul[@id="altImages"]/ul/li/span/span/span/span/img
	feature_list = []
	image_list = []
	size_list = []
	raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
	feature = parser.xpath(XPATH_FEATURE)
	#print feature
	images = parser.xpath(XPATH_IMAGE)
	size = parser.xpath(XPATH_SIZE)
	#print size_list
	#print images
	for im in images:
		extracted_im = im.xpath('./li')
	for ii in extracted_im[1:]:
		 iii = ii.xpath('./span/span/span/span/text()')
		 print iii

	for ss in size:
		extracted_ss = ss.xpath('./option/text()')
		for i in extracted_ss:
			size_list.append(''.join(i).strip())
	
	#print size_list


	for feac in feature:
		extracted_feature = feac.xpath('./li/span/text()')
		#print extracted_feature
		for i in extracted_feature:
			feature_list.append(''.join(i).strip())
	#print feature_list
    #desc = parser.xpath(XPATH_PRODUCT_DESC)
	desc1 = parser.xpath(XPATH_PRODUCT_DESC)
	product_price = ''.join(raw_product_price).replace(',','')
	desc = ''.join(desc1).strip()
	raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
	product_name = ''.join(raw_product_name).strip()
	total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
	#print total_ratings
	reviews = parser.xpath(XPATH_REVIEW_SECTION)

	ratings_dict = {}
	reviews_list = []

	#grabing the rating  section in product page
	for ratings in total_ratings:
		extracted_rating = ratings.xpath('./td//a//text()')
		if extracted_rating:
			rating_key = extracted_rating[0]
			raw_raing_value = extracted_rating[1]
			rating_value = raw_raing_value
			if rating_key:
				ratings_dict.update({rating_key:rating_value})

	#Parsing individual reviews
	for review in reviews:
		XPATH_RATING  ='./div//div//i//text()'
		XPATH_REVIEW_HEADER = './div//div//span[contains(@class,"text-bold")]//text()'
		XPATH_REVIEW_POSTED_DATE = './/a[contains(@href,"/profile/")]/parent::span/following-sibling::span/text()'
		XPATH_REVIEW_TEXT_1 = './/div//span[@class="MHRHead"]//text()'
		XPATH_REVIEW_TEXT_2 = './/div//span[@data-action="columnbalancing-showfullreview"]/@data-columnbalancing-showfullreview'
		XPATH_REVIEW_COMMENTS = './/a[contains(@class,"commentStripe")]/text()'
		XPATH_AUTHOR  = './/a[contains(@href,"/profile/")]/parent::span//text()'
		XPATH_REVIEW_TEXT_3  = './/div[contains(@id,"dpReviews")]/div/text()'
		raw_review_author = review.xpath(XPATH_AUTHOR)
		raw_review_rating = review.xpath(XPATH_RATING)
		raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
		raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
		raw_review_text1 = review.xpath(XPATH_REVIEW_TEXT_1)
		raw_review_text2 = review.xpath(XPATH_REVIEW_TEXT_2)
		raw_review_text3 = review.xpath(XPATH_REVIEW_TEXT_3)

		author = ' '.join(' '.join(raw_review_author).split()).strip('By')

		#cleaning data
		review_rating = ''.join(raw_review_rating).replace('out of 5 stars','')
		review_header = ' '.join(' '.join(raw_review_header).split())
		review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
		review_text = ' '.join(' '.join(raw_review_text1).split())

		#grabbing hidden comments if present
		if raw_review_text2:
			json_loaded_review_data = json.loads(raw_review_text2[0])
			json_loaded_review_data_text = json_loaded_review_data['rest']
			cleaned_json_loaded_review_data_text = re.sub('<.*?>','',json_loaded_review_data_text)
			full_review_text = review_text+cleaned_json_loaded_review_data_text
		else:
			full_review_text = review_text
		if not raw_review_text1:
			full_review_text = ' '.join(' '.join(raw_review_text3).split())

		raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)
		review_comments = ''.join(raw_review_comments)
		review_comments = re.sub('[A-Za-z]','',review_comments).strip()
		review_dict = {
							'review_comment_count':review_comments,
							'review_text':full_review_text,
							'review_posted_date':review_posted_date,
							'review_header':review_header,
							'review_rating':review_rating,
							'review_author':author

						}
		reviews_list.append(review_dict)

	data = {
				'ratings':ratings_dict,
				'reviews':reviews_list,
				'url':amazon_url,
				'price':product_price,
				'name':product_name,
				'productDescription':desc,
				'features':feature_list,
				'size':size_list[1	:],
				'images':image_list
			}
	return data


def ReadAsin():
	#Add your own ASINs here
	AsinList = ['B01L7DYXL0',,'B016O81ZKU','B01KA62BRI']
	extracted_data = []
	for asin in AsinList:
		print "Downloading and processing page http://www.amazon.in/dp/"+asin
		extracted_data.append(ParseReviews(asin))
		#sleep(5)
	f=open('data.json','w')
	json.dump(extracted_data,f,indent=4)

if __name__ == '__main__':
	ReadAsin()

#