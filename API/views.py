from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from BasicArticle.models import Articles
from BasicArticle.serializers import ArticleSerializer
from rest_framework.renderers import JSONRenderer
import json
import os
import urllib.request
# Create your views here.

class get_Recommendations(APIView):
	def get(self,request):
		#exec(open('/Recommend/predict.py').read())
		user_id = request.user.id
		#print('userid is ', request.user.id)
		output = urllib.request.urlopen("http://10.196.7.8:3445/rec?user=" + str(user_id)).read()
		result = []
		output = json.loads(output.decode())
		for x in output["predictions"]:
			result.append({'id':output['map'][x]})
		serializer = ArticleSerializer(result,many=True)
		return JsonResponse({'output': result})
		

	def post(self):
		pass
