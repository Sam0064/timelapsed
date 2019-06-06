from rest_framework.test import APITestCase

from django.contrib.auth.models import User

from ..models import Users, Topic, Date_Range, Card, Subclass, Card_Relationships, Topic_Relationships,  Subclass_Relationships

from django.test import TestCase

import json



### NOTE: MIGRATE TO get_object_or_404 when searching for an item in the serializers ###

## Use decode_response do get object payload ##

def decode_response(res):
  d = res.content.decode()
  return json.loads(d)


class TestUsersResponses(APITestCase):


  def setUp(self):
    #Runs before every test

    ###USE THE FOLLOWING BOILERPLATE BEFORE EVERY REQUEST###
    user = User.objects.create_user('test@test.com', 'test@test.com')
    self.client.force_authenticate(user)
    ######################################################


  def tearDown(self):
    #Runs after every test
    pass

  def test_if_rejects_get(self):
    response = self.client.get('/api/user/')
    self.assertEqual(response.status_code, 405)
  
  def test_if_rejects_put(self):
    response = self.client.put('/api/user/')
    self.assertEqual(response.status_code, 405)

  def test_if_rejects_delete(self):
    response = self.client.delete('/api/user/')
    self.assertEqual(response.status_code, 405)

  def test_if_accepts_post(self):
    response = self.client.post('/api/user/', {'Email' : 'Test@test.com'})
    self.assertEqual(response.status_code, 201)

  def test_if_returns_200_when_valid(self):
    Users.objects.create(Email = 'Test@test.com')
    self.client.post('/api/user/', {'Email' : 'Test@test.com'}, format = 'json')    
    response = self.client.post('/api/user/', {'Email' : 'Test@test.com'}, format = 'json')
    self.assertEqual(response.status_code, 200)

    ### The services response that we get here is found in test_services.py

class TestTopicResponses(APITestCase):

  def setUp(self):

    #Runs before every test

    ###USE THE FOLLOWING BOILERPLATE BEFORE EVERY REQUEST###
    user = User.objects.create_user('test@test.com', 'test@test.com')
    self.client.force_authenticate(user)
    ######################################################
    Users.objects.create(Email = 'test@test.com')    


  def tearDown(self):
    Topic.objects.all().delete()    
    #clears the test database after every test. 


  def test_if_rejects_get(self):
    response = self.client.get('/api/topic/')
    self.assertEqual(response.status_code, 405)

  def test_if_accepts_put(self):
    pk = Topic.objects.create(Name = 'first', Position = 1, Email = Users.objects.get(Email = 'test@test.com'))
    response = self.client.put(f'/api/topic/{pk.id}/', {'Name': 'Changed'})
    self.assertEqual(response.status_code, 200)

  def test_if_rejects_put_for_invalid_id(self):
    response = self.client.put(f'/api/topic/80000/', {'Name': 'Exist'})
    self.assertEqual(response.status_code, 404)
  
  def test_if_accepts_post(self):
    response = self.client.post('/api/topic/', {'Name': 'Second'} )
    self.assertEqual(response.status_code, 201)
 
  def test_if_accepts_delete(self):
    pk = Topic.objects.create(Name = 'second', Position = 2,  Email = Users.objects.get(Email = 'test@test.com') )
    response = self.client.delete(f'/api/topic/{pk.id}/')
    self.assertEqual(response.status_code, 204)

  def test_if_rejects_delete_for_invalid_id(self):
    response = self.client.delete(f'/api/topic/80000/')
    self.assertEqual(response.status_code, 404)    


class TestTopicFunctionality(APITestCase):

  def setUp(self):

    #Runs before every test

    ###USE THE FOLLOWING BOILERPLATE BEFORE EVERY REQUEST###
    user = User.objects.create_user('test@test.com', 'test@test.com')
    self.client.force_authenticate(user)
    ######################################################
    Users.objects.create(Email = 'test@test.com')    


  def tearDown(self):
    Topic.objects.all().delete()    
    #clears the test database after every test. 

  def test_post_correctly_creates_topic_name(self):
    response = self.client.post('/api/topic/', {'Name': 'Testing'})
    self.assertEqual(decode_response(response)['Data']['Name'], 'Testing')

  def test_post_creates_topic_position(self):
    response = self.client.post('/api/topic/', {'Name': 'Testing'})    
    temp = Topic.objects.get(id = decode_response(response)['Data']['id'])
    ### As of now, position is not returned ###

    self.assertEqual(temp.Position, 1)

  def test_post_correctly_iterates_position(self):
    self.client.post('/api/topic/', {'Name': 'Testing'})    
    response = self.client.post('/api/topic/', {'Name': 'Two'})    
    temp = Topic.objects.get(id = decode_response(response)['Data']['id'])  
    self.assertEqual(temp.Position, 2)  

  
  def test_post_creates_card_list(self):
    response = self.client.post('/api/topic/', {'Name': 'Testing'})
    temp = decode_response(response)['Data']
    self.assertEqual(type(temp['Cards']), list)

  def test_post_creates_empty_cards_list(self):
    response = self.client.post('/api/topic/', {'Name': 'Testing'})
    temp = decode_response(response)['Data']
    self.assertEqual(len(temp['Cards']), 0)

  def test_put_correctly_changes_name(self):
    

    pass

  def test_put_correctly_changes_position(self):
    pass
  
  def test_put_correctly_changes_name_and_position(self):
    pass

  def test_delete_properly_deletes_topic(self):
    pass

  def test_post_reuses_position_after_deletion(self):
    pass

  def test_post_properly_iterates_highest_position_with(self):
    pass

  def test_post_allows_for_name_reuse(self):
    pass

  def test_put_allows_for_name_reuse(self):
    pass

  
  
  # def test_if_name_changes_correctly(self):
  #   Numbers may need changed. 
  #   temp = Topic.objects.create(Name = 'second', Position = 2, Email = Users.objects.get(Email = 'test@test.com'))
  #   response = self.client.put('/api/topic/2/', {'Name': 'Changed'})
  #   temp = Topic.objects.values('Name').get(Position = 2 )
  #   self.assertEqual(temp['Name'], 'Changed')
  


  # Add under cards. 
  # def test_if_cards_delete_when_topic_deletes(self):
  #   pass

