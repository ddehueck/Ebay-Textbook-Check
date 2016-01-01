import urllib2
import json

def canbefloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False
#Ended at 23 last night
for j in range(49, 101):
	print "On loop: " + str(j)

	listingsPage = str(j)
	categoryId = '171243' #http://pages.ebay.com/sellerinformation/growing/categorychanges/books.html for different categoryIds
	appID = 'DevindeH-618e-4c32-8f45-33931bd2bd72'

	listingsUrl = 'http://svcs.ebay.com/services/search/FindingService/v1?'
	listingsUrl += 'OPERATION-NAME=findItemsByCategory'
	listingsUrl += '&SERVICE-VERSION=1.0.0'
	listingsUrl += '&SECURITY-APPNAME=' + appID
	listingsUrl += '&RESPONSE-DATA-FORMAT=JSON'
	listingsUrl += '&REST-PAYLOAD'
	listingsUrl += '&categoryId=' + categoryId
	listingsUrl += '&paginationInput.pageNumber=' + listingsPage

	response = urllib2.urlopen(listingsUrl)
	listingsJSON = json.load(response)

	if listingsJSON['findItemsByCategoryResponse'][0]['ack'][0] == 'Success':
		
		if 'item' in listingsJSON['findItemsByCategoryResponse'][0]['searchResult'][0].keys():

			listingArray = listingsJSON['findItemsByCategoryResponse'][0]['searchResult'][0]['item']
			loopCounter = 0

			for item in listingArray:
				#Some items appear to not always have a product ID
				if 'productId' in item.keys():

					productId = item['productId'][0]['__value__']

					if 'shippingServiceCost' in item['shippingInfo'][0].keys():
						shippingCost = item['shippingInfo'][0]['shippingServiceCost'][0]['__value__']
					else:
						shippingCost = 0.00

					itemCost = item['sellingStatus'][0]['currentPrice'][0]['__value__']

					totalCost = float(itemCost) + float(shippingCost)

					productDetailsUrl = 'http://svcs.ebay.com/services/marketplacecatalog/ProductService/v1?';
					productDetailsUrl += 'OPERATION-NAME=getProductDetails'
					productDetailsUrl += '&SERVICE-VERSION=1.3.0';
					productDetailsUrl += '&SECURITY-APPNAME=' + appID;
					productDetailsUrl += '&GLOBAL-ID=EBAY-US';
					productDetailsUrl += '&RESPONSE-DATA-FORMAT=JSON';
					productDetailsUrl += '&productDetailsRequest.productIdentifier.ePID=' + productId;

					productDetailsResponse = urllib2.urlopen(productDetailsUrl)
					productDetailsJSON = json.load(productDetailsResponse)

					if 'productDetails' in productDetailsJSON['getProductDetailsResponse'][0]['product'][0].keys():
						
						ISBN = productDetailsJSON['getProductDetailsResponse'][0]['product'][0]['productDetails'][0]['value'][0]['text'][0]['value'][0]

						#Make sure the ISBN is the right length
						if len(ISBN) <= 13:
							bookScouterUrl = 'http://bookscouter.com/tools/historic.php?isbn=' + ISBN

							bookScouterResponse = urllib2.urlopen(bookScouterUrl)
							html = bookScouterResponse.read(bookScouterResponse)

							#Make sure there isn't a captch before looping again
							if html.find('Verify to continue') != -1:
								check = raw_input("There may be a captcha check then comback and ENTER 'y' to continue: ")
								bookScouterUrl = 'http://bookscouter.com/tools/historic.php?isbn=' + ISBN

								bookScouterResponse = urllib2.urlopen(bookScouterUrl)
								html = bookScouterResponse.read(bookScouterResponse)

							counter = 0
							sellForPrice = 0

							for i in range(len(html)):
								if counter >= 2:
									break
								elif html[i] == '$':
									priceString = html[i + 1] + html[i + 2] + html[i + 3] + html[i + 4]
									
									if canbefloat(priceString):
										sellForPrice = sellForPrice + float(priceString)
									else:
										sellForPrice = 0
										break

									counter = counter + 1
							
							sellForPrice = sellForPrice / 2
							print sellForPrice
							
							if sellForPrice > totalCost:
								print "The profit is: $" + str(sellForPrice - totalCost)
								print "Get the book from here: " + item['viewItemURL'][0]
								print "Sell the book here: " + bookScouterUrl

	else:
		
		print 'There was an Error: ' + listingsJSON['findItemsByCategoryResponse'][0]['errorMessage'][0]['error'][0]['message'][0]


