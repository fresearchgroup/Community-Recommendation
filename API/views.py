from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from BasicArticle.models import Articles
from BasicArticle.serializers import ArticleSerializer
from rest_framework.renderers import JSONRenderer
import os
# Create your views here.

class get_Recommendations(APIView):
	def get(self,request):
		#exec(open('/Recommend/predict.py').read())
		user_id = 10
		output = os.popen("python /home/ajay/Collaboration-System/API/predict.py --u /home/ajay/Collaboration-System/API/model/row.npy --v /home/ajay/Collaboration-System/API/model/col.npy --user-id "+ str(user_id)).read()
		'''article_ids = [1,3,5,6,9]
		output = []
		for article_id in article_ids:
			article = Articles.objects.get(id=article_id)
			#article = Articles.objects.all()
			output.append({'id':article.id,'title':article.title,'body':article.body})
		serializer = ArticleSerializer(output,many=True)'''
		return Response(output)
		
	def post(self):
		pass
