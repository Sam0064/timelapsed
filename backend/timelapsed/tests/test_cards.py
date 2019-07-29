from rest_framework.test import APITestCase

from django.contrib.auth.models import User

from ..models import Users, Topic, Date_Range, Card, Subclass, Topic_Relationships,  Subclass_Relationships

from django.test import TestCase

import json

from django.core.exceptions import ObjectDoesNotExist

import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError


## Use decode_response do get object payload ##

def decode_response(res):
  d = res.content.decode()
  return json.loads(d)


class CardModelTest(TestCase):

  @classmethod
  def setUpTestData(cls):
    Users.objects.create(Email = 'test@test.com')
    Topic.objects.create(Name = 'ModelsTest', Position = 1, Email = Users.objects.get(Email = 'test@test.com'))

  def test_succeds_with_proper_information(self):
    test = Card.objects.create(Name = 'First', Description = 'Test', Position = 1, Email = Users.objects.get(Email = 'test@test.com'), Topic = Topic.objects.get(Name = 'ModelsTest') )
    data = Card.objects.get(Name = 'First', Description = 'Test', Position = 1)
    self.assertEqual(data.Name, 'First' )
    self.assertEqual(data.Description, 'Test')
    self.assertEqual(data.Position, 1)

  def test_fails_when_incomplete(self):
    with self.assertRaises(ValidationError):
      Card.objects.create(Name = 'First', Position = 1, Email = Users.objects.get(Email = 'test@test.com'), Topic = Topic.objects.get(Name = 'ModelsTest') )          

  




class TestCardResponses(APITestCase):

  # This class tests our post responses without considering our date/times. Use the date_range classes for that. 

  topic_id = 0

  def setUp(self):
    #Runs before every test

    ###USE THE FOLLOWING BOILERPLATE BEFORE EVERY REQUEST###
    user = User.objects.create_user('test@test.com', 'test@test.com')
    self.client.force_authenticate(user)
    ######################################################


  @classmethod
  def setUpTestData(cls):
    Users.objects.create(Email = 'test@test.com')
    set_up_topic = Topic.objects.create(Name = 'UseForTesting', Position = 1, Email = Users.objects.get(Email = 'test@test.com') )
    cls.topic_id = set_up_topic.id

  def test_for_topic_setup(self):
    #Checks to make sure a topic ID was added
    self.assertNotEqual(self.topic_id, 0)

  def test_if_rejects_get(self):
    response = self.client.get('/api/card/')

    self.assertEqual(response.status_code, 405) 

  def test_if_accepts_post(self):
    response = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')

    self.assertEqual(response.status_code, 201)

  def test_if_rejects_Empty_post(self):
    response = self.client.post('/api/card/', {})

    self.assertEqual(response.status_code, 400) 
  def test_if_rejects_wrong_post_name(self):
    response = self.client.post('/api/card/', {'Data': {'Drame': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')

    self.assertEqual(response.status_code, 400)

  def test_if_post_rejects_invalid_topic(self):
    response = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': 800000}}, format = 'json')

    self.assertEqual(response.status_code, 400)

  def test_if_accepts_put_with_Name(self):
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']
    response = self.client.put(f'/api/card/{first_id}/', {'Data':{'Name': 'First'}}, format= 'json')

    self.assertEqual(response.status_code, 200)

  def test_if_accepts_put_with_description(self):
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']
    response = self.client.put(f'/api/card/{first_id}/', {'Data':{'Description': 'Changed'}}, format= 'json')    

    self.assertEqual(response.status_code, 200)

  def test_if_rejects_empty_put(self):
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']
    response = self.client.put(f'/api/card/{first_id}/', {}, format= 'json')

    self.assertEqual(response.status_code, 400)

  def test_if_put_rejects_invalid_id(self):

    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']
    response = self.client.put(f'/api/card/8000/', {'Data':{'Name': 'First'}}, format= 'json')

    self.assertEqual(response.status_code, 404)

  def test_if_put_rejects_invalid_topic(self):
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']
    response = self.client.put(f'/api/card/{first_id}/', {'Data':{'Topic': 8000}}, format= 'json')    

    self.assertEqual(response.status_code, 400)

  def test_if_put_accepts_valid_position(self):

    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']
    second = self.client.post('/api/card/', {'Data': {'Name': 'Second', 'Description': 'Tester', 'Topic': self.topic_id}}, format = 'json')
    second_id = decode_response(second)['Data']['id']    

    response = self.client.put(f'/api/card/{second_id}/', {'Data':{'Switch_Position': first_id}}, format= 'json')      

    self.assertEqual(response.status_code, 200)

  def test_if_put_rejects_invalid_position(self):

    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']

    response = self.client.put(f'/api/card/{first_id}/', {'Data':{'Switch_Position': 8000}}, format= 'json')      

    self.assertEqual(response.status_code, 400)

  def test_if_put_accepts_valid_topic(self):
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']

    switch_topic = Topic.objects.create(Name = 'UseForTesting', Position = 2, Email = Users.objects.get(Email = 'test@test.com') )

    response = self.client.put(f'/api/card/{first_id}/', {'Data':{'Switch_Topic': switch_topic.id}}, format= 'json')    

    self.assertEqual(response.status_code, 200)
  
  def test_if_put_accepts_own_topic(self):
    #Yes it's dumb, but there may be issues (especially with concurrency) where you may have this situation. 
    #We are going to allow it is it does nothing to harm the product. 
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']


    response = self.client.put(f'/api/card/{first_id}/', {'Data':{'Switch_Topic': self.topic_id}}, format= 'json')    

    self.assertEqual(response.status_code, 200)
  
  def test_if_put_accepts_own_position(self):
    #Reasoning is same as above. 
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']


    response = self.client.put(f'/api/card/{first_id}/', {'Data':{'Switch_Position': first_id}}, format= 'json')    

    self.assertEqual(response.status_code, 200)    

  
  def test_if_accepts_delete(self):

    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']


    response = self.client.delete(f'/api/card/{first_id}/')    

    self.assertEqual(response.status_code, 200)    


  def test_if_delete_rejects_invalid_id(self):

    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']


    response = self.client.delete(f'/api/card/8000/')    

    self.assertEqual(response.status_code, 404)    



class TestCardFunctionality(APITestCase):
  topic_id = 0

  def setUp(self):
    #Runs before every test

    ###USE THE FOLLOWING BOILERPLATE BEFORE EVERY REQUEST###
    user = User.objects.create_user('test@test.com', 'test@test.com')
    self.client.force_authenticate(user)
    ######################################################


  @classmethod
  def setUpTestData(cls):
    Users.objects.create(Email = 'test@test.com')
    set_up_topic = Topic.objects.create(Name = 'UseForTesting', Position = 1, Email = Users.objects.get(Email = 'test@test.com') )
    cls.topic_id = set_up_topic.id

  def test_for_topic_setup(self):
    #Checks to make sure a topic ID was added
    self.assertNotEqual(self.topic_id, 0)

  def test_card_name_creates_correctly(self):

    response = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    self.assertEqual(decode_response(response)['Data']['Name'], 'First' )

  def test_card_description_creates_correctly(self):
    
    response = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    self.assertEqual(decode_response(response)['Data']['Description'], 'Test' )    

  def test_card_position_creates_correctly(self):
    response = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json') 
    response_id = decode_response(response)['Data']['id']       
    self.assertEqual( Card.objects.get(id = response_id).Position , 1)

  def test_card_creates_in_proper_topic(self):
    
    response = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json') 
    response_id = decode_response(response)['Data']['id']       
    self.assertEqual( Card.objects.get(id = response_id).Topic , Topic.objects.get(id = self.topic_id))    

  def test_card_updates_name_correctly(self):
    
    response = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    response_id = decode_response(response)['Data']['id']  

    second =  self.client.put(f'/api/card/{response_id}/', {'Data': {'Name': 'Changed'}}, format = 'json' )

    self.assertEqual(decode_response(second)['Edit'][f'{response_id}']['Name'], 'Changed')

  def test_card_updates_description_correctly(self):

    response = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    response_id = decode_response(response)['Data']['id']  

    second =  self.client.put(f'/api/card/{response_id}/', {'Data': {'Description': 'Changed'}}, format = 'json' )

    self.assertEqual(decode_response(second)['Edit'][f'{response_id}']['Description'], 'Changed')   

  def test_card_names_not_unique(self):

    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'REally_First', 'Topic': self.topic_id}}, format = 'json')
    second = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Second', 'Topic': self.topic_id}}, format = 'json')        
    first_name = decode_response(first)['Data']['Name']      
    second_name = decode_response(second)['Data']['Name']    

    self.assertEqual(first_name, second_name)  

  def test_card_descriptions_not_unique(self):
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    second = self.client.post('/api/card/', {'Data': {'Name': 'Second', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')        
    first_description = decode_response(first)['Data']['Description']      
    second_description = decode_response(second)['Data']['Description']    

    self.assertEqual(first_description, second_description)      


  def test_card_changes_topic_correctly(self):

    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']  
    changed_topic =  Topic.objects.create(Name = 'changed', Position = 2, Email = Users.objects.get(Email = 'test@test.com') )
    self.client.put(f'/api/card/{first_id}/', {'Data': {'Switch_Topic': changed_topic.id}}, format = 'json' ) 

    self.assertEqual(Card.objects.get(id = first_id).Topic, changed_topic)

  def test_card_changes_position_correctly(self):   

    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'test', 'Topic': self.topic_id}}, format = 'json')
    second = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'test', 'Topic': self.topic_id}}, format = 'json')        
    first_id = decode_response(first)['Data']['id']      
    second_id = decode_response(second)['Data']['id']    
    self.client.put(f'/api/card/{first_id}/', {'Data': {'Switch_Position': second_id}}, format = 'json' )

    self.assertEqual(Card.objects.get(id = first_id).Position, 2)    
  
  def test_card_goes_to_correct_position_when_moved_to_new_topic(self):
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']  
    changed_topic =  Topic.objects.create(Name = 'changed', Position = 2, Email = Users.objects.get(Email = 'test@test.com') )
    second = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'test', 'Topic': changed_topic.id}}, format = 'json') 
    second_id = decode_response(second)['Data']['id']        
    self.client.put(f'/api/card/{first_id}/', {'Data': {'Switch_Topic': changed_topic.id}}, format = 'json' ) 

    self.assertEqual(Card.objects.get(id = first_id).Position, 2)


  def test_card_goes_to_correct_position_when_topic_and_position_changed(self):
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']  
    changed_topic =  Topic.objects.create(Name = 'changed', Position = 2, Email = Users.objects.get(Email = 'test@test.com') )
    second = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'test', 'Topic': changed_topic.id}}, format = 'json') 
    second_id = decode_response(second)['Data']['id']        
    self.client.put(f'/api/card/{first_id}/', {'Data': {'Switch_Topic': changed_topic.id, 'Switch_Position': second_id}}, format = 'json' ) 

    self.assertEqual(Card.objects.get(id = first_id).Position, 1)


  def test_if_cards_delete_when_topic_deletes(self):
    to_delete =  Topic.objects.create(Name = 'changed', Position = 2, Email = Users.objects.get(Email = 'test@test.com') )
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'test', 'Topic': to_delete.id}}, format = 'json') 
    first_id = decode_response(first)['Data']['id']
    self.client.delete(f'/api/topic/{to_delete.id}/')

    with self.assertRaises(ObjectDoesNotExist):
      Card.objects.get(id = to_delete.id)

  def test_card_iterates_highest_position_in_topic(self):
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'test', 'Topic': self.topic_id}}, format = 'json')
    second = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'test', 'Topic': self.topic_id}}, format = 'json')
    third = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'test', 'Topic': self.topic_id}}, format = 'json')
    second_id = decode_response(second)['Data']['id']

    self.client.delete(f'/api/card/{second_id}/')
    fourth = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'test', 'Topic': self.topic_id}}, format = 'json')
    fourth_id = decode_response(fourth)['Data']['id']
    self.assertEqual(Card.objects.get(id = fourth_id).Position, 4)

  def test_card_iterates_highest_position_in_topic_after_move_out(self):
    second_topic =  Topic.objects.create(Name = 'changed', Position = 2, Email = Users.objects.get(Email = 'test@test.com') )
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'test', 'Topic': second_topic.id}}, format = 'json') 
    first_id = decode_response(first)['Data']['id']
    self.client.put(f'/api/card/{first_id}/', {'Data': {'Switch_Topic': self.topic_id}}, format = 'json'  )
    second = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'test', 'Topic': second_topic.id}}, format = 'json')
    second_id = decode_response(second)['Data']['id']

    self.assertEqual(Card.objects.get(id = second_id).Position, 1)

  def test_card_deletes_correctly(self):
    first = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')
    first_id = decode_response(first)['Data']['id']      
    self.client.delete(f'/api/card/{first_id}/')

    with self.assertRaises(ObjectDoesNotExist):
      Card.objects.get(id = first_id)


