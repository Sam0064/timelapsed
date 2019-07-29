from django.shortcuts import render
from rest_framework import viewsets 
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import json
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.

from .models import Users, Topic, Date_Range, Card, Subclass, Topic_Relationships, Card_Relationship_Parent_Action

from .serializers import UsersSerializer, AddTopicSerializer, CreateCardSerializer, EditTopicSerializer , DeleteTopicSerializer, DeleteCardSerializer, UpdateCardSerializer, CreateSubclassSerializer, TopicRelationshipsSerializer, EditSubclassSerializer, DeleteSubclassSerializer, GetSubclassSerializer, CreateCardRelationshipsSerializer, CircularityCheckSerializer, CircularityCutSerializer, CircularityPruneSerializer, DeleteCardRelationshipsSerializer

import  timelapsed.services as services



class UsersView(viewsets.ModelViewSet):
  #UsersView is designed to either create a user, or respond back with a users data.
  queryset= Users.objects.all()
  permission_classes = (IsAuthenticated, )
  serializer_class= UsersSerializer
  http_method_names = ['post']


  def create(self, request):
    queryset= Users.objects.all()
    serializer = UsersSerializer(data = request.data)
    if serializer.is_valid():
      test = Users.objects.filter(Email = serializer.data['Email'])
      if test:
        info = services.get_user_information(serializer.data)
        #Returning information about an exising record.

        return Response(info, 200)
      

      serializer.create(serializer.data)
      
      return Response(serializer.data, 201)

      #We created a new record
    return Response('not found', 400)




class TopicView(viewsets.ModelViewSet):
  serializer_class= AddTopicSerializer
  queryset= Topic.objects.all()
  permission_classes = (IsAuthenticated, )
  http_method_names = ['post', 'put', 'delete']

  def create (self, request):
    serializer = AddTopicSerializer(data = request.data)
    if serializer.is_valid():
      created = serializer.create(serializer.data, request.user.email)
      return Response(created, 201)
    
    print(serializer.errors)
    
    return Response('Bad request', 400)


  def update(self, request, pk):
    
    serializer = EditTopicSerializer(data = request.data)
    if serializer.is_valid():
      updated = serializer.update(serializer.data, pk)
      return Response(updated, 200)
    
    print(serializer.errors)

    return Response('Bad Request', 400)


  def destroy(self, request, pk):
    serializer = DeleteTopicSerializer(data = {})
    if serializer.is_valid():
      serializer.delete(pk)
      return Response('deleted', 204)
    
    print(serializer.errors)      

    return Response('Bad Request', 400)



class CardView(viewsets.ModelViewSet):
  serializer_class= CreateCardSerializer
  queryset= Card.objects.all()
  permission_classes = (IsAuthenticated, )
  http_method_names = ['post', 'put', 'delete' ]

  def create(self, request):
    serializer = CreateCardSerializer(data= request.data)
    if(serializer.is_valid()):
      created =  serializer.create(serializer.data, request.user.email)
      return Response(created , 201)


      print(serializer.errors)

    return Response('Bad Request', 400)

  def update(self, request, pk):
    serializer = UpdateCardSerializer(data = request.data)
    if(serializer.is_valid()):
      updated = serializer.update(serializer.data, pk, request.user.email)
      return Response(updated, 200)

    print(serializer.errors)
    
    return Response('Bad Request', 400)

  def destroy(self, request, pk):
    serializer = DeleteCardSerializer(data = {id:pk})
    if(serializer.is_valid()):
      destroy = serializer.destroy(pk)
      return Response(destroy, 200)

    print(serializer.errors)
    
    return Response('Bad Request', 400) 

class SubclassesView(viewsets.ModelViewSet):
  serializer_class= CreateSubclassSerializer
  queryset= Subclass.objects.all()
  permission_classes = (IsAuthenticated, )
  http_method_names = ['get', 'post', 'put', 'delete' ]

  def retrieve(self, request, pk):
    serializer = GetSubclassSerializer(data = request.data)
    if serializer.is_valid():
      found = serializer.get(pk)
      return Response(found, 200)

    print(serializer.errors)

    return Response('Bad Request', 400)


  def create(self, request):
    serializer = CreateSubclassSerializer(data = request.data)
    if serializer.is_valid():
      created = serializer.create(serializer.data, request.user.email)
      return Response(created, 201)
    
    print(serializer.errors)

    return Response('Bad Request', 400)


  def update(self, request, pk):
    serializer = EditSubclassSerializer(data = request.data)
    if serializer.is_valid():
      updated = serializer.update(serializer.data, pk, request.user.email)
      return Response(updated, 200)

    print(serializer.errors)

    return Response('Bad Request', 400)


  def destroy(self, request, pk):
    #request has the id of the card
    serializer = DeleteSubclassSerializer(data = request.data)
    if serializer.is_valid():
      serializer.destroy(pk)
      return Response('Deleted', 204)

    print(serializer.errors)

    return Response('Bad Request', 400)

class CardRelationshipsView(viewsets.ModelViewSet):
  queryset= Card_Relationship_Parent_Action.objects.all()
  permission_classes = (IsAuthenticated, )
  http_method_names = ['post', 'delete' ]

  def create(self, request):

    serializer = CreateCardRelationshipsSerializer(data = request.data)
    if serializer.is_valid():
      created = serializer.create(serializer.data, request.user.email)
      return Response(created, 201)

    print(serializer.errors)

    return Response('Bad Request', 400)


    #Allows for the following arguments: Move, Same, Delete, Subclass, Tag

    return
  def destroy(self, request, pk):

    serializer = DeleteCardRelationshipsSerializer(data = request.data)
    if serializer.is_valid():
      serializer.destroy(pk)
      return Response('Deleted', 204)

    return Response('Bad Request', 400)


class TopicRelationshipsView(viewsets.ModelViewSet):
  serializer_class= TopicRelationshipsSerializer
  queryset= Topic_Relationships.objects.all()
  permission_classes = (IsAuthenticated, )
  http_method_names = ['post', 'put', 'delete' ]

  def create(self, request):
    
    return
  def update(self, request):
    return
  def destroy(self, request):
    return


class CircularityCheckView(viewsets.ModelViewSet):
  serializer_class= CircularityCheckSerializer
  queryset= Card.objects.all()
  permission_classes = (IsAuthenticated, )
  http_method_names = ['get']

  def retrieve(self, request):

    #checks for circularity from a card.

    #If no circularity, then returns a 200.

    #If circularity, will return the option to either cut or prune. 

    #Cutting simply removes a bad relationship, the existing relationships are split at the bad relationship. 

    #Pruning deletes a relationship and every relationship afterwards. 


    return

class CircularityCheckCut(viewsets.ModelViewSet):
  serializer_class= CircularityCutSerializer
  queryset= Card.objects.all()
  permission_classes = (IsAuthenticated, )
  http_method_names = ['get']


class CircularityCheckPrune(viewsets.ModelViewSet):
  serializer_class= CircularityPruneSerializer
  queryset= Card.objects.all()
  permission_classes = (IsAuthenticated, )
  http_method_names = ['get']