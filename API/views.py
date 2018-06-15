from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from BasicArticle.models import Articles
from BasicArticle.serializers import ArticleSerializer

# Create your views here.

class get_Recommendations(APIView):
	def get(self,request):
	
		'''
		 Sample article id's are taken
		'''
		
		article_ids = [1,3,5,6,9]
		output = []
		for article_id in article_ids:
			article = Articles.objects.get(id=article_id)
			output.append({'id':article.id,'title':article.title,'body':article.body})
		serializer = ArticleSerializer(output,many=True)
		return Response(serializer.data)
		
	def post(self):
		pass
