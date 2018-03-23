from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from IPython.core.display import display, HTML

class HobbyKingSaleFinder:
    mydict = {}
    
    
    """
        Handes the conection and cheks for getting the html
    """
    def __simple_get(self,url):
        try:
            with closing(get(url, stream=True)) as resp:
                if self.__is_good_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            self.__log_error('Error during requests to {0} : {1}'.format(url, str(e)))
            return None
        
        
    """
        Checks if the response is good getting the HTML
    """
    def __is_good_response(self,resp):
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200 
                and content_type is not None 
                and content_type.find('html') > -1)
    
    
    """
        Logs any Errors getting the HTML
    """
    def __log_error(self,e):
        print(e)
        
        
    """
        Gets the HTML form the given URL an converts to BeautifulSoup
    """
    def __getPage(self,pageURL):
        pageURL = pageURL+"&limit=150"
        #vvprint(pageURL)
        raw_html = self.__simple_get(pageURL)
        html = BeautifulSoup(raw_html, 'html.parser')
        return html

    
    """
        Finds the page count for searching the other pages
    """
    def __getPageCount(self,html):
        page_count = 1
        pages = html.findAll("div", class_="amount amount--has-pages")
        if(len(pages)>0):
            pages = pages[0].find_all('span')[1]
            page_count = pages.text.strip()[2:].strip()
        print ("Pages To Scan: "+str(page_count)) 

        return int(page_count)
            
        
    """
        Finds all the Items where "You Save is marked"
        extracs the discounted price, oraganal price, and product link
        stors the data in mydict
    """
    def __matchPage(self,html):
        for  i, ol  in enumerate(html.findAll("div", class_="product-shop")):
            name = None
            linkUrl = ""
            imgUrl = ""
            for child in list(ol.parent.children):

                if (child.name == 'div'):
                    if "product-image" in child['class']:
                         for img in child.div.findAll('img'):
                            imgUrl = str(img)
                            
                    if "product-shop" in child['class']:
                        for link in child.div.div.findAll('a'):
                            linkUrl=  str(link)
                                
                    if "product-list-bottom" in child['class'] and link is not "":
                        buyoption = child.findAll("form", class_="ajax-form")
                        if(len(buyoption) > 0):
                            priccList = child.findAll("span", class_="price-bargain")
                            if(len(priccList) > 1):
                                save = float(priccList[0].text.strip()[1:].replace(",",""))
                                price = priccList[1].text.strip().replace(",","")[1:]
                                if(float(price)>0 ):
                                    self.mydict["("+price+") "+imgUrl+linkUrl] = save 
    
    """
        Will retrive the given Url to search for the page count.
        will search for deals on the given page Url.
        if page count is found, will search for deals on
        all other pages off the given page URL.
    """
    def FindDeals(self,pageURL):
        self.mydict = {}
        
        if "?" not in pageURL:
            pageURL = pageURL+"?"
            
        html = self.__getPage(pageURL)
        page_count = self.__getPageCount(html)
        print ("page "+str(1)+" of "+ str(page_count))
        self.__matchPage(html)
        for thispage in range(2,int(page_count)+1):
            print ("page "+str(thispage)+" of "+ str(page_count))
            self.__matchPage(self.__getPage(pageURL+'p='+str(thispage)))
            
                                        
    """
        Displays a sorted by amount saved, list of the items found
    """
    def DisplayByPrice(self):
        for key in sorted(self.mydict, key=self.mydict.get, reverse=True):
            display(HTML("You save $"+str(self.mydict[key])+"  Now"+key))
            
            
    """
        Displays a sorted by percent off list of the items found
    """
    def DisplayByDiscount(self):
        newset = {}
        for key in sorted(self.mydict, key=self.mydict.get, reverse=True):
            list = key.split(')',1)
            name = list[1]
            price = list[0][1:]
            save = float(self.mydict[key])
            
            tag = "You save $"+str(self.mydict[key])+",-- Now("+price+") "+name
            newset[tag] = int((save/(save+float(price)))*100)

        for key in sorted(newset, key=newset.get, reverse=True):  
            #print ("%s: %s" % (newset[key],key))
            display(HTML(str(newset[key])+"% off,-- "+key))
            
