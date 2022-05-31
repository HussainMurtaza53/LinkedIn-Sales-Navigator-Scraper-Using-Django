from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from scraping.utils import *


class LinkedIn_Scraping(APIView):
    
    def post(self, request):
        
        try:
            params = request.data
            serializer = LinkedInSerializer(data = params)
            
            if serializer.is_valid(raise_exception = True):
                
                try:
                    query = params['query']
                    limit = params['limit']

                    link = "https://www.linkedin.com/sales/search/people?query={0}&limit={1}".format(query, limit)
                    
                    s_nav_scraper = Sales_Navigator_Scraper()
                    s_nav_scraper.start_browser(link)
                    s_nav_scraper.scrape(limit)
                    
                    context = {'Success': True}
                    return Response(context)
                    
                except Exception as e:
                    context = {'Error': str(e)}
                    return Response(context)

        except Exception as e:
            return Response({'Error': str(e)})