from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from scraping.models import *
import csv
from django.http import HttpResponse
from .thread import *


class Create_Job(APIView):
    
    def post(self, request):
        
        try:
            params = request.data
            serializer = LinkedInSerializer(data = params)
            
            if serializer.is_valid(raise_exception = True):
                
                try:
                    query = params['query']
                    limit = params['limit']

                    link = "https://www.linkedin.com/sales/search/people?query={0}&limit={1}".format(query, limit)
                    
                    job = Job_Status(total_records = limit, job_status = 'running')
                    job.save()
                    job_id = job.job_id
                    
                    Sales_Navigator_Scraper(link, limit, job_id).start()
                    
                    context = {'job_id': job_id}
                    return Response(context)
                    
                except Exception as e:
                    context = {'Error': str(e)}
                    return Response(context)

        except Exception as e:
            return Response({'Error': str(e)})

class Get_Job_Status(APIView):
    
    def get(self, request, *args, **kwargs):
        
        try:
            job_id = int(str(self.request).split('/')[-1].replace("'>", ""))
            job_status = Job_Status.objects.filter(job_id = job_id).values()
            
            return Response(job_status)

        except Exception as e:
            return Response({'Error': str(e)})

class Download_Job(APIView):
    
    def get(self, request, *args, **kwargs):
        
        try:
            job_id = int(str(self.request).split('/')[-1].replace("'>", ""))
            data_name = 'LinkedIn_Sales_Navigator_ID#{0}_Data.csv'.format(job_id)
            data = pd.read_csv('./LinkedIn_Data/{0}'.format(data_name))
            
            try:
                del data['Unnamed: 0']
            except:
                pass

            response = HttpResponse('')
            response['Content-Disposition'] = 'attachment; filename={0}'.format(data_name)
            writer = csv.writer(response)
            writer.writerow(['First_Name', 'Last_Name', 'Company', 'Company_URL', 'Job_Title', 'Location']
                        )
            
            records = data.to_records(index=False)
            result = list(records)

            for field in result:
                writer.writerow(field)
            
            return response

        except Exception as e:
            return Response({'Error': str(e)})